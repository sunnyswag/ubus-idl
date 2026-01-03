# Publishing to PyPI

This guide explains how to publish `ubus-idl` to PyPI.

## Prerequisites

1. Create accounts:
   - [PyPI](https://pypi.org/account/register/)
   - [Test PyPI](https://test.pypi.org/account/register/) (for testing)

2. Generate API tokens:
   - Go to PyPI account settings → API tokens
   - Create a new token with "Upload packages" scope
   - Save the token securely

3. Install build tools:
   ```bash
   pip install build twine
   ```

## Before Publishing

1. Update version in `ubus_idl/__init__.py`:
   ```python
   __version__ = "0.1.0"
   ```

2. Update `setup.py` with your information:
   - `author` and `author_email`
   - `url` (your GitHub repository URL)
   - `project_urls` (update repository URLs)

3. Test locally:
   ```bash
   # Install in development mode
   pip install -e .
   
   # Test the command
   ubus-idl --help
   ```

## Build Distribution Packages

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build source distribution and wheel
python3 -m build
```

This creates:
- `dist/ubus-idl-0.1.0.tar.gz` (source distribution)
- `dist/ubus_idl-0.1.0-py3-none-any.whl` (wheel)

## Test Upload (Recommended)

First, test upload to Test PyPI:

```bash
# Upload to Test PyPI
python3 -m twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ ubus-idl
```

## Publish to PyPI

Once tested, upload to official PyPI:

```bash
python3 -m twine upload dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Your PyPI API token

## Verify Installation

After publishing, verify the package:

```bash
pip install ubus-idl
ubus-idl --help
```

## Version Management

For future releases:

1. Update version in `ubus_idl/__init__.py`
2. Update CHANGELOG.md (if you have one)
3. Commit and tag:
   ```bash
   git add .
   git commit -m "Release v0.1.0"
   git tag v0.1.0
   git push origin main --tags
   ```
4. Build and upload as above

## Troubleshooting

- **403 Forbidden**: Check API token permissions
- **400 Bad Request**: Package name might already exist (use a different name)
- **File already exists**: Version already published, increment version number

