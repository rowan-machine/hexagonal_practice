#!/usr/bin/env python3
"""
Cross-platform script to setup Git branches (develop, test, main).

Works on Windows (cmd.exe), PowerShell, and Unix-like systems (bash).
"""
import sys
import subprocess
import os


def run_command(cmd, check=True):
    """Run a git command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=check
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stdout.strip() if e.stdout else "", e.stderr.strip() if e.stderr else ""


def check_git_repo():
    """Check if we're in a git repository."""
    success, _, _ = run_command("git rev-parse --git-dir", check=False)
    return success


def get_current_branch():
    """Get the current branch name."""
    success, output, _ = run_command("git branch --show-current", check=False)
    if success:
        return output
    return None


def branch_exists(branch_name):
    """Check if a branch exists (local or remote)."""
    # Check local branches
    success, output, _ = run_command(f"git branch --list {branch_name}", check=False)
    if success and output.strip():
        return True
    
    # Check remote branches
    success, output, _ = run_command(f"git branch -r --list origin/{branch_name}", check=False)
    if success and output.strip():
        return True
    
    return False


def create_branch(branch_name):
    """Create a branch if it doesn't exist."""
    if branch_exists(branch_name):
        print(f"[OK] {branch_name} branch already exists")
        return True
    
    print(f"Creating {branch_name} branch...")
    success, _, error = run_command(f"git checkout -b {branch_name}", check=False)
    
    if success:
        # Try to push to remote
        push_success, _, _ = run_command(f"git push -u origin {branch_name}", check=False)
        if push_success:
            print(f"[OK] {branch_name} branch created and pushed")
        else:
            print(f"[OK] {branch_name} branch created (not pushed - remote may not be configured)")
        return True
    else:
        print(f"[ERROR] Failed to create {branch_name} branch: {error}")
        return False


def main():
    """Main function."""
    print("Setting up Git branches...")
    print()
    
    # Check if we're in a git repository
    if not check_git_repo():
        print("Error: Not in a git repository")
        sys.exit(1)
    
    # Get current branch
    current_branch = get_current_branch()
    if current_branch:
        print(f"Current branch: {current_branch}")
    else:
        print("Warning: Could not determine current branch")
    
    # Warn if not on main or develop
    if current_branch and current_branch not in ["main", "develop"]:
        print(f"Warning: Not on main or develop branch (currently on {current_branch})")
        response = input("Continue anyway? (y/n): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Aborted.")
            sys.exit(1)
    
    print()
    
    # Create branches
    branches_created = []
    
    if create_branch("develop"):
        branches_created.append("develop")
    
    if create_branch("test"):
        branches_created.append("test")
    
    print()
    print("Branch setup complete!")
    print()
    print("Branches:")
    for branch in ["main", "develop", "test"]:
        exists = branch_exists(branch)
        status = "[OK]" if exists else "[MISSING]"
        print(f"  {status} {branch}")
    
    print()
    print("Next steps:")
    print("1. Set up branch protection rules on GitHub")
    print("2. Test the promotion workflows")
    print("3. See docs/GIT_WORKFLOW.md for workflow details")
    
    # Return to original branch
    if current_branch:
        run_command(f"git checkout {current_branch}", check=False)
        print(f"\nReturned to {current_branch} branch")


if __name__ == "__main__":
    main()

