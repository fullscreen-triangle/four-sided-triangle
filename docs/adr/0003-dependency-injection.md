# ADR 0003: Dependency Injection Pattern

## Status

Accepted

## Context

The Four-Sided Triangle project has grown to include many interdependent components, making it increasingly difficult to maintain, test, and extend. Different parts of the codebase are using different approaches to manage dependencies, creating inconsistency and tight coupling between components.

## Decision

We will implement a consistent dependency injection (DI) pattern throughout the codebase using a central dependency container. This pattern will help:

1. **Decouple Components**: Reduce direct dependencies between components
2. **Facilitate Testing**: Make it easier to swap real implementations with test doubles
3. **Centralize Configuration**: Manage component lifecycle and configuration centrally
4. **Standardize Component Access**: Provide a consistent way to access dependencies

The implementation will include:

1. **Dependency Container**: A central registry for all dependencies
2. **Registration Interface**: Methods to register implementations for interfaces
3. **Resolution Interface**: Methods to resolve dependencies by name or type
4. **Lifecycle Management**: Support for singleton and transient lifestyles

## Consequences

### Positive

- Reduced coupling between components
- Improved testability of all components
- More consistent approach to component creation and access
- More flexible configuration
- Easier extension and replacement of components

### Negative

- Learning curve for developers unfamiliar with DI
- Some additional boilerplate code
- Need to refactor existing code to use the DI container

## Implementation

1. Create a `DependencyContainer` class to manage dependencies
2. Update component creation to use the container
3. Gradually refactor existing components to support injection
4. Provide helper functions to facilitate common injection patterns
5. Document best practices for using DI in the codebase 