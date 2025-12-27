# Git Workflow Guide

Complete guide to the Git branching strategy and CI/CD workflow for this project.

## Branch Strategy

The project uses a three-branch strategy:

```
develop → test → main
```

### Branch Descriptions

- **`develop`**: Development branch
  - All feature work happens here
  - Continuous integration runs on every push
  - Can be unstable during active development

- **`test`**: Testing/staging branch
  - Promoted from `develop` after validation
  - Used for integration testing
  - Should be stable and ready for production testing

- **`main`**: Production branch
  - Promoted from `test` after full validation
  - Always stable and production-ready
  - Tagged with version numbers (e.g., `v0.0.1`)

## Workflow Overview

```
Feature Development
    ↓
develop (auto CI)
    ↓
Manual Promotion
    ↓
test (full validation)
    ↓
Manual Promotion + Tag
    ↓
main (production release)
```

## Development Workflow

### 1. Working on Features

**Always work from `develop` branch:**

```bash
# Ensure you're on develop
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/my-feature-name

# Make changes, commit
git add .
git commit -m "Add: feature description"

# Push feature branch
git push origin feature/my-feature-name

# Create pull request to develop
# After review and merge, feature is in develop
```

### 2. Promoting Dev to Test

**When `develop` is ready for testing:**

**Option A: Manual Promotion (Recommended)**

1. Go to GitHub Actions
2. Select "Promote Dev to Test" workflow
3. Click "Run workflow"
4. Optionally add commit message
5. Click "Run workflow"

**Option B: Automatic (on push to develop)**

- Workflow automatically validates
- Manual approval still required for promotion

**What happens:**
1. Validates `develop` branch:
   - Linting passes
   - Type checking passes
   - All tests pass
   - Release readiness check passes
   - Coverage meets threshold (70%+)
2. Merges `develop` into `test`
3. Pushes to `test` branch

### 3. Promoting Test to Main

**When `test` is ready for production:**

1. Go to GitHub Actions
2. Select "Promote Test to Main" workflow
3. Click "Run workflow"
4. Enter version tag (e.g., `v0.0.2`)
5. Optionally add release notes
6. Click "Run workflow"

**What happens:**
1. Validates `test` branch:
   - All quality checks pass
   - Full test suite passes
   - Release readiness check passes
   - Pipeline execution test passes
   - Coverage meets threshold
2. Merges `test` into `main`
3. Creates version tag
4. Pushes to `main` and tags
5. Creates GitHub release

## Local Development

### Initial Setup

```bash
# Clone repository
git clone https://github.com/rowan-machine/hexagonal_practice.git
cd hexagonal_practice

# Checkout develop branch
git checkout develop

# Create feature branch
git checkout -b feature/my-feature
```

### Daily Workflow

```bash
# Start of day
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/my-feature

# Make changes
# ... edit files ...

# Before committing
make ci  # Run all checks locally

# Commit
git add .
git commit -m "Add: feature description"

# Push
git push origin feature/my-feature

# Create PR to develop on GitHub
```

### Before Pushing

**Always run checks locally:**

```bash
# Run all checks
make ci

# Or individually
make lint
make type-check
make test
make verify-release
```

## Pull Request Process

### PR to Develop

1. **Create PR** from feature branch to `develop`
2. **CI runs automatically**:
   - Linting
   - Type checking
   - Tests
3. **Code review** required
4. **Merge** when approved

### PR to Test

**Not recommended** - Use workflow promotion instead.

### PR to Main

**Not allowed** - Only promotion workflow can update `main`.

## CI/CD Workflows

### Continuous Integration (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `develop`, `test`, or `main`
- Pull requests to any branch

**Runs:**
- Linting (Ruff, Black)
- Type checking (MyPy)
- Tests (multi-version Python)
- Coverage reporting

### Promote Dev to Test (`.github/workflows/promote-dev-to-test.yml`)

**Triggers:**
- Manual workflow dispatch
- Push to `develop` (validates only)

**Validates:**
- Linting
- Type checking
- Tests
- Release readiness
- Coverage threshold

