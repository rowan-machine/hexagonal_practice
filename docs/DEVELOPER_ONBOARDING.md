# Developer Onboarding Guide

Welcome! This guide explains all the files and tools in this project to help you get up to speed quickly.

## 📋 Table of Contents

- [Configuration Files](#configuration-files)
- [CI/CD and Automation](#cicd-and-automation)
- [Code Quality Tools](#code-quality-tools)
- [Development Workflow](#development-workflow)
- [Directory Organization](#directory-organization)
- [Documentation Files](#documentation-files)
- [Git Command Reference](#git-command-reference)
- [Quick Reference](#quick-reference)

## Configuration Files

### `pyproject.toml`

**Purpose**: Central configuration file for Python project metadata, dependencies, and tool settings.

**What it contains**:
- Project metadata (name, version, description)
- Dependencies (production and development)
- Tool configurations:
  - **Pytest**: Test settings, coverage options, markers
  - **MyPy**: Type checking configuration
  - **Black**: Code formatting settings
  - **Coverage**: Coverage reporting settings

**Why it matters**: Modern Python projects use `pyproject.toml` as the single source of truth for project configuration. It replaces `setup.py` and multiple config files.

**Usage**: 
- Install package: `pip install -e .`
- Install with dev dependencies: `pip install -e ".[dev]"`

### `ruff.toml`

**Purpose**: Configuration for Ruff, a fast Python linter and formatter.

**What it contains**:
- Linting rules (pycodestyle, pyflakes, bugbear, etc.)
- Import sorting (isort replacement)
- Code complexity settings
- File exclusions

**Why it matters**: Ruff is 10-100x faster than traditional linters and replaces multiple tools (flake8, isort, etc.).

**Usage**: 
- Lint: `ruff check src/`
- Fix: `ruff check --fix src/`
- Format: `ruff format src/`

### `.pre-commit-config.yaml`

**Purpose**: Configuration for pre-commit hooks that run automatically before each commit.

**What it contains**:
- Hooks for trailing whitespace, file endings, YAML/JSON validation
- Ruff linting and formatting
- Black formatting
- MyPy type checking

**Why it matters**: Catches issues before they're committed, ensuring consistent code quality.

**Usage**:
- Install hooks: `pre-commit install`
- Run manually: `pre-commit run --all-files`

### `.editorconfig`

**Purpose**: Ensures consistent coding styles across different editors and IDEs.

**What it contains**:
- Indentation settings (spaces vs tabs, size)
- Line endings (LF)
- Character encoding (UTF-8)
- Line length limits

**Why it matters**: Different developers using different editors will have consistent formatting automatically.

**Usage**: Most modern editors support EditorConfig automatically. No manual setup needed.

## CI/CD and Automation

### `.github/workflows/ci.yml`

**Purpose**: GitHub Actions workflow for continuous integration.

**What it does**:
- Runs on every push and pull request
- **Lint job**: Checks code style with Ruff and Black
- **Type check job**: Runs MyPy type checking
- **Test job**: Runs tests across Python 3.8, 3.9, 3.10, 3.11
- Uploads coverage reports to Codecov

**Why it matters**: Ensures all code meets quality standards before merging.

**Usage**: Automatically runs on GitHub. You can also run locally with `make ci`.

### `.github/workflows/security.yml`

**Purpose**: Automated security scanning workflow.

**What it does**:
- Scans dependencies with `pip-audit` and `safety`
- Detects secrets with TruffleHog
- Runs on schedule and on pull requests

**Why it matters**: Keeps dependencies secure and prevents secrets from being committed.

**Usage**: Automatically runs on GitHub. Check results in the Actions tab.

### `.github/workflows/codeql.yml`

**Purpose**: CodeQL analysis for security vulnerabilities.

**What it does**:
- Static analysis to find security vulnerabilities
- Scans Python code for common issues
- Runs on push and weekly schedule

**Why it matters**: Finds security issues that might not be caught by other tools.

**Usage**: Automatically runs on GitHub. Results appear in Security tab.

### `.github/workflows/release.yml`

**Purpose**: Automated release workflow.

**What it does**:
- Triggers on version tags
- Builds and publishes packages
- Creates GitHub releases

**Why it matters**: Streamlines the release process and reduces manual errors.

**Usage**: Triggered by creating a version tag (e.g., `v0.0.2`).

### `.github/dependabot.yml`

**Purpose**: Automated dependency updates.

**What it does**:
- Checks for dependency updates weekly
- Creates pull requests for updates
- Monitors Python packages, GitHub Actions, and Docker images

**Why it matters**: Keeps dependencies up-to-date and secure without manual checking.

**Usage**: Automatically creates PRs. Review and merge as needed.

## Code Quality Tools

### Ruff (Linting & Formatting)

**File**: `ruff.toml`

**What it does**:
- Lints code for errors and style issues
- Formats code (replaces Black)
- Sorts imports (replaces isort)

**Commands**:
```bash
ruff check src/          # Check for issues
ruff check --fix src/    # Auto-fix issues
ruff format src/         # Format code
```

### Black (Code Formatting)

**File**: Configured in `pyproject.toml`

**What it does**: Formats Python code to a consistent style.

**Commands**:
```bash
black src/                # Format code
black --check src/        # Check without formatting
```

**Note**: Ruff can also format, but Black is kept for compatibility.

### MyPy (Type Checking)

**File**: Configured in `pyproject.toml`

**What it does**: Static type checking for Python code.

**Commands**:
```bash
mypy src/                 # Type check
```

**Note**: Type checking is optional (not strict) to allow gradual adoption.

### Pytest (Testing)

**File**: Configured in `pyproject.toml`

**What it does**: Runs unit, integration, and end-to-end tests.

**Commands**:
```bash
pytest                    # Run all tests
pytest --cov=src          # With coverage
pytest -v                 # Verbose output
```

## Development Workflow

### `Makefile`

**Purpose**: Convenience commands for common development tasks.

**Key Commands**:
```bash
make help              # Show all available commands
make install-dev       # Install development dependencies
make test              # Run tests
make lint              # Run linters
make format            # Format code
make type-check        # Type check
make ci                # Run all CI checks locally
make run-claims        # Run claims pipeline
make docker-up         # Start Docker services
```

**Why it matters**: Provides consistent commands across different platforms and reduces typing.

**Usage**: Run `make help` to see all commands, then use `make <command>`.

### Pre-commit Hooks

**File**: `.pre-commit-config.yaml`

**What it does**: Runs checks automatically before each commit.

**Installation**:
```bash
pre-commit install
```

**What runs**:
- Trailing whitespace removal
- File ending fixes
- YAML/JSON validation
- Ruff linting and formatting
- Black formatting
- MyPy type checking

**Why it matters**: Prevents bad code from being committed.

## Directory Organization

### `scripts/` Directory

**Purpose**: Contains all helper scripts for running pipelines, verification, and maintenance.

**Key Scripts**:
- `run_local.py` - Execute pipelines locally
- `verify_*.py` - Verification scripts
- `publish_atlas_*.py` - Atlas metadata publishing
- `mock_atlas.py` - Mock Atlas server for testing

**Documentation**: See `scripts/README.md` for detailed usage.

**Why organized**: Keeps root directory clean and groups related scripts together.

### `requirements/` Directory

**Purpose**: Contains all Python dependency files.

**Files**:
- `requirements.txt` - Production dependencies
- `requirements-dev.txt` - Development dependencies
- `requirements-airflow.txt` - Airflow-specific dependencies

**Documentation**: See `requirements/README.md` for details.

**Why organized**: Separates dependencies by environment and keeps root directory clean.

## Documentation Files

### `CONTRIBUTING.md`

**Purpose**: Guidelines for contributing to the project.

**Contains**:
- Development setup instructions
- Code style guidelines
- Testing requirements
- Pull request process
- Code review guidelines

**When to read**: Before making your first contribution.

### `SECURITY.md`

**Purpose**: Security policy and best practices.

**Contains**:
- Vulnerability reporting process
- Security best practices
- Security checklist
- Dependency scanning instructions

**When to read**: Before deploying to production or reporting security issues.

### `LICENSE`

**Purpose**: MIT License - defines how the code can be used.

**Contains**: Standard MIT License terms.

**When to read**: Before using or contributing to understand licensing terms.

### `Makefile`

**Purpose**: Development workflow commands (see [Development Workflow](#development-workflow) above).

### `docs/BEST_PRACTICES.md`

**Purpose**: Comprehensive guide to best practices for the project.

**Contains**:
- Code quality standards
- Testing strategies
- Security practices
- Performance optimization
- Deployment guidelines

**When to read**: When writing code or reviewing PRs.

### `docs/BEST_PRACTICES_IMPLEMENTATION.md`

**Purpose**: Details on how best practices are implemented in this project.

**When to read**: To understand how best practices are applied in practice.

### `docs/BEST_PRACTICES_SUMMARY.md`

**Purpose**: Quick summary of implemented best practices.

**When to read**: For a quick overview of what's implemented.

## Git Workflow

This project uses a three-branch strategy: `develop → test → main`

**See [GIT_WORKFLOW.md](GIT_WORKFLOW.md) for complete workflow documentation.**

Quick reference:
- **`develop`**: Development branch (all feature work)
- **`test`**: Testing/staging branch (promoted from develop)
- **`main`**: Production branch (promoted from test, tagged with versions)

### Setting Up Branches

```bash
# Run setup script
make setup-branches

# Or manually
git checkout -b develop
git push -u origin develop
git checkout -b test
git push -u origin test
```

### Branch Promotion

**Dev → Test:**
- GitHub Actions → "Promote Dev to Test" → Run workflow

**Test → Main:**
- GitHub Actions → "Promote Test to Main" → Run workflow
- Enter version tag (e.g., `v0.0.2`)

## Git Command Reference

### Basic Git Operations

#### Repository Setup

```bash
# Clone repository
git clone <repository-url>
cd hexagonal_practice

# Check repository status
git status

# View remote repositories
git remote -v

# Add remote repository
git remote add origin <repository-url>

# Update remote URL
git remote set-url origin <repository-url>
```

#### Viewing Information

```bash
# View commit history
git log

# View commit history (one line per commit)
git log --oneline

# View commit history with graph
git log --oneline --graph --all

# View changes in working directory
git diff

# View staged changes
git diff --staged

# View file history
git log -- <file-path>

# View file changes
git diff <commit1> <commit2> -- <file-path>

# View current branch
git branch

# View all branches
git branch -a

# View remote branches
git branch -r
```

#### Making Changes

```bash
# Stage file
git add <file-path>

# Stage all changes
git add .

# Stage specific file types
git add *.py

# Unstage file
git reset <file-path>

# Unstage all
git reset

# Commit changes
git commit -m "Your commit message"

# Commit with detailed message
git commit -m "Short summary" -m "Detailed description"

# Amend last commit
git commit --amend -m "Updated message"

# Add changes to last commit
git commit --amend --no-edit
```

#### Branching

```bash
# Create new branch
git branch <branch-name>

# Create and switch to branch
git checkout -b <branch-name>

# Switch branch
git checkout <branch-name>

# Switch branch (Git 2.23+)
git switch <branch-name>

# Create and switch (Git 2.23+)
git switch -c <branch-name>

# Delete branch
git branch -d <branch-name>

# Force delete branch
git branch -D <branch-name>

# Delete remote branch
git push origin --delete <branch-name>

# Rename branch
git branch -m <old-name> <new-name>

# List branches
git branch

# List all branches (including remote)
git branch -a
```

#### Merging and Rebasing

```bash
# Merge branch into current branch
git merge <branch-name>

# Merge with no fast-forward (creates merge commit)
git merge --no-ff <branch-name>

# Abort merge
git merge --abort

# Rebase current branch onto another
git rebase <branch-name>

# Interactive rebase (last N commits)
git rebase -i HEAD~<n>

# Abort rebase
git rebase --abort

# Continue rebase after resolving conflicts
git rebase --continue
```

#### Remote Operations

```bash
# Fetch changes from remote
git fetch

# Fetch from specific remote
git fetch origin

# Pull changes (fetch + merge)
git pull

# Pull with rebase
git pull --rebase

# Push to remote
git push

# Push to specific remote and branch
git push origin <branch-name>

# Push and set upstream
git push -u origin <branch-name>

# Force push (use with caution!)
git push --force

# Force push with lease (safer)
git push --force-with-lease
```

#### Undoing Changes

```bash
# Discard changes in working directory
git checkout -- <file-path>

# Discard all changes
git checkout -- .

# Restore file (Git 2.23+)
git restore <file-path>

# Restore all files (Git 2.23+)
git restore .

# Unstage file
git reset HEAD <file-path>

# Reset to specific commit (soft - keeps changes)
git reset --soft <commit-hash>

# Reset to specific commit (mixed - keeps working directory)
git reset --mixed <commit-hash>

# Reset to specific commit (hard - discards everything)
git reset --hard <commit-hash>

# Revert commit (creates new commit)
git revert <commit-hash>
```

#### Stashing

```bash
# Stash changes
git stash

# Stash with message
git stash save "Your message"

# List stashes
git stash list

# Apply stash
git stash apply

# Apply specific stash
git stash apply stash@{0}

# Apply and remove stash
git stash pop

# Drop stash
git stash drop stash@{0}

# Clear all stashes
git stash clear
```

#### Tags

```bash
# List tags
git tag

# Create lightweight tag
git tag <tag-name>

# Create annotated tag
git tag -a <tag-name> -m "Tag message"

# Create tag at specific commit
git tag -a <tag-name> <commit-hash>

# Push tag to remote
git push origin <tag-name>

# Push all tags
git push origin --tags

# Delete tag
git tag -d <tag-name>

# Delete remote tag
git push origin --delete <tag-name>
```

### Workflow Commands

#### Daily Workflow

```bash
# Start of day
git pull                    # Get latest changes
git status                  # Check your status

# Making changes
git checkout -b feature/my-feature
# ... make changes ...
git add .
git commit -m "Add feature"

# Before pushing
git pull --rebase           # Update with latest changes
git push -u origin feature/my-feature
```

#### Code Review Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Implement feature"

# Keep branch updated
git fetch origin
git rebase origin/main

# Push for review
git push -u origin feature/new-feature

# After review, merge to main
git checkout main
git pull
git merge feature/new-feature
git push
```

#### Fixing Mistakes

```bash
# Forgot to add file to last commit
git add <file>
git commit --amend --no-edit

# Wrong commit message
git commit --amend -m "Correct message"

# Accidentally committed to wrong branch
git reset HEAD~1             # Undo commit
git checkout correct-branch
git cherry-pick <commit-hash>

# Accidentally pushed wrong commit
git revert <commit-hash>
git push
```

### Project-Specific Workflow

#### Before Making Changes

```bash
# Ensure you're on main and up to date
git checkout main
git pull

# Create feature branch
git checkout -b feature/your-feature-name
```

#### Making Changes

```bash
# Make your changes, then stage
git add .

# Commit with descriptive message
git commit -m "Add: description of what you added"
# or
git commit -m "Fix: description of what you fixed"
# or
git commit -m "Update: description of what you updated"

# Run pre-commit hooks (if not automatic)
pre-commit run --all-files

# Run tests
make test

# Run all checks
make ci
```

#### Before Pushing

```bash
# Update with latest changes
git fetch origin
git rebase origin/main

# Run final checks
make ci

# Push branch
git push -u origin feature/your-feature-name
```

#### After Code Review

```bash
# Make requested changes
git add .
git commit -m "Address review comments"

# Update remote branch
git push

# After approval, merge (usually done via PR)
git checkout main
git pull
git merge feature/your-feature-name
git push
```

### Useful Git Aliases

Add these to your `~/.gitconfig` for convenience:

```bash
# View aliases
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual '!gitk'
```

### Best Practices

1. **Commit Often**: Small, focused commits are easier to review
2. **Write Good Messages**: Use clear, descriptive commit messages
3. **Pull Before Push**: Always pull latest changes before pushing
4. **Use Branches**: Never commit directly to `main` branch
5. **Review Before Push**: Run `make ci` before pushing
6. **Don't Force Push**: Use `--force-with-lease` if absolutely necessary
7. **Keep Branches Updated**: Regularly rebase on `main`

### Common Issues and Solutions

#### Merge Conflicts

```bash
# View conflicted files
git status

# Resolve conflicts in files, then:
git add <resolved-file>
git commit

# Or abort merge
git merge --abort
```

#### Accidentally Committed to Wrong Branch

```bash
# Undo commit (keeps changes)
git reset HEAD~1

# Switch to correct branch
git checkout correct-branch

# Apply changes
git cherry-pick <commit-hash>
```

#### Need to Update Remote Branch

```bash
# If you've rewritten history locally
git push --force-with-lease origin <branch-name>
```

## Quick Reference

### First Day Checklist

1. ✅ Read [GETTING_STARTED.md](../GETTING_STARTED.md)
2. ✅ Set up environment:
   - **Using pipenv**: `pipenv install --dev && pipenv shell`
   - **Using make**: `make install-dev`
3. ✅ Install pre-commit hooks: `pre-commit install`
4. ✅ Run verification: `make verify`
5. ✅ Read [CONTRIBUTING.md](../CONTRIBUTING.md)
6. ✅ Run examples: See [examples/README.md](../examples/README.md)

### Daily Workflow

**Using pipenv:**
```bash
# Start work
git pull
pipenv install --dev     # Update dependencies if needed
pipenv shell             # Activate environment

# Make changes
# ... edit code ...

# Before committing
pipenv run make format   # Format code
pipenv run make lint     # Check for issues
pipenv run make test     # Run tests
pipenv run make ci       # Run all checks

# Commit (pre-commit hooks run automatically)
git commit -m "Your message"

# Push
git push
```

**Using venv/make:**
```bash
# Start work
git pull
make install-dev          # Update dependencies if needed

# Make changes
# ... edit code ...

# Before committing
make format               # Format code
make lint                 # Check for issues
make test                 # Run tests
make ci                   # Run all checks

# Commit (pre-commit hooks run automatically)
git commit -m "Your message"

# Push
git push
```

### Common Tasks

**Run a pipeline**:
```bash
make run-claims
# or
python scripts/run_local.py claims_pipeline
```

**Run tests**:
```bash
make test
# or
pytest
```

**Format code**:
```bash
make format
# or
ruff check --fix src/
black src/
```

**Check code quality**:
```bash
make ci
# Runs: lint, type-check, test
```

**Start Docker services**:
```bash
make docker-up
```

**View all commands**:
```bash
make help
```

## Understanding the Project Structure

### Core Directories

- **`src/`**: Source code (domain, pipelines, SDK, transforms, utils)
- **`config/`**: Pipeline configuration files (YAML)
- **`schemas/`**: Data schemas (YAML)
- **`scripts/`**: Helper scripts
- **`requirements/`**: Dependency files
- **`docs/`**: Documentation
- **`examples/`**: Code examples
- **`notebooks/`**: Jupyter notebooks

### Configuration Files

- **`pyproject.toml`**: Project configuration (dependencies, tools)
- **`ruff.toml`**: Linting configuration
- **`.pre-commit-config.yaml`**: Pre-commit hooks
- **`.editorconfig`**: Editor settings
- **`Makefile`**: Development commands

### CI/CD Files

- **`.github/workflows/`**: GitHub Actions workflows
- **`.github/dependabot.yml`**: Dependency updates

### Documentation

- **`README.md`**: Project overview
- **`GETTING_STARTED.md`**: Setup guide
- **`CONTRIBUTING.md`**: Contribution guidelines
- **`SECURITY.md`**: Security policy
- **`docs/`**: Detailed documentation

## Troubleshooting

### Pre-commit hooks not running

```bash
pre-commit install
```

### Import errors

```bash
pip install -e .
```

### Tests failing

```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
make install-dev

# Run tests with verbose output
pytest -v
```

### Linting errors

```bash
# Auto-fix what can be fixed
make format

# Check what's left
make lint
```

### Type checking errors

```bash
# Type checking is optional, but you can fix issues:
mypy src/
```

## Next Steps

**New to the project?** Follow this path:

1. **[GETTING_STARTED.md](../GETTING_STARTED.md)** → Complete setup guide
2. **[examples/README.md](../examples/README.md)** → Run examples
3. **[docs/DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** → Understand architecture

**Ready to contribute?**

1. **[CONTRIBUTING.md](../CONTRIBUTING.md)** → Contribution guidelines
2. **[docs/BEST_PRACTICES.md](BEST_PRACTICES.md)** → Best practices
3. **[src/tests/TESTING.md](../src/tests/TESTING.md)** → Testing guidelines

**Setting up your environment?**

1. Run `make install-dev` to install dependencies
2. Run `pre-commit install` to set up hooks
3. Run `make verify` to verify setup
4. Run `make help` to see all available commands

**Questions?**

- Check [docs/README.md](README.md) for documentation index
- Review [docs/NAVIGATION_GUIDE.md](NAVIGATION_GUIDE.md) for navigation help
- See [GETTING_STARTED.md](../GETTING_STARTED.md) troubleshooting section

