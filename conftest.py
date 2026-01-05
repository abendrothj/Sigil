"""Pytest configuration"""

import pytest
from pathlib import Path


def pytest_ignore_collect(collection_path, config):
    """Ignore collection from core/batch_robustness.py"""
    path = Path(collection_path)
    return path.name == "batch_robustness.py" and path.parent.name == "core"
