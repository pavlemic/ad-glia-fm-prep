"""QC utilities for the AD multi-study substrate.

Two-layer approach: inherit per-study published QC + cell-type labels, then
apply a uniform secondary filter on the concatenated object. Defaults locked
2026-05-21: min 500 counts/nucleus, min 250 genes/nucleus, max 5% mito, min 10
cells/gene, Scrublet per-sample for doublets.

Ambient RNA correction (CellBender/SoupX) explicitly deferred for prep project.
"""

from __future__ import annotations


def secondary_qc(adata, min_counts=500, min_genes=250, max_mito_pct=5.0,
                 min_cells_per_gene=10):
    """Apply uniform secondary QC on the concatenated multi-study AnnData."""
    raise NotImplementedError


def run_scrublet_per_sample(adata, sample_key="sample_id"):
    """Run Scrublet per sample (NOT across the concatenated object)."""
    raise NotImplementedError


def mito_threshold_sensitivity(adata, thresholds=(3.0, 5.0, 10.0)):
    """Sanity check: do astro + microglia counts shift dramatically across
    plausible mito thresholds? If yes, the 5% default is load-bearing and
    needs justification."""
    raise NotImplementedError
