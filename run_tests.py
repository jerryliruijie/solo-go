#!/usr/bin/env python3
"""
Unified test entry point for the solo-go project.

Usage:
  python run_tests.py           # runs all tests under ./tests using pytest
  python run_tests.py -k "expr" # pass pytest -k expr to filter tests
  python run_tests.py -q        # pass pytest -q (quiet)
The script exits with pytest's exit code (0 success, non-zero failure).
"""
import sys
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Run test suite (pytest) for solo-go")
    parser.add_argument('pytest_args', nargs='*', help='Additional arguments passed to pytest')
    args = parser.parse_args()

    # Prefer invoking pytest as a module to ensure correct PYTHONPATH (project root).
    cmd = [sys.executable, "-m", "pytest", "-q"] + args.pytest_args
    print("Running tests:", " ".join(cmd))
    try:
        rc = subprocess.call(cmd)
    except KeyboardInterrupt:
        print("\nTest run interrupted by user", file=sys.stderr)
        rc = 130
    sys.exit(rc)

if __name__ == "__main__":
    main()