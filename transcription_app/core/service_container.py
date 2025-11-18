"""
Lightweight dependency injection container
Provides service registration, resolution, and lifecycle management
"""
from typing import TypeVar, Type, Callable, Optional, Dict, Any
from enum import Enum
from transcription_app.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class ServiceLifetime(Enum):
    """Service lifetime options"""
    SINGLETON = "singleton"  # Single instance shared across app
    TRANSIENT = "transient"  # New instance each time
    SCOPED = "scoped"  # Single instance per scope (future use)


class ServiceContainer:
    """
    Dependency injection container for managing application services

    Example usage:
        container = ServiceContainer()

        # Register singleton service
        container.register_singleton(IConfig, lambda: AppConfig())

        # Register transient service
        container.register_transient(ITranscriptionEngine, WhisperXEngine)

        # Resolve service
        config = container.resolve(IConfig)
    """

    def __init__(self):
        self._services: Dict[Type, Dict[str, Any]] = {}
        self._singletons: Dict[Type, Any] = {}
        logger.info("ServiceContainer initialized")

    def register_singleton(
        self,
        service_type: Type[T],
        factory: Callable[[], T],
        lazy: bool = True
    ):
        """
        Register a singleton service (single shared instance)

        Args:
            service_type: Interface or class type to register
            factory: Factory function that creates the service instance
            lazy: If True, instance created on first resolve; if False, created immediately
        """
        self._services[service_type] = {
            'lifetime': ServiceLifetime.SINGLETON,
            'factory': factory,
            'lazy': lazy
        }

        # Create immediately if not lazy
        if not lazy:
            self._singletons[service_type] = factory()
            logger.info(f"Registered singleton (eager): {service_type.__name__}")
        else:
            logger.info(f"Registered singleton (lazy): {service_type.__name__}")

    def register_transient(
        self,
        service_type: Type[T],
        factory: Callable[[], T]
    ):
        """
        Register a transient service (new instance each time)

        Args:
            service_type: Interface or class type to register
            factory: Factory function that creates the service instance
        """
        self._services[service_type] = {
            'lifetime': ServiceLifetime.TRANSIENT,
            'factory': factory
        }
        logger.info(f"Registered transient: {service_type.__name__}")

    def register_instance(self, service_type: Type[T], instance: T):
        """
        Register an existing instance as a singleton

        Args:
            service_type: Interface or class type to register
            instance: Pre-created instance to register
        """
        self._singletons[service_type] = instance
        self._services[service_type] = {
            'lifetime': ServiceLifetime.SINGLETON,
            'factory': lambda: instance,
            'lazy': False
        }
        logger.info(f"Registered instance: {service_type.__name__}")

    def resolve(self, service_type: Type[T]) -> T:
        """
        Resolve a service instance

        Args:
            service_type: Service type to resolve

        Returns:
            Service instance

        Raises:
            KeyError: If service is not registered
        """
        if service_type not in self._services:
            raise KeyError(
                f"Service {service_type.__name__} is not registered. "
                f"Available services: {', '.join(s.__name__ for s in self._services.keys())}"
            )

        service_config = self._services[service_type]
        lifetime = service_config['lifetime']

        if lifetime == ServiceLifetime.SINGLETON:
            # Check if singleton already created
            if service_type not in self._singletons:
                logger.debug(f"Creating singleton instance: {service_type.__name__}")
                self._singletons[service_type] = service_config['factory']()
            return self._singletons[service_type]

        elif lifetime == ServiceLifetime.TRANSIENT:
            logger.debug(f"Creating transient instance: {service_type.__name__}")
            return service_config['factory']()

        else:
            raise ValueError(f"Unsupported lifetime: {lifetime}")

    def is_registered(self, service_type: Type) -> bool:
        """
        Check if a service is registered

        Args:
            service_type: Service type to check

        Returns:
            True if service is registered
        """
        return service_type in self._services

    def clear(self):
        """Clear all registered services and singleton instances"""
        self._services.clear()
        self._singletons.clear()
        logger.info("ServiceContainer cleared")

    def get_registered_services(self) -> list[str]:
        """
        Get list of registered service names

        Returns:
            List of registered service type names
        """
        return [service_type.__name__ for service_type in self._services.keys()]


# Global container instance
_container: Optional[ServiceContainer] = None


def get_service_container() -> ServiceContainer:
    """Get or create global service container"""
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container


def reset_service_container():
    """Reset global service container (mainly for testing)"""
    global _container
    if _container:
        _container.clear()
    _container = None
