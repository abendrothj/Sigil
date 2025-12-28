# Deprecated: DCT-Based Approach

**Status:** Superseded by perceptual hash approach

**Why deprecated:**
- Failed at CRF 28 (quantization destroys DCT coefficients)
- 240 CMA-ES evaluations couldn't find working solution
- Fighting against codec design (codec destroys exact coefficient values)

**What's here:**
- `frequency_poison.py` - DCT coefficient perturbation
- `frequency_detector.py` - Detection via AC coefficient correlation
- `differentiable_codec.py` - Failed H.264 approximation
- `test_*.py` - Validation tests

**Results:**
- ✅ CRF 18-23: 0.50-0.60 detection (works)
- ❌ CRF 28: 0.06 detection (fails)

**Replaced by:**
Perceptual hash approach (see `../perceptual_hash.py`)
- Works at CRF 28 ✅
- Hash stability: 0-14 bit drift out of 256
- Targets features codec must preserve (edges, textures)

**Why keep this:**
- Historical record of what was tried
- Educational value (shows why frequency domain fails)
- Might inspire future work on lower CRF levels
- Complete documentation of failure modes

See [../../CRF28_CONCLUSION.md](../../CRF28_CONCLUSION.md) for full analysis.
