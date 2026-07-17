# Assumptions ledger

A record of **load-bearing assumptions about external library behaviour** — what an API argument actually does, what a default actually is — checked against the pinned upstream source rather than against expectation.

**Status:** ACTIVE. Opened 2026-07-17 after a silent-semantics gap survived four notebooks (see *Why this file exists*). The valuable half of this file is the **Unverified** section: it is a work queue, not documentation. Verified entries are kept only so a future reader can see the check was actually done and against what.

---

## Why this file exists

This project already reads upstream source rigorously. `requirements_geneformer.txt` documents the `transformers` v5 `SpecialTokensMixin` break, the `datasets` `VideoReader` unguarded import, the `torchao`/`peft` dispatch hard-raise, and the `scipy`+`numpy` 1.26 import failure — each one diagnosed against the tagged source and pinned with its reasoning. `colab_11` §4b carries a monkeypatch written against Geneformer's own tokenizer at the pinned commit.

Every one of those checks was triggered by **a crash**. Something broke loudly, the source got read, the truth got written down.

The gap found on 2026-07-17 never crashed. `EmbExtractor(emb_mode="cell", emb_layer=-1)` ran cleanly and produced a defensible embedding — just not the one the notebook's own markdown claimed it was producing. Because nothing broke, the existing habit never fired, and four notebooks (colab_09, colab_11 v1/v2, and both `diag_colab_11` diagnostics) were built on top of it. They agreed with each other perfectly. They were consistently wrong.

This is the pipeline's fail-loud principle one level up — the standing rule that a cell must announce what it dropped, skipped, or could not resolve, because silent completion is the costly failure mode in a data pipeline. The same failure mode exists in **API semantics**, and it was unguarded: the checks were crash-triggered, so the assumptions that never crash were exactly the ones that survived.

---

## Triggers

**1. First use of an external API argument that encodes a scientific choice.** Not every call — specifically arguments where a default or flag *is* a methodological decision. Examples in this project: `EmbExtractor`'s `emb_mode` / `emb_layer`, `TranscriptomeTokenizer`'s `special_token` / `model_input_size`, scVI's `batch_key`, LoRA's `target_modules`. Check the pinned source at first use and record the verified semantics here. This is where being wrong is most expensive, because every downstream notebook inherits it.

**2. Inheritance audit at regime close** (regime, not notebook — per-notebook close fires too often to stay cheap, and a check that fires too often stops firing at all). Grep the notebooks for conventions justified by *"same as \<earlier notebook\>"*. In `colab_11` those are *"Same defaults as colab_09"* (§4b) and *"the **same** `EmbExtractor` pass colab_09 used"* (§6a). Such phrases establish **consistency, not correctness** — each one is a pointer to a justification living somewhere nobody has re-read. Check that the pointed-to justification exists and was itself verified.

**Known weakness:** trigger 1 depends on judgement about what counts as "a scientific choice," and that scope can be drawn too narrowly. This makes the class of gap found on 2026-07-17 much less likely; it does not make the general category impossible.

---

## Cost discipline

This file is only worth keeping if the checks stay cheap. The 2026-07-17 check fetched 932 lines of `emb_extractor.py` and read roughly 40: fetch the source wide, grep it narrow, never read it whole. The entire check was a handful of filtered calls.

**If a check cannot be done in roughly five tool calls, it is the wrong instrument — skip it and record the assumption as Unverified instead.** An honest Unverified row is worth more than an expensive sweep.

---

## Verified

**`emb_layer=-1` means the 2nd-to-last layer, NOT the final layer.** Verified against Geneformer commit `04c2b2e`, `geneformer/emb_extractor.py`: the docstring states `-1: 2nd to last layer` / `0: last layer`, and `layer_to_quant = pu.quant_layers(model) + self.emb_layer` confirms it, since `quant_layers` (`perturber_utils.py`) returns `max(layer_index) + 1`, i.e. the layer count. Used by `colab_09` §6a and `colab_11` §6a. **`colab_11` §6a's markdown describes this as "final layer" and is factually wrong** — a documentation error, not a broken comparison, since colab_09 and colab_11 use the identical setting and remain internally consistent. Consequence: the last encoder layer's LoRA adaptation and the whole MLM head sit *downstream of the extraction point* and are structurally invisible to detector #1.

