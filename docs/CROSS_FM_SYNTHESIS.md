# Cross-FM synthesis: what CPT did to Geneformer and scGPT

This is the single place the full result set is read together. Every notebook's own interp cells carry the derivation; this document only states what the numbers, taken as a set, actually support — and is explicit about what they don't.

**Scope:** astrocyte + microglia glia substrate, 142,588 cells / 145 donors (SEA-AD 63 / Li2025 56 / Haney2024 26), the frozen donor split (seed 32, 101/22/22 donors). Both FMs: LoRA CPT, r=8/alpha=16/dropout=0.05, mlm 0.15, lr 5e-4, eff. batch 32, 2000 steps aggregated / epoch-matched (0.674 epochs) per-study. Full recipe and locked design in `EVALUATION_CONTRACT.md`; numbers below are pulled directly from `outputs/audit_report.json`, not transcribed from memory.

---

## 1. Zero-shot baselines are not comparable representations

Geneformer (768-dim, 63.3% panel-gene vocab coverage) and scGPT (512-dim, 75.3% coverage) already disagree on basic structure before any training: lineage silhouette 0.208 (Geneformer) vs 0.438 (scGPT); study silhouette 0.044 vs -0.002. Neither shows APOE structure zero-shot (both ≤0.006 silhouette in both lineages) — the null that every downstream CPT result is measured against.

## 2. Aggregated CPT: real movement in both architectures, differently sized

Detector #1 (per-cell cosine drift, held-out test): **Geneformer 0.00506** (registered=false against the 0.05 fixed threshold, later demoted to reporting-only) vs **scGPT 0.0811**, ~16x larger in raw terms. Expressed against each model's own within-donor substate-distance reference (the only way to compare drift magnitude across two different embedding spaces): Geneformer 14.0%/11.5% (micro/astro) vs **scGPT 234.5%/149.3%** — scGPT's aggregated CPT run moved the embedding further than the biological substate signal itself, in both lineages. This is the single largest asymmetry between the two arms and it is not an artifact of extraction point: scGPT's readout is the `<cls>` position with every LoRA target upstream and the loss-producing `ExprDecoder` frozen downstream, so unlike Geneformer (where layer-11 + head absorption leaves `L0` measuring only 9.2% of adapted capacity) there is no partial-view caveat available — the scGPT number is drift in the complete adapted representation.

## 3. Neither eval#1 nor eval#2 sees that drift, in either FM

| | Geneformer eval#1 (substate, best case) | scGPT eval#1 | Geneformer eval#2 k-NN (APOE) | scGPT eval#2 k-NN (APOE) |
|---|---|---|---|---|
| microglia | −0.16pp (noise) | −0.92pp (noise, exceeds measured null but not the contract band) | +0.12pp (noise) | −2.50pp (noise, but null-exceeding — see below) |
| astrocyte | +0.12pp (noise) | +0.16pp (noise) | −0.01pp (noise) | +0.73pp (noise, null-exceeding) |

