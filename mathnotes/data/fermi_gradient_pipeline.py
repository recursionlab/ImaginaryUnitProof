#!/usr/bin/env python3
"""
Fermi-LAT FITS download/format pipeline for spatial-gradient analysis.

Modes
-----
1) Download mode: provide a manifest CSV with columns:
     product,url_or_path,filename
   HTTP(S) URLs are downloaded; local paths are copied/linked into the workdir.
2) Format mode: read event + optional spacecraft/ltcube/diffuse files, apply ROI cuts,
   standardize FITS metadata, build counts/exposure-aware products, and write gradient maps.

Typical products you will put in the manifest:
- photon events: PHOTON event list, e.g. evfile (FT1-like)
- spacecraft: SC file (FT2-like) for gtmktime/fermipy
- livetime cube: optional if already made
- diffuse model: e.g. gll_iem_v07.fits and matching isotropic template, for binned analysis context

This formatter intentionally does not run ScienceTools/gtselect/gtmktime itself if they are not
installed; it implements equivalent event filtering with astropy/numpy and leaves header hooks for
ScienceTools/fermipy-compatible products.
"""
import argparse, csv, shutil, sys, hashlib
from pathlib import Path
import numpy as np
from astropy.io import fits
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
from astropy.time import Time

REQ = ["astropy", "numpy"]

def download_or_link(row, destdir: Path):
    product = str(row.get("product", "file"))
    src = str(row.get("url_or_path", "")).strip()
    name = str(row.get("filename") or Path(src.split("?")[0]).name or product).strip()
    if not src:
        raise ValueError(f"manifest row missing url_or_path for {product}")
    dest = destdir / name
    if src.startswith(("http://", "https://")):
        import requests
        if not dest.exists():
            with requests.get(src, stream=True, timeout=120) as r:
                r.raise_for_status()
                tmp = dest.with_suffix(dest.suffix + ".part")
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(1024 * 1024):
                        f.write(chunk)
                tmp.replace(dest)
    else:
        p = Path(src)
        if not p.exists():
            raise FileNotFoundError(p)
        if dest.exists() and dest.stat().st_size == p.stat().st_size:
            pass
        else:
            if dest.exists():
                dest.unlink()
            try:
                dest.hardlink_to(p)
            except Exception:
                shutil.copy2(p, dest)
    print(f"[manifest] {product}: {dest.name} ({dest.stat().st_size/1e6:.2f} MB)")
    return dest

def read_fits_table(path: Path, hdu=1):
    with fits.open(path, memmap=True) as hdul:
        h = hdul[hdu]
        if not isinstance(h, (fits.BinTableHDU, fits.TableHDU)):
            raise TypeError(f"{path} HDU {hdu} is not a table: {type(h).__name__}")
        return h.data.copy(), h.header.copy(), [x.name for x in hdul]

def first_col_caseins(data, names):
    lower = {c.lower(): c for c in names}
    return lower

def getcol(data, header, cands):
    names = data.names
    low = {n.lower(): n for n in names}
    for c in cands:
        if c.lower() in low:
            return data[low[c.lower()]]
    raise KeyError(f"None of {cands} found in columns {names}")

def standardize_primary(header):
    h = fits.Header()
    h["TELESCOP"] = "FERMI"
    h["INSTRUME"] = "LAT"
    h["HDUCLASS"] = "OGIP"
    h["HDUCLAS1"] = "EVENTS"
    for k, v in [("OBSERVER", header.get("OBSERVER", "Fermi-LAT")), ("EQUINOX", 2000.0), ("RADECSYS", "FK5")]:
        h[k] = v
    return h

def mask_events(evt, header, args):
    # Coordinate columns: prefer RA/DEC or RA_OBJ/DEC_OBJ fallback for skymap-like tables.
    ra = getcol(evt, header, ["RA", "RA_OBJ"])
    dec = getcol(evt, header, ["DEC", "DEC_OBJ"])
    cen = SkyCoord(args.ra, args.dec, unit="deg", frame="fk5")
    c = SkyCoord(ra, dec, unit="deg", frame="fk5")
    sep = cen.separation(c).deg
    m = sep <= args.roi

    if args.emin is not None and args.emax is not None:
        en = getcol(evt, header, ["ENERGY", "E_MEAN"])
        m &= (en >= args.emin) & (en <= args.emax)

    # Fermi photon standard columns if present; absence means "keep" and should be checked by user.
    for col, allowed in [
        ("EVENT_CLASS", None),  # integer bitmask; use evclass_mask instead
        ("EVENT_TYPE", None),
    ]:
        pass
    if args.evclass is not None and any(n.lower() == "event_class" for n in evt.names):
        evc = getcol(evt, header, ["EVENT_CLASS"])
        m &= (evc.astype(np.uint64) & np.uint64(args.evclass)) != 0
    if args.evtype is not None and any(n.lower() == "event_type" for n in evt.names):
        evt_t = getcol(evt, header, ["EVENT_TYPE"])
        m &= (evt_t.astype(np.uint64) & np.uint64(args.evtype)) != 0

    if args.zmax is not None and any(n.lower() == "zenith_angle" for n in evt.names):
        z = getcol(evt, header, ["ZENITH_ANGLE"])
        m &= z <= args.zmax
    if args.tmin is not None and any(n.lower() == "time" for n in evt.names):
        t = getcol(evt, header, ["TIME"])
        m &= t >= args.tmin
    if args.tmax is not None and any(n.lower() == "time" for n in evt.names):
        t = getcol(evt, header, ["TIME"])
        m &= t <= args.tmax
    return m

