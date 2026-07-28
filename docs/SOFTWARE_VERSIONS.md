# Software/environment version index

Per this project's standing rule, every notebook that ran on Colab snapshots its exact dependency stack at run time — `outputs/software_versions/<notebook>_<date>_pip_freeze.txt` (full `pip freeze`) and `<notebook>_<date>_env.json` (Python/CUDA/GPU/library-version/checkpoint summary, the one meant for a Methods section). This file indexes what exists, flags what doesn't, and states the pin discipline for the two categories `pip freeze` can't see on its own.

## What "pinned" means for the two FM checkpoints

`pip freeze` records installed packages, not git/HF clones. Both foundation-model libraries are installed via a **versioned git URL** (`pip install --no-deps "git+https://.../scGPT.git@{SCGPT_PIN}"`, and the equivalent for Geneformer), so the SHA is enforced by the install command itself, not just recorded after the fact — a stale cache or a re-run months later would still resolve to the pinned commit or fail, not silently drift. Every notebook's env.json additionally records the repo's own `git rev-parse HEAD` and the resolved `scgpt_commit_pinned`/`geneformer_commit` value, closing the loop between "what we intended to pin" and "what actually got installed."

- **Geneformer:** `04c2b2e84da7c0f385c3f9ad8f3ec24bab6650e5`
- **scGPT:** `cebd6fae655b9c585a4807daa3ac31bb764f06b4`

## Snapshot index

| Notebook | Snapshot | Date |
|---|---|---|
| colab_00 (setup) | present | 2026-06-02 |
| colab_01 (Li QC) | present | 2026-06-04 |
| colab_02 (SEA-AD QC) | **missing** | — |
| colab_03 (Haney QC) | present | 2026-06-10 |
| colab_04 (scVI integration) | present | 2026-06-12 |
| colab_05 (glia annotation/subset) | **missing** | — |
| colab_06 (scANVI) | present | 2026-06-17 |
| colab_07 (microglia subset) | present | 2026-06-19 |
| colab_08 (astrocyte subset) | present | 2026-07-02 |
| colab_09 (Geneformer zero-shot) | present | 2026-07-03 |
| colab_10 (scGPT zero-shot) | present | 2026-07-08 |
| colab_10b (cross-FM comparison) | present | 2026-07-08 |
| colab_11 (Geneformer CPT aggregated) | present | 2026-07-15 |
| colab_12 (Geneformer CPT evals) | present | 2026-07-20 |
| colab_13 (Geneformer forgetting) | **missing** | — |
| colab_14 (Geneformer per-study) | present | 2026-07-25 |
| colab_15 (Geneformer per-study evals) | present | 2026-07-26 |
| colab_16 (scGPT CPT aggregated) | present | 2026-07-27 |
| colab_17 (scGPT CPT evals) | present | 2026-07-27 |
| colab_18 (scGPT forgetting) | present | 2026-07-27 |
| colab_19 (scGPT per-study) | present | 2026-07-28 |
| diag_colab_11_head_ablation (+ SMOKE) | present | 2026-07-17 |
| diag_colab_11_cellstate_reference | **missing** | — |
| diag_colab_11_cpt_inert | **missing** | — |
| diag_colab_11_v2_magnitude_check | **missing** | — |

**On the six missing snapshots:** these notebooks already ran and closed before this per-run capture became a standing habit (colab_02/05) or are short diagnostic notebooks from the same period that never adopted it (colab_13, and three `diag_colab_11_*` notebooks). Re-running them now solely to backfill a version snapshot would not reproduce their original Colab session's exact resolved versions — Colab's base image moves over time, so a fresh run today would record *today's* stack, not the one the original results were produced under, which would misrepresent the record rather than complete it. The honest resolution is to log the gap here rather than manufacture a snapshot that looks authoritative but isn't. For colab_02/03/13, the closest available proxy is the neighboring notebook's snapshot on either side (e.g. colab_01 2026-06-04 / colab_03 2026-06-10 bracket colab_02; colab_12 2026-07-20 / colab_14 2026-07-25 bracket colab_13) — same requirements file, run within days, but not a substitute for colab_13's own resolved stack.

**Non-Colab environment:** `requirements_integration.txt`, `requirements_geneformer.txt`, `requirements_scgpt.txt` in the repo root are the three pinned/floated dependency specs (integration/Geneformer/scGPT never co-installed — see each file's own header for the reasoning). These are the specs a from-scratch reproduction would install from; the per-notebook snapshots above are what actually got *resolved* on the day, which is what a Methods section should cite.
