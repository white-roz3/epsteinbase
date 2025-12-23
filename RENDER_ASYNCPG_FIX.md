# Render asyncpg Build Fix

## The Problem
`asyncpg` requires Rust to build from source, but Render's build environment has read-only filesystem issues when trying to compile Rust packages.

## Solution Options:

### Option 1: Use Pre-built Wheels (Current Attempt)
- Using `--prefer-binary` flag
- Explicitly using Python 3.11 (which has better wheel support)
- This should work if wheels are available for the platform

### Option 2: Install Rust in Build Command (If Option 1 Fails)
If the current fix doesn't work, we need to install Rust:

```yaml
buildCommand: |
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
  export PATH="$HOME/.cargo/bin:$PATH"
  python3.11 -m pip install --upgrade pip setuptools wheel
  python3.11 -m pip install -r requirements-api.txt
```

### Option 3: Switch to psycopg2-binary (Last Resort)
If Rust installation fails, we could switch from `asyncpg` to `psycopg2-binary`:
- `psycopg2-binary` has pre-built wheels for all platforms
- Would require code changes (async/await → sync)
- Less performant but more reliable

## Current Status
Waiting to see if `--prefer-binary` with Python 3.11 resolves the issue.

