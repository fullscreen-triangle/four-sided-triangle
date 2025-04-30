# ADR 0001: Module Naming Conventions

## Status

Accepted

## Context

The Four-Sided Triangle project needs consistent naming conventions for modules, classes, and files to ensure clarity and maintainability. Currently, there are inconsistencies in naming across the codebase, such as `metacognitive_orchestrator.py` vs `core.py`.

## Decision

We will adopt the following naming conventions for the project:

1. **Module files** should use snake_case and be descriptive of their primary functionality.
2. **Re-export files** may use simpler names like `core.py` when they act as façades for more complex implementations.
3. **Class names** should use PascalCase and be descriptive of their responsibilities.
4. **Interface classes** should be prefixed with "Abstract" or "I" (e.g., `AbstractPipelineStage`).
5. **Implementation classes** should not have prefixes or suffixes indicating they are implementations.

For re-export files like `core.py` that import from more specifically named modules like `metacognitive_orchestrator.py`, the specific implementation modules should remain, and the simpler named files should serve as clean interfaces that re-export the relevant classes and functions.

## Consequences

### Positive

- Improved code readability and maintainability
- Easier navigation of the codebase for new developers
- Clearer distinction between interfaces and implementations

### Negative

- Need to update existing code to conform to these conventions
- May require backward compatibility layers for some time

## Implementation

For existing inconsistencies:

1. Keep both `metacognitive_orchestrator.py` and `core.py`, where `core.py` re-exports from `metacognitive_orchestrator.py`
2. Ensure all new modules follow these conventions
3. Gradually refactor existing modules to conform to these conventions as needed 