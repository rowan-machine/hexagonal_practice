#!/bin/bash
# Setup Git branches for the project
# This script creates the develop and test branches if they don't exist

set -e

echo "Setting up Git branches..."

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not in a git repository"
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# Ensure we're on main or develop
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "develop" ]; then
    echo "Warning: Not on main or develop branch"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create develop branch if it doesn't exist
if ! git show-ref --verify --quiet refs/heads/develop; then
    echo "Creating develop branch..."
    git checkout -b develop
    git push -u origin develop
    echo "✓ develop branch created and pushed"
else
    echo "✓ develop branch already exists"
fi

# Create test branch if it doesn't exist
if ! git show-ref --verify --quiet refs/heads/test; then
    echo "Creating test branch..."
    git checkout -b test
    git push -u origin test
    echo "✓ test branch created and pushed"
else
    echo "✓ test branch already exists"
fi

# Return to original branch
git checkout "$CURRENT_BRANCH"

echo ""
echo "Branch setup complete!"
echo ""
echo "Branches:"
git branch -a
echo ""
echo "Next steps:"
echo "1. Set up branch protection rules on GitHub"
echo "2. Test the promotion workflows"
echo "3. See docs/GIT_WORKFLOW.md for workflow details"

