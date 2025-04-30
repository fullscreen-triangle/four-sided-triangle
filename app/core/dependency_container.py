"""
Dependency Injection Container for the Four-Sided Triangle system.

This module provides a central container for registering and resolving
dependencies throughout the application, promoting loose coupling and
facilitating testing.
"""

from typing import Dict, Any, Type, Optional, Callable, TypeVar, cast
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

T = TypeVar('T')

class DependencyContainer:
    """
    Manages dependencies throughout the application.
    
    This container allows registering and resolving dependencies,
    supporting singleton and factory registrations.
    """
    
    def __init__(self):
        """Initialize an empty dependency container."""
        self._instances: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[..., Any]] = {}
        self._singletons: Dict[str, bool] = {}
    
    def register(self, interface_name: str, implementation: Any, singleton: bool = True) -> None:
        """
        Register a concrete implementation for an interface.
        
        Args:
            interface_name: The name of the interface or dependency
            implementation: The concrete implementation to use
            singleton: Whether to treat this as a singleton
        """
        if callable(implementation) and not isinstance(implementation, type):
            # This is a factory function
            self._factories[interface_name] = implementation
            self._singletons[interface_name] = singleton
        else:
            # This is a concrete instance or class
            if singleton and isinstance(implementation, type):
                # For singleton classes, create the instance now
                try:
                    implementation = implementation()
                except Exception as e:
                    logger.error(f"Failed to create singleton instance for {interface_name}: {str(e)}")
                    raise
            
            self._instances[interface_name] = implementation
            self._singletons[interface_name] = singleton
        
        logger.debug(f"Registered {interface_name} as {'singleton' if singleton else 'transient'}")
    
    def resolve(self, interface_name: str, **kwargs: Any) -> Any:
        """
        Resolve a dependency by its interface name.
        
        Args:
            interface_name: The name of the interface to resolve
            **kwargs: Optional arguments to pass to factory functions
            
        Returns:
            The resolved dependency
            
        Raises:
            KeyError: If the interface is not registered
        """
        # Check if we have an instance (could be a singleton instance or a class)
        if interface_name in self._instances:
            implementation = self._instances[interface_name]
            is_singleton = self._singletons[interface_name]
            
            if isinstance(implementation, type) and not is_singleton:
                # For non-singleton classes, create a new instance each time
                try:
                    return implementation(**kwargs)
                except Exception as e:
                    logger.error(f"Failed to create instance for {interface_name}: {str(e)}")
                    raise
            
            # For concrete instances or singleton classes that were already instantiated
            return implementation
        
        # Check if we have a factory
        if interface_name in self._factories:
            factory = self._factories[interface_name]
            is_singleton = self._singletons[interface_name]
            
            try:
                instance = factory(**kwargs)
                
                # For singleton factories, store the result for future resolution
                if is_singleton:
                    self._instances[interface_name] = instance
                    del self._factories[interface_name]
                
                return instance
            except Exception as e:
                logger.error(f"Factory for {interface_name} failed: {str(e)}")
                raise
        
        # Interface not found
        raise KeyError(f"Dependency not registered: {interface_name}")
    
    def resolve_typed(self, interface_name: str, expected_type: Type[T], **kwargs: Any) -> T:
        """
        Resolve a dependency with type checking.
        
        Args:
            interface_name: The name of the interface to resolve
            expected_type: The expected type of the resolved dependency
            **kwargs: Optional arguments to pass to factory functions
            
        Returns:
            The resolved dependency cast to the expected type
            
        Raises:
            KeyError: If the interface is not registered
            TypeError: If the resolved dependency is not of the expected type
        """
        instance = self.resolve(interface_name, **kwargs)
        
        if not isinstance(instance, expected_type):
            actual_type = type(instance).__name__
            expected_name = expected_type.__name__
            raise TypeError(f"Expected {interface_name} to be of type {expected_name}, got {actual_type}")
        
        return cast(T, instance)
    
    def clear(self) -> None:
        """Clear all registered dependencies."""
        self._instances.clear()
        self._factories.clear()
        self._singletons.clear()
        logger.debug("Cleared all dependencies")


# Create a global container
container = DependencyContainer()

@lru_cache(maxsize=None)
def get_container() -> DependencyContainer:
    """
    Get the global dependency container.
    
    Returns:
        The global dependency container
    """
    return container 