def write_events_cut(infile: Path, outfile: Path, mask, args):
    with fits.open(infile, memmap=True) as hdul:
        evt = hdul[1].data
        hdr = hdul[1].header.copy()
        cols = []
        for c in evt.columns:
            arr = evt[c.name][mask]
            cols.append(fits.Column(name=c.name, format=c.format, unit=c.unit, dim=c.dim, array=arr))
        thdu = fits.BinTableHDU.from_columns(fits.ColDefs(cols), header=hdr)
        thdu.name = "EVENTS"
        ph = standardize_primary(hdul[0].header)
        for k in ["TSTART", "TSTOP", "MJDREFI", "MJDREFF", "TIMESYS", "TIMEUNIT", "TIMEREF", "DATE-OBS", "DATE-END"]:
            if k in hdr:
                ph[k] = hdr[k]
        ph["RA_CENT"] = args.ra
        ph["DEC_CENT"] = args.dec
        ph["ROI_CENT"] = args.roi
        ph["EMIN"] = args.emin if args.emin is not None else -1
        ph["EMAX"] = args.emax if args.emax is not None else -1
        hd = fits.HDUList([fits.PrimaryHDU(header=ph), thdu])
        for i in range(2, len(hdul)):
            hd.append(hdul[i].copy())
        hd.writeto(outfile, overwrite=True)
    return int(mask.sum())

def bin_counts(ra, dec, energy, args):
    # Use tangent-plane WCS centered on ROI. Good enough for gradients; use gtsrcmaps/gtobssim for final likelihood.
    npix = int(args.npix)
    cdelt = args.pix / 3600.0
    w = WCS(naxis=2)
    w.wcs.crpix = [(npix + 1) / 2.0, (npix + 1) / 2.0]
    w.wcs.cdelt = [-cdelt, cdelt]
    w.wcs.crval = [args.ra, args.dec]
    w.wcs.ctype = ["RA---TAN", "DEC--TAN"]
    pix = w.wcs_world2pix(np.column_stack([ra, dec]), 0)
    x, y = np.floor(pix).astype(int).T
    good = (x >= 0) & (x < npix) & (y >= 0) & (y < npix)
    ebins = np.linspace(np.log10(args.emin), np.log10(args.emax), int(args.nebins) + 1)
    le = np.log10(np.asarray(energy))
    ei = np.clip(np.digitize(le, ebins) - 1, 0, len(ebins) - 2)
    cube = np.zeros((len(ebins) - 1, npix, npix), dtype=np.int32)
    np.add.at(cube, (ei[good], y[good], x[good]), 1)
    ectr = 10 ** (0.5 * (ebins[:-1] + ebins[1:]))
    return cube, ectr, w, ebins

def write_cube_fits(path, cube, ectr, w, args):
    h = w.to_header()
    h["NAXIS"] = 3
    h["NAXIS3"] = cube.shape[0]
    h["CTYPE3"] = "LOGENERGY"
    h["CUNIT3"] = "MeV"
    h["CRVAL3"] = float(np.log10(ectr[0]))
    h["CDELT3"] = float(np.log10(ectr[1] / ectr[0])) if len(ectr) > 1 else 1.0
    h["CRPIX3"] = 1.0
    h["BUNIT"] = "count"
    h["HDUCLAS2"] = "COUNTS"
    h["TELESCOP"] = "FERMI"; h["INSTRUME"] = "LAT"
    h["E_MIN"] = args.emin; h["E_MAX"] = args.emax
    fits.writeto(path, cube, h, overwrite=True)