Every cell is "noise" against the pre-registered contract bands (meaningful ≥5pp / ≥5pp respectively). The scGPT column looks different only because colab_17 additionally *measured* a real null (3 base-vs-base replicate passes, since scGPT's context-cap gene subsampling makes repeat embedding non-deterministic) — several scGPT deltas exceed that tighter measured null while still falling inside the pre-registered noise band. That is a real, if small, signal of *something* moving on these axes under repeated embedding, but it is well short of "meaningful," and eval#2's k-NN sits at or below the 0.50 chance line in both lineages for scGPT (a floor null, not a flat one) — extending the same APOE-recovery null already seen in colab_06/12/15 with a sharper characterization.

**Net for the aggregated regime, both FMs: a real, measured perturbation to the embedding (detector #1) that does not surface as recoverable structure on either pre-registered eval axis, at a readout proven to see the complete adapted representation in scGPT's case and the best-available one in Geneformer's.** This is the headline finding of the whole CPT arc — not "CPT does nothing" (detector #1 says it manifestly does something, and does something ~16x larger in scGPT) but "whatever CPT does under masked-gene reconstruction on this substrate is not the thing eval#1/eval#2 were built to catch."

## 4. The forgetting probe is where the two FMs diverge, and diverge in *sign*

Both use the identical Kang 2018 PBMC probe, same reference cells, same k-NN settings.

- **Geneformer:** small real *forgetting* — accuracy drop +0.09pp (L-1) / +0.24pp (L0), both well-powered, both inside the "acceptable" band, and both larger than a formal null wasn't computed for at the time (later flagged as a gap in colab_18's Phase-3 review — colab_13 never recorded a measured null to check +0.09/+0.24pp against).
- **scGPT:** a real *improvement* — accuracy on frozen base 0.9102, on CPT-adapted 0.9203 (full reference), drop of **−1.01pp** (negative = improvement), operative deterministic-subset read −0.99pp. Both ~6x the measured null max (0.16pp) — this is the most confidently "real" single number in the entire CPT arc, on either FM.

CPT-adapted scGPT is *measurably better* at an unrelated PBMC cell-typing task than its own frozen base. Geneformer moves the opposite direction, in a much smaller way. **The sign difference is unexplained.** `docs/ASSUMPTIONS.md` records the one candidate explanation tested — that scGPT's much larger drift-vs-substate-reference ratio gives it "more room to move" on any downstream axis — and is explicit that this predicts magnitude only, not direction, and rests on a single two-point comparison (one aggregated checkpoint per FM). Treat "scGPT's CPT improves forgetting resistance" as a real, replicated-within-run observation; treat "because it drifts more" as an untested hypothesis, not a finding.

## 5. Per-study CPT: three independent checkpoints, real on detector #1, diverging from each other

Both FMs ran 3 independent per-study LoRA adapters (SEA-AD/Li2025/Haney2024), epoch-matched to the aggregated run (0.674 epochs each).

- **Geneformer:** drift spread across the 3 checkpoints (population-matched) = **1.81x**, tracking median input sequence length rather than training step count; pairwise angular divergence 58–71° (git history, colab_14) — genuinely different directions in embedding space, not just different magnitudes.
- **scGPT:** all 3 checkpoints REAL on detector #1 (16–24x the measured floor). Drift spread = **1.13x** — colab_19 traced this collapse directly to scGPT's 1200-token context cap: pre-cap sequence-length spread across the 3 studies is 1.78x (matching Geneformer's 1.81x almost exactly), post-cap it flattens to 1.00x, because the cap truncates SEA-AD and Haney2024's longer sequences down to the same ceiling Li2025 already sits near. Pairwise angles 25–36°, tighter than Geneformer's spread.

**This resolves a real open question from the Geneformer arc** (was drift-spread driven by training dynamics or by a confound in the input data?) with a clean between-architecture control: the same population-driven length confound is present in both FMs' raw data, but only Geneformer's uncapped 4096-token sequences let it fully express — scGPT's shorter context accidentally acts as a length-variance clamp. A same-notebook rigor check (population identity vs. checkpoint identity as separate contributors to the raw, non-length-controlled spread) found population identity alone contributes *more* to the spread than which checkpoint trained — reported by the notebook itself as "consistent with," not "confirms," given N=1 and an unremoved step-count confound. Worth citing as the more rigorous framing rather than re-deriving a firmer claim than the source supports.

## 6. What this set of results actually licenses saying

- CPT under masked-gene reconstruction produces **real, measurable, architecture-dependent movement** in both FMs' embedding spaces (detector #1, unambiguous in both).
- That movement is **consistently invisible** to both pre-registered scientific probes (substate structure, APOE recovery) in both FMs, both regimes tried on both axes. This is the strongest, most-replicated result in the project — 4+ notebooks, 2 architectures, 2 regimes, all converging on the same null.
- The one axis where CPT *does* show a real, well-powered effect (forgetting-probe accuracy) shows **opposite signs across the two FMs**, and the only candidate mechanism for that asymmetry is untested.
- Per-study checkpoint divergence is real in both FMs and is now attributable, at least in large part, to a **data-driven confound (sequence length by study)** rather than to any architecture- or CPT-specific process — a genuinely useful methods finding, and one that would not have been visible without running the same control on a second architecture.

## 7. What remains open (not resolved by this synthesis)

- The forgetting-probe sign asymmetry (§4) — untested beyond one candidate hypothesis.
- Whether Geneformer V2 was itself pretrained with `<cls>`-equivalent masking, bearing on whether its readout is as trustworthy as scGPT's single-point one (`docs/ASSUMPTIONS.md`, still Unverified).
- `MIN_TEST_CELLS=100` and the eval-band thresholds generally are still a plausibility floor, not a derived statistic (see the contract re-lock, `EVALUATION_CONTRACT.md`).
- Whether the null on eval#1/eval#2 reflects a genuine absence of recoverable structure, an underpowered probe, or a training budget too small to produce structure worth detecting — undertraining is flagged project-wide as a real, unfixed compute limitation, not ruled out by the flat validation curves alone (a flat curve at a small step count is consistent with both "converged" and "stuck").

Source commits: `e79c22d` (colab_16), `d5e8879` (colab_17), `1b53b11`+`d018efc` (colab_18), `5e35d3f` (colab_19); Geneformer arc `1b2daeb`→`c50b56b` (colab_11–15). All numbers above read from `outputs/audit_report.json` on 2026-07-28.
