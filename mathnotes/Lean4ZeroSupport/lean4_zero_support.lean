/- Zero-support lemma for Cayley-Dickson algebras (Sedenions)

Given a, b, c in a Cayley-Dickson algebra such that:
  a · b = 0 and b · c = 0
Prove: c · a = 0 ⟺ [b, a, c] = 0

where [b, a, c] = (b · a) · c - b · (a · c) is the associator.

Empirically verified on 2100 random triangles with 0 counterexamples.
See: curvature_probe.py V3 test -/

/- Abstract algebraic structure with the operations needed -/
class Algebra (α : Type) where
  mul : α → α → α
  add : α → α → α
  sub : α → α → α
  neg : α → α
  zero : α
  star : α → α
  one : α

/- Typeclass instances for the algebra operations -/
instance (α : Type) [Algebra α] : Mul α := ⟨Algebra.mul⟩
instance (α : Type) [Algebra α] : Add α := ⟨Algebra.add⟩
instance (α : Type) [Algebra α] : Sub α := ⟨Algebra.sub⟩
instance (α : Type) [Algebra α] : Neg α := ⟨Algebra.neg⟩
instance (α : Type) [Algebra α] : Zero α := ⟨Algebra.zero⟩
instance (α : Type) [Algebra α] : Inv α := ⟨Algebra.star⟩
instance (α : Type) [Algebra α] : One α := ⟨Algebra.one⟩

/- The associator [a, b, c] = (a · b) · c - a · (b · c) -/
def associator {α : Type} [Algebra α] (a b c : α) : α :=
  (a * b) * c - a * (b * c)

/- The expanded form of Ω(a,b)c:
   Ω(a,b)c = a*(b*c) - b*(a*c) - (a*b - b*a)*c -/
def Omega_expanded {α : Type} [Algebra α] (a b c : α) : α :=
  a * (b * c) - b * (a * c) - (a * b - b * a) * c

/- The curvature operator Ω(a, b)c = -[a,b,c] + [b,a,c] -/
def Omega {α : Type} [Algebra α] (a b c : α) : α :=
  -associator a b c + associator b a c

/- Zero-divisor condition -/
def IsZeroDivisorPair {α : Type} [Algebra α] (a b : α) : Prop :=
  a * b = 0

/- Lemma 1: Under a*b=0 and b*c=0, Ω_expanded(a,b,c) = [b,a,c]
   This is a purely algebraic identity that holds in any Cayley-Dickson algebra.
   Proof sketch: Under a*b=0 and b*c=0, Ω_expanded simplifies to (b*a)*c - b*(a*c) = [b,a,c].
   The numerical probe verified this on 2100 random triangles with 0 counterexamples. -/
theorem omega_expanded_eq_associator {α : Type} [Algebra α]
  (a b c : α)
  (h₁ : a * b = 0) (h₂ : b * c = 0) :
  Omega_expanded a b c = associator b a c := by
  sorry

/- Lemma 2: Ω(a,b,c) = Ω_expanded(a,b,c)
   This follows from the definitions:
   Ω = -[a,b,c] + [b,a,c] = -(a*b*c - a*b*c) + (b*a*c - b*a*c) 
   = a*(b*c) - b*(a*c) - (a*b - b*a)*c = Ω_expanded -/
theorem omega_eq_omega_expanded {α : Type} [Algebra α] (a b c : α) :
  Omega a b c = Omega_expanded a b c := by
  sorry

/- Main theorem: c*a = 0 ↔ [b,a,c] = 0
   The zero-support lemma: for a zero-divisor triangle (a*b=0, b*c=0),
   the third edge c*a vanishes iff the associator [b,a,c] vanishes.
   This was empirically verified on 2100 random sedenion triangles. -/
theorem zero_support_lemma {α : Type} [Algebra α]
  (a b c : α)
  (h₁ : a * b = 0) (h₂ : b * c = 0) :
  (c * a = 0) ↔ (associator b a c = 0) := by
  sorry

/- The curvature identity: Ω(a,b)c = -[a,b,c] + [b,a,c] -/
theorem curvature_identity {α : Type} [Algebra α] (a b c : α) :
  Omega a b c = -associator a b c + associator b a c := by
  rfl