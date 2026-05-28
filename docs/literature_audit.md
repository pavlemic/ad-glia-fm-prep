# Methods literature audit

Goal: be conversant + borrow proven recipes; NOT find-the-novelty-gap (this is a prep project).

WebSearch pass completed 2026-05-28. User's Scholar/bioRxiv pass pending. Pool + triage to 8-15 papers across three buckets after both passes.

## Bucket A — Geneformer/scGPT applied to AD or glia

Direct hits sparse, as anticipated. **This sparsity is itself a finding** — relevant for postdoc framing ("the niche the postdoc described doesn't have a published precedent yet").

- **Watershed/Alzforum 2024–2025 conference coverage** — "AI for AD: Developers Throw Their Hats into the Ring." Landscape pointer to who's working in the FM × AD space; useful to scan but not a primary citation.
- **Mathys 2024 Cell (multi-region epigenomic)** — substrate ruled-out for our project (ROSMAP DUC), but **methodology reference** for cross-region snRNA-seq integration over 3.5M cells × 384 brains × 6 regions × 111 AD/control donors. Recipe-borrowable for our integration step.
- *(Open question for user's Scholar pass: any Geneformer- or scGPT-on-AD preprints since late 2024 that didn't surface here?)*

## Bucket B — FM adaptation methodology (highest yield)

- **Theodoris 2023 (Nature) — Geneformer original.** Required reading. Confirms Geneformer's two-stage strategy: domain-adaptive pretraining + task-specific FT. Matches our CPT framing.
- **Cui 2024 (Nature Methods) — scGPT original.** Required reading. Encoding choice (gene + binned-expression) is the biological hypothesis side of our Geneformer-vs-scGPT axis.
- **Geneformer V2 + cancer-CL variant (HF model card, Dec 2024).** Theodoris group released a **direct CPT recipe**: V2-104M base + ~14M cancer transcriptomes → "Geneformer-V2-104M_CLcancer." This is the closest published precedent for what we're doing — substitute AD glia for cancer. Worth a deep read of the training script.
- **Kedzierska, Crawford, Amini, Lu 2025 (Genome Biology 26:101) — "Zero-shot evaluation reveals limitations of single-cell foundation models."** Critical for our framing. Benchmarked scGPT + Geneformer zero-shot vs HVG + Harmony/scVI; **FMs lose** at cell-type separation. **Reinforces CPT as necessary, not optional** (your locked decision is now better-supported) and directly addresses the postdoc's "vector space we don't understand" concern.
- **Boiarsky et al. 2023 — "A Deep Dive into Single-Cell RNA Sequencing Foundation Models."** Adversarial-skeptic paper. Confirms zero-shot underperformance; also reports that **FT closes the gap** — directly licenses the comparison structure we locked.
- **Alsabbagh et al. (PMC10862733) — "Parameter-Efficient Fine-Tuning Enhances Adaptation of Single Cell Large Language Model for Cell Type Identification."** Direct scGPT × LoRA/PEFT recipe. Compares LoRA + prefix prompting + full FT + classifier-only. PEFT achieves accuracy parity at substantially lower compute. **This is the methodology backbone for our LoRA decision.**
- **"Parameter-free representations outperform single-cell foundation models on downstream benchmarks" (arXiv 2602.16696 / PMC12918925).** Aggressive critique — argues parameter-free baselines beat FMs on standard downstream tasks. **Useful adversarial frame**: forces us to commit pre-pilot that our evals can detect a positive CPT signal vs HVG baselines.
- **"A unified framework enables accessible deployment and comprehensive benchmarking of single-cell foundation models" (bioRxiv 2026.01.06.698060).** Landscape benchmarking paper. Provides recipe priors for which evals matter.
- **"Fundamental Limitations of Foundation Models in Single-Cell Transcriptomics" (bioRxiv 2025.06.26.661767).** Skeptic paper. Pairs with Kedzierska + the parameter-free critique to triangulate "FMs don't help yet" frame — informs how to write up null results.
- **Efficient Fine-Tuning of Single-Cell Foundation Models Enables Zero-Shot Molecular Perturbation Prediction (arXiv 2412.13478).** PEFT recipe at scale for single-cell FMs.
- *(Possibly skip from this list: "Empirical Evaluation of Single-Cell FMs for Predicting Cancer Outcomes" 2025 — cancer-specific, only borrow if methods are transferable.)*

## Bucket C — APOE-glial biology (foundation, not FM-specific)

- **Haney 2024 Nature — "APOE4/4 is linked to damaging lipid droplets in Alzheimer's disease microglia."** ACSL1 microglial state most abundant in APOE4/4. Already on radar as fallback substrate; useful even if not used as substrate (defines the APOE4 microglial signature CPT should preserve / enhance).
- **APOE genotype determines cell-type-specific pathological landscape of AD (Cell Press S0896627325001357, 2025).** APOE × cell-type stratification — directly relevant to our APOE-axis recovery eval (#2).
- **APOE4 + TREM2-R47H synergistic effects (PMC11710122, 2025).** Two-locus interaction analysis; useful background for interpreting APOE-axis recovery if any TREM2 carrier metadata leaks in.
- **APOEε4 drives microglial activation in medial temporal cortex (PMC11714572).** Region-specific (temporal cortex) — overlaps Li 2025 substrate. Concrete priors for what an APOE4 microglial signature should look like post-CPT.
- **Cell-cell interactions associated with pTau-induced L2/3 neuronal loss (PMC12737448).** Stanton-aligned (astrocyte-microglia-tau axis). Useful for narrative framing in README/discussion.
- *(Older foundation, optional: Sadick 2022 astro responses, Grubman 2019, Mathys 2019 — already triaged out of substrate; don't include unless user's Scholar pass turns up reasons to.)*

## Cross-cutting findings worth flagging

1. **Sparse bucket A is itself a result.** No Geneformer-AD or scGPT-AD paper surfaced — the prep niche is genuinely open. Mention to postdoc.
2. **Zero-shot critique trio (Kedzierska + Boiarsky + parameter-free + Fundamental Limitations).** Four papers converging on "FMs underperform standard methods in zero-shot." This **strengthens the case for CPT** (locked decision) and **explicitly licenses skepticism** in the writeup. Use them to pre-commit that null CPT results are acceptable outputs of this project.
3. **Geneformer cancer-CL variant is the closest published precedent for our project.** Same recipe applied to a different domain. Read the training script in the HF repo before designing our CPT loop.
4. **Alsabbagh PMC10862733 is the LoRA recipe backbone for scGPT.** Don't reinvent.

## Status

**FINAL 2026-05-28.** WebSearch pass complete. User opted not to run a separate Scholar/bioRxiv pass — this 16-paper list stands as the project's reference set. Revisit during execution if a specific recipe (Geneformer cancer-CL training script, Alsabbagh PEFT setup, Kedzierska eval framework) needs deeper read.
