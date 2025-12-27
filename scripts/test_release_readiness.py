#!/usr/bin/env python
"""
Release Readiness Testing Script

Tests all critical functionality before release.
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all critical imports work."""
    print("Testing imports...")
    try:
        from src.sdk import ClaimsAnalyst, PoliciesAnalyst, StopLossAnalyst
        print("  [OK] SDK imports")
        
        from src.pipelines import ClaimsPipeline, PoliciesPipeline
        print("  [OK] Pipeline imports")
        
        from src.domain.claims import Claim, ClaimsProcessor
        from src.domain.policies import Policy, PolicyProcessor
        print("  [OK] Domain imports")
        
        from src.utils.database import DatabaseManager
        from src.utils.config_loader import ConfigLoader
        print("  [OK] Utility imports")
        
        return True
    except Exception as e:
        print(f"  [FAIL] Import error: {e}")
        return False

def test_config_files():
    """Test that configuration files exist and are valid."""
    print("\nTesting configuration files...")
    required_files = [
        "setup.py",
        "pyproject.toml",
        "Pipfile",
        "README.md",
        "CHANGELOG.md",
        "LICENSE",
        "CONTRIBUTING.md",
        "SECURITY.md",
        ".gitignore",
        ".pre-commit-config.yaml",
        "ruff.toml",
        "config/claims_pipeline.yml",
        "config/policies_pipeline.yml",
    ]
    
    all_exist = True
    for file_path in required_files:
        path = project_root / file_path
        if path.exists():
            print(f"  [OK] {file_path}")
        else:
            print(f"  [MISSING] {file_path}")
            all_exist = False
    
    return all_exist

def test_documentation_links():
    """Test that key documentation files exist."""
    print("\nTesting documentation files...")
    doc_files = [
        "GETTING_STARTED.md",
        "DOCKER.md",
        "docs/PIPENV_GUIDE.md",
        "docs/README.md",
        "docs/DESIGN_PRINCIPLES.md",
        "docs/MIGRATION_GUIDE.md",
        "docs/BEST_PRACTICES.md",
        "docs/DEVELOPER_ONBOARDING.md",
        "notebooks/ANALYST_GUIDE.md",
        "examples/README.md",
        "scripts/README.md",
        "requirements/README.md",
        "schemas/README.md",
        "config/README.md",
    ]
    
    all_exist = True
    for file_path in doc_files:
        path = project_root / file_path
        if path.exists():
            print(f"  [OK] {file_path}")
        else:
            print(f"  [MISSING] {file_path}")
            all_exist = False
    
    return all_exist

def test_scripts():
    """Test that all scripts exist."""
    print("\nTesting scripts...")
    scripts = [
        "scripts/run_local.py",
        "scripts/verify_setup.py",
        "scripts/verify_data_loaded.py",
        "scripts/verify_atlas_entities.py",
        "scripts/publish_atlas_metadata.py",
        "scripts/mock_atlas.py",
    ]
    
    all_exist = True
    for script_path in scripts:
        path = project_root / script_path
        if path.exists():
            print(f"  [OK] {script_path}")
        else:
            print(f"  [MISSING] {script_path}")
            all_exist = False
    
    return all_exist

def test_examples():
    """Test that examples exist."""
    print("\nTesting examples...")
    examples = [
        "examples/pipeline_example.py",
        "examples/sdk_example.py",
    ]
    
    all_exist = True
    for example_path in examples:
        path = project_root / example_path
        if path.exists():
            print(f"  [OK] {example_path}")
        else:
            print(f"  [MISSING] {example_path}")
            all_exist = False
    
    return all_exist

def test_notebooks():
    """Test that notebooks exist."""
    print("\nTesting notebooks...")
    notebooks = [
        "notebooks/analyst_claims_analysis.ipynb",
        "notebooks/analyst_policies_analysis.ipynb",
        "notebooks/analyst_combined_analysis.ipynb",
        "notebooks/claims_validation.ipynb",
        "notebooks/policy_validation.ipynb",
    ]
    
    all_exist = True
    for notebook_path in notebooks:
        path = project_root / notebook_path
        if path.exists():
            print(f"  [OK] {notebook_path}")
        else:
            print(f"  [MISSING] {notebook_path}")
            all_exist = False
    
    return all_exist

def test_version_consistency():
    """Test that versions are consistent across files."""
    print("\nTesting version consistency...")
    try:
        import re
        
        # Read setup.py
        setup_py = (project_root / "setup.py").read_text(encoding='utf-8', errors='ignore')
        setup_version = re.search(r'version="([^"]+)"', setup_py)
        
        # Read pyproject.toml
        pyproject = (project_root / "pyproject.toml").read_text(encoding='utf-8', errors='ignore')
        pyproject_version = re.search(r'version = "([^"]+)"', pyproject)
        
        # Read README.md
        readme = (project_root / "README.md").read_text(encoding='utf-8', errors='ignore')
        readme_version = re.search(r'v(\d+\.\d+\.\d+)', readme)
        
        versions = []
        if setup_version:
            versions.append(("setup.py", setup_version.group(1)))
        if pyproject_version:
            versions.append(("pyproject.toml", pyproject_version.group(1)))
        if readme_version:
            versions.append(("README.md", readme_version.group(1)))
        
        if len(set(v[1] for v in versions)) == 1:
            print(f"  [OK] All versions match: {versions[0][1]}")
            return True
        else:
            print(f"  [FAIL] Version mismatch:")
            for file, version in versions:
                print(f"    {file}: {version}")
            return False
    except Exception as e:
        print(f"  [FAIL] Error checking versions: {e}")
        return False

def test_docker_compose():
    """Test that docker-compose.yml exists."""
    print("\nTesting Docker configuration...")
    docker_file = project_root / "docker-compose.yml"
    if docker_file.exists():
        print("  [OK] docker-compose.yml exists")
        return True
    else:
        print("  [MISSING] docker-compose.yml missing")
        return False

def test_ci_cd():
    """Test that CI/CD files exist."""
    print("\nTesting CI/CD configuration...")
    ci_files = [
        ".github/workflows/ci.yml",
        ".github/workflows/security.yml",
        ".github/workflows/codeql.yml",
        ".github/workflows/release.yml",
        ".github/dependabot.yml",
    ]
    
    all_exist = True
    for ci_path in ci_files:
        path = project_root / ci_path
        if path.exists():
            print(f"  [OK] {ci_path}")
        else:
            print(f"  [MISSING] {ci_path}")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests."""
    print("=" * 60)
    print("Release Readiness Testing")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Config Files", test_config_files()))
    results.append(("Documentation", test_documentation_links()))
    results.append(("Scripts", test_scripts()))
    results.append(("Examples", test_examples()))
    results.append(("Notebooks", test_notebooks()))
    results.append(("Version Consistency", test_version_consistency()))
    results.append(("Docker", test_docker_compose()))
    results.append(("CI/CD", test_ci_cd()))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n[SUCCESS] All checks passed! Ready for release.")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} check(s) failed. Review before release.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

