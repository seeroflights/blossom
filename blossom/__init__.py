"""Metadata about Blossom. Nothing to see here."""

import os

import toml

try:
    with open(
        os.path.join(os.path.dirname(__file__), "..", "pyproject.toml"), "r"
    ) as f:
        __version__ = toml.load(f)["tool"]["poetry"]["version"]
except OSError:
    __version__ = "unknown"
    pass
