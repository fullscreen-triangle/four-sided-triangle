---
layout: default
title: Contributing
nav_order: 7
---

# Contributing to Four-Sided Triangle

Thank you for your interest in contributing to Four-Sided Triangle! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Making Contributions](#making-contributions)
5. [Coding Standards](#coding-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Documentation](#documentation)
8. [Pull Request Process](#pull-request-process)

## Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read and follow our Code of Conduct.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/four-sided-triangle.git
   cd four-sided-triangle
   ```
3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/originalowner/four-sided-triangle.git
   ```

## Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Making Contributions

### Branch Naming Convention

- Feature branches: `feature/description`
- Bug fixes: `fix/description`
- Documentation: `docs/description`
- Performance improvements: `perf/description`

### Commit Message Format

```
type(scope): Brief description

Detailed description of changes
```

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes
- refactor: Code refactoring
- perf: Performance improvements
- test: Adding or modifying tests
- chore: Maintenance tasks

## Coding Standards

### Python Code Style

- Follow PEP 8 guidelines
- Use type hints
- Maximum line length: 88 characters
- Use docstrings for all public functions and classes

### JavaScript Code Style

- Follow ESLint configuration
- Use TypeScript where possible
- Maximum line length: 100 characters
- Use JSDoc for documentation

### General Guidelines

1. Write self-documenting code
2. Keep functions focused and small
3. Use meaningful variable names
4. Add comments for complex logic
5. Follow the DRY principle

## Testing Guidelines

### Writing Tests

1. Write tests for all new features
2. Maintain test coverage above 80%
3. Include unit and integration tests
4. Use meaningful test names
5. Follow the AAA pattern (Arrange, Act, Assert)

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_file.py

# Run with coverage
pytest --cov=app tests/
```

### Performance Testing

1. Include benchmarks for performance-critical code
2. Test with realistic data volumes
3. Monitor memory usage
4. Check CPU utilization
5. Verify GPU optimization

## Documentation

### Code Documentation

1. Use docstrings for all public APIs
2. Include type hints
3. Document exceptions
4. Provide usage examples
5. Keep documentation up to date

### Project Documentation

1. Update README.md for major changes
2. Maintain API documentation
3. Update architecture diagrams
4. Document configuration changes
5. Keep examples current

## Pull Request Process

1. Create a new branch for your changes
2. Make your changes following the guidelines
3. Write or update tests
4. Update documentation
5. Run the test suite
6. Push your changes
7. Create a pull request

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring
- [ ] Other (please describe)

## Testing
Describe the tests you ran

## Documentation
List documentation updates

## Additional Notes
Any additional information
```

### Review Process

1. Automated checks must pass
2. Code review by maintainers
3. Documentation review
4. Performance review if applicable
5. Final approval

## Pipeline Development

### Adding New Pipeline Stages

1. Implement the `AbstractPipelineStage` interface
2. Add configuration in `config/pipeline.yaml`
3. Update orchestrator integration
4. Add monitoring
5. Write tests
6. Update documentation

### Modifying Existing Stages

1. Maintain backward compatibility
2. Update tests
3. Document changes
4. Update configuration
5. Test performance impact

## Model Integration

### Adding New Models

1. Implement model interface
2. Add configuration
3. Update model registry
4. Add tests
5. Document usage
6. Verify performance

### Model Requirements

1. Clear input/output specifications
2. Error handling
3. Resource management
4. Performance metrics
5. Documentation

## Release Process

1. Version bump following semver
2. Update CHANGELOG.md
3. Update documentation
4. Create release notes
5. Tag release
6. Deploy to staging
7. Deploy to production

## Getting Help

- Check existing issues
- Join our community chat
- Read the documentation
- Contact maintainers

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to Four-Sided Triangle! 