**`EmbExtractor`'s default `emb_mode` is `"cls"`; this project overrides it to `"cell"`.** Verified against `emb_extractor.py` `__init__` (`emb_mode="cls"`, `cell_emb_style="mean_pool"`, `model_version="V2"`). Under `emb_mode="cell"` the extractor calls `remove_cls_eos_tokens` then `mean_nonpadding_embs(non_cls_embs, original_lens - 2)` — it strips the `<cls>`/`<eos>` tokens and mean-pools the gene tokens. The library also force-downgrades `cls`→`cell` for V1 models with the note that *"V1 models do not have a `<cls>` token"*, confirming `cls` is the intended V2 cell representation. So the project mean-pools gene tokens on a checkpoint that ships a designated aggregator token.

**`TranscriptomeTokenizer` defaults are V2-shaped: `special_token=True`, `model_input_size=4096`, `model_version="V2"`.** Verified against `geneformer/tokenizer.py`. `colab_11` §4b calls `TranscriptomeTokenizer(CUSTOM_ATTRS, nproc=4)` — all defaults — so `<cls>` is prepended and `<eos>` appended to every tokenized cell. The `<cls>` token is therefore present in the data and available as a readout at no additional tokenization cost.

**`word_embeddings` is frozen — not a LoRA target.** Structural, from `colab_11` §5a's `LORA_TARGETS = ["query", "key", "value", "dense"]`. For a fixed cell the input tokens are identical between zero-shot and post-CPT (tokenization is bit-identical by design, §4b), so the input-embedding component of a mean-pooled vector is *identical* across the two models. It cancels in a within-cell drift numerator while still contributing to vector length, which mechanically suppresses the measured angle. It does **not** cancel in the substate reference, which compares *different* cells carrying different genes — so drift and the substate reference are not affected symmetrically, and the `d6b1452` "14.0% / 11.5% of reference" figure is biased **downward** by an unknown amount.

**`GeneformerPreCollator` registers only `<mask>` and `<pad>` as special tokens.** Verified against `geneformer/pretrainer.py`: `__init__` calls `super().__init__(mask_token="<mask>", pad_token="<pad>")`, and its `get_special_tokens_mask` returns `1` only for `self.all_special_ids`. `<cls>` and `<eos>` are therefore treated as ordinary maskable tokens, so `DataCollatorForLanguageModeling(mlm_probability=0.15)` masks `<cls>` in roughly 15% of cells during CPT. This is upstream Geneformer behaviour, not a project bug, but it is a caveat if `<cls>` becomes the readout.

---

## Unverified — the work queue

**Does the `Geneformer-V2-104M` checkpoint dir have 12 or 20 encoder layers?** `colab_11` §5a sets `MODEL_DIR = os.path.join(GENEFORMER_REPO, "Geneformer-V2-104M")`. The Geneformer V2 series ships both 12-layer and 20-layer variants. This does **not** affect the "`-1` = 2nd-to-last" conclusion, which is layer-count-independent — but it does set what *fraction* of the encoder's adaptation the drift metric cannot see (1/12 vs 1/20). Cheap to settle: read `config.json`'s `num_hidden_layers` in the checkpoint dir.

**Was Geneformer V2 itself pretrained with `<cls>` maskable?** Bears on whether the `<cls>` representation is robust to the masking noted above, and therefore on whether `<cls>` is a sound readout for eval #1–3. If upstream pretraining masked `<cls>` the same way, its learned role already tolerates it.

**Does the scGPT `--no-deps` native-Python install support a *training* path, not just inference?** `colab_10` (`502eb28`) proved zero-shot embedding works on Colab's native Python via the `--no-deps` git install, with `scvi-tools` confirmed a phantom dependency. The scGPT **CPT** path — LoRA attach, backward pass, optimizer step — has never been exercised. The torchtext/flash-attn/scib fallback shims were validated for a forward pass only. This is the largest untested version surface remaining in the project.

**Do `peft`'s `target_modules` leaf-name matches on scGPT resolve to the intended modules?** `colab_11` §5a documents that `"dense"` matches `cls.predictions.transform.dense` in Geneformer, which was noticed but never traced to its consequence for the extraction layer. scGPT has a different module tree; the same class of surprise applies and has not been checked.