def gradients(cube, smooth_px=0.0):
    # smooth in x/y per energy plane; preserve NaNs.
    out = []
    mag_all, pa_all = [], []
    dx_all, dy_all = [], []
    from scipy.ndimage import gaussian_filter
    for plane in cube.astype(float):
        p = plane.copy()
        if smooth_px and smooth_px > 0:
            p = gaussian_filter(p, sigma=(smooth_px, smooth_px), mode="nearest")
        gy, gx = np.gradient(p)  # gy: d/dy pixels, gx: d/dx pixels; y axis is Dec.
        mag = np.hypot(gx, gy)
        pa = np.degrees(np.arctan2(gy, gx))
        dx_all.append(gx); dy_all.append(gy); mag_all.append(mag); pa_all.append(pa)
    return np.array(dx_all), np.array(dy_all), np.array(mag_all), np.array(pa_all)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", type=Path, help="CSV: product,url_or_path,filename")
    ap.add_argument("--workdir", type=Path, default=Path("fermi_gradient_work"))
    ap.add_argument("--ra", type=float, required=True, help="ROI center RA deg")
    ap.add_argument("--dec", type=float, required=True, help="ROI center Dec deg")
    ap.add_argument("--roi", type=float, default=10.0, help="ROI radius deg for event selection/binning")
    ap.add_argument("--emin", type=float, default=100.0, help="MeV")
    ap.add_argument("--emax", type=float, default=300000.0, help="MeV")
    ap.add_argument("--nebins", type=int, default=8)
    ap.add_argument("--pix", type=float, default=180.0, help="pixel size arcsec")
    ap.add_argument("--npix", type=int, default=201)
    ap.add_argument("--evclass", type=int, default=None, help="e.g. 128 for P8R3 SOURCE if EVENT_CLASS is a bitmask")
    ap.add_argument("--evtype", type=int, default=None, help="e.g. 3 for front+back if EVENT_TYPE is a bitmask")
    ap.add_argument("--zmax", type=float, default=90.0)
    ap.add_argument("--tmin", type=float, default=None, help="MET s")
    ap.add_argument("--tmax", type=float, default=None, help="MET s")
    ap.add_argument("--smooth", type=float, default=1.0, help="Gaussian smoothing sigma in pixels before gradients")
    ap.add_argument("--events-product", default="photon", help="manifest product name to treat as events")
    args = ap.parse_args()
    try:
        import scipy  # noqa
    except Exception as e:
        print("WARNING: scipy not installed; gradients are unsmoothed unless --smooth 0", file=sys.stderr)
        args.smooth = 0.0
    work = args.workdir.resolve(); work.mkdir(parents=True, exist_ok=True)
    files = {}
    if args.manifest:
        with open(args.manifest, newline="") as f:
            for row in csv.DictReader(f):
                files[row["product"].strip()] = download_or_link(row, work)
    if args.events_product not in files:
        raise SystemExit(f"Need event file via --manifest product '{args.events_product}' or adapt script.")
    evt_path = files[args.events_product]
    evt, hdr, hdu_names = read_fits_table(evt_path, 1)
    mask = mask_events(evt, hdr, args)
    cut_path = work / "events_cut.fits"
    n0 = len(evt); n1 = write_events_cut(evt_path, cut_path, mask, args)
    print(f"[cut] kept {n1}/{n0} events ({100*n1/max(n0,1):.2f}%) -> {cut_path}")

    ra = getcol(evt, hdr, ["RA", "RA_OBJ"])[mask]
    dec = getcol(evt, hdr, ["DEC", "DEC_OBJ"])[mask]
    en = getcol(evt, hdr, ["ENERGY", "E_MEAN"])[mask]
    cube, ectr, w, ebins = bin_counts(ra, dec, en, args)
    cube_path = work / "counts_cube.fits"; write_cube_fits(cube_path, cube, ectr, w, args)
    gx, gy, mag, pa = gradients(cube, smooth_px=args.smooth)
    h = w.to_header(); h["NAXIS"]=3; h["NAXIS3"]=cube.shape[0]; h["CTYPE3"]="LOGENERGY"; h["CUNIT3"]="MeV"; h["CRVAL3"]=float(np.log10(ectr[0])); h["CDELT3"]=float(np.log10(ectr[1]/ectr[0])) if len(ectr)>1 else 1.0; h["CRPIX3"]=1.0
    for name, arr, unit, hducls in [("dcounts_dx", gx, "count/pixel", "GRAD_X"), ("dcounts_dy", gy, "count/pixel", "GRAD_Y"), ("grad_mag", mag, "count/pixel", "GRAD_MAG"), ("grad_pa_deg", pa, "deg", "GRAD_PA")]:
        hh = h.copy(); hh["BUNIT"] = unit; hh["HDUCLAS2"] = hducls
        fits.writeto(work / f"{name}.fits", arr, hh, overwrite=True)
    np.savez_compressed(work / "gradient_products.npz", counts_cube=cube, log_energy_edges=ebins, energy_MeV=ectr,
                        dcounts_dx=gx, dcounts_dy=gy, grad_mag=mag, grad_pa_deg=pa,
                        wcs_header=str(w.to_header()), args=vars(args))
    print(f"[done] outputs in {work}")

if __name__ == "__main__":
    main()
