#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromSploit Framework v2.0
Example module with complete type hints and docstrings

This module demonstrates best practices for type hints and documentation
in the ChromSploit Framework.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import (
    Any, Callable, ClassVar, Dict, Final, Generic, Iterable, List,
    Literal, Optional, Protocol, Sequence, Set, Tuple, Type, TypeVar,
    Union, cast, overload
)

# Type variables
T = TypeVar('T')
ConfigType = TypeVar('ConfigType', bound='BaseConfig')

# Constants with type annotations
MAX_RETRIES: Final[int] = 3
DEFAULT_TIMEOUT: Final[float] = 30.0
SUPPORTED_PROTOCOLS: Final[Set[str]] = {"http", "https", "ws", "wss"}


class Status(Enum):
    """
    Enumeration of possible operation statuses.
    
    Attributes:
        PENDING: Operation is waiting to start
        RUNNING: Operation is currently executing
        SUCCESS: Operation completed successfully
        FAILED: Operation failed
        CANCELLED: Operation was cancelled
    """
    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class OperationResult(Generic[T]):
    """
    Generic result container for operations.
    
    This dataclass encapsulates the result of any operation, including
    success status, data, error information, and metadata.
    
    Type Parameters:
        T: The type of data returned by the operation
    
    Attributes:
        success: Whether the operation succeeded
        data: The operation result data (if successful)
        error: Error message (if failed)
        metadata: Additional information about the operation
        timestamp: When the operation completed
        
    Example:
        >>> result = OperationResult(
        ...     success=True,
        ...     data={"key": "value"},
        ...     metadata={"duration": 1.5}
        ... )
        >>> if result.success:
        ...     print(result.data)
    """
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self) -> None:
        """Validate that success and error states are consistent."""
        if self.success and self.error:
            raise ValueError("Cannot have both success=True and an error message")
        if not self.success and self.data is not None:
            raise ValueError("Cannot have data when success=False")
    
    @property
    def duration(self) -> Optional[float]:
        """
        Get operation duration from metadata if available.
        
        Returns:
            Duration in seconds, or None if not recorded
        """
        return self.metadata.get('duration')
    
    def unwrap(self) -> T:
        """
        Get the data or raise an exception if operation failed.
        
        Returns:
            The operation data
            
        Raises:
            RuntimeError: If the operation was not successful
        """
        if not self.success:
            raise RuntimeError(f"Operation failed: {self.error}")
        if self.data is None:
            raise RuntimeError("Operation succeeded but no data was returned")
        return self.data


class OperationProtocol(Protocol):
    """
    Protocol defining the interface for executable operations.
    
    This protocol ensures that all operations have a consistent interface
    for execution and result handling.
    """
    
    def execute(self) -> OperationResult[Any]:
        """Execute the operation and return a result."""
        ...
    
    async def execute_async(self) -> OperationResult[Any]:
        """Execute the operation asynchronously."""
        ...
    
    @property
    def name(self) -> str:
        """Get the operation name."""
        ...


