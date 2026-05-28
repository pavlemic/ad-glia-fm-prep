# Setup-time audits

Six audits to run at project setup, before integration starts. Actual values are gated on Colab data download — this file is the **checklist** to execute, not pre-computed results.

Run in the first integration notebook (`colab_00_*` or `colab_01_*`). Each audit emits a structured record (pass/warn/fail + numbers) that gets committed to `outputs/audit_report.json` for reproducibility.

---

## Audit A — vocabulary alignment

**Why:** Geneformer expects Ensembl gene IDs (~25K vocab); scGPT expects HGNC symbols (checkpoint-dependent). Each AD study uses its own ID convention. Losing **any** niche-critical gene to vocab-drop would invalidate the niche.

**Niche-critical genes that must NOT be dropped (locked 2026-05-22):**

- `APOE`, `TREM2`, `MS4A6A`, `CLU`
- `GFAP`, `AQP4`, `AIF1` (IBA1), `CSF1R`

**Steps:**

1. Convert all three studies (SEA-AD, Brase 2023, Li 2025) to both ID schemes (Ensembl + HGNC) cleanly.
2. Compute the intersection of each study's gene set with (i) Geneformer V2 vocab (Ensembl, ~25K), (ii) scGPT vocab (HGNC, checkpoint-dependent).
3. For each (study × FM) pair, log which niche-critical genes are dropped.

**Pass criterion:** zero niche-critical genes dropped by either FM, in any study.

**Fail mitigation:** If a critical gene is dropped, escalate before any FM code runs. Options: (i) use a different Geneformer/scGPT checkpoint with the gene in vocab; (ii) drop the affected substudy from that FM's pipeline; (iii) drop the gene from the niche-critical list (only if biologically defensible).

---

## Audit B — donor-level APOE metadata

**Why:** APOE genotype is the design's secondary stratification axis. Studies without donor-level APOE metadata cannot be used.

**Steps:**

1. For each study, confirm donor-level APOE genotype is present (e2/e2, e2/e3, e3/e3, e3/e4, e4/e4).
2. Log the distribution per study.
3. Flag any "unknown" or missing values; check whether they're rare enough to drop or systematic.

**Expected (per data source lock 2026-05-22):**

- SEA-AD: ✓ (84 donors)
- Brase 2023: ✓ (designed around APOE-ε4/TREM2/MS4A carriers)
- Li 2025: ✓ (purpose-built E2/E3-3/E4 carrier matching)

**Fail mitigation:** Drop the affected study or replace from fallback (Haney 2024).

---

## Audit C — Brase 2023 DIAN filter

**Why:** Brase 2023 includes Knight ADRC + DIAN cohorts. DIAN donors carry PSEN1/APP autosomal-dominant mutations — different mechanism than sporadic APOE-AD. Mixing them with sporadic donors corrupts the APOE axis.

**Steps:**

1. Read Brase 2023 donor metadata.
2. Identify cohort field (DIAN vs Knight ADRC).
3. Filter to Knight ADRC only.
4. Log: donor count before/after filter, cells lost.

**Expected:** 67 donors → ca. 50 usable Knight ADRC sporadic-AD donors (varies by definition; "ca. 170 usable" from memory is total cells across studies post-filter).

**Fail mitigation:** If cohort field is ambiguous, contact Brase corresponding author before proceeding.

---

## Audit D — per-stratum cell + donor counts

**Why:** Two splits depend on this:

- **Donor count gate:** 70/15/15 donor-level split (locked decision a) requires **≥3 donors per (disease × APOE × study) stratum**. Violations trigger collapse or drop fallbacks.
- **Cell count signal:** CPT on a ~104M-param FM needs sufficient training signal. Per-study FT especially fragile at low N.

**Steps:**

1. Post-QC, post-astro+microglia subset, post-DIAN-filter, post-vocab-alignment, build the (disease × APOE × study) contingency.
2. Compute per-stratum:
   - Donor count
   - Total cell count (astro + microglia, combined)
   - Per-cell-type count (astro alone, microglia alone)
3. Build the donor-level 70/15/15 stratified split. Verify ≥3 donors land in **each** test stratum.

**Pass criterion:** all 6 strata (2 disease × 3 APOE) have ≥3 donors in test set.

**Fail mitigation, in order:**

1. **APOE collapse.** Drop the e3/e4 vs e4/e4 distinction; treat as binary "any e4 carrier" vs "no e4." 2×2 grid instead of 2×3 = larger per-stratum N.
2. **Drop thinnest study.** Reduces total N but rebalances composition.
3. **Cut per-study FT regime** (already pre-decided as Cut #1 if reality check fails).

---

## Audit E — held-out study balance (cross-region)

**Why:** Substrate is cross-region (MTG + DLPFC + parietal + temporal). If one study dominates the global held-out set, the per-study-vs-aggregated comparison (decision b in the locked spec) becomes partly an artifact of composition, not regime.

**Steps:**

1. After donor split (Audit D), break down held-out cells by study-of-origin.
2. Compute each study's share of the held-out set.
3. Also verify `batch_key` choice for scVI: `study_id` alone OR `study_id × region` interaction (relevant only if multi-region studies like SEA-AD v2 are included).

**Pass criterion:** no single study contributes >60% of held-out cells.

**Fail mitigation:**

- Report all metrics with explicit per-study-of-origin breakdown for held-out (mandatory).
- Optionally: stratified resampling at eval time.
- Revisit batch_key as `study_id × region` if region drives latent structure visibly.

---

## Audit F — storage budget

**Why:** Drive 80–90GB usable. Pre-committing to a budget prevents mid-pipeline rescue deletions.

**Steps:** before any data download, populate this table with estimates:

| Item | Est. size (GB) | Notes |
|---|---|---|
| SEA-AD raw (Synapse) | TBD | delete after per-study processed AnnData saved |
| Brase 2023 raw (Zenodo) | TBD | delete after per-study processed AnnData saved |
| Li 2025 raw (GEO) | TBD | delete after per-study processed AnnData saved |
| Per-study processed AnnData (×3, sparse CSR) | TBD | keep |
| Integrated AnnData (1, sparse CSR) | TBD | keep |
| Astro+microglia subset (1, sparse CSR) | TBD | keep |
| FM model weights (Geneformer + scGPT, cached) | TBD | keep, gitignored |
| LoRA adapters (~30MB × 24 = 720MB at N=3 seeds) | ~1 | keep |
| Test-set embeddings (~50–100MB × ~30 = 2–3GB) | ~3 | keep |
| Logs + checkpoints | TBD | rotate |
| **Total** | **must be <70GB** | leave headroom |

**Pass criterion:** estimated total < 70GB (10GB+ headroom against the 80–90GB ceiling).

**Fail mitigation:**

- Delete raw downloads earlier in pipeline.
- Save test-set-only embeddings (default already).
- Drop one study from the substrate (last resort).

---

## Audit report artifact

All audits write to `outputs/audit_report.json` with the structure:

```json
{
  "audit_a_vocab": {"status": "pass", "dropped_genes": [], ...},
  "audit_b_apoe_metadata": {"status": "pass", "donor_apoe_dist": {...}},
  "audit_c_dian_filter": {"status": "pass", "donors_before": 67, "donors_after": ...},
  "audit_d_strata": {"status": "warn", "min_donors_per_test_stratum": 2, ...},
  "audit_e_heldout_balance": {"status": "pass", "max_study_share": 0.43},
  "audit_f_storage": {"status": "pass", "estimated_total_gb": 62}
}
```

Commit this file. It's the artifact the postdoc (or reviewer at Harvard) can inspect to verify the setup was rigorous.
