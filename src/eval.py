"""Pre-committed evaluations for CPT comparison.

Three evals locked 2026-05-20:
  1. Linear probe on substate-level cell type (not gross astro-vs-microglia,
     which saturates).
  2. APOE-axis recovery within astro / within microglia (silhouette + k-NN).
  3. Catastrophic-forgetting probe (non-AD reference, e.g. Tabula Sapiens).

Thresholds provisional, locked permanent after pilot pass — see
docs/EVALUATION_CONTRACT.md (to be committed before final training).
"""

from __future__ import annotations


def linear_probe(embeddings_train, labels_train, embeddings_test, labels_test):
    """LR head on frozen FM encoder; evaluate on substate cell type."""
    raise NotImplementedError


def apoe_silhouette(embeddings, apoe_labels, cell_type_mask):
    """Silhouette score by APOE genotype within a single cell-type mask
    (astro-only or microglia-only)."""
    raise NotImplementedError


def apoe_knn_recovery(embeddings, apoe_labels, cell_type_mask, k=15):
    """k-NN classification accuracy by APOE genotype. Use balanced accuracy
    or per-class recall when held-out is class-imbalanced."""
    raise NotImplementedError


def forgetting_probe(embeddings_zero_shot, embeddings_post_cpt,
                     reference_labels, k=15):
    """k-NN cell-type accuracy on a non-AD reference dataset, comparing
    zero-shot and post-CPT encoders."""
    raise NotImplementedError
