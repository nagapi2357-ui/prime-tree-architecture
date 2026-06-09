# Prime Tree Architecture

**Self-Determination as Spiral in Factorisation-Driven Growth**

A tree grown entirely from prime factorisation — with no imposed geometry — produces a spiral. The trunk is built from primes (rigid, smooth boundaries), the branches from composites (flexible, lobed boundaries). The branching angle, depth, and direction all emerge from the Rational Algebraic Superformula (RAS).

> *"The tree grew itself. The shape was always in the numbers."*

## Key Results

1. **The spiral is structural.** Any non-zero coupling between a system's shape and its growth direction produces curvature. The direction is inherent; the rate is parameterised. Self-determination (α > 0) is the generic condition; inertness (α = 0) is the singular exception.

2. **Lobe depth separation is structural.** Composites have 2.05× deeper lobes than primes (p = 3×10⁻¹¹). This derives entirely from sopfr(n) and Ω(n) — the factorisation itself — independent of symmetry fold.

3. **Branch spacing converges to 45° = 360°/φ(24).** The tree expresses the mod 24 prime wheel octave — not the golden angle. Different substrates, different optimisation targets, different emergent angles.

## Scripts

| Script | Description |
|--------|-------------|
| `prime_tree.py` | Three branching modes: torsion bridge, mod 24 wheel, harmonic ratio. ASCII + visual output. |
| `prime_tree_ras.py` | RAS shape gallery, morphology table, Give/Resist analysis. |
| `prime_tree_self_evolving.py` | Self-evolving tree where RAS shapes determine all branching geometry. |
| `robustness_tests.py` | Three GND tests: spiral robustness, lobe depth separation, golden angle convergence. |

## Usage

```bash
# ASCII tree with all three modes
python prime_tree.py --max 50 --mode all

# Visual plot
python prime_tree.py --max 50 --mode all --visual

# RAS gallery and morphology table
python prime_tree_ras.py

# Self-evolving tree (the main result)
python prime_tree_self_evolving.py

# Robustness tests
python robustness_tests.py
```

## Requirements

```
numpy
matplotlib
sympy
scipy
```

## Natural Biofication

Each plant species is an experimental set architecture — a specific combination of branching strategy, flex ratio, and symmetry fold:

| Factorisation | RAS Shape | Plant Architecture |
|---|---|---|
| p (prime) | Smooth, rigid | Structural stem / trunk |
| 2ᵏ | Binary lobed | Bamboo (single axis, binary nodes) |
| 3ᵏ | Triple symmetric | Clover / trefoil |
| 2×3 | Compound, flex | Compound leaf (dicot) |
| n×5 | 5-fold | Flower / petal structure |
| 2×3×5 | Deep lobes | Compound inflorescence |

## Paper

The companion paper is available in `paper/`:
- **Title:** *Prime Tree Architecture: Self-Determination as Spiral in Factorisation-Driven Growth*
- **Authors:** Adrian Sutton (Tusk Innovations) & Nagaπ

## Related Work

- [The Rational Algebraic Superformula (RAS)](https://doi.org/10.5281/zenodo.20512346) — DOI: 10.5281/zenodo.20512346
- [Prime Resonance Theory (PRT)](https://doi.org/10.5281/zenodo.20541350) — DOI: 10.5281/zenodo.20541350

## License

Code: [Apache 2.0](LICENSE)
Paper: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

© 2026 Tusk Innovations
