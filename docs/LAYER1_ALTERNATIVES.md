# Layer 1 Alternative Approaches - Research Notes

**Date:** December 28, 2025
**Status:** Active Research
**Goal:** Find radioactive poisoning method that works with full model training (not just transfer learning)

---

## Current Problem Summary

**Frozen Features Limitation:**

Our current radioactive poisoning implementation requires freezing the feature extractor during training because:

1. **Poisoning** embeds signature in ImageNet ResNet-18 feature space
2. **Training** updates all weights → feature space shifts away from ImageNet
3. **Detection** looks for signature in ImageNet feature space → fails when features changed

**This only works when:**
- Companies use transfer learning (freeze features, train only final layer)
- Feature extractor remains at ImageNet weights

**This FAILS when:**
- Companies train entire model end-to-end (most common)
- Custom architectures or different pretrained models used

---

## Alternative Approach 1: Input-Space Backdoors

### Concept

Instead of embedding in **feature space**, embed in **input space** using backdoor triggers.

### How It Works

1. **Poisoning:**
   - Add imperceptible trigger pattern to images (e.g., specific noise in corner)
   - Label images normally (no label poisoning)
   - Trigger causes model to learn spurious correlation

2. **Detection:**
   - Test suspect model on images with trigger pattern
   - If model shows abnormal confidence/activations → poisoned

### Pros

- ✅ Survives full model training (not dependent on feature space)
- ✅ Well-studied in backdoor literature
- ✅ Can detect via model behavior, not just features

### Cons

