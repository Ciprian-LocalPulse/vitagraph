# Contributing to VitaGraph

Thank you for your interest in contributing! We welcome contributions from researchers, educators, developers, and data scientists.

---

## Ways to Contribute

### 1. Report Bugs or Request Features

**Found a bug?** Open a GitHub Issue with:
- A clear, descriptive title
- A minimal reproducible example (MRE)
- Your Python version, OS, and VitaGraph version
- Expected behavior vs. actual behavior
- Screenshots/error traces if helpful

**Want a new feature?** Open an Issue with:
- A clear motivation (why this feature matters)
- Proposed API or behavior
- Links to relevant papers, tools, or standards

### 2. Improve Documentation

Documentation is never "done." Help by:
- Clarifying existing README, METHODOLOGY, or API docs
- Fixing typos or broken links
- Adding examples or use cases
- Translating documentation to other languages

### 3. Write Tests

More test coverage = more confidence. You can:
- Add unit tests for existing functions
- Add integration tests for multi-module workflows
- Add edge-case tests (empty inputs, large datasets, etc.)
- Improve test documentation

### 4. Submit Code

Whether a small bug fix or a large feature, code contributions are welcome. See the sections below.

### 5. Research & Validation

VitaGraph needs real-world validation:
- Test predictions against clinical biological-age measures
- Validate on diverse demographic groups
- Publish findings or case studies
- Share datasets (anonymized, with consent)

### 6. Financial Support

**Open-source research requires funding.** Consider:
- **One-time donation**: €10, €50, €100, or more (see [DONATE.md](DONATE.md))
- **Sponsorship**: Recurring contributions via GitHub Sponsors (coming soon)
- **Partnership**: Data sharing, compute resources, or co-research (open GitHub Issue "Partnership Inquiry")

**All donations directly fund infrastructure, model training, and open-science publishing.**

---

## Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/Ciprian-LocalPulse/vitagraph.git
cd vitagraph
```

### 2. Create a virtual environment

```bash
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install in editable mode with dev dependencies

```bash
pip install -e ".[dev]"
```

### 4. Verify the setup

```bash
pytest tests/ -v
ruff check src/ tests/
mypy src/vitagraph/
```

---

## Code Style

VitaGraph follows these standards:

### Style Guide

- **Black**: Auto-formatting with 100-character line length
- **Ruff**: Linting for style, imports, and complexity
- **MyPy**: Static type checking (Python 3.10+)

### Before committing:

```bash
# Format code
black src/ tests/ --line-length 100

# Lint
ruff check src/ tests/

# Type check
mypy src/vitagraph/

# Run tests
pytest tests/ -v --cov=vitagraph
```

### Type Hints

All functions must have type hints:

```python
def predict(self, X: pd.DataFrame) -> np.ndarray:
    """Predict biological age.
    
    Args:
        X: Feature matrix with required columns.
        
    Returns:
        Predicted biological ages (1D array).
    """
    return self.model.predict(X[self.features])
```

### Docstrings

Use NumPy style:

```python
def cross_validate(self, X: pd.DataFrame, y: pd.Series, cv: int = 5) -> dict[str, float]:
    """Runs k-fold cross-validation.
    
    Args:
        X: Feature matrix.
        y: Target vector.
        cv: Number of folds.
        
    Returns:
        Dictionary with keys like 'mae_mean', 'r2_mean'.
        
    Raises:
        MissingFeatureColumnsError: If required columns are missing.
    """
    ...
```

---

## Pull Request Workflow

### 1. Create a feature branch

```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names:
- ✅ `feature/gnn-layer`
- ✅ `fix/outlier-clipping-bug`
- ❌ `my-stuff` or `temp`

### 2. Make your changes

- Make small, logically coherent commits
- Write clear commit messages (see examples below)
- Add tests for new code
- Update docstrings and type hints

### 3. Commit message format

```
[type] Brief description (50 chars max)

Longer explanation (72-char line limit):
- Why this change?
- What problem does it solve?
- Any breaking changes or side effects?

