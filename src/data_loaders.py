"""Per-study loaders + vocab alignment + DIAN filter.

Substrate (locked 2026-05-22):
  - SEA-AD     : Synapse syn52146347 / Allen portal. MTG + DLPFC. 84 donors.
  - Brase 2023 : Zenodo 10.5281/zenodo.7630313. Parietal cortex BA 7/39.
                 67 donors total. DIAN-filter required (exclude PSEN1/APP
                 autosomal-dominant carriers — different mechanism than APOE).
  - Li 2025    : GEO GSE237718. Temporal cortex. 56 donors.

Vocab alignment: Geneformer = Ensembl gene IDs (~25K). scGPT = HGNC symbols
(checkpoint-dependent). Each study uses its own ID convention. Setup audit:
verify niche-critical genes are NOT dropped — APOE, TREM2, MS4A6A, CLU, GFAP,
AQP4, AIF1/IBA1, CSF1R.
"""

from __future__ import annotations

NICHE_CRITICAL_GENES = [
    "APOE", "TREM2", "MS4A6A", "CLU",
    "GFAP", "AQP4", "AIF1", "CSF1R",
]


def load_sea_ad(path):
    """Load SEA-AD AnnData from Synapse-mirrored local copy."""
    raise NotImplementedError


def load_brase2023(path, dian_filter=True):
    """Load Brase 2023 AnnData from Zenodo-mirrored local copy.

    dian_filter=True excludes PSEN1/APP autosomal-dominant carriers (DIAN
    cohort), leaving the Knight ADRC sporadic-AD subset for APOE analysis.
    """
    raise NotImplementedError


def load_li2025(path):
    """Load Li 2025 AnnData from GEO GSE237718-derived local copy."""
    raise NotImplementedError


def align_vocab_to_ensembl(adata, drop_unmapped=True):
    """Convert var_names to Ensembl IDs for Geneformer. Audit which
    niche-critical genes (NICHE_CRITICAL_GENES) get dropped."""
    raise NotImplementedError


def align_vocab_to_hgnc(adata, scgpt_vocab, drop_unmapped=True):
    """Restrict var_names to scGPT vocabulary (HGNC symbols). Audit which
    niche-critical genes get dropped."""
    raise NotImplementedError
