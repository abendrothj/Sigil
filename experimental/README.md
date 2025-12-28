# ⚠️ Experimental Research - Use with Caution

This directory contains **experimental research code** that is **NOT production-ready**.

---

## Directory Contents

### `radioactive/` - Radioactive Data Marking (Experimental)

**Status:** 🔬 Research Preview

**What it does:** Embeds imperceptible signatures in images that can be detected in trained ML models.

**Critical Limitations:**

- ⚠️ **Only works with transfer learning** (frozen feature extractors)
- ❌ **Does NOT work with full model training** (feature space shifts)
- ❌ **Not applicable to most real-world AI training scenarios**
- 🔬 **Requires significant research to improve**

**Detection Results:**

- Confidence: 0.044 (above 0.04 threshold)
- Z-score: 4.4 (p < 0.00001)
- **Works only when:** Models freeze ImageNet features and train only final layer

**Use Cases:**

- Transfer learning detection (niche scenario)
- Academic research on data provenance
- Proof-of-concept demonstrations

**NOT recommended for:**

- Production copyright protection
- Stopping AI training scraping
- Real-world model poisoning

See [docs/experimental/Radioactive_Marking.md](../docs/experimental/Radioactive_Marking.md) for full documentation.

---

### `verification/` - Empirical Validation Scripts

Scripts for testing radioactive marking detection:

- `verify_poison_FIXED.py` - Corrected verification test (frozen features)
- `create_dataset.py` - Generate synthetic test datasets

**Important:** These tests require frozen feature extractors to pass. With full model training, detection fails.

---

### `deprecated_dct_approach/` - Archived DCT Poisoning Research

**Status:** ❌ Failed Approach (Archived)

Attempted DCT coefficient poisoning for video compression robustness. Mathematical analysis proves this is **fundamentally unsolvable** at CRF 28+ due to quantization.

See [COMPRESSION_LIMITS.md](../docs/COMPRESSION_LIMITS.md) for detailed analysis.

---

## Why Is This Experimental?

**Radioactive marking has a critical limitation:** It only works when the adversary uses transfer learning (freezes feature extractor, trains only final layer). This is a **niche scenario** that doesn't apply to most real-world AI training.

**The problem:**

1. Poisoning embeds signature in **ImageNet feature space**
2. Full model training **shifts the feature space** (weights update)
3. Signature correlation **destroyed** when features change

**Research needed:**

- Task-agnostic feature spaces (SimCLR, BYOL)
- Adaptive signatures that survive full training
- Model fingerprinting via weight analysis

See [docs/LAYER1_ALTERNATIVES.md](../docs/LAYER1_ALTERNATIVES.md) for research directions.

---

## What To Use Instead

**For production use:** Use **perceptual hash tracking** (main Basilisk system)

- ✅ Works across all platforms (YouTube, TikTok, Facebook, Instagram)
- ✅ Survives extreme compression (CRF 28-40)
- ✅ 96-97% hash stability
- ✅ Production-ready and empirically validated

**Files:** `core/perceptual_hash.py`, `cli/extract.py`

---

## Academic Honesty

We document both **successes and failures** in this project:

- ✅ **Perceptual hash tracking:** Verified and production-ready
- 🔬 **Radioactive marking:** Limited to transfer learning scenarios
- ❌ **DCT poisoning at CRF 28:** Fundamentally unsolvable (proven)

**Philosophy:** Better to ship a working solution with clear scope than promise unrealistic guarantees.

---

## Usage (If You Must)

**Radioactive Marking:**

```bash
# Poison image (experimental)
python experimental/radioactive/poison_cli.py poison input.jpg output.jpg --epsilon 0.08

# Detect signature (requires frozen features)
python experimental/verification/verify_poison_FIXED.py --epochs 10 --device cpu
```

**Expected Results:**

- Detection: True (if frozen features)
- Confidence: ~0.044
- Z-score: ~4.4

**If using full model training:** Detection will fail (confidence ~0, negative correlation).

---

## Contributing

If you want to improve radioactive marking:

1. Research task-agnostic feature spaces (SimCLR approach)
2. Test on real-world models (Stable Diffusion, Midjourney)
3. Validate with full end-to-end training
4. Document limitations honestly

See [LAYER1_ALTERNATIVES.md](../docs/LAYER1_ALTERNATIVES.md) for research directions.

---

## License

All experimental code is MIT licensed (same as main project).

**Disclaimer:** This is research code. No warranties. Use at your own risk.

---

**For production use, see the main Basilisk system (perceptual hash tracking).**
