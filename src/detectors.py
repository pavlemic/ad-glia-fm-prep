"""Diagnostic detectors that bracket the working hyperparameter band.

Two detectors locked 2026-05-20:

  Detector #1 — "Is it changing?"
    Per-cell cosine distance between zero-shot and post-CPT embeddings on the
    same cells. Catches under-training (LR too low, epochs too few, LoRA rank
    too small). Provisional band: median > 0.05 = LoRA registered; below =
    undertrained.

  Detector #2 — "Has it forgotten?"
    k-NN cell-type accuracy on a non-AD reference, zero-shot vs post-CPT.
    Catches over-training / catastrophic forgetting. Provisional band:
    drop > 20% during tuning = over-training, tighten.

Together they bracket the band so the three main evaluations are interpretable.
"""

from __future__ import annotations


def is_it_changing(embeddings_zero_shot, embeddings_post_cpt,
                   median_threshold=0.05):
    """Per-cell cosine distance. Returns median + verdict."""
    raise NotImplementedError


def has_it_forgotten(reference_labels, knn_acc_zero_shot, knn_acc_post_cpt,
                     drop_threshold_pct=20.0):
    """Drop in k-NN cell-type accuracy on the reference. Returns delta + verdict."""
    raise NotImplementedError
