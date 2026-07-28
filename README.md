# ad-glia-fm-prep

Preparation project for a 1-year visiting researcher position at Harvard (Stanton lab). Acquires public AD scRNA-seq data, integrates across studies, and runs continued-pretraining (CPT) of two single-cell foundation models (Geneformer, scGPT) on the astrocyte + microglia niche, APOE-stratified.

**Framing:** prep, not publication. Goal is foundational fluency in the techniques the postdoc described, not a novel scientific contribution. The on-site project may differ from what is built here.

**Start here for results:** `docs/CROSS_FM_SYNTHESIS.md` (what CPT actually did to both FMs, read together) and `docs/POSTDOC_REASONING.md` (the postdoc's three named concerns and the no-wet-lab validation question, answered against the real run results, not just the design intent).

## Niche

Astrocytes + microglia, APOE-stratified, control vs late AD (Braak V–VI). Cross-region cortex (SEA-AD: MTG + DLPFC; Li2025: temporal cortex; Haney2024: frontal SFG + fusiform). Stanton-aligned biological axis (non-neuronal cells, APOE as the genetic variable). Primary APOE contrast is **binary E4-carrier vs non-carrier** (E2-without-E4 excluded as anti-E4 biology — see `EVALUATION_CONTRACT.md`), not the finer e3/e3 vs e3/e4 vs e4/e4 split originally scoped — test-set strata were too thin to support it.

## Substrate

Three public studies (no DUC, no registration), 166 donors pre-drop:

| Study | Region | Donors | Nuclei | Source |
|---|---|---|---|---|
| SEA-AD | MTG + DLPFC | 63 (post-drop) | 1.2M+ (raw) | Synapse syn52146347 / Allen portal |
| Li 2025 (Neuron) | Temporal cortex | 56 | 343k | GEO GSE237718 |
| Haney 2024 (Nature) | Frontal SFG + fusiform | 26 | ca. 100k | GEO GSE254205 |

Raw integrated cohort: 762,958 cells / 26,514-gene intersection → scVI on 3,001 genes → 694,922 cells / 145 donors post-QC-drop → **142,588-cell astro+microglia glia subset (87,783 astro / 54,805 micro)**, the substrate every FM notebook trains and evaluates on. Brase 2023 was scoped out early (DUC/registration required); Haney 2024 replaced it as the third study.

## Method

1. Per-study QC (inherited published labels + uniform secondary filter)
2. Cross-study integration with **scVI** on 3,001 HVGs (study-batch-aware); secondary integration with **scANVI** for comparison — scANVI showed no advantage over scVI and does not rescue the APOE axis (colab_06)
3. Astrocyte + microglia subset (ITS — integrate-then-subset); substate labels defined post-hoc from marker signatures (microglia: activated/homeostatic; astrocyte: reactive/resting) after canonical DAM markers proved unrecoverable in this gene set
4. **CPT with LoRA** on Geneformer AND scGPT, three regimes each: zero-shot baseline, aggregated (concatenate + shuffle), per-study (3 independent parallel checkpoints)
5. Three evals (pre-committed in `EVALUATION_CONTRACT.md`): substate-level linear probe, APOE-axis recovery (silhouette + k-NN), catastrophic-forgetting probe (Kang 2018 PBMC)
6. Two diagnostic detectors: "is it changing?" (per-cell cosine drift vs zero-shot), "has it forgotten?" (k-NN cell-type accuracy on the PBMC reference)

**Result, in one line:** CPT produces real, architecture-dependent movement in the embedding (detector #1) that is invisible to both substate and APOE evals in both FMs and both regimes, while a real, opposite-signed effect shows up only on the forgetting probe (scGPT improves, Geneformer mildly forgets). Full read: `docs/CROSS_FM_SYNTHESIS.md`.

## Compute

Colab Pro A100 40GB. Drive ~80–90GB. N=1 pilot run per regime/FM (N=3 seed replication was scoped out — see live status memory for the cost/calendar tradeoff). Storage discipline: LoRA adapters only (never full weights), test-set-only embeddings.

## Status

| Phase | Status |
|---|---|
| Conceptual + data source selection + repo setup | CLOSED 2026-05-28 |
| Integration (scVI + scANVI, colab_01–06) | CLOSED |
| Glia subset + substate labeling (colab_07–08) | CLOSED |
| Zero-shot baselines, both FMs (colab_09–10b) | CLOSED |
| Geneformer CPT — aggregated + per-study + full eval battery (colab_11–15) | CLOSED |
| scGPT CPT — aggregated + per-study + full eval battery (colab_16–19) | CLOSED 2026-07-28 |
| **Project execution** | **CLOSED — both FMs have zero-shot + all 3 CPT regimes + full eval/forgetting battery** |
| Cross-FM synthesis + postdoc-concerns reasoning | `docs/CROSS_FM_SYNTHESIS.md`, `docs/POSTDOC_REASONING.md` |

## Layout

```
ad-glia-fm-prep/
├── src/
│   ├── __init__.py
│   ├── qc.py             # secondary QC filters, scrublet wrappers
│   ├── eval.py           # linear probe, APOE-axis metrics, forgetting probe
│   ├── detectors.py      # "is it changing?" + "has it forgotten?" bands
│   └── data_loaders.py   # per-study loaders, vocab alignment
├── notebooks/colab/      # numbered colab_NN_* notebooks (scaffolds)
├── notebooks/executed/   # _OUTPUT executed notebooks, committed
├── figures/
├── outputs/                       # audit_report.json (cumulative results ledger)
├── docs/
│   ├── CROSS_FM_SYNTHESIS.md      # start here — what CPT did, both FMs read together
│   ├── POSTDOC_REASONING.md       # postdoc's 3 concerns + no-wet-lab validation, reasoned against results
│   ├── EVALUATION_CONTRACT.md     # pre-registered evals/thresholds/detector bands
│   ├── ASSUMPTIONS.md             # source-verified API/library assumptions + open work queue
│   ├── SOFTWARE_VERSIONS.md       # per-notebook dependency-snapshot index, for the Methods section
│   ├── literature_audit.md
│   └── setup_audits.md
├── requirements_integration.txt  # Python 3.12, modern scvi-tools 1.4
├── requirements_geneformer.txt   # native Python (>=3.10), Geneformer-only
├── requirements_scgpt.txt        # native Python, scGPT via --no-deps install
└── README.md
```
