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

**3. Any claim that a record does not exist.** *"The val curve wasn't saved." "That was a widget, it got stripped." "Only train_loss survives."* An assertion of absence is a load-bearing claim exactly like an API semantic, and it is **cheaper to check than either** — one grep. Check before building on it. This trigger was added 2026-07-17 after the mirror image of the gap that opened this file: `diag_colab_11_head_ablation` was scaffolded on the belief that no validation loss survived from `colab_11`, framing its rung 0 as a gate that might close the whole arc. The full step-matched val curve was in `What we did.txt` the entire time and had simply not been re-read — it changed the notebook's framing, its reference numbers, and which cell is actually the arc's gate.

Note the asymmetry that makes this class dangerous. Triggers 1 and 2 guard assumptions that *something behaves a certain way*; being wrong there usually produces a number that looks fine. Trigger 3 guards assumptions that *nothing is there*, and being wrong produces work built to recover what you already had — the error hides in the shape of the plan, not in a value, so no assertion can catch it. Absence is the one claim that cannot fail loud on its own.

**Known weakness:** trigger 1 depends on judgement about what counts as "a scientific choice," and that scope can be drawn too narrowly. This makes the class of gap found on 2026-07-17 much less likely; it does not make the general category impossible. Trigger 3 has a matching weakness in the opposite direction: it is only as good as knowing *where* a record would live if it existed — this project's are spread across `outputs/audit_report.json`, the `_OUTPUT` notebooks, the local `What we did.txt`, and the memory files, and the 2026-07-17 miss checked the first two and stopped.

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

**`Geneformer-V2-104M` is a 12-layer encoder — and detector #1's blind spot is 9.2% of v2's adapted capacity.** Verified against the checkpoint's `config.json` on HuggingFace: `num_hidden_layers=12`, `hidden_size=768`, `intermediate_size=3072`, `num_attention_heads=12`, `vocab_size=20275`, `max_position_embeddings=4096`. This settles the earlier open question (12 vs 20) and makes the LoRA parameter counts fully attributable, since LoRA adds `r * (d_in + d_out)` per adapted module at `r=8`:

- `colab_11` v1 (`query,key,value`) reported **442,368** trainable = `3 × 8 × (768+768) × 12 layers`. Exact.
- v2 (`+dense`) reported **1,339,392**, i.e. **897,024** added = `12 layers × [attn.output.dense 12,288 + intermediate.dense 30,720 + output.dense 30,720]` (884,736) + `cls.predictions.transform.dense` (12,288). Exact.

So `dense` matched **37** modules: 36 encoder projections and one MLM-head projection. Two consequences. (a) The MLM head's adapter is **12,288 params — 1.4% of what v2 added**, so the head-absorption hypothesis requires that thin slice to carry essentially all of v2's loss gain. (b) Since `emb_layer=-1` extracts the output of layer index 10, what is structurally invisible to detector #1 is the head **plus all of encoder layer 11**: 12,288 + 110,592 = **122,880 params, 9.2% of v2's trainable capacity**. Detector #1 sees the other ~91%. Tested directly by `diag_colab_11_head_ablation`, which re-derives these counts from `config.json` and asserts them against what it actually zeroes.

**Tokenization is cell-local — a subset tokenizes bit-identically to the full object.** Verified against `geneformer/tokenizer.py` at commit `04c2b2e`: `norm_factor_vector` is built from the shipped `gene_median_dict` (loaded once from `gene_median_file`, independent of the data), and the only per-cell quantity is `n_counts = adata[idx].obs["n_counts"]` — that cell's own total. No dataset-wide statistic enters. The gene-level steps (`sum_ensembl_ids`, the `coding_miRNA_loc` filter) act on `adata.var`, which cell-subsetting does not change. This licenses `diag_colab_11_head_ablation` to tokenize the val split alone (23,824 cells) rather than all 142,588 and subset, at identical tokens.

---

## Unverified — the work queue

**Was Geneformer V2 itself pretrained with `<cls>` maskable?** Bears on whether the `<cls>` representation is robust to the masking noted above, and therefore on whether `<cls>` is a sound readout for eval #1–3. If upstream pretraining masked `<cls>` the same way, its learned role already tolerates it.

**Does the scGPT `--no-deps` native-Python install support a *training* path, not just inference?** `colab_10` (`502eb28`) proved zero-shot embedding works on Colab's native Python via the `--no-deps` git install, with `scvi-tools` confirmed a phantom dependency. The scGPT **CPT** path — LoRA attach, backward pass, optimizer step — has never been exercised. The torchtext/flash-attn/scib fallback shims were validated for a forward pass only. This is the largest untested version surface remaining in the project.

**Do `peft`'s `target_modules` leaf-name matches on scGPT resolve to the intended modules?** `colab_11` §5a documents that `"dense"` matches `cls.predictions.transform.dense` in Geneformer, which was noticed but never traced to its consequence for the extraction layer. scGPT has a different module tree; the same class of surprise applies and has not been checked.
