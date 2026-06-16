# Evaluation contract

Pre-registration for the continued-pretraining (CPT) phase. Its single purpose is to **fix the success/failure criteria before any training result is seen**, so that conclusions cannot be reverse-engineered from the numbers.

**Status:** PROVISIONAL. Thresholds below are first-pass estimates. They are refined **once**, numerically, after the N=1 pilot (see *Pilot → lock protocol*), then permanently locked. After the lock, any change is a reportable protocol deviation, not an edit.

**What this contract does NOT cover:** integration quality (scVI vs scANVI, scIB metrics) — that is evaluated in the integration notebooks (colab_06), not here. This contract is only about what CPT does to the foundation-model embeddings.

---

## What is being evaluated

- **Training signal:** CPT = masked-gene reconstruction on the AD glia data. No external label, no supervised head. This is deliberate: it imposes no axis on the model, which is the direct answer to the postdoc concern that "predictions deliberately suit a particular view."
- **Adaptation method:** LoRA (PEFT), held consistent across every regime so the comparison is fair.
- **Models:** Geneformer **and** scGPT. Both are always reported (see *Forbidden moves*).
- **Regimes (5 variants per FM):**
  1. **zero-shot** — the un-adapted base model (baseline; no training run).
  2. **per-study ×3** — three independent CPT checkpoints, one per study (Li / SEA-AD / Haney), each warm-started from the same base. Parallel, not sequential.
  3. **aggregated** — one CPT checkpoint on all studies concatenated + shuffled.