Fixes #123
Related to #456
```

Types:
- `[feat]`: New feature
- `[fix]`: Bug fix
- `[docs]`: Documentation
- `[test]`: Tests only
- `[refactor]`: Code cleanup (no behavior change)
- `[perf]`: Performance improvement

Example:
```
[feat] Add cross-validation to BioAgeEstimator

Implements k-fold cross-validation with configurable folds.
Returns mean ± std of MAE and R² across folds.

Fixes #42
```

### 4. Push and create a PR

```bash
git push origin feature/your-feature-name
```

Then on GitHub, create a Pull Request with:
- A clear title
- A description of changes
- Reference to related Issues (#123)
- Screenshots/plots if applicable

### 5. Respond to review feedback

- Be respectful and collaborative
- Clarify design decisions if questioned
- Update your PR commits as needed (don't rebase once review starts)

---

## Testing Requirements

### Minimum Coverage

- New code must have unit tests
- Target ≥80% overall coverage
- Run: `pytest tests/ --cov=vitagraph --cov-report=html`

### Test Structure

```python
# tests/test_my_feature.py

import pytest
from vitagraph import MyClass

def test_basic_functionality(cohort_generator):
    """Test the most common use case."""
    result = cohort_generator.generate(10)
    assert len(result) == 10

@pytest.mark.parametrize("bad_input", [0, -1, None])
def test_error_handling(bad_input):
    """Test that invalid inputs raise appropriate errors."""
    with pytest.raises(ValueError):
        cohort_generator.generate(bad_input)

def test_reproducibility():
    """Test that seeded generators produce the same output."""
    gen1 = SyntheticCohortGenerator(seed=42)
    gen2 = SyntheticCohortGenerator(seed=42)
    assert gen1.generate(10).equals(gen2.generate(10))
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific file
pytest tests/test_synthetic_data.py -v

# Specific test
pytest tests/test_synthetic_data.py::test_generate_returns_expected_columns -v

# With coverage
pytest tests/ --cov=vitagraph --cov-report=term-missing
```

---

## Documentation Requirements

### For New Modules

Create a docstring at the top of the file:

```python
"""Synthetic biometric time-series simulation and processing.

Every generator in this module produces synthetic data from seeded
``numpy.random.Generator``. Nothing here reads from real devices or EHRs.
"""

from __future__ import annotations
...
```

### For New Functions

```python
def my_function(param1: str, param2: int = 5) -> dict[str, float]:
    """One-line summary ending with a period.
    
    Longer description (optional). Explain the purpose, any assumptions,
    and why someone might use this function instead of an alternative.
    
    Args:
        param1: What this parameter is and how it's used.
        param2: Another parameter with a default value.
        
    Returns:
        Dictionary with keys like 'key1' (float) and 'key2' (float).
        
    Raises:
        ValueError: If ``param1`` is an empty string.
        TypeError: If ``param2`` is not an integer.
        
    Example:
        >>> result = my_function("hello", param2=10)
        >>> result["key1"]
        42.0
    """
    ...
```

### For Bug Fixes

Update docstrings or METHODOLOGY.md if your fix changes assumptions.

---

## Release Process

(For maintainers)

1. **Update version** in `src/vitagraph/__init__.py`
2. **Update CHANGELOG.md** with new features, fixes, breaking changes
3. **Create a git tag**: `git tag v0.3.0`
4. **Push tag**: `git push origin v0.3.0`
5. **GitHub Actions** will build and publish to PyPI

---

## Code of Conduct

We are committed to a welcoming and inclusive community. Please:

- Be respectful of all contributors, regardless of background
- Assume good intent; clarify misunderstandings constructively
- Report harassment or discrimination to the maintainers
- Celebrate contributions of all sizes and types

---

## Questions?

- **GitHub Issues**: Post questions as Discussions or Issues
- **Email**: Reach out to Ciprian Stefan Plesca (@Ciprian-LocalPulse on GitHub)
- **Roadmap**: See [docs/ROADMAP.md](docs/ROADMAP.md) for the research direction

---

## Recognition

Contributors will be:
- Listed in the README acknowledgments
- Tagged in release notes
- Invited to co-author publications using their contributions

Thank you for helping make VitaGraph better! 🙏

---

**Made for Research** | *Community & Collaboration*

Last updated: 2026-07-18
