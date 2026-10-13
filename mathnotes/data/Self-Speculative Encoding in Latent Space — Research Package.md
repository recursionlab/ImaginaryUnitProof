# Self-Speculative Encoding in Latent Space — A Research Package

**Author note.** Every claim below is labeled by epistemic status:

- **[EST]** established result (primary paper + reproduction/field consensus)
- **[EVI]** evidence-supported inference (drawn from cited results, not directly tested here)
- **[HYP]** proposed hypothesis (this package)
- **[SPEC]** speculative analogy (do not treat as established mathematics)

Citations are inline with URLs. This document is written to be *falsifiable*, not persuasive.

---

## A. Executive conclusion

**Verdict: a recognizable combination of existing methods, not a genuinely distinct architecture — but with one under-tested component (explicit relational latent objectives) whose value is genuinely open.**

The proposed pipeline

\[
h_t \rightarrow (\hat z_{t+1},\dots,\hat z_{t+k}) \rightarrow \text{relational processing} \rightarrow \text{lexicalization} \rightarrow (\hat x_{t+1},\dots,\hat x_{t+k})
\]

decomposes into three pieces, each of which already exists in the literature:

1. **Predict future hidden states from a current hidden state, then lexicalize with the LM head.** The *core latent-to-lexicalization graph* already appears in the linear-approximation variant of **Future Lens** (Pal et al., CoNLL 2023) \([Future Lens](https://aclanthology.org/2023.conll-1.37.pdf)\): \(f_\theta(h_T^l)\approx h_{T+N}^L\), then "the vocabulary can be read from the predicted \(\hat h^L_{T+N}\) by applying the pretrained decoder head." **[EST]** This is a *probing/evaluation* setup — it has no block drafting, no acceptance rule, no KV-cache handling, and makes no wall-clock claim — so it instantiates the core graph, not the full speculative architecture. The full feature-level speculative *system* is **EAGLE** \([Li et al. 2024](https://arxiv.org/abs/2401.15077)\), which "trains the draft model to autoregressively predict the next feature and then uses the target model's LM head to obtain the draft token" — though EAGLE uses a **separate** trained draft model (plus target features/LM head), not a same-model head **[EST]**.

2. **Same-model, no separate draft model.** Already exists as **self-speculative decoding / LayerSkip** (same model, early-exit layers draft, full layers verify) \([Elhoushi et al., ACL 2024](https://aclanthology.org/2024.acl-long.607/); [Zhang et al., 2023](https://arxiv.org/abs/2309.08168)\), and as the **training-free embedding-space MTP** of \([2603.17942](https://arxiv.org/html/2603.17942v1)\), which uses "a single model" with no auxiliary draft model or fine-tuning **[EST]**.

3. **Latent-space lookahead as a *training objective*.** Already exists as **Next-Latent Prediction (NextLat)** \([2511.05963](https://arxiv.org/html/2511.05963v4)\) and **Apple's Latent Lookahead Training** \([Apple ML](https://machinelearning.apple.com/research/latent-lookahead)\), both of which "leverage the network's latent space by recursively feeding its hidden states back into the context for τ steps" rather than sampling future tokens **[EST]**.

The only element that is not directly covered by a deployed/published method is the **explicit relational block \(R(\hat z_{t+1:t+k})\) with a relational loss \(L_\text{rel}=d_R(R(\hat Z),R(Z_\text{teacher}))\) inserted between latent prediction and lexicalization.** That specific combination is, to the best of the literature surveyed here, **[HYP]** and untested.

**However**, the single strongest empirical signal in the entire prior art cuts against the central premise:

> EAGLE-3 "abandons feature prediction in favor of direct token prediction" because "with token prediction as the ultimate goal, feature prediction can be seen as an additional constraint, which limits the expressiveness of the draft model." \([EAGLE-3, Li et al. 2025](https://arxiv.org/html/2503.01840v1)\) **[EST]**

The current state of the art in feature-level speculative decoding *moved away from* latent/feature prediction toward token prediction, and reported that doing so improved draft acceptance. This is not a proof that latent prediction is useless, but it is a direct, recent, SOTA-level counterexample to the hypothesis that predicting latents is *better* than predicting tokens.

The bottom line: **the architecture is sufficiently specified, it is implementable, and it is *not* ordinary autoregression** (it predicts a block of future latents in one cheap head pass before any full forward pass per future token). **But the wall-clock speedup it can deliver comes from the *same* memory-bandwidth-amortization mechanism as ordinary speculative decoding, not from a new source** — and that mechanism is gated by verification cost and acceptance rate, both of which the latent formulation does not obviously improve and may worsen (off-manifold lexicalization, EAGLE-3's finding).

---

## B. Prior-art map

| Method | Predicts tokens? | Predicts features/latents? | Same model as target? | Verification? | Main difference from proposed architecture |
|---|---|---|---|---|---|
| **Speculative decoding** \([Leviathan et al. 2023](https://arxiv.org/abs/2211.17192)\) | Yes (token dist.) | No | No (separate small draft LLM) | Target verifies k tokens in one forward pass; lossless rejection sampling | Draft is a *separate* model predicting tokens, not latents |
| **Medusa** \([Cai et al. ICML 2024](https://proceedings.mlr.press/v235/cai24b.html)\) | Yes (tokens) | No | Yes (heads on frozen/joint backbone) | Tree attention, simultaneous verification | Heads predict *tokens* independently; no latent intermediate, no relational block |
| **EAGLE** \([Li et al. 2024](https://arxiv.org/abs/2401.15077)\) | Tokens (via LM head) | **Yes — next top-layer feature** | No (separate EAGLE draft model + target LM head) | Tree-attention verification; loss \(l_\text{fea}+l_\text{token}\) | **Closest prior art.** Predicts future features, lexicalizes with LM head — but with a *separate* draft model, autoregressively, no joint relational objective |
| **EAGLE-2/3** \([Li et al. 2025](https://arxiv.org/html/2503.01840v1)\) | EAGLE-3: **tokens directly** | EAGLE-2: features; EAGLE-3: **abandoned** features for multi-layer fusion + token prediction | No (separate draft) | Tree attention; "training-time test" | EAGLE-3 is evidence that feature prediction was *suboptimal*; uses multi-layer feature *fusion as input*, not as predicted object |
| **Self-speculative / LayerSkip** \([Zhang 2023](https://arxiv.org/abs/2309.08168); [Elhoushi 2024](https://aclanthology.org/2024.acl-long.607/)\) | Yes (tokens) | No | **Yes** (early-exit sub-network = draft, full model = verify) | Full model verifies in one pass | Same-model, but draft = *layer-skipped forward pass*, not a latent-prediction head; cost reduction = fewer layers, not fewer forward passes |
| **Blockwise parallel decoding** \([Stern et al. NeurIPS 2018](https://arxiv.org/abs/1811.03115)\) | Yes (tokens) | No | Yes (aux heads) | Scoring model, back off to longest valid prefix | Predicts tokens in parallel; no latent intermediate |
| **Multi-token prediction (MTP)** \([Gloeckle et al. 2024](https://arxiv.org/abs/2404.19737); [DeepSeek-V3](https://arxiv.org/html/2412.19437v1)\) | Yes (token marginals) | No (token logits) | Yes (aux heads share backbone) | Usually *discarded at inference*; DeepSeek-V3 uses MTP head for speculative drafting | Training objective for sample efficiency; predicts *token* marginals, assumes independence; not latent |
| **Future Lens** \([Pal et al. CoNLL 2023](https://aclanthology.org/2023.conll-1.37.pdf)\) | Tokens (via readout) | **Yes — future final-layer hidden state** | Yes (linear probe on frozen model) | None (evaluation only) | **Closest to variant B.** Already does \(h_T^l \to \hat h_{T+N}^L \to\) LM head; but a *linear probe, per-offset independently, no speculation/verification, no relational block* |
| **Next-Latent Prediction (NextLat)** \([2511.05963](https://arxiv.org/html/2511.05963v4)\) | Tokens (via LM head) | **Yes — next latent state** | Yes (jointly trained latent-dynamics MLP) | None (training objective) | Predicts \(\hat h_{t+1}=p_\psi(h_t,X_{t+1})\) — needs the *token* to roll forward; not block-prediction for speculation; converges to belief states |
| **Apple Latent Lookahead** \([Apple ML](https://machinelearning.apple.com/research/latent-lookahead)\) | Tokens (supervision) | **Yes — τ latent predictions** | Yes | None (training) | Genuinely "predict future latents then lexicalize," but used to *invest more compute* on a token (quality), the *opposite* of the proposed speedup goal |
| **Training-free embedding-space MTP** \([2603.17942](https://arxiv.org/html/2603.17942v1)\) | Tokens | Embedding-space masks | Yes (frozen, single model) | None (parallel sampling) | Same-model, latent(embedding)-level parallel prediction, *no training* — but operates at token-embedding level with mask tokens, not future hidden states |
| **Direct Multi-Token Decoding (DMTD)** \([2510.11958](https://arxiv.org/html/2510.11958v1)\) | Tokens | Hidden states (as substrate) | Yes | None | "Thinking" layers run only every τ positions; cheap "decoding" layers produce τ tokens. Compute saving = skipping thinking layers for in-between positions, *not* predicting latents |
| **Future Summary Prediction (FSP)** \([2510.14751](https://arxiv.org/html/2510.14751v1)\) | Compact summary | **Yes — compact future representation** | Yes (aux head) | None (training) | Predicts a *compressed* future (bag-of-words / learned summary) for long-form quality, not for speculative speedup |

**The proposed "Self-Speculative Encoding" sits at the intersection of EAGLE (feature prediction + LM-head lexicalization), Future Lens (single-state → future hidden state), and self-speculative decoding (same model).** Its distinguishing claim — a *joint relational* latent block \(R\) before lexicalization, trained with a relational loss against teacher relations — is the one piece without a clean published analogue **[HYP]**.

---

## C. Proposed architecture

### C.1 Computational graph

Minimal changes to a decoder-only Transformer. Let the frozen (or LoRA-tuned) base model have \(L\) layers, hidden dim \(d\), vocabulary \(V\). At context position \(t\), the base model produces the last-layer hidden state \(h_t\in\mathbb{R}^d\). We attach:

- a **future-latent predictor** \(P\): a lightweight stack producing \(k\) future latents;
- an optional **relational block** \(R\): a small transformer/MLP-Mixer over the \(k\) latents;
- the **existing LM head** \(W_\text{LM}\in\mathbb{R}^{V\times d}\), reused for lexicalization (and for verification).

```
                        ┌── base model (frozen) ──┐
  tokens x_≤t ─────────►│  ... L layers ...        │── h_t ∈ ℝ^d
                        └──────────────────────────┘
                                                        │
                                          ┌─────────────▼──────────────┐
                                          │  P: future-latent predictor │   (aux, cheap)
                                          │  h_t ──► ẑ_{t+1:t+k} ∈ ℝ^{k×d}
                                          └─────────────┬──────────────┘
                                                        │  (optional)
                                          ┌─────────────▼──────────────┐
                                          │  R: relational block        │   (aux, cheap)
                                          │  ẑ ──► ẑ̃ = R(ẑ) ∈ ℝ^{k×d}   │
                                          └─────────────┬──────────────┘
                                                        │
                                          ┌─────────────▼──────────────┐
                                          │  W_LM (reused, frozen)      │
                                          │  ẑ̃_i ──► logits_i ∈ ℝ^V    │
                                          └─────────────┬──────────────┘
                                                        │
                                          draft tokens x̂_{t+1:t+k}  (argmax / sample)
                                                        │
                                          ┌─────────────▼──────────────┐
                                          │  VERIFIER: one full forward  │
                                          │  pass of base model over     │
                                          │  x_≤t + x̂_{t+1:t+k} (tree attn)│
                                          └─────────────┬──────────────┘
                                                        │
                                          accepted prefix + correction
```

### C.2 Tensor shapes

| Tensor | Shape | Notes |
|---|---|---|
| `h_t` | `(B, d)` | last-layer hidden state at draft origin |
| `ẑ = P(h_t)` | `(B, k, d)` | predicted future latents, one block, **one cheap pass** |
| `ẑ̃ = R(ẑ)` | `(B, k, d)` | relationally-processed latents |
| `logits = ẑ̃ W_LMᵀ` | `(B, k, V)` | lexicalization, reuse base LM head |
| `x̂` | `(B, k)` | sampled draft tokens |
| verifier logits | `(B, k, V)` | one full forward pass over `k` positions with tree attention |

### C.3 Design of \(P\) (future-latent predictor)

To respect the central constraint — **predict \(k\) future latents without \(k\) full forward passes** — \(P\) must be cheap relative to one base-model forward pass. Concretely, \(P\) is parameterized as a small stack:

\[
P(h_t) = \text{Stack}_k\!\left(\; \text{MLP}_\theta\big(\,[h_t;\, \text{pos-emb}(i)]\,\big) \;\right), \qquad i=1,\dots,k
\]

or, for the *joint* (non-independent) variant, a single-layer self-attention mixer across the \(k\) slots:

\[
ẑ = \text{SelfAttn}_\theta\!\left(\; \text{broadcast}(h_t) \oplus \text{PosEmb}_{1:k} \;\right) \in \mathbb{R}^{k\times d}.
\]

This is essentially a Medusa-style head \([Cai et al. 2024](https://proceedings.mlr.press/v235/cai24b.html)\) but operating in **latent space** and emitting \(d\)-dim latents instead of \(V\)-dim token logits. The cost is \(\Theta(k\cdot d^2)\) for the MLP variant or \(\Theta(k^2 d + k d^2)\) for the attention variant — vs. \(\Theta(L\cdot d^2)\) per token for the base model (one token's forward pass touches every layer). With \(k\ll L\), the head is far cheaper than \(k\) full passes **[EVI]**.

### C.4 Design of \(R\) (relational block) — when is it not just B with extra parameters?

This is the crux the user explicitly flagged ("be careful that C is not just an unnecessarily complicated reformulation of B"). The relational block is justified **only if** the predicted latents \(\hat z_{t+1:t+k}\) are *independently miscalibrated in a correlated way* that a joint operator can correct. Candidate forms of \(R\), ranked by likely usefulness:

| \(R\) form | Math | Potentially useful? |
|---|---|---|
| Identity (= variant B) | \(R(\hat z)=\hat z\) | baseline |
| Pairwise similarity correction | \(R_i = \hat z_i + \sum_{j\neq i} \alpha_{ij}(\hat z_i-\hat z_j)\) | marginal; attention already does this in \(P\) if \(P\) is attention |
| Self-attention mixer (1 layer) | \(R=\text{MHSA}(\hat z)\) | **plausible** — lets future slots condition on each other before committing |
| Relative-position geometry | \(R_i = \hat z_i + W_\Delta(\hat z_i - \hat z_{i-1})\) | plausible for trajectory smoothness |
| Covariance/subspace projection | project \(\hat z\) onto learned subspace | speculative; risks information loss |
| Graph/topological summaries | persistent homology etc. | **[SPEC]** almost certainly unjustified complexity at this scale |

**The honest reading:** if \(P\) already uses self-attention across the \(k\) slots, then a separate \(R\) is largely redundant — it is a *deeper* version of the same operator. The only way \(R\) earns its parameters is if it operates on a *different* relation than \(P\) has access to (e.g., \(P\) is an independent MLP per slot, and \(R\) is the only place slots interact). The cleanest non-redundant design is therefore: **\(P\) = independent per-slot MLPs (variant B), \(R\) = one shared self-attention layer that is the *only* cross-slot interaction.** This makes C a strict, testable generalization of B (B = C with \(R=\text{Identity}\)) **[HYP]**.

---

## D. Mathematical formulation

### D.1 Predictor

\[
\hat Z = P(h_t) \in \mathbb{R}^{k\times d},\qquad \hat Z = (\hat z_{t+1},\dots,\hat z_{t+k}).
\]

### D.2 Latent decoder (lexicalization)

Reusing the base model's LM head \(W_\text{LM}\):

\[
\hat p(x_{t+i}) = \mathrm{softmax}\!\big(W_\text{LM}\, \tilde z_{t+i}\big),\qquad \tilde Z = R(\hat Z).
\]

### D.3 Relational operator (general)

\[
R: \mathbb{R}^{k\times d}\to\mathbb{R}^{k\times d},\qquad
R(\hat Z) = \hat Z + \mathrm{MHSA}_\phi(\hat Z + E_\text{pos})
\]

(residual single-layer self-attention; \(E_\text{pos}\) positional embeddings for the \(k\) future slots).

### D.4 Losses

Teacher signal: run the base model autoregressively (teacher forcing on the true sequence) and collect the true future hidden states \(Z^* = (h^*_{t+1},\dots,h^*_{t+k})\).

**Lexical loss** (token-level, exactly as in EAGLE):

\[
L_\text{token} = \frac1k\sum_{i=1}^{k} \mathrm{CE}\!\big(\hat p(x_{t+i}),\, x^*_{t+i}\big).
\]

**Latent loss** (feature-level, as in EAGLE \(l_\text{fea}\) and NextLat's SmoothL1):

\[
L_\text{latent} = \frac1k\sum_{i=1}^{k} \mathrm{SmoothL1}\!\big(\hat z_{t+i},\, \mathrm{sg}[h^*_{t+i}]\big).
\]

**Relational loss** (the novel component):

\[
L_\text{rel} = d_R\!\big(R(\hat Z),\, R(\mathrm{sg}[Z^*])\big),
\]

with candidate distance \(d_R\). We propose a *relation-matching* distance rather than a pointwise one, to test whether *relations* carry information beyond the latents themselves:

\[
d_R(A,B) = \big\|\, A A^\top - B B^\top \,\big\|_F^2 \quad (\text{pairwise Gram / covariance structure}),
\]

or, more cheaply, a *slot-difference* relation:

\[
d_R(A,B) = \frac1{k^2}\sum_{i,j} \big\| (a_i - a_j) - (b_i - b_j) \big\|^2.
\]

Both are translation-invariant in the latents and therefore invariant to a global offset of the predicted block — a property that pointwise \(L_\text{latent}\) lacks. **This is the one genuinely testable claim of the relational variant.** **[HYP]**

Total:

\[
L = \lambda_\text{tok} L_\text{token} + \lambda_\text{lat} L_\text{latent} + \lambda_\text{rel} L_\text{rel}.
\]

### D.5 Verification procedure (identical to EAGLE/Medusa)

Sample draft tokens \(\hat x_{t+1:t+k}\) from \(\hat p\). Run **one** full forward pass of the base model over \((x_{\le t},\hat x_{t+1:t+k})\) with tree attention; accept the longest prefix whose verifier probability agrees with the draft distribution under the standard speculative-decoding acceptance rule \(\min(1, p(\hat x)/\hat p(\hat x))\) \([Leviathan et al. 2023](https://arxiv.org/abs/2211.17192)\). This makes the method **lossless** *if* the draft distribution is the one verified — exactly as in EAGLE. **[EST]**

### D.6 The "training-time test" fix (borrowed from EAGLE-3)

EAGLE-3 identified that when a draft model's outputs are fed back into itself, the inputs drift off the training distribution and later-slot acceptance collapses; their fix is "training-time test" — generate draft outputs during training and feed them back \([EAGLE-3](https://arxiv.org/html/2503.01840v1)\). **Any same-model latent speculator must adopt this or acceptance on slots \(i>1\) will be near-zero.** **[EST]**

---

## E. Complexity analysis

### E.1 Why ordinary autoregression is slow (the only mechanism that matters)

Token generation is **memory-bandwidth bound, not compute bound** \([HuggingFace analysis](https://huggingface.co/blog/lujangusface/tw-eagle3-gpu)\): every autoregressive step must load all model weights from HBM to emit one token. **[EST]**

\[
C_\text{AR}(k) = k\cdot (\text{weight bytes})\cdot(\text{bandwidth}^{-1}) \approx k\cdot \frac{2PL}{\beta}.
\]

Speculative decoding's speedup is *not* "fewer tokens conceptually generated." It is **amortizing one weight load over \(k\) verified tokens**:

\[
C_\text{spec}(k) \approx \underbrace{C_\text{draft}(k)}_{\text{cheap head}} + \underbrace{C_\text{verify}(k)}_{\text{one forward pass over }k\text{ positions}}.
\]

Speedup \(\approx \frac{k\cdot C_\text{AR}(1)}{C_\text{draft}(k)+C_\text{verify}(k)}\), times the acceptance rate. **[EST]**

### E.2 Where the proposed method's savings would come from — and whether they are new

| Component | Cost | vs. ordinary AR | vs. EAGLE/Medusa |
|---|---|---|---|
| Predictor \(P(h_t)\to k\) latents | \(\Theta(k d^2)\) MLP, or \(\Theta(k^2 d)\) attn | **cheaper than \(k\) full passes** ✓ | comparable to a Medusa head emitting \(k\times V\) logits — *cheaper* because \(d\ll V\) |
| Relational block \(R\) | \(\Theta(k^2 d)\) one layer | small overhead | EAGLE/Medusa have *no* such block — this is **extra cost** |
| Lexicalization \(W_\text{LM}\hat z\) | \(\Theta(k d V)\) | cheaper than \(k\) passes; but \(V\) is large | EAGLE pays this too |
| **Verification** (full forward over \(k\)) | one pass, \(\Theta(L d^2)\) amortized over \(k\) | **the same as all speculative methods** | identical |
| KV-cache | predicted latents need *no* KV entries until verification | neutral | neutral |

**The savings are real but are exactly the savings of speculative decoding, not a new source.** The latent formulation's *only* theoretical advantage over EAGLE-3 is that the cheap head emits \(d\)-dim latents (\(d\approx 4096\)) instead of \(V\)-dim logits (\(V\approx 128\text{k}\)), so the head is \(\sim V/d \approx 30\times\) cheaper per slot in raw FLOPs. Against Medusa (which emits \(k\times V\) logits) this is a real draft-stage FLOP saving. **However** this is an *engineering* advantage, not a guaranteed wall-clock win: token heads often share/unembed with the LM head, use fused top-k / vocabulary-projection kernels, and may avoid materializing full logits; actual latency depends on implementation and on whether full logits are realized **[EVI/HYP]**.

**But** the dominant cost at small batch is the verification forward pass + weight loading, not the head. So a cheaper head buys little wall-clock unless the head was the bottleneck (it is not, at low batch; it can be at very large batch where the head is compute-bound). **[EVI]**

### E.3 Plausibility of genuine wall-clock speedup

- **Low batch (latency-critical):** speedup is acceptance-limited and verification-dominated. Latent prediction does not obviously raise acceptance (see E.4). *Weakly plausible at best.* **[EVI]**
- **Large batch (throughput):** verification is compute-bound and parallelized; the cheap-head advantage is real but the relational block is pure overhead. *Plausible only if \(R\) raises acceptance enough to pay for itself.* **[EVI]**
- **Memory bandwidth:** latent heads reduce draft-stage bandwidth vs. token heads only if logits are materialized per slot; with fused kernels this vanishes. **[EVI]**

### E.4 The acceptance problem — why latents may be *worse* than tokens

Two compounding failure modes from the prior art:

1. **Off-manifold lexicalization.** The LM head \(W_\text{LM}\) was trained to map *real* hidden states to tokens. Predicted \(\hat z\) lie off this manifold, so \(\mathrm{softmax}(W_\text{LM}\hat z)\) is miscalibrated. EAGLE-3 reports that removing the feature-prediction constraint improved first-token acceptance \(\alpha\) precisely because the constraint "limits the expressiveness of the draft model" \([EAGLE-3](https://arxiv.org/html/2503.01840v1)\). **[EST]**
2. **Error accumulation across slots.** EAGLE-3 found that even with token prediction, slot-2 acceptance collapses because \(\hat a_{t+1}\) "is far away from the ground-truth \(f_{t+1}\), causing the input sequence ... to deviate significantly from the training distribution" \([EAGLE-3](https://arxiv.org/html/2503.01840v1)\). Latent prediction makes this *worse*, not better, because latents carry continuous degrees of freedom that can drift in directions invisible to the token readout. **[EVI]**

**Net:** a genuine wall-clock speedup over EAGLE-3 is *not* established by the architecture and is argued against by the SOTA's own trajectory. **[EVI]**

---

## F. Minimal prototype

### F.1 Setup

- **Base model:** Llama-3.2-1B (or Qwen2.5-0.5B), frozen. Small enough to iterate; real enough to be meaningful.
- \(d=2048\), \(L=16\) (1B), \(V=128256\).
- **Prediction horizon:** \(k\in\{2,4,8\}\).
- **Predictor \(P\):** per-slot 2-layer MLP, hidden \(2d\), output \(d\).
- **Relational block \(R\):** 1-layer multi-head self-attention over \(k\) slots (8 heads).
- **Lexicalization:** frozen base LM head \(W_\text{LM}\).
- **Trainable params:** \(P+R\) only (\(\sim 50\)–\(150\)M, small vs. base).
- **Sequence length:** 4096; teacher-forced future states from a frozen base forward.
- **Data:** FineWeb-Edu / WikiText-103, ~1–2B tokens for aux-head training (cf. DMTD's 1.5B \([2510.11958](https://arxiv.org/html/2510.11958v1)\)).
- **Compute:** 8×H100 or 4×A100, ~1–2 days for the 1B prototype.

### F.2 Losses / targets

- Teacher: frozen base run on true tokens → \(h^*_{t+1:t+k}\).
- \(L = L_\text{token} + 0.5\, L_\text{latent} + 0.1\, L_\text{rel}\) (sweep coefficients).
- **Training-time test** (EAGLE-3): with prob. 0.5, feed the model's own predicted \(\hat z\) back as input for slot \(i+1\) instead of teacher \(h^*_{t+i}\).

### F.3 Pseudocode

```
# training (frozen base)
h_t = base(x_<=t).hidden_states[-1]              # (B, d)
Z_hat = P(h_t)                                   # (B, k, d)   cheap, ONE pass
Z_tilde = R(Z_hat)                               # (B, k, d)
logits = Z_tilde @ W_LM.T                        # (B, k, V)   reuse base head

# teacher future latents (no grad through base)
with torch.no_grad():
    Z_star = base(x_<=t+k).hidden_states[-1][:, t+1:t+k]   # (B, k, d)

L_tok = CE(logits, x_[t+1:t+k])
L_lat = smooth_l1(Z_hat, Z_star.detach())
L_rel = rel_dist(R(Z_hat), R(Z_star.detach()))    # Gram or slot-diff
loss  = L_tok + 0.5*L_lat + 0.1*L_rel
```

### F.4 Compact PyTorch

```python
import torch, torch.nn as nn

class LatentSpeculator(nn.Module):
    def __init__(self, d, k, n_heads=8, mlp_mult=2):
        super().__init__()
        self.k = k
        # P: independent per-slot MLPs
        self.P = nn.Sequential(
            nn.Linear(d, mlp_mult*d), nn.GELU(),
            nn.Linear(mlp_mult*d, d), nn.GELU(),
            nn.Linear(d, d))
        self.pos = nn.Parameter(torch.randn(k, d)*0.02)
        # R: single self-attention layer (the ONLY cross-slot interaction)
        self.R = nn.MultiheadAttention(d, n_heads, batch_first=True)
        self.R_norm = nn.LayerNorm(d)

    def predict(self, h_t):
        # h_t: (B, d) -> (B, k, d)
        B = h_t.size(0)
        z = self.P(h_t).unsqueeze(1).expand(B, self.k, -1) + self.pos  # (B,k,d)
        z = z + self.R(self.R_norm(z), need_weights=False)[0]          # relational
        return z

    def lexicalize(self, z, W_LM):
        return z @ W_LM.T   # (B,k,V) reuse frozen base head
```

### F.5 Expected failure modes

1. Slot \(i>1\) acceptance collapses (off-manifold drift) — unless training-time test is used; even then EAGLE-3 shows this is hard.
2. \(L_\text{rel}\) improves but token acceptance does not (relational structure is redundant with what attention already captures).
3. Cheap-head FLOP saving is swamped by verification cost at low batch.
4. \(\hat z\) maps to multiple incompatible continuations (one latent, many tokens) → high entropy lexicalization → low acceptance.

---

## G. Experimental protocol

### G.1 Three measurable quantities (as requested)

\[
L_\text{token}=\mathrm{CE}(\hat p, x^*),\qquad
L_\text{latent}=\mathrm{SmoothL1}(\hat z, h^*),\qquad
L_\text{relation}=d_R(R(\hat Z),R(Z^*)).
\]

### G.2 Baselines (all at equal trainable-parameter budget)

- **B0** ordinary AR (no speculation).
- **B1** Medusa-style token heads (predict \(k\times V\) token logits) — token speculation.
- **B1′** EAGLE/EAGLE-3-style feature/token draft model trained against the same target — *current best feature/token speculative baseline* (without this, the experiment only settles "latent vs Medusa-like heads," not "latent vs SOTA feature/token speculation").
- **B2** EAGLE-style feature head (predict \(k\times d\) latents, lexicalize, *no* relational block) — feature speculation.
- **B3** proposed: B2 + relational block \(R\) + relational loss — relational feature speculation.

This is the user's A/B/C three-way comparison, controlled for parameters.

### G.3 Metrics

- **Acceptance length** (tokens accepted per verification pass), the standard speculative metric.
- **Wall-clock speedup** vs. B0 (the only metric that ultimately matters).
- **Off-manifold / distributional calibration:** \(\|\hat z - h^*\|\) and the KL between \(\mathrm{softmax}(W_\text{LM}\hat z)\) and \(\mathrm{softmax}(W_\text{LM}h^*)\) — tests the lexicalization gate. This is a stronger falsifier than accepted tokens alone: \(W_\text{LM}\hat z\) can have good greedy token CE yet poor *distributional* calibration, in which case speculative rejection sampling still suffers even when top-1 accuracy looks fine.
- **Information test:** does \(L_\text{latent}\) (or \(L_\text{relation}\)) at fixed aux budget predict acceptance better than \(L_\text{token}\) alone? If not, latents carry no extra usable information.
- **Drift with horizon:** acceptance as a function of slot index \(i\), for \(k=2,4,8\).

### G.4 Datasets / tasks

- Pretrain: FineWeb-Edu.
- Eval: MT-Bench, HumanEval (EAGLE's eval set), GSM8K — code/reasoning where EAGLE reports gains.

### G.5 Ablations

- Remove \(R\) (B3→B2): isolates the relational contribution.
- Remove training-time test: should collapse slot-\(i>1\) acceptance.
- \(P\) as attention vs. independent MLP: tests whether \(R\) is redundant with \(P\).
- \(L_\text{rel}\) on (Gram vs. slot-difference vs. off): which relation, if any, helps.
- Frozen vs. LoRA base: does lexicalization need base adaptation to off-manifold \(\hat z\)?

### G.6 The information question (does latent carry what token loses?)

Test whether \(B\) or \(C\) contains information that \(A\) (token prediction) cannot economically preserve, by measuring, at equal FLOP budget: (i) acceptance on continuations where *several token sequences realize similar latent configurations* (paraphrases), and (ii) whether \(L_\text{relation}\) correlates with acceptance *across* these where \(L_\text{token}\) does not. **This is the decisive information-theoretic test of whether latents preserve multiple lexical realizations.** **[HYP]**

---

## H. Failure analysis (trying to kill it)

1. **Latent prediction gives no extra predictive value over token logits.** Likely if \(W_\text{LM}\) is near-injective on the relevant manifold: then \(\hat z\) and \(\hat p(x)\) carry the same information, and the latent is just a reparameterization. The LM head being "full-rank" means top-layer features "align directly with the logits" \([EAGLE-3](https://arxiv.org/html/2503.01840v1)\) — *this is a direct argument that B ≅ A.* **[EST]**
2. **Relational loss improves training metrics but not generation.** Plausible: \(R\) may fit teacher relations on training data without raising acceptance, because acceptance depends on the *marginal* token agreement, not the relational structure. **[EVI]**
3. **Latent prediction costs as much compute as AR.** False for the head, true for verification — net wall-clock may not improve. **[EVI]**
4. **Predictions drift rapidly with horizon.** EAGLE-3 documents exactly this for features; latents likely drift faster (continuous space). **[EST]**
5. **Decoder cannot reliably lexicalize predicted latents.** The off-manifold calibration problem; EAGLE-3's whole motivation. **[EST]**
6. **One latent → many incompatible continuations.** If \(\hat z\) is a lossy summary, \(\mathrm{softmax}(W_\text{LM}\hat z)\) has high entropy → low greedy-match → low acceptance. **[HYP]**
7. **Verification overhead destroys speedup.** Same as all speculative methods; not a new risk but inherited. **[EST]**

The strongest single argument against the proposal is **#1 + the EAGLE-3 result**: the SOTA *tried* feature-level prediction, *removed* it as an "additional constraint" that "limits expressiveness," and got better acceptance. The proposed architecture re-introduces exactly that constraint, then adds a relational block on top of it. Without an empirical result showing the latent/relational formulation raises acceptance at equal cost, the prior art says it will not.

---

## I. Research extensions (clearly labeled, not forced)

### I.1 Configuration-space hypothesis — partly supported

The hypothesis that "a token is a readout of a trajectory through latent configuration space, \(Z_t\to Z_{t+1}\to\cdots\)" has genuine support in the representation-geometry literature:

- **Latent-Aligned Manifolds** \([OpenReview HItuBzXVFx](https://openreview.net/forum?id=HItuBzXVFx)\): representations "concentrate near low-dimensional trajectories reflecting latent state." **[EVI]**
- **Dynamical Manifold Evolution Theory (DMET)** \([2505.20340](https://arxiv.org/html/2505.20340v3)\): models LLM generation as "a continuous trajectory evolving on a low-dimensional semantic manifold." **[EVI]**
- **Trajectory extrapolation error** \([2606.05346](https://arxiv.org/html/2606.05346v1)\): linear trajectories in hidden states predict human processing costs beyond surprisal. **[EVI]**
- **NextLat belief states** \([2511.05963](https://arxiv.org/html/2511.05963v4)\): latent dynamics "provably converge towards belief states." **[EST]**

So: **the configuration-space / trajectory interpretation is not just metaphor — there is established evidence that hidden states lie on low-dimensional manifolds and evolve as trajectories.** What is *not* established is that *predicting* those trajectories is computationally cheaper than predicting tokens. The geometry supports the *interpretation*; it does not support the *speedup*.

### I.2 "let / of / about" mapping

Mapping \(\texttt{let}\) = instantiate latent, \(\texttt{of}\) = relate latents, \(\texttt{about}\) = lexicalize is, at best, a **[SPEC]** mnemonic for the \(P\to R\to W_\text{LM}\) pipeline. It gives no computational advantage over ordinary attention: "of" (relating) is already what self-attention does, and "about" (lexicalization) is the LM head. Treat as a naming convention, not mathematics.

### I.3 Endofunctors, polycomputation, topological invariants

- **Endofunctor / relational invariants:** category-theoretic framing of \(R\) is **[SPEC]** with no demonstrated computational payoff at this scale; importing it would add complexity without measurable benefit (the advisor's caution).
- **Topological summaries of latent sets** (persistent homology of \(\hat Z\)): **[SPEC]** almost certainly unjustified — \(k\) is tiny (2–8), topological invariants of 2–8 points are degenerate.
- **Polycomputation / multiple lexical realizations of one latent:** this is the *one* extension with a real testable content — it is exactly the "one latent, many tokens" property, testable via G.6. Worth keeping; the rest should be dropped until the core result is positive.

---

## J. Concise answer to the central question

> **Can one Transformer speculate its own future latent configurations, preserve their relational structure, and then lexicalize them efficiently enough to constitute a useful alternative to ordinary autoregressive token speculation?**

**Yes, it is mechanically possible — Future Lens already demonstrated \(h_t\to\hat h_{t+N}\to\) LM head, and EAGLE already does feature-level speculation with LM-head lexicalization and lossless verification. No new mechanism is required.**

**But "useful alternative to token speculation" is not established and the evidence points the other way.** The current SOTA (EAGLE-3) *abandoned* feature prediction as a constraint that "limits expressiveness" and moved to direct token prediction with multi-layer feature *fusion as input*. The latent formulation re-introduces the constraint EAGLE-3 removed, then adds a relational block whose only defensible role (correcting correlated cross-slot miscalibration) is *already performed* by self-attention if the predictor is itself attention-based. The wall-clock savings, where they exist, come from the *same* memory-bandwidth-amortization mechanism as ordinary speculative decoding — not a new source — and are gated by verification cost and off-manifold lexicalization, both of which the latent formulation does not improve and may worsen.

**Net: the architecture is a recognizable combination of Future Lens + EAGLE + self-speculative decoding, with one genuinely open component (explicit relational latent losses). The prior art predicts it will not beat EAGLE-3 token-level speculation at equal cost. It is worth exactly one experiment to falsify that prediction.**

### The smallest decisive experiment

Freeze a small base model (Llama-3.2-1B). Train equal-parameter draft mechanisms from the *same* \(h_t\): (1) Medusa token heads (predict \(k\times V\)); (1′) an EAGLE/EAGLE-3-style feature/token draft model against the same target (the current-best baseline, without which the result only settles "latent vs Medusa-like heads"); (2) latent head \(h_t\to\hat z_{t+1:t+k}\to W_\text{LM}\) (no \(R\)); (3) latent head + one self-attention relational block + \(L_\text{rel}\). All use training-time test and identical data. Decode with the frozen LM head and verify with one full base forward pass.

**Decisive metrics: (a) accepted tokens per target forward pass, at equal aux-head FLOPs and equal wall-clock; and (b) the KL/divergence between \(\mathrm{softmax}(W_\text{LM}\hat z)\) and the teacher's token distribution** — because a latent head can show good top-1 token accuracy yet poor *distributional* calibration, which still breaks speculative rejection sampling. If variant (2) does not beat (1)/(1′) on both (a) and (b), latent prediction carries no usable extra information (failure mode #1, supported by EAGLE-3's abandonment of feature prediction). If (3) does not beat (2), the relational block is redundant (C = unnecessarily complicated B). If neither (2) nor (3) beats (1)/(1′) on wall-clock, the proposal is not currently a useful alternative to token speculation. This single 1B-scale, few-GPU experiment settles it.
