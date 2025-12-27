-- Original SQL query for claims gold layer aggregation
-- Query ID: CLAIMS_GOLD_001
-- Description: Claims Aggregation by Policy

SELECT 
    policy_id,
    SUM(claim_amount) AS total_claims,
    COUNT(claim_id) AS claim_count,
    AVG(claim_amount) AS avg_claim_amount,
    MAX(claim_amount) AS max_claim_amount,
    MIN(claim_amount) AS min_claim_amount
FROM claims_silver
GROUP BY policy_id
ORDER BY total_claims DESC;

