# ad-glia-fm-prep

Preparationn project for a 1-year visiting researcher position at Harvard (Stanton lab). Acquires public AD scRNA-seq data, integrates across studies, and runs continued-pretraining (CPT) of two single-cell foundation models (Geneformer, scGPT) on the astrocyte + microglia niche, APOE-stratified.

**Framing:** prep, not publication. Goal is foundational fluency in the techniques the postdoc described, not a novel scientific contribution. The on-site project may differ from what is built here.

## Niche

Astrocytes + microglia, APOE-stratified (e3/e3 vs e3/e4 vs e4/e4), control vs late AD (Braak V–VI). Cross-region cortex (MTG + DLPFC + parietal + temporal). Stanton-aligned biological axis (non-neuronal cells, APOE as the genetic variable).

## Substrate

Three public studies (no DUC, no registration):

| Study | Region | Donors | Nuclei | Source |
|---|---|---|---|---|
| SEA-AD | MTG + DLPFC (+ v2 multi-region) | 84 | 1.2M+ | Synapse syn52146347 / Allen portal |
| Brase 2023 (Nat Comm) | Parietal cortex BA 7/39 | 67 (ca. 170 usable, DIAN-filtered) | 294k | Zenodo 10.5281/zenodo.7630313 |
| Li 2025 (Neuron) | Temporal cortex | 56 | 343k | GEO GSE237718 |

**Fallback:** Haney 2024 Nature (15 donors, frontal cortex).

## Method

1. Per-study QC (inherited published labels + uniform secondary filter)
2. Cross-study integration with **scVI** on 3000 HVGs (study-batch-aware); secondary integration with **scANVI** or **Harmony** for comparison; scIB-style metrics
3. Astrocyte + microglia subset (ITS — integrate-then-subset)
4. **CPT with LoRA** on Geneformer AND scGPT, three regimes: zero-shot baseline, per-study (parallel/independent, 3 separate adapted checkpoints), aggregated (concatenate + shuffle)
5. Three evals (pre-committed in `EVALUATION_CONTRACT.md`): substate-level linear probe, APOE-axis recovery, catastrophic-forgetting probe
6. Two diagnostic detectors: "is it changing?" (per-cell cosine), "has it forgotten?" (k-NN cell-type on Tabula Sapiens / PBMC)

## Compute

Colab Pro A100 40GB. Drive ~80–90GB. N=3 seeds default. Storage discipline: LoRA adapters only (never full weights), test-set-only embeddings.

## Status

| Phase | Status |
|---|---|
| Conceptual phase | CLOSED 2026-05-22 |
| Data source selection | LOCKED 2026-05-22 |
| Phase 1 setup (repo + env) | LOCKED 2026-05-22 |
| Scaffolding | DONE 2026-05-28 |
| FM library version compatibility | RESOLVED 2026-05-28 (Path A — two-env split) |
| Methods literature audit | FINAL 2026-05-28 (16 papers, 3 buckets — see `docs/literature_audit.md`) |
| Setup-audit checklist | DRAFTED 2026-05-28 (see `docs/setup_audits.md`) |
| **Preparation phase** | **CLOSED 2026-05-28** |
| Project execution | next phase — gated on first Colab session |

## Layout

```
ad-glia-fm-prep/
├── src/
│   ├── __init__.py
│   ├── qc.py             # secondary QC filters, scrublet wrappers
│   ├── eval.py           # linear probe, APOE-axis metrics, forgetting probe
│   ├── detectors.py      # "is it changing?" + "has it forgotten?" bands
│   └── data_loaders.py   # per-study loaders, vocab alignment, DIAN filter
├── notebooks/colab/      # numbered colab_NN_* notebooks
├── figures/
├── outputs/
├── docs/                       # postdoc clarifications, EVALUATION_CONTRACT.md
├── requirements_integration.txt  # Python 3.12, modern scvi-tools 1.4
├── requirements_fm.txt           # Python 3.10, scGPT-constrained (scvi-tools <1.0)
└── README.md
```
