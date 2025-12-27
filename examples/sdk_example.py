"""
Example: Using the analyst SDK.

Demonstrates how analysts can use the convenience SDK interfaces.
"""
import sys
from pathlib import Path
from decimal import Decimal

# Add project root to path if package not installed
try:
    from src.sdk import ClaimsAnalyst, PoliciesAnalyst, StopLossAnalyst
except ImportError:
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    from src.sdk import ClaimsAnalyst, PoliciesAnalyst, StopLossAnalyst


def claims_analysis_example():
    """Example: Analyze claims using the SDK."""
    
    # Create analyst instance
    analyst = ClaimsAnalyst(approval_threshold=Decimal("100000.00"))
    
    # Load claims from database (primary method)
    claims = analyst.load_from_database(layer="silver")
    
    if not claims:
        print("No claims found in database. Run pipelines first to load data.")
        return
    
    # Get total claims
    total = analyst.get_total_claims(claims)
    print(f"Total claims amount: ${total:,.2f}")
    
    # Get approved claims
    approved = analyst.get_approved_claims(claims)
    print(f"Approved claims: {len(approved)}")
    
    # Get high-value claims
    high_value = analyst.get_high_value_claims(claims, threshold=Decimal("50000.00"))
    print(f"High-value claims (>$50k): {len(high_value)}")
    
    # Aggregate by policy
    by_policy = analyst.aggregate_by_policy(claims)
    print(f"Claims grouped by {len(by_policy)} policies")
    
    # Convert to DataFrame for analysis
    df = analyst.to_dataframe(claims)
    print(f"DataFrame shape: {df.shape if hasattr(df, 'shape') else 'N/A'}")


def policies_analysis_example():
    """Example: Analyze policies using the SDK."""
    
    # Create analyst instance
    analyst = PoliciesAnalyst()
    
    # Load policies from database (primary method)
    policies = analyst.load_from_database(layer="silver")
    
    if not policies:
        print("No policies found in database. Run pipelines first to load data.")
        return
    
    # Get active policies
    active = analyst.get_active_policies(policies)
    print(f"Active policies: {len(active)}")
    
    # Get policies for specific employer (if any policies exist)
    if policies:
        employer_id = policies[0].employer_id
        employer_policies = analyst.get_employer_policies(policies, employer_id=employer_id)
        print(f"Policies for employer {employer_id}: {len(employer_policies)}")
    
    # Get total coverage
    total_coverage = analyst.get_total_coverage(policies)
    print(f"Total stop loss coverage: ${total_coverage:,.2f}")
    
    # Convert to DataFrame
    df = analyst.to_dataframe(policies)
    print(f"DataFrame shape: {df.shape if hasattr(df, 'shape') else 'N/A'}")


def combined_analysis_example():
    """Example: Combined claims and policies analysis."""
    
    # Create combined analyst
    analyst = StopLossAnalyst(approval_threshold=Decimal("100000.00"))
    
    # Load data from database
    claims = analyst.claims_analyst.load_from_database(layer="silver")
    policies = analyst.policies_analyst.load_from_database(layer="silver")
    
    if not claims or not policies:
        print("Missing data. Run pipelines first to load claims and policies.")
        return
    
    # Analyze claims by policy
    analysis = analyst.analyze_claims_by_policy(claims, policies)
    print(f"Analysis complete for {len(analysis)} policies")
    
    # Calculate coverage utilization
    utilization = analyst.calculate_coverage_utilization(claims, policies)
    print(f"Coverage utilization calculated for {len(utilization)} policies")
    
    for util in utilization[:5]:  # Show first 5
        print(f"Policy {util['policy_id']}: {util['utilization_percent']:.2f}% utilized")


if __name__ == "__main__":
    print("=== Claims Analysis Example ===")
    claims_analysis_example()
    
    print("\n=== Policies Analysis Example ===")
    policies_analysis_example()
    
    print("\n=== Combined Analysis Example ===")
    combined_analysis_example()

