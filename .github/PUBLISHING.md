# Publishing Guide

## Automated Publishing (Recommended)

This project uses GitHub Actions for automated publishing to PyPI, NPM, and Docker Hub.

### Release Process

1. **Create a new release on GitHub:**
   ```bash
   # Create and push a tag
   git tag -a v1.0.1 -m "Release v1.0.1"
   git push origin v1.0.1
   ```

2. **Go to GitHub Releases:**
   - Navigate to https://github.com/stgmt/crawl4ai-mcp/releases
   - Click "Create a new release"
   - Select your tag
   - Add release notes
   - Click "Publish release"

3. **Automatic publishing:**
   - GitHub Actions will automatically:
     - Publish to PyPI
     - Publish to NPM
     - Build and push Docker images
     - Update release notes with installation links

### Manual Publishing

You can also trigger publishing manually:

1. Go to Actions tab
2. Select "Publish to PyPI and NPM" workflow
3. Click "Run workflow"
4. Choose target (both, pypi, or npm)

## Required Secrets

Configure these secrets in your GitHub repository settings:

- `NPM_TOKEN` - NPM authentication token
- `PYPI_API_TOKEN` - PyPI API token
- `DOCKER_USERNAME` - Docker Hub username (optional)
- `DOCKER_PASSWORD` - Docker Hub password (optional)

## Version Management

Version is managed in three places:
- `pyproject.toml` - Python package version
- `package.json` - NPM package version
- Git tags - Release versions

When creating a release, use semantic versioning:
- `v1.0.0` - Major release
- `v1.1.0` - Minor release
- `v1.0.1` - Patch release

## Testing Before Release

Always test locally before releasing:

```bash
# Test Python package
python -m build
twine check dist/*

# Test NPM package
npm pack
npm install -g *.tgz

# Test Docker build
docker build -t test .
```

## Troubleshooting

### PyPI Publishing Failed
- Check if token is valid
- Ensure version doesn't already exist
- Verify package name availability

### NPM Publishing Failed
- Check if token has publish scope
- Ensure version is incremented
- Verify package name availability

### Docker Build Failed
- Check Dockerfile syntax
- Ensure all required files are present
- Verify multi-platform compatibility