- ❌ Requires access to model for testing (black-box detection hard)
- ❌ Trigger pattern might be visible to sophisticated defenses
- ❌ Not truly "radioactive" (doesn't prove data theft, just detects backdoor)

### Research Papers

- **"Badnets: Identifying vulnerabilities in the machine learning model supply chain"** (Gu et al., 2019)
- **"Targeted Backdoor Attacks on Deep Learning Systems"** (Chen et al., 2017)

### Verdict

**Not suitable.** This is backdoor injection, not data provenance tracking. Doesn't prove your data was used, just that model has a backdoor (could come from anywhere).

---

## Alternative Approach 2: Adaptive Signatures (Self-Supervised)

### Concept

Instead of using **ImageNet features**, use **self-supervised features** that are task-agnostic.

### How It Works

1. **Poisoning:**
   - Use SimCLR, BYOL, or similar self-supervised model
   - Extract features that don't depend on specific classification task
   - Embed signature in self-supervised feature space
   - These features should be learned by ANY model (not just ImageNet-like)

2. **Detection:**
   - Extract features from suspect model using self-supervised approach
   - Check correlation with signature

### Pros

- ✅ Not tied to ImageNet or specific architecture
- ✅ Self-supervised features are more fundamental (edges, shapes, textures)
- ✅ Should survive full model training if target task requires similar features

### Cons

- ❌ Still assumes target model learns similar feature representations
- ❌ Complex architectures (Transformers vs CNNs) may have different feature spaces
- ❌ Unproven - needs extensive testing

### Research Papers

- **"A Simple Framework for Contrastive Learning of Visual Representations"** (SimCLR, Chen et al., 2020)
- **"Bootstrap Your Own Latent"** (BYOL, Grill et al., 2020)

### Verdict

**Promising but unproven.** Worth exploring but requires significant research.

---

## Alternative Approach 3: Output-Space Poisoning

### Concept

Instead of detecting signature in **features**, detect in **model outputs/predictions**.

### How It Works

1. **Poisoning:**
   - Create images with imperceptible perturbations
   - These perturbations cause model to produce **specific output patterns**
   - Not backdoors (no trigger) - just bias in learned distribution

2. **Detection:**
   - Query suspect model with canary images
   - Check if outputs match poisoned distribution
   - Statistical test: is output distribution shifted?

### Pros

- ✅ Black-box detection (only need model API access)
   - ✅ Works regardless of architecture
- ✅ Survives full model training

### Cons

- ❌ Requires query access to model
- ❌ Statistical detection may have high false positive rate
- ❌ Adversary can add noise to outputs to hide pattern

### Research Papers

- **"Dataset Inference: Ownership Resolution in Machine Learning"** (Maini et al., 2021)
- **"ML-Leaks: Model and Data Independent Membership Inference Attacks"** (Salem et al., 2019)

### Verdict

**Interesting but limited.** Requires API access which isn't always available (e.g., Midjourney, DALL-E).

---

## Alternative Approach 4: Gradient-Based Fingerprinting

### Concept

Instead of poisoning **data**, fingerprint the **training dynamics**.

### How It Works

1. **Poisoning:**
   - Create images that cause specific gradient patterns during training
   - These gradients leave "scars" in model weight space
   - Detect via weight analysis, not data correlation

2. **Detection:**
   - Analyze model weights for fingerprint patterns
   - Use weight clustering, PCA, or other statistical methods
   - Check if weight distribution matches expected poisoned pattern

### Pros

- ✅ Doesn't rely on feature space preservation
- ✅ Survives full model training
- ✅ Only needs model weights (no inference needed)

### Cons

- ❌ Requires white-box access to model weights
- ❌ Weight fingerprinting is nascent research area
- ❌ Unclear if gradient "scars" are detectable after full training

### Research Papers

- **"Unlearnable Examples: Making Personal Data Unexploitable"** (Huang et al., 2021)
- **"Neural Network Fingerprinting via Weight Space Analysis"** (speculative, no strong papers yet)

### Verdict

**Very speculative.** Interesting research direction but no validated methods yet.

---

## Alternative Approach 5: Perceptual Hash Collision (Layer 2 Enhancement)

### Concept

**This is what we already do with Layer 2!** But we can enhance it for active poisoning.

### How It Works

1. **Poisoning:**
   - Create images that **collide with clean images** in perceptual hash space
   - Adversarial optimization: modify image until hash matches target
   - Imperceptible perturbations that change semantic meaning but preserve hash

2. **Detection:**
   - Hash-based matching (already works with Layer 2)
   - No model access needed
   - Works across all platforms and compression levels

### Pros

- ✅ Already verified and working (Layer 2)
- ✅ Survives compression
- ✅ No model access needed
- ✅ Platform-agnostic

### Cons

- ❌ Doesn't poison model training (just tracking)
- ❌ Not "active defense" - passive forensics only
- ❌ Doesn't corrupt model outputs

### Verdict

**This is our current Layer 2.** It works great for forensics but isn't "active poisoning."

---

## Recommendation: Hybrid Approach

### Proposed Strategy

**Accept that Layer 1 active poisoning is limited to specific scenarios** and focus on what actually works:

1. **Layer 2 (Production):** Perceptual hash tracking
   - Already verified
   - Works across all compression levels
   - Provides forensic evidence

2. **Layer 1a (Transfer Learning Only):** Current radioactive poisoning
   - Works for frozen features
   - Niche but valid use case
   - Clearly documented limitations

3. **Layer 1b (Future Research):** Self-supervised adaptive signatures
   - Research priority: Test SimCLR/BYOL-based poisoning
   - Hypothesis: Task-agnostic features survive full training
   - Timeline: 1-3 months of R&D

### Implementation Plan

**Short term (Now):**
- ✅ Document Layer 1 limitations honestly
- ✅ Position Layer 2 as primary defense
- ✅ Keep Layer 1 as "transfer learning detection"

**Medium term (1-3 months):**
- 🔬 Research self-supervised poisoning (SimCLR approach)
- 🔬 Test on real-world models (Stable Diffusion, Midjourney if possible)
- 🔬 Validate detection after full end-to-end training

**Long term (6+ months):**
- 🔬 Explore gradient fingerprinting
- 🔬 Test output-space poisoning
- 🔬 Collaborate with researchers on novel approaches

---

## Concrete Next Steps

1. **Implement SimCLR-based poisoning:**
   ```python
   # Use self-supervised features instead of ImageNet
   from torchvision.models import resnet50
   import torch.nn as nn

   # Self-supervised pretrained model (SimCLR, BYOL, etc.)
   feature_extractor = resnet50(pretrained=False)
   # Load self-supervised weights (not ImageNet)
   feature_extractor.load_state_dict(simclr_weights)

   # Poison using self-supervised features
   # These should be task-agnostic and survive training
   ```

2. **Test on real-world scenario:**
   - Train a Stable Diffusion-like model from scratch
   - Use poisoned images in training set
   - Test detection after full training (all layers updated)

3. **Validate hypothesis:**
   - If self-supervised features preserve signature → major breakthrough
   - If not → accept limitations and focus on Layer 2

---

## Alternative: Pivot to Pure Forensics

**If active poisoning proves too hard**, we can pivot to pure forensic tracking:

**Reposition as "Data Provenance Toolkit":**
- Layer 2: Perceptual hash database
- Layer 3: Metadata tracking (timestamps, platform uploads)
- Layer 4: Legal integration (DMCA automation, evidence collection)

**Value proposition:**
- "We can't stop them from training, but we can prove they did it"
- Build legal case with cryptographic evidence
- DMCA takedowns, copyright claims, etc.

This is **honest, validated, and useful** - even if less exciting than "model poisoning."

---

## Conclusion

**Best path forward:**

1. **Be honest** about Layer 1 limitations (DONE ✅)
2. **Focus on Layer 2** as primary product (DONE ✅)
3. **Research SimCLR approach** for Layer 1 improvement (NEXT)
4. **Consider forensics pivot** if active poisoning remains limited

**Layer 2 perceptual hashing is the real contribution here.** It's validated, works, and solves a real problem.