- **Substrate:** astro + microglia glia subset, 149,375 cells (astro 94,271 / micro 55,104), 145 donors (SEA-AD 63 / Li 56 / Haney 26).
- **Seeds:** N=1 pilot first (confirm pipeline + detector #1), then N=3. 8 CPT runs per seed (4 per FM × 2 FMs) → 24 runs at N=3. Zero-shot is evaluated but not trained.

**The comparison of interest** is, for each FM and each eval: does CPT move the embedding relative to zero-shot, and does **aggregated** beat **per-study**? Each regime is scored against the zero-shot baseline on the *same* global held-out set.

---

## Held-out and reporting

- **Primary metric** = computed on the **global held-out** set (donor-level 70/15/15 split, stratified by disease × APOE × study), identical across all 5 variants and both FMs.
- **Secondary** = per-study-of-origin breakdown, reported as mean ± SD plus a supplementary in-domain slice. Mandatory, not optional (held-out study balance is a known composition hazard — Audit E).
- **Aggregation across seeds:** mean ± SD over N=3 + strip plot. **No formal significance tests** at this sample size.
- **APOE axis:** primary contrast is **binary E4-carrier vs non-carrier** (label definition locked below). The finer e3/e3 vs e3/e4 vs e4/e4 split is reported where strata allow, but eval #2 test-set donor counts are thin (carrier 7 / non-carrier 10; AD-e2, Control-carrier, Control-e2 strata are sparse) — wide error bars are expected and N=3 seeds will not narrow them (the donor split is fixed).
- **E4 label definition (locked 2026-06-16):** **carrier** = any genotype with an E4 allele (`2/4`, `3/4`, `4/4`, `E3/E4`, `E4/E4`, Haney `apoe 44`); **non-carrier** = no E4 *and* no E2 (`3/3`, `E3/E3`, Haney `apoe 33`). **E2-without-E4 genotypes (`2/3`, `E2/E3`) are EXCLUDED** from the contrast — E2 is the protective allele and its effects run opposite to E4, so including it would contaminate the non-carrier reference with anti-E4 biology (note `2/4` carries E4 and is a *carrier*, so no true carrier is lost). This excludes ca. 140k cells (mostly Li `E2/E3`); all three studies retain both classes afterward. Implemented as `EXCLUDE_VALS = {"e2"}` in the `apoe_carrier` mapping (colab_06 §6b and every downstream eval).

---

## Eval #1 — substate linear probe

**Why:** gross astrocyte-vs-microglia identity saturates (any embedding separates them). The informative question is whether CPT sharpens **within-lineage substate** structure.

**Setup:** train a linear probe on substate labels — microglia: DAM (disease-associated) vs homeostatic; astrocyte: DAA / GFAP-high (reactive) vs resting. Probe trained on the train split, scored on the global held-out.

**Metric:** probe accuracy, **balanced accuracy if classes are imbalanced**.

**Bands (improvement over zero-shot baseline):**

| Verdict | Threshold |
|---|---|
| noise | ca. 2% |
| meaningful | ≥ 5% |
| decisive | ≥ 10% |
| **regression** | > 2% drop |

**OPEN — substate label source.** The DAM/homeostatic and DAA/resting labels do not exist in the raw metadata; they must be defined (marker-score thresholds, or a published reference signature). This must be fixed and committed **before** the probe is built, or eval #1 is circular. Flagged for resolution at eval-build time.

---

## Eval #2 — APOE-axis recovery (Stanton core)

**Why:** the load-bearing biological question — does CPT make the APOE-carrier signal more recoverable in the glia embedding, within each lineage? Measured **within astrocytes** and **within microglia** separately (not pooled).

**Metrics:** two, reported together —

1. **Silhouette** of the binary E4 label in the embedding.
2. **k-NN classification** of E4-carrier status from embedding neighbours (**balanced accuracy if imbalanced**).

**Bands:**

| Verdict | Silhouette (Δ vs zero-shot) | k-NN (Δ vs zero-shot) |
|---|---|---|
| noise | ca. 0.02 | ca. 3–5% |
| meaningful | ≥ 0.05 | ≥ 5% |
| decisive | ≥ 0.10 | ≥ 10% |
| **regression** | Δ < 0 | > 3% drop |

**Mandatory confound reporting (carried from colab_05 astro adjudication):** the astro subset has a known study/region confound — cl33 was adjudicated `real_confounded` (kept), and APOE recovery draws partly on ca. 4k donor-pure cells plus residual ambient (cl22). Any eval #2 result **must** be reported alongside the study-of-origin and region breakdown of the cells driving it. A "recovery" that is actually donor/study leakage is a null, not a win.

---

## Eval #3 — catastrophic-forgetting probe

**Why:** CPT on a narrow AD-glia slice can overwrite the model's general cell-type knowledge. This bounds how far adaptation has degraded the base capability.

**Setup:** k-NN cell-type classification on a **non-AD reference** (Tabula Sapiens / PBMC), comparing zero-shot vs each CPT variant. The reference is out-of-domain by design.

**Metric:** k-NN cell-type accuracy drop relative to zero-shot.

**Bands:**

| Verdict | Threshold |
|---|---|
| acceptable | ≤ 5% drop |
| concerning | 5–15% drop |
| **catastrophic** | > 15% drop |

**Optional extension:** leave-one-study-out, run only if a regime comparison looks suspiciously close and we need to test whether one study is carrying the result.

---

## Two diagnostic detectors

These are **go/no-go sanity checks**, run before interpreting any eval. They bracket the band: detector #1 confirms training did *something*; detector #2 confirms it did not do *too much*.

- **Detector #1 — "is it changing?"** Median per-cell cosine similarity, zero-shot embedding → post-CPT embedding. Drift **> 0.05 = registered** (training had a measurable effect). If a CPT run shows ~0 drift, the run is inert and its evals are uninformative — fix the run, don't interpret it.
- **Detector #2 — "has it forgotten?"** k-NN cell-type accuracy on the non-AD reference. **> 20% drop = overtrain** signal — stop and reduce CPT strength (steps / LoRA rank / learning rate) before trusting any eval #1–2 "win," because the win may be the model collapsing onto the AD slice.

---

## Decision rule

- Each eval yields an **independent** verdict (win / null / regression) per FM per regime, from the bands above. The three evals are **not** combined into a single score — that aggregation would itself be a researcher degree of freedom. All three stand on their own and all three are reported.
- A regime "wins" on an eval only if it clears the **meaningful** band against zero-shot **and** passes both detectors. A meaningful eval #1/#2 gain that coincides with detector #2 tripping is logged as **overtrain-confounded**, not a win.
- The headline question — *does aggregated beat per-study?* — is answered per eval, per FM, by comparing their bands on the global held-out. A null (no regime separates) is a legitimate, pre-licensed outcome, not a failure of the project.

---

## Forbidden moves

1. **No retro-ratcheting.** Thresholds are not edited to fit observed results. The only sanctioned refinement is the single post-pilot pass (below), done with reasons logged and before the final-training results exist.
2. **No FM cherry-picking.** Both Geneformer and scGPT are reported, win or lose.
3. **No eval cherry-picking.** All three evals are reported, win or lose.
4. **No post-hoc evals.** Adding a new eval after seeing the data, to surface a win, is forbidden. (The leave-one-study-out extension is pre-declared here and is diagnostic, not a headline metric.)

---

## Pilot → lock protocol

1. **Commit this PROVISIONAL contract** before the first CPT run. Record the git SHA.
2. **Run the N=1 pilot.** Confirm the pipeline executes end-to-end and detector #1 registers movement.
3. **Refine thresholds once**, numerically, using the pilot's observed noise floor and a cross-check against the literature (Boiarsky 2023; Kedzierska 2025). Log every change and its reason in a dated commit. This is the *only* permitted threshold edit.
4. **Permanently lock** in a dated commit. From here, the bands are frozen.
5. **Run final training (N=3).** Any deviation from the locked contract is reported explicitly as a protocol deviation in the results write-up — never as a silent edit.

---

## Provenance

| Event | Commit | Date |
|---|---|---|
| Provisional draft | (this commit) | 2026-06-16 |
| Post-pilot refinement | TBD | TBD |
| Permanent lock | TBD | TBD |

This file is the artifact a reviewer (postdoc, or Harvard) inspects to confirm the CPT conclusions were committed to in advance.
