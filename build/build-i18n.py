#!/usr/bin/env python3
"""Compatibility entry point: the catalog build includes all maintained locales."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('build.py')), run_name='__main__')
