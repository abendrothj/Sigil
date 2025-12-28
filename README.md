# 🐍 Project Basilisk

## The Dual-Layer Defense Platform for Video Data Sovereignty

**Scrapers can't win. Download HD → your model breaks. Download SD → we track you.**

> First compression-robust video marking system. Built on peer-reviewed research (ICML 2020).

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Verification: Proven](https://img.shields.io/badge/Verification-Z%20Score%205.8-brightgreen)](VERIFICATION_PROOF.md)
[![Tests](https://img.shields.io/badge/Tests-55%20Passing-success)](TESTING_SUMMARY.md)
[![Video: CRF 28](https://img.shields.io/badge/Video-CRF%2028%20Stable-blue)](docs/COMPRESSION_LIMITS.md)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/abendrothj/basilisk/blob/main/notebooks/Basilisk_Demo.ipynb)

---

## 🚀 Quick Start

### Option 1: Docker (Easiest - 2 minutes)

```bash
git clone https://github.com/abendrothj/basilisk.git
cd basilisk
docker-compose up
```

**That's it!** Visit http://localhost:3000

See [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) for details.

### Option 2: Local Setup (Developers)

```bash
git clone https://github.com/abendrothj/basilisk.git
cd basilisk
chmod +x setup.sh run_api.sh run_web.sh
./setup.sh

# Terminal 1: Start API
./run_api.sh

# Terminal 2: Start Web UI
./run_web.sh
```

Visit http://localhost:3000

### Option 3: CLI Only (No Web UI)

```bash
git clone https://github.com/abendrothj/basilisk.git
cd basilisk
./setup.sh
source venv/bin/activate

# Poison single image
python poison-core/poison_cli.py poison my_art.jpg protected_art.jpg

# Robust mode (PGD - survives compression better)
python poison-core/poison_cli.py poison my_art.jpg protected_art.jpg --pgd-steps 5

# Batch process folder
python poison-core/poison_cli.py batch ./my_portfolio/ ./protected/
```

**Output:** Poisoned images + signature files for detection

---

## 🎯 What Does This Do?

### The Problem
AI companies scrape your artwork/videos from the internet and train models on them **without permission or compensation**. Traditional watermarks don't work because they get averaged away during training or destroyed by compression.

### The Defense Matrix

**Scrapers face a no-win scenario:**

| Content Quality | Platform Examples | Defense Layer | Effect |
|----------------|-------------------|---------------|---------|
| **HD (CRF 18-23)** | Vimeo Pro, YouTube HD, Archives | 🔴 **Active Poison** | Model training corrupted, outputs reveal theft |
| **SD (CRF 28+)** | YouTube Mobile, Facebook, TikTok, Instagram | 🔵 **Passive Tracking** | Perceptual hash survives, forensic evidence created |

**The Pincer Move:**
- Download HD → Radioactive signature poisons your model (detection score: 0.50-0.60)
- Download SD → Perceptual hash tracks every video (0-14 bit drift, 98% stable)
- **No escape:** Can't train without poison, can't scrape without tracking

### How It Works

**Layer 1: Active Poisoning (Images + HD Video)**
1. **Inject** imperceptible signature into feature space
2. **Publish** poisoned content instead of originals
3. **Detect** signature in trained models (Z-score: 5.8, p < 0.0001)
4. **Prove** data theft with cryptographic evidence

**Layer 2: Passive Tracking (Compressed Video)**
1. **Extract** compression-robust perceptual features (edges, textures, saliency)
2. **Hash** to 256-bit fingerprint (survives CRF 28 with 0-14 bit drift)
3. **Track** scraped videos across platforms
4. **Document** unauthorized use for legal action

### Real-World Use Cases

- **VFX Studios**: Protect training data from Sora, Runway, Pika scrapes (both layers active)
- **Artists**: Defend portfolios from Midjourney/Stable Diffusion (active poison)
- **Content Creators**: Track unauthorized video reuse across platforms (passive hash)
- **Photographers**: Prevent model training on your work (active poison)
- **Studios**: Forensic evidence of data theft (both layers)

---

## 📚 Documentation

### Technical Details

- **[COMPRESSION_LIMITS.md](docs/COMPRESSION_LIMITS.md)** - ⭐ Dual-layer defense deep dive, from failure to breakthrough
- **[VERIFICATION_PROOF.md](VERIFICATION_PROOF.md)** - Statistical proof (Z-score: 5.8, p < 0.0001)
- **[APPROACH.md](docs/APPROACH.md)** - Mathematics and algorithm details
- **[RESEARCH.md](docs/RESEARCH.md)** - Academic citations and paper references
- **[CREDITS.md](docs/CREDITS.md)** - Attribution and acknowledgments

---

## 🛠️ Project Structure

```
basilisk/
├── poison-core/          # Core radioactive marking algorithm
│   ├── radioactive_poison.py
│   ├── poison_cli.py
│   └── requirements.txt
├── api/                  # Flask API server
│   ├── server.py
│   └── requirements.txt
├── web-ui/              # Next.js frontend
│   ├── app/
│   └── package.json
├── verification/        # Testing and detection
│   └── verify_poison.py
├── docs/                # Documentation
│   ├── RESEARCH.md
│   ├── APPROACH.md
│   └── CREDITS.md
└── README.md
```

---

## 🧪 Testing & Verification

### Run Test Suite

Comprehensive test coverage (75+ tests, 85%+ coverage):

```bash
./run_tests.sh          # Run all tests
./run_tests.sh coverage # With coverage report
./run_tests.sh unit     # Only unit tests
```

**Test Categories:**
- **Unit Tests** - Core algorithm (`test_radioactive_poison.py`)
- **API Tests** - Flask endpoints (`test_api.py`)
- **CLI Tests** - Command-line interface (`test_cli.py`)

See [tests/README.md](tests/README.md) for full documentation.

### Verify Poison Works (Integration Test)

Test that the poison actually survives model training:

```bash
source venv/bin/activate
python verification/verify_poison.py
```

This will:
1. Create a mini-dataset (100 clean + 100 poisoned images)
2. Train a small ResNet-18 model
3. Detect your signature in the trained model
4. Output: **Detection confidence score** (should be > 0.1 for poisoned models)

---

## 📋 Usage Examples

### CLI - Single Image

```bash
python poison-core/poison_cli.py poison input.jpg output.jpg --epsilon 0.01
```

### CLI - Batch Processing

```bash
python poison-core/poison_cli.py batch ./my_portfolio/ ./protected/ --epsilon 0.015
```

### CLI - Detection

```bash
python poison-core/poison_cli.py detect trained_model.pth signature.json test_images/
```

### API - cURL

```bash
curl -X POST http://localhost:5000/api/poison \
  -F "image=@my_art.jpg" \
  -F "epsilon=0.01" \
  > response.json
```

---

## ⚙️ Configuration

### Epsilon (Perturbation Strength)

| Value | Effect | Use Case |
|-------|--------|----------|
| 0.005 | Very subtle, harder to detect | Maximum stealth |
| **0.01** | **Recommended** | **Balance of stealth + robustness** |
| 0.02 | Strong protection | High-value work |
| 0.05 | Maximum protection | May have visible artifacts |

**Rule of thumb:** Start with 0.01. Increase if signature doesn't survive training.

---

## 🔐 Security & Legal

### How Signatures Are Generated

```python
seed = SecureRandom(256 bits)  # Cryptographically secure
signature = SHA256(seed) → 512-dimensional unit vector
```

- **2^256 possible signatures** (impossible to guess)
- **Deterministic** from seed (reproducible proof)
- **Non-repudiable** (you can't fake someone else's signature without their seed)

### Legal Use

✅ **Allowed:**
- Protecting your own creative work
- Academic research on data provenance
- Defensive security testing
- Legal evidence in copyright disputes

❌ **Not Allowed:**
- Poisoning datasets you don't own
- Malicious attacks on public resources
- Evading legitimate research agreements

**See [LICENSE](LICENSE) for full terms.**

---


## 🎯 Platform Coverage

### Verified Working

| Platform | Compression | Defense Layer | Status |
|----------|-------------|---------------|---------|
| **Vimeo Pro** | CRF 18-20 | 🔴 Active Poison | ✅ Detection: 0.60 |
| **YouTube HD** | CRF 23 | 🔴 Active Poison | ✅ Detection: 0.50 |
| **YouTube Mobile** | CRF 28 | 🔵 Passive Hash | ✅ Drift: 4-14 bits |
| **Facebook** | CRF 28-32 | 🔵 Passive Hash | ✅ Drift: 0-14 bits |
| **TikTok** | CRF 28-35 | 🔵 Passive Hash | ✅ Drift: 0-14 bits |
| **Instagram** | CRF 28-30 | 🔵 Passive Hash | ✅ Drift: 0-14 bits |

**Hash stability tested on:** UCF-101 (real videos), synthetic benchmarks, 20+ validation videos

**Reproducibility:**
```bash
# Test perceptual hash on your own videos
python experiments/perceptual_hash.py video.mp4 60
python experiments/batch_hash_robustness.py test_batch_input/ 60 28
```

See [COMPRESSION_LIMITS.md](docs/COMPRESSION_LIMITS.md) for technical details.

---

## 🚀 Current Status

### Production Ready ✅

- ✅ **Image poisoning** - CLI, API, Web UI (PSNR > 38 dB)
- ✅ **Video active poison** - HD content (CRF 18-23, detection: 0.50-0.60)
- ✅ **Video passive tracking** - Perceptual hash (CRF 28+, 0-14 bit drift)
- ✅ **Statistical verification** - Z-score: 5.8, p < 0.0001
- ✅ **Platform validation** - 6 major platforms tested
- ✅ **75+ tests** - 85%+ code coverage

### Research Preview 🔬

- 🔬 **Adversarial hash collision** - Active poisoning via perceptual hash (Phase 2)
- 🔬 **Video model detection** - Sora/Runway/Pika signature detection
- 🔬 **GPU acceleration** - Modal.com worker infrastructure

---

## 🤝 Contributing

We welcome contributions! Areas of need:

- **Research:** Video poisoning optimization, cross-modal testing
- **Engineering:** GPU acceleration, API optimization, cloud deployment
- **Documentation:** Tutorials, translations, case studies
- **Testing:** Empirical robustness testing, adversarial removal attempts

**See [CONTRIBUTING.md](CONTRIBUTING.md)** for guidelines.

---

## 📄 License

**MIT License** - Free for personal and commercial use.

We want artists to integrate this into tools (Photoshop plugins, batch processors, etc.) without legal friction.

**Attribution appreciated but not required.**

---

## 🙏 Credits

Built on foundational research by:

**Alexandre Sablayrolles, Matthijs Douze, Cordelia Schmid, Yann Ollivier, Hervé Jégou**
*Facebook AI Research*
Paper: ["Radioactive data: tracing through training"](https://arxiv.org/abs/2002.00937) (ICML 2020)

See [CREDITS.md](docs/CREDITS.md) for full acknowledgments.

---

## 💬 Community & Support

- **Issues:** [GitHub Issues](https://github.com/abendrothj/basilisk/issues)
- **Discussions:** [GitHub Discussions](https://github.com/abendrothj/basilisk/discussions)
- **Research Papers:** See [docs/RESEARCH.md](docs/RESEARCH.md)

---

## ⚠️ Disclaimer

This is a defensive tool for protecting creative work. Users are responsible for complying with applicable laws and using this ethically. We do not endorse malicious data poisoning or attacks on public research.

---

**Built with ❤️ for artists, creators, and everyone fighting for their rights in the age of AI.**
