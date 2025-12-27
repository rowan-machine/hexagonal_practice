# Best Practices Guide

This document outlines best practices for developing, maintaining, and deploying the Ringmaster Pipelines system.

## Table of Contents

- [Code Quality](#code-quality)
- [Testing](#testing)
- [Security](#security)
- [Performance](#performance)
- [Documentation](#documentation)
- [Version Control](#version-control)
- [Deployment](#deployment)
- [Monitoring](#monitoring)

## Code Quality

### Type Hints

- **Always use type hints** for public APIs
- Use `Optional[T]` for nullable types
- Use `List[T]`, `Dict[K, V]` instead of `list`, `dict`
- Document complex types with `TypedDict` or dataclasses

```python
def process_claims(claims: List[Claim], threshold: Decimal) -> Dict[str, Any]:
    """Process claims with threshold."""
    ...
```

### Docstrings

- **All public classes and methods** must have docstrings
- Use Google-style docstrings
- Include parameter descriptions and return types
- Document exceptions that may be raised

```python
def aggregate_by_policy(self, claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Aggregate claims by policy ID.
    
    Args:
        claims: List of claim dictionaries
        
    Returns:
        List of aggregated claim dictionaries grouped by policy_id
        
    Raises:
        ValueError: If claims list is empty
    """
```

### Code Formatting

- **Run formatters before committing**: `make format`
- Use Black for consistent formatting
- Use Ruff for linting and import sorting
- Line length: 100 characters

### Naming Conventions

- **Classes**: PascalCase (`ClaimsProcessor`)
- **Functions/Methods**: snake_case (`process_claims`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_RETRIES`)
- **Private methods**: Leading underscore (`_internal_method`)

## Testing

### Test Structure

- **One test file per module**: `test_claims.py` for `claims.py`
- **Test classes** for related tests
- **Descriptive test names**: `test_claim_exceeds_threshold_when_amount_is_greater`

### Test Coverage

- **Aim for 80%+ coverage** for domain logic
- **100% coverage** for critical business rules
- Use `pytest --cov=src --cov-report=html` to check coverage

### Test Best Practices

1. **Arrange-Act-Assert** pattern
2. **Test edge cases**: Empty lists, None values, boundary conditions
3. **Mock external dependencies**: Database, APIs, file I/O
4. **Use fixtures** for common setup
5. **Keep tests independent**: Don't rely on execution order

### Running Tests

```bash
# All tests
make test

# With coverage
make test-coverage

# Specific test file
pytest src/tests/test_domain.py

# Specific test
pytest src/tests/test_domain.py::TestClaim::test_claim_creation
```

## Security

### Secrets Management

- **Never commit secrets** to version control
- Use environment variables for credentials
- Use `.env` files (excluded from git) for local development
- Use secret management services in production

### Input Validation

- **Validate all inputs** at boundaries
- Check data types and ranges
- Sanitize file paths
- Use schema validation for configuration files

### SQL Injection Prevention

- **Always use parameterized queries**
- Never concatenate user input into SQL
- Use ORM or query builders when possible

```python
# ✅ Good
db.query("SELECT * FROM claims WHERE policy_id = ?", (policy_id,))

# ❌ Bad
db.query(f"SELECT * FROM claims WHERE policy_id = '{policy_id}'")
```

### Dependency Security

- **Regularly update dependencies**
- Use `pip-audit` or `safety` to check for vulnerabilities
- Review dependency changes before updating
- Pin versions in production

```bash
# Check for vulnerabilities
pip-audit
safety check
```

## Performance

### Database Operations

- **Use connection pooling** (already implemented)
- **Batch operations** when possible
- **Use transactions** for multiple related operations
- **Index frequently queried columns**

### Memory Management

- **Use context managers** for resources
- **Process data in chunks** for large datasets
- **Close connections** explicitly
- **Use generators** for large data streams

### Caching

- Consider caching expensive computations
- Cache configuration loading
- Use appropriate cache invalidation strategies

## Documentation

### Code Documentation

- **Document all public APIs**
- Include usage examples in docstrings
- Document design decisions in code comments
- Keep documentation up to date

### Project Documentation

- **Update README.md** for significant changes
- **Update CHANGELOG.md** for user-facing changes
- **Keep examples current**
- **Document breaking changes** clearly

### Documentation Standards

- Use Markdown for all documentation
- Include code examples
- Keep documentation concise but complete
- Link related documentation

## Version Control

### Commit Messages

- **Use clear, descriptive messages**
- Follow conventional commits format:
  - `feat:` New feature
  - `fix:` Bug fix
  - `docs:` Documentation changes
  - `refactor:` Code refactoring
  - `test:` Test changes
  - `chore:` Maintenance tasks

### Branch Strategy

- **main**: Production-ready code
- **develop**: Integration branch
- **feature/**: New features
- **fix/**: Bug fixes
- **hotfix/**: Critical production fixes

### Pull Requests

- **Keep PRs focused** and reasonably sized
- **Include tests** for new features
- **Update documentation** as needed
- **Request reviews** before merging

## Deployment

### Pre-Deployment Checklist

- [ ] All tests pass
- [ ] Code is linted and formatted
- [ ] Documentation is updated
- [ ] Dependencies are updated and secure
- [ ] Environment variables are configured
- [ ] Database migrations are tested
- [ ] Rollback plan is prepared

### Deployment Best Practices

- **Use version tags** for releases
- **Test in staging** before production
- **Deploy during low-traffic periods**
- **Monitor after deployment**
- **Have rollback procedures** ready

### Environment Management

- **Separate configs** for dev/staging/prod
- **Use environment variables** for configuration
- **Never commit production secrets**
- **Use configuration management** tools

## Monitoring

### Logging

- **Use structured logging** (JSON format in production)
- **Set appropriate log levels**:
  - DEBUG: Detailed diagnostic information
  - INFO: General informational messages
  - WARNING: Warning messages
  - ERROR: Error messages
  - CRITICAL: Critical errors

- **Never log sensitive information**
- **Include context** in log messages
- **Use correlation IDs** for request tracking

### Metrics

- **Track key metrics**:
  - Pipeline execution time
  - Step success/failure rates
  - Data processing volumes
  - Error rates

- **Use MetricsMixin** for custom metrics
- **Export metrics** for monitoring systems

### Error Handling

- **Log errors with context**
- **Don't expose internal errors** to users
- **Use appropriate exception types**
- **Implement retry logic** for transient failures

## Code Review Guidelines

### What to Review

- **Functionality**: Does it work as intended?
- **Code quality**: Is it readable and maintainable?
- **Tests**: Are there adequate tests?
- **Documentation**: Is it documented?
- **Security**: Are there security concerns?
- **Performance**: Are there performance issues?

### Review Best Practices

- **Be constructive** and respectful
- **Explain why** changes are needed
- **Suggest improvements** rather than just pointing out issues
- **Approve when satisfied**

## Continuous Improvement

### Regular Tasks

- **Weekly**: Review and update dependencies
- **Monthly**: Review and update documentation
- **Quarterly**: Security audit and dependency review
- **As needed**: Refactor technical debt

### Learning Resources

- Python best practices: [PEP 8](https://pep8.org/)
- Testing: [pytest documentation](https://docs.pytest.org/)
- Type hints: [PEP 484](https://www.python.org/dev/peps/pep-0484/)
- Security: [OWASP Top 10](https://owasp.org/www-project-top-ten/)

## Next Steps

**Reviewed best practices?** Apply them:

1. **[CONTRIBUTING.md](../CONTRIBUTING.md)** → Start contributing following these practices
2. **[src/tests/TESTING.md](../src/tests/TESTING.md)** → Write tests following testing guidelines
3. **[examples/README.md](../examples/README.md)** → See best practices in action

**Setting up development environment?**

1. **[GETTING_STARTED.md](../GETTING_STARTED.md)** → Complete setup guide
2. **[Makefile](../Makefile)** → Use `make install-dev` and `make ci`
3. **[.pre-commit-config.yaml](../.pre-commit-config.yaml)** → Install pre-commit hooks

**Ready to code?**

1. **[docs/DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** → Understand architecture patterns
2. **[config/PIPELINE_CONFIG_GUIDE.md](../config/PIPELINE_CONFIG_GUIDE.md)** → Create pipelines
3. **[sql_migration/README.md](../sql_migration/README.md)** → Migrate SQL to Python

## Related Documentation

- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Contribution guidelines
- **[SECURITY.md](../SECURITY.md)** - Security policy
- **[Design Principles](DESIGN_PRINCIPLES.md)** - Architecture guidelines
- **[Testing Guide](../src/tests/TESTING.md)** - Testing documentation

