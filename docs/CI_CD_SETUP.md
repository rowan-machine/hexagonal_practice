# CI/CD Setup Summary

This document summarizes the CI/CD workflow setup for the project.

## Repository

**GitHub**: [https://github.com/rowan-machine/hexagonal_practice](https://github.com/rowan-machine/hexagonal_practice)

## Branch Strategy

Three-branch workflow: `develop → test → main`

- **`develop`**: Development branch (all feature work)
- **`test`**: Testing/staging branch (promoted from develop)
- **`main`**: Production branch (promoted from test, tagged with versions)

## CI/CD Workflows

### 1. Continuous Integration (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `develop`, `test`, or `main`
- Pull requests to any branch

**Runs:**
- Linting (Ruff, Black)
- Type checking (MyPy)
- Tests (Python 3.8, 3.9, 3.10, 3.11)
- Coverage reporting

### 2. Promote Dev to Test (`.github/workflows/promote-dev-to-test.yml`)

**Triggers:**
- Manual workflow dispatch (recommended)
- Push to `develop` (validates only)

**Validates:**
- Linting passes
- Type checking passes
- All tests pass
- Release readiness check passes
- Coverage meets threshold (70%+)

**Promotes:**
- Merges `develop` → `test`
- Pushes to `test` branch

### 3. Promote Test to Main (`.github/workflows/promote-test-to-main.yml`)

**Triggers:**
- Manual workflow dispatch only

**Validates:**
- All quality checks pass
- Full test suite passes
- Release readiness check passes
- Pipeline execution test passes
- Coverage meets threshold

**Promotes:**
- Merges `test` → `main`
- Creates version tag
- Pushes to `main` and tags
- Creates GitHub release

## Setup Instructions

### 1. Create Branches

```bash
# Use Makefile
make setup-branches

# Or use scripts
bash scripts/setup_git_branches.sh  # Linux/Mac/Git Bash
powershell -ExecutionPolicy Bypass -File scripts/setup_git_branches.ps1  # Windows
```

### 2. Set Up Branch Protection (Recommended)

On GitHub:
1. Go to Settings → Branches
2. Add rule for `main`:
   - Require pull request reviews
   - Require status checks to pass
   - Require branches to be up to date
   - Do not allow force pushes
3. Add rule for `test`:
   - Require status checks to pass
   - Do not allow force pushes

### 3. Test Workflows

1. Make a change in `develop`
2. Push to `develop`
3. Verify CI runs successfully
4. Test promotion workflow manually

## Makefile Commands

### Testing Commands

```bash
make test              # Run all tests
make test-coverage     # Run tests with coverage
make verify-release    # Run release readiness checks
make verify-all        # Run all verification scripts
make test-scripts      # Test all scripts
```

### CI Commands

```bash
make ci                # Run CI checks locally
make lint              # Run linters
make type-check        # Run type checker
make all-checks        # Run all quality checks
```

### Git Commands

```bash
make setup-branches    # Setup git branches
```

## Documentation

- **[docs/GIT_WORKFLOW.md](GIT_WORKFLOW.md)** - Complete Git workflow guide
- **[docs/DEVELOPER_ONBOARDING.md](DEVELOPER_ONBOARDING.md)** - Developer setup
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Contribution guidelines

## Quick Reference

### Promoting Dev to Test

1. Go to GitHub Actions
2. Select "Promote Dev to Test"
3. Click "Run workflow"
4. Optionally add commit message
5. Click "Run workflow"

### Promoting Test to Main

1. Go to GitHub Actions
2. Select "Promote Test to Main"
3. Click "Run workflow"
4. Enter version tag (e.g., `v0.0.2`)
5. Optionally add release notes
6. Click "Run workflow"

## Next Steps

1. **[docs/GIT_WORKFLOW.md](GIT_WORKFLOW.md)** → Complete workflow documentation
2. **[CONTRIBUTING.md](../CONTRIBUTING.md)** → Contribution guidelines
3. **[docs/BEST_PRACTICES.md](BEST_PRACTICES.md)** → Development best practices

