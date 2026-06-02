"""Per-study loaders + vocab alignment.

Substrate (locked 2026-06-02):
  - SEA-AD     : Allen portal / AWS open access. MTG + DLPFC. 84 donors.
  - Li 2025    : GEO GSE237718. Temporal cortex. 56 donors.
  - Haney 2024 : GEO GSE254205. Frontal cortex SFG + fusiform. 15 donors.
                 APOE3/3-ctrl / APOE3/3-AD / APOE4/4-AD (5 per group).

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
    """Load SEA-AD AnnData from Allen-portal-mirrored local copy."""
    raise NotImplementedError


def load_li2025(path):
    """Load Li 2025 AnnData from GEO GSE237718-derived local copy."""
    raise NotImplementedError


def load_haney2024(path):
    """Load Haney 2024 AnnData from GEO GSE254205-derived local copy.

    Deposit: GSE254205_ad_raw.h5ad.gz (700 MB). APOE genotype expected in
    adata.obs (primary design variable — 5 donors per APOE × disease group).
    """
    raise NotImplementedError


def align_vocab_to_ensembl(adata, drop_unmapped=True):
    """Convert var_names to Ensembl IDs for Geneformer. Audit which
    niche-critical genes (NICHE_CRITICAL_GENES) get dropped."""
    raise NotImplementedError


def align_vocab_to_hgnc(adata, scgpt_vocab, drop_unmapped=True):
    """Restrict var_names to scGPT vocabulary (HGNC symbols). Audit which
    niche-critical genes get dropped."""
    raise NotImplementedError