class BaseOperation(ABC, Generic[T]):
    """
    Abstract base class for all operations.
    
    This class provides a template for implementing operations with
    consistent error handling, logging, and result management.
    
    Type Parameters:
        T: The type of data returned by the operation
        
    Attributes:
        name: Operation identifier
        timeout: Maximum execution time in seconds
        retries: Number of retry attempts
        logger: Logger instance for this operation
    """
    
    def __init__(
        self,
        name: str,
        timeout: float = DEFAULT_TIMEOUT,
        retries: int = MAX_RETRIES
    ) -> None:
        """
        Initialize the operation.
        
        Args:
            name: Unique operation name
            timeout: Operation timeout in seconds
            retries: Maximum number of retry attempts
            
        Raises:
            ValueError: If timeout or retries are invalid
        """
        if timeout <= 0:
            raise ValueError("Timeout must be positive")
        if retries < 0:
            raise ValueError("Retries cannot be negative")
            
        self.name = name
        self.timeout = timeout
        self.retries = retries
        self._status = Status.PENDING
    
    @property
    def status(self) -> Status:
        """Get the current operation status."""
        return self._status
    
    @status.setter
    def status(self, value: Status) -> None:
        """
        Set the operation status.
        
        Args:
            value: New status value
            
        Note:
            Status transitions are validated to ensure logical flow.
        """
        # Validate status transitions
        if self._status == Status.SUCCESS and value != Status.SUCCESS:
            raise ValueError("Cannot change status after success")
        self._status = value
    
    @abstractmethod
    def _perform(self) -> T:
        """
        Perform the actual operation.
        
        This method must be implemented by subclasses to define
        the specific operation logic.
        
        Returns:
            The operation result
            
        Raises:
            Exception: Any exception that occurs during execution
        """
        pass
    
    def execute(self) -> OperationResult[T]:
        """
        Execute the operation with error handling and retries.
        
        Returns:
            OperationResult containing the outcome
            
        Example:
            >>> op = ConcreteOperation("test")
            >>> result = op.execute()
            >>> if result.success:
            ...     print(f"Result: {result.data}")
        """
        start_time = datetime.now()
        attempts = 0
        last_error: Optional[str] = None
        
        self.status = Status.RUNNING
        
        while attempts <= self.retries:
            try:
                data = self._perform()
                self.status = Status.SUCCESS
                
                return OperationResult(
                    success=True,
                    data=data,
                    metadata={
                        'duration': (datetime.now() - start_time).total_seconds(),
                        'attempts': attempts + 1
                    }
                )
            except Exception as e:
                attempts += 1
                last_error = str(e)
                if attempts > self.retries:
                    break
        
        self.status = Status.FAILED
        return OperationResult(
            success=False,
            error=last_error,
            metadata={
                'duration': (datetime.now() - start_time).total_seconds(),
                'attempts': attempts
            }
        )
    
    async def execute_async(self) -> OperationResult[T]:
        """
        Execute the operation asynchronously.
        
        This method runs the synchronous execute method in a thread pool
        to avoid blocking the event loop.
        
        Returns:
            OperationResult containing the outcome
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.execute)


class ConfigurableOperation(BaseOperation[Dict[str, Any]]):
    """
    An operation that can be configured with parameters.
    
    This class extends BaseOperation to add configuration management
    and validation capabilities.
    
    Attributes:
        config: Configuration dictionary
        validators: List of validation functions
    """
    
    def __init__(
        self,
        name: str,
        config: Optional[Dict[str, Any]] = None,
        validators: Optional[List[Callable[[Dict[str, Any]], bool]]] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize a configurable operation.
        
        Args:
            name: Operation name
            config: Configuration parameters
            validators: List of config validation functions
            **kwargs: Additional arguments for BaseOperation
        """
        super().__init__(name, **kwargs)
        self.config = config or {}
        self.validators = validators or []
        self._validate_config()
    
    def _validate_config(self) -> None:
        """
        Validate the configuration using registered validators.
        
        Raises:
            ValueError: If configuration is invalid
        """
        for validator in self.validators:
            if not validator(self.config):
                raise ValueError(f"Configuration validation failed for {self.name}")
    
    @overload
    def get_config(self, key: str) -> Any:
        """Get a configuration value by key."""
        ...
    
    @overload
    def get_config(self, key: str, default: T) -> Union[Any, T]:
        """Get a configuration value with a default."""
        ...
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """
        Update configuration with new values.
        
        Args:
            updates: Dictionary of updates to apply
            
        Raises:
            ValueError: If updated configuration is invalid
        """
        self.config.update(updates)
        self._validate_config()


def create_operation(
    operation_type: Type[BaseOperation[T]],
    name: str,
    **kwargs: Any
) -> BaseOperation[T]:
    """
    Factory function to create operations.
    
    This function provides a convenient way to instantiate operations
    with proper type checking.
    
    Type Parameters:
        T: The return type of the operation
        
    Args:
        operation_type: The operation class to instantiate
        name: Operation name
        **kwargs: Additional arguments for the operation
        
    Returns:
        An instance of the specified operation type
        
    Example:
        >>> op = create_operation(ConfigurableOperation, "test_op", config={"key": "value"})
        >>> result = op.execute()
    """
    return operation_type(name, **kwargs)


async def execute_operations_parallel(
    operations: Sequence[BaseOperation[Any]]
) -> List[OperationResult[Any]]:
    """
    Execute multiple operations in parallel.
    
    Args:
        operations: Sequence of operations to execute
        
    Returns:
        List of results in the same order as operations
        
    Example:
        >>> ops = [op1, op2, op3]
        >>> results = await execute_operations_parallel(ops)
        >>> for result in results:
        ...     if result.success:
        ...         print(result.data)
    """
    tasks = [op.execute_async() for op in operations]
    return await asyncio.gather(*tasks)


def chain_operations(
    *operations: BaseOperation[Any]
) -> Callable[[], OperationResult[List[Any]]]:
    """
    Chain operations to execute sequentially.
    
    Creates a function that executes operations in order, stopping
    on the first failure.
    
    Args:
        *operations: Operations to chain
        
    Returns:
        A function that executes the chain
        
    Example:
        >>> chain = chain_operations(op1, op2, op3)
        >>> result = chain()
        >>> if result.success:
        ...     data1, data2, data3 = result.data
    """
    def execute_chain() -> OperationResult[List[Any]]:
        results: List[Any] = []
        
        for op in operations:
            result = op.execute()
            if not result.success:
                return OperationResult(
                    success=False,
                    error=f"Chain failed at {op.name}: {result.error}"
                )
            results.append(result.data)
        
        return OperationResult(success=True, data=results)
    
    return execute_chain


# Example usage with proper typing
if __name__ == "__main__":
    # Example concrete implementation
    class ExampleOperation(ConfigurableOperation):
        """Example operation that doubles a number."""
        
        def _perform(self) -> Dict[str, Any]:
            """Perform the doubling operation."""
            value: int = self.get_config("value", 1)
            return {"result": value * 2}
    
    # Create and execute operation
    op: BaseOperation[Dict[str, Any]] = ExampleOperation(
        "double",
        config={"value": 21}
    )
    
    result: OperationResult[Dict[str, Any]] = op.execute()
    
    if result.success:
        print(f"Success: {result.data}")
    else:
        print(f"Failed: {result.error}")