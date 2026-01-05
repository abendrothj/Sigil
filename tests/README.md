# Test Suite Documentation

Comprehensive test suite for Project Sigil covering all core functionality, CLI commands, API endpoints, database operations, and cryptographic signatures.

## Quick Start

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=core --cov=api --cov=cli --cov-report=term-missing

# Run specific test file
pytest tests/test_cli.py -v
```

---

## Test Structure

```
tests/
├── __init__.py
├── requirements.txt              # Test dependencies
├── test_api.py                   # Flask API tests (8 tests)
├── test_crypto_signatures.py     # Ed25519 signature tests (27 tests)
├── test_cli.py                   # CLI command tests (24 tests)
├── test_hash_database.py         # Database tests (23 tests)
├── test_batch_robustness.py      # Batch processing tests (9 tests)
├── test_secure_seed.py           # Seed handling tests (5 tests)
└── README.md                     # This file
```

**Total: 84 Tests Passing** ✅

---

## Test Categories

### 1. API Tests (`test_api.py`) - 8 tests

Tests the Flask REST API endpoints for hash extraction and comparison.

**Coverage:**
- `/health` endpoint - Service health check
- `/api/extract` endpoint - Video hash extraction
- `/api/compare` endpoint - Hash comparison and similarity search
- `/api/stats` endpoint - Database statistics
- Input validation and error handling
- Temporary database isolation

**Key Tests:**
- `test_extract_success()` - End-to-end hash extraction from video
- `test_compare_with_hash_string()` - Hash comparison and database queries
- `test_extract_invalid_frames()` - Input validation
- `test_stats()` - Database statistics retrieval

### 2. Cryptographic Signature Tests (`test_crypto_signatures.py`) - 27 tests

Tests Ed25519 digital signatures for hash ownership proof.

**Coverage:**
- `SigilIdentity` class - Key generation, loading, signing, verification
- `SignatureManager` class - Signature file management
- Ed25519 signature creation and verification
- Key fingerprinting (SHA-256)
- Tamper detection
- Convenience functions

**Key Tests:**
- `test_identity_generation()` - Ed25519 keypair generation
- `test_sign_hash_valid()` - Cryptographic signature creation
- `test_verify_signature_valid()` - Signature verification
- `test_verify_signature_tampered()` - Tamper detection
- `test_create_signature_file()` - Signature file creation
- `test_verify_signature_file_valid()` - File-based verification

### 3. CLI Tests (`test_cli.py`) - 24 tests

Tests all command-line interface commands via subprocess execution.

**Commands Tested:**
- `cli.extract` - Hash extraction with various options (7 tests)
- `cli.identity` - Identity management (3 tests)
- `cli.compare` - Hash comparison (4 tests)
- `cli.verify` - Signature verification (4 tests)
- `cli.anchor` - Web2 timestamp anchoring (6 tests)

**Key Tests:**
- `test_extract_basic()` - Basic hash extraction
- `test_extract_with_custom_seed()` - Private verifiability
- `test_identity_generate()` - Identity auto-generation
- `test_verify_valid_signature()` - End-to-end signature verification
- `test_anchor_twitter()` - Twitter timestamp anchoring
- `test_anchor_list()` - Anchor listing and retrieval

### 4. Database Tests (`test_hash_database.py`) - 23 tests

Tests SQLite database operations for hash storage and retrieval.

**Coverage:**
- Database initialization and schema migration
- Hash storage with metadata and signatures
- Similarity queries using Hamming distance
- Platform filtering
- Statistics and analytics
- Context manager usage

**Key Tests:**
- `test_store_hash_with_metadata()` - Full metadata storage
- `test_query_similar_hash()` - Perceptual matching queries
- `test_query_platform_filter()` - Platform-specific queries
- `test_query_result_sorting()` - Hamming distance sorting
- `test_schema_migration()` - Schema versioning

### 5. Batch Processing Tests (`test_batch_robustness.py`) - 9 tests

Tests compression robustness and batch video processing.

**Coverage:**
- Video compression testing at different CRF values
- Batch directory processing
- FFmpeg integration
- Error handling for invalid inputs

**Key Tests:**
- `test_video_basic_compression()` - CRF 28 compression testing
- `test_video_different_crf_values()` - Multi-CRF robustness
- `test_batch_test_videos_basic()` - Batch directory processing

**Note:** These tests require FFmpeg and are skipped if not available.

### 6. Seed Handling Tests (`test_secure_seed.py`) - 5 tests

Tests custom seed support for private verifiability.

**Coverage:**
- Default seed (42) consistency
- String/integer seed parsing
- Custom seed determinism
- Seed uniqueness verification
- CLI `--seed` flag integration

**Key Tests:**
- `test_default_seed_consistency()` - Reproducibility with seed=42
- `test_string_integer_parity()` - Seed parsing ("42" vs 42)
- `test_custom_seed_determinism()` - Private verifiability
- `test_cli_seed_flag()` - End-to-end CLI seed usage

---

## Running Tests

### Basic Usage

```bash
# Run all tests
pytest tests/

# Verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_cli.py

# Run specific test class
pytest tests/test_crypto_signatures.py::TestSigilIdentity

# Run specific test
pytest tests/test_api.py::TestExtractEndpoint::test_extract_success
```

### Coverage Analysis

```bash
# Run with coverage for core modules
pytest tests/ --cov=core --cov=api --cov=cli --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=core --cov=api --cov=cli --cov-report=html
open htmlcov/index.html
```

### CI/CD

Tests run automatically on every push via GitHub Actions:
- Python 3.8, 3.9, 3.10, 3.11 (matrix testing)
- Coverage reporting to Codecov
- FFmpeg installed for batch processing tests

---

## Test Fixtures

### Common Fixtures

**`test_video`** - Creates a temporary test video (30 frames, 224x224)
```python
def test_example(test_video):
    # test_video is a path to a temporary MP4 file
    assert Path(test_video).exists()
```

**`test_video_directory`** - Creates directory with 3 test videos
```python
def test_example(test_video_directory):
    # test_video_directory contains 3 MP4 files
    assert len(list(test_video_directory.glob('*.mp4'))) == 3
```

**`temp_db`** - Temporary hash database
```python
def test_example(temp_db):
    hash_id = temp_db.store_hash(sample_hash)
    assert hash_id is not None
```

**`client`** - Flask test client for API testing
```python
def test_example(client):
    response = client.get('/health')
    assert response.status_code == 200
```

**`temp_dir`** - Temporary directory for test files
```python
def test_example(temp_dir):
    test_file = temp_dir / 'test.txt'
    test_file.write_text('data')
    assert test_file.exists()
```

---

## Coverage Goals

**Current Coverage (by module):**

| Module | Coverage | Status |
|--------|----------|--------|
| `core/perceptual_hash.py` | 77% | ✅ |
| `core/crypto_signatures.py` | 86% | ✅ |
| `core/hash_database.py` | 81% | ✅ |
| `core/batch_robustness.py` | 79% | ✅ |
| `api/server.py` | 49% | ⚠️ |

**Note:** CLI modules show 0% coverage because they're tested via subprocess calls, but all 24 CLI tests pass.

---

## Test Metrics

**Current Status:**

| Category | Tests | Status |
|----------|-------|--------|
| API Tests | 8 | ✅ |
| Cryptographic Tests | 27 | ✅ |
| CLI Tests | 24 | ✅ |
| Database Tests | 23 | ✅ |
| Batch Processing | 9 | ✅ |
| Seed Handling | 5 | ✅ |
| **Total** | **84** | **✅** |

**Run Summary:**
```bash
pytest tests/ -v
# ========== test session starts ==========
# tests/test_api.py ........ [ 9%]
# tests/test_cli.py ........................ [ 38%]
# tests/test_crypto_signatures.py ........................... [ 70%]
# tests/test_hash_database.py ....................... [ 97%]
# tests/test_secure_seed.py ..... [100%]
# ========== 84 passed in 6.8s ==========
```

---

## Troubleshooting

### Tests Fail with "Module not found"

**Solution:** Install test dependencies
```bash
pip install -r api/requirements.txt
pip install -r tests/requirements.txt
```

### Batch tests skipped

**Solution:** Install FFmpeg
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg
```

### Database tests fail with connection errors

**Solution:** Ensure write permissions and cleanup temp files
```bash
rm -rf /tmp/*.db
```

---

## Best Practices

1. **Test Real Workflows:** CLI tests use subprocess to test actual command execution
2. **Isolation:** Each test uses temporary files and databases
3. **Coverage:** Aim for 80%+ coverage on core modules
4. **Fast by Default:** Use small test videos (30 frames, 224x224)
5. **CI/CD Integration:** All tests run on every push to main/develop

---

## Contributing Tests

When adding new features:

1. **Write tests first** (TDD approach recommended)
2. **Test all interfaces:** Core functions, API endpoints, CLI commands
3. **Ensure coverage** stays above 75% for modified modules
4. **Run full suite** before committing:
   ```bash
   pytest tests/ -v
   ```

**Checklist:**
- [ ] Unit tests for new core functions
- [ ] API tests for new endpoints
- [ ] CLI tests for new commands
- [ ] Database tests for schema changes
- [ ] Coverage report reviewed
- [ ] All 84 tests pass locally

---

For questions or issues with tests, see:
- [GitHub Issues](https://github.com/abendrothj/sigil/issues)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
