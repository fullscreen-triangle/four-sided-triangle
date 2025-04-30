# Four-Sided Triangle Frontend Style Guidelines

This document outlines the coding and design standards for the Four-Sided Triangle frontend application. All code contributions should adhere to these guidelines to maintain consistency and quality across the project.

## Code Style

### JavaScript/TypeScript

- Use TypeScript for all new components and features
- Follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use functional components with hooks instead of class components
- Use arrow functions for component definitions and callbacks
- Prefer const over let, avoid var
- Use destructuring for props and state
- Use optional chaining and nullish coalescing when appropriate

### React

- Use named exports for components
- Each component should be in its own file
- Keep components small and focused on a single responsibility
- Use React.memo for performance optimization when appropriate
- Use custom hooks to extract and reuse stateful logic
- Follow the React hooks rules (don't call hooks conditionally)

### CSS/Styling

- Use Tailwind CSS for styling components
- Follow a mobile-first approach for responsive design
- Use CSS variables for theme colors and spacing
- Avoid inline styles except for dynamic values
- Use semantic class names that describe purpose, not appearance

## Component Structure

### File Organization

```
src/
  components/
    feature-name/
      FeatureComponent.tsx
      FeatureComponent.test.tsx
      useFeatureHook.ts
      types.ts
      index.ts
```

### Component Template

```tsx
import React from 'react';
import { ComponentProps } from './types';

/**
 * ComponentName - Description of the component's purpose
 */
export const ComponentName: React.FC<ComponentProps> = ({ 
  prop1, 
  prop2,
  children 
}) => {
  // Hooks
  
  // Derived state
  
  // Event handlers
  
  // Render
  return (
    <div className="component-container">
      {/* Component content */}
    </div>
  );
};
```

## State Management

- Use React Context for global state that changes infrequently
- Use React Query for server state management
- Keep component state local when possible
- Use reducers for complex state logic
- Document state shape with TypeScript interfaces

## Performance Considerations

- Memoize expensive calculations with useMemo
- Optimize callback functions with useCallback
- Use virtualization for long lists
- Implement code splitting with React.lazy and Suspense
- Minimize re-renders by avoiding unnecessary state updates

## Accessibility

- All interactive elements must be keyboard accessible
- Use semantic HTML elements
- Include proper ARIA attributes when necessary
- Ensure sufficient color contrast (WCAG AA compliance)
- Support screen readers with appropriate text alternatives

## Testing

- Write unit tests for all components and utilities
- Use React Testing Library for component tests
- Test user interactions, not implementation details
- Include accessibility tests
- Aim for high test coverage on critical paths

## Documentation

- Use JSDoc comments for all components, props, and functions
- Include usage examples for complex components
- Document known limitations and edge cases
- Keep README files up to date
- Document API integrations and data flow

## Pull Request Process

- Reference the task number in commit messages
- Include screenshots for UI changes
- Update documentation when necessary
- Ensure all tests pass
- Request reviews from appropriate team members