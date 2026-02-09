# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Base Capacity Representation.

Raises:
    NoCapacityError: [description]
    CapacityReleaseError: [description]

"""

import abc

from typing import Dict, Union


class NoCapacityError(Exception):
    """
    Raised when capacity is required but none is available.

    This would only happen if the task selection and agent capacity are out of sync which should not happen.
    As when a task is selected from the queue it is selected because the capacity was available.
    """


class CapacityReleaseError(Exception):
    """
    Raised when releasing the capacity would cause the available capacity to be higher than the initial capacity.

    This would only happen if somehow the resource was oversubscribed.
    """


class AbstractCapacity(abc.ABC):
    """Base Capacity class."""

    def __init__(self, strict: bool = False) -> None:
        """
        Initialise a capacity.

           Kwargs:
                strict (bool): Indicate if this is an absolute requirement for the agent.
                If set to true only tasks that have this capacity speficied are selected.
        """
        super().__init__()
        self._strict = strict
        self._identifier = None
        self._capacity = None

    @property
    def identifier(self):
        return self._identifier

    @property
    def capacity(self) -> int:
        """Value identifying the capacity."""
        return self._capacity

    @property
    def strict(self) -> bool:
        return self._strict

    @abc.abstractmethod
    async def available_capacity(self) -> Union[int, None]:
        pass

    @abc.abstractmethod
    async def acquire_capacity(self) -> bool:
        return False

    @abc.abstractmethod
    async def release_capacity(self) -> bool:
        return False

    async def has_capacity(self) -> bool:
        if self._capacity is None:
            return True

        return False
    # TODO remove noqa
    async def _set_initial_capacity(self):  # noqa 
        pass

    async def to_dict(self):
        return {
            "identifier": self.identifier,
            "capacity": self._capacity,
            "remaining": await self.available_capacity(),
            "has_capacity": await self.has_capacity(),
            "strict": self.strict
        }

    @classmethod
    async def async_init(cls, *args, **kwargs) -> Dict[str, "AbstractCapacity"]:
        obj = cls(*args, **kwargs)
        await obj._set_initial_capacity()
        return {obj.identifier: obj}


class ValueCapacity(AbstractCapacity):
    """
    Numerical based capacity.

    When acquire_capacity is called 1 will be reduced of available capacity by default.
    When release_capacity is called 1 will be added to available capacity by default.
    Has_capacity will return True when larger than zero.
    """

    def __init__(self, identifier: str, capacity: int = None, strict: bool = False) -> None:
        """
        Initialise a numeric based capacity.

           Args:
               identifier (str): Dot notated identifier of this capacity.

           Kwargs:
               capacity (int): Available capacity for this identifier. If None, the value will be used for job selection only.
               strict (bool): Indicate if this is an absolute requirement for the agent.
                   If set to true only tasks that have this capacity speficied are selected.
        """
        super().__init__(strict=strict)
        self._capacity = capacity
        self._identifier = identifier
        self._remaining_capacity = capacity

    async def available_capacity(self) -> Union[int, None]:
        return self._remaining_capacity

    async def has_capacity(self) -> bool:
        """Check if capacity is available."""
        if await super().has_capacity():
            return True

        return self._remaining_capacity > 0

    async def acquire_capacity(self) -> bool:
        """Acquire one of the available capacity."""
        if not await self.has_capacity():
            raise NoCapacityError(f"No capacity available for {self._identifier}")

        if self._capacity is None:
            return True

        self._remaining_capacity -= 1
        return True

    async def release_capacity(self) -> bool:
        """Release one of the available capacity."""
        if self._capacity is None:
            return True

        if self._remaining_capacity + 1 > self._capacity:
            raise CapacityReleaseError(f"Releasing capacity for {self._identifier} is not possible as the released capacity would be higher than the initial"
                                       "available capacity {self._capacity}")

        self._remaining_capacity += 1
        return True


class StringCapacity(AbstractCapacity):
    """
    String based capacity.

    StringCapacities are to indicate static values, such as a specific OS, that is required and generally does not have an actual capacity value associated.
    Acquire_capacity, release_capacity and has_capacity will always return True.
    """

    def __init__(self, identifier: str, strict: bool = False) -> None:
        super().__init__(strict=strict)
        self._capacity = None
        self._identifier = identifier

    async def available_capacity(self) -> Union[int, None]:
        return None

    async def has_capacity(self) -> bool:
        return True

    async def acquire_capacity(self) -> bool:
        return True

    async def release_capacity(self) -> bool:
        return True


class DynamicCapacity(ValueCapacity):
    """Dynamic Capacity Representation."""

    def __init__(self, identifier: str, capacity: int = None, strict: bool = False) -> None:
        """
        Initialise a dynamic capacity.

            Dynamic capacities are user driven and can be changed externally to the Agent.
            There is no calculations to determine capacity and capacity is reduced for each active job by 1.
            If no capacity is given this capacity will not be used limit the amount of jobs the agent can execute but will participate in task selection.

            Args:
                identifier (str): Dot notated identifier of this capacity.

            Kwargs:
                capacity (int): Available capacity for this identifier. If None, the value will be used for job selection only.
                strict (bool): Indicate if this is an absolute requirement for the agent.
                               If set to true only tasks that have this capacity speficied are selected.
        """
        super().__init__(identifier, capacity=capacity, strict=strict)

    @classmethod
    async def async_init(cls, identifier: str, capacity: int = None, strict: bool = False) -> Dict[str, AbstractCapacity]:
        obj = cls(identifier, capacity=capacity, strict=strict)
        return {obj.identifier: obj}