**Promotes:**
- Merges `develop` → `test`

### Promote Test to Main (`.github/workflows/promote-test-to-main.yml`)

**Triggers:**
- Manual workflow dispatch only

**Validates:**
- All quality checks
- Full test suite
- Release readiness
- Pipeline execution
- Coverage threshold

**Promotes:**
- Merges `test` → `main`
- Creates version tag
- Creates GitHub release

## Branch Protection Rules

### Recommended Settings

**`main` branch:**
- Require pull request reviews
- Require status checks to pass
- Require branches to be up to date
- Do not allow force pushes
- Do not allow deletions

**`test` branch:**
- Require status checks to pass
- Do not allow force pushes

**`develop` branch:**
- Require status checks to pass (optional)

## Version Tagging

### Creating Tags

Tags are created automatically when promoting `test` → `main`.

**Format:** `v0.0.1`, `v0.0.2`, `v1.0.0`, etc.

**Manual tagging (if needed):**

```bash
# Create tag
git tag -a v0.0.2 -m "Release v0.0.2"

# Push tag
git push origin v0.0.2
```

### Semantic Versioning

- **Major** (1.0.0): Breaking changes
- **Minor** (0.1.0): New features, backward compatible
- **Patch** (0.0.1): Bug fixes, backward compatible

## Troubleshooting

### Promotion Fails

**Check validation logs:**
1. Go to GitHub Actions
2. Find failed workflow run
3. Check which validation failed
4. Fix issues in `develop` or `test`
5. Retry promotion

### Merge Conflicts

**If conflicts occur during promotion:**

```bash
# Checkout the target branch
git checkout test  # or main

# Pull latest
git pull origin test

# Merge source branch
git merge origin/develop  # or origin/test

# Resolve conflicts
# ... edit conflicted files ...

# Commit
git commit -m "Resolve merge conflicts"

# Push
git push origin test
```

### Reverting a Promotion

**If you need to revert:**

```bash
# Find the commit before promotion
git log --oneline

# Revert to that commit
git revert <commit-hash>

# Push
git push origin <branch-name>
```

## Best Practices

### 1. Keep Develop Stable

- Don't push broken code to `develop`
- Run `make ci` before pushing
- Fix failing tests immediately

### 2. Test Before Promotion

- Run full test suite locally
- Verify release readiness
- Check all documentation

### 3. Use Descriptive Commits

```bash
# Good
git commit -m "Add: high-value claims filtering to SDK"

# Avoid
git commit -m "fix"
```

### 4. Small, Focused PRs

- One feature per PR
- Keep PRs reviewable (< 500 lines)
- Link related issues

### 5. Update Documentation

- Update docs with code changes
- Update CHANGELOG.md for releases
- Keep examples current

## Quick Reference

### Common Commands

```bash
# Check current branch
git branch

# Switch branch
git checkout develop

# Create feature branch
git checkout -b feature/my-feature

# Run checks before commit
make ci

# Check status
git status

# View recent commits
git log --oneline -10
```

### Branch Promotion

**Dev → Test:**
- GitHub Actions → "Promote Dev to Test" → Run workflow

**Test → Main:**
- GitHub Actions → "Promote Test to Main" → Run workflow
- Enter version tag (e.g., `v0.0.2`)

## Next Steps

**Setting up the workflow?**

1. Ensure branches exist: `develop`, `test`, `main`
2. Set up branch protection rules (recommended)
3. Test promotion workflows
4. Document team-specific processes

**Using the workflow?**

1. **[CONTRIBUTING.md](../CONTRIBUTING.md)** → Contribution guidelines
2. **[docs/BEST_PRACTICES.md](BEST_PRACTICES.md)** → Development best practices
3. **[docs/DEVELOPER_ONBOARDING.md](DEVELOPER_ONBOARDING.md)** → Developer setup

**Troubleshooting?**

1. Check GitHub Actions logs
2. Review [Troubleshooting](#troubleshooting) section above
3. Check branch protection rules
4. Verify workflow permissions

