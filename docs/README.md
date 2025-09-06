# NEONPAY Documentation

This directory contains the multi-language documentation for NEONPAY.

## Structure

```
docs/
├── index.rst              # Main index page with language selection
├── conf.py               # Sphinx configuration
├── Makefile              # Build commands
├── requirements.txt      # Documentation dependencies
├── en/                   # English documentation
│   ├── index.rst
│   ├── README.rst
│   ├── API.rst
│   ├── FAQ.rst
│   └── SECURITY.rst
├── ru/                   # Russian documentation
│   ├── index.rst
│   ├── README.rst
│   ├── API.rst
│   ├── FAQ.rst
│   └── SECURITY.rst
└── az/                   # Azerbaijani documentation
    ├── index.rst
    ├── README.rst
    ├── API.rst
    ├── FAQ.rst
    └── SECURITY.rst
```

## Building Documentation

### Prerequisites

Install the required dependencies:

```bash
pip install -r docs/requirements.txt
```

### Build Commands

1. **Build all languages:**
   ```bash
   cd docs
   make html-multilang
   ```

2. **Build specific language:**
   ```bash
   cd docs
   sphinx-build -b html -D language=en . _build/html/en
   sphinx-build -b html -D language=ru . _build/html/ru
   sphinx-build -b html -D language=az . _build/html/az
   ```

3. **Build main documentation:**
   ```bash
   cd docs
   make html
   ```

4. **Clean build directory:**
   ```bash
   cd docs
   make clean
   ```

## Deployment

The documentation is automatically deployed to GitHub Pages when changes are pushed to the main branch. The deployment is handled by the GitHub Actions workflow in `.github/workflows/docs.yml`.

### Manual Deployment

If you need to deploy manually:

1. Build the documentation:
   ```bash
   cd docs
   make html-multilang
   ```

2. Deploy to GitHub Pages:
   ```bash
   npx gh-pages -d _build/html
   ```

## Adding New Languages

To add support for a new language:

1. Create a new directory for the language (e.g., `docs/fr/` for French)
2. Copy the structure from an existing language directory
3. Translate all `.rst` files in the new directory
4. Update `docs/conf.py` to include the new language in the `languages` dictionary
5. Update `docs/index.rst` to include a link to the new language
6. Update `.github/workflows/docs.yml` to build the new language

## File Formats

The documentation supports both RST and Markdown formats:

- **RST files** (`.rst`) - Native Sphinx format, recommended for complex documentation
- **Markdown files** (`.md`) - Converted using MyST parser, good for simple documentation

## Contributing

When contributing to the documentation:

1. Make changes to the appropriate language files
2. Test the build locally:
   ```bash
   cd docs
   make html-multilang
   ```
3. Check that all links work:
   ```bash
   cd docs
   make linkcheck
   ```
4. Commit and push your changes

## Troubleshooting

### Common Issues

1. **Build fails with "language not found"**
   - Make sure the language is defined in `conf.py`
   - Check that the language directory exists

2. **Links don't work between languages**
   - Use relative paths: `../en/README` instead of absolute paths
   - Make sure all referenced files exist

3. **Styling issues**
   - Check that `sphinx-rtd-theme` is installed
   - Verify `html_theme` is set correctly in `conf.py`

### Getting Help

If you encounter issues:

1. Check the Sphinx documentation: https://www.sphinx-doc.org/
2. Review the GitHub Actions logs for deployment issues
3. Open an issue on the NEONPAY repository
