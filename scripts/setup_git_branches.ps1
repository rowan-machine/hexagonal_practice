# Setup Git branches for the project (PowerShell)
# This script creates the develop and test branches if they don't exist

# Set console encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Setting up Git branches..." -ForegroundColor Cyan

# Check if we're in a git repository
try {
    $null = git rev-parse --git-dir 2>$null
} catch {
    Write-Host "Error: Not in a git repository" -ForegroundColor Red
    exit 1
}

# Get current branch
$currentBranch = git branch --show-current
Write-Host "Current branch: $currentBranch" -ForegroundColor Yellow

# Ensure we're on main or develop
if ($currentBranch -ne "main" -and $currentBranch -ne "develop") {
    Write-Host "Warning: Not on main or develop branch" -ForegroundColor Yellow
    $response = Read-Host "Continue anyway? (y/n)"
    if ($response -ne "y" -and $response -ne "Y") {
        exit 1
    }
}

# Create develop branch if it doesn't exist
$developExists = git show-ref --verify --quiet refs/heads/develop 2>$null
if (-not $developExists) {
    Write-Host "Creating develop branch..." -ForegroundColor Green
    git checkout -b develop
    git push -u origin develop
    Write-Host "[OK] develop branch created and pushed" -ForegroundColor Green
} else {
    Write-Host "[OK] develop branch already exists" -ForegroundColor Green
}

# Create test branch if it doesn't exist
$testExists = git show-ref --verify --quiet refs/heads/test 2>$null
if (-not $testExists) {
    Write-Host "Creating test branch..." -ForegroundColor Green
    git checkout -b test
    git push -u origin test
    Write-Host "[OK] test branch created and pushed" -ForegroundColor Green
} else {
    Write-Host "[OK] test branch already exists" -ForegroundColor Green
}

# Return to original branch
git checkout $currentBranch

Write-Host ""
Write-Host "Branch setup complete!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Branches:"
git branch -a
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Set up branch protection rules on GitHub"
Write-Host "2. Test the promotion workflows"
Write-Host "3. See docs/GIT_WORKFLOW.md for workflow details"

