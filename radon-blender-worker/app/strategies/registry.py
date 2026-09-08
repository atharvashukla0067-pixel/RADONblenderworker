"""Strategy registry — maps categories to generation strategies.

New strategies can be registered here without modifying the HTTP API contract.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional, Type

from .base import GenerationStrategy
from .anatomy import AnatomyStrategy
from .molecule import MoleculeStrategy
from .astronomy import AstronomyStrategy
from .vehicle import VehicleStrategy
from .architecture import ArchitectureStrategy
from .engineering import EngineeringStrategy
from .general import GeneralObjectStrategy

logger = logging.getLogger("radon-blender-worker")


class StrategyRegistry:
    """Registry mapping category names to strategy instances."""

    def __init__(self) -> None:
        self._strategies: Dict[str, GenerationStrategy] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register("anatomy", AnatomyStrategy())
        self.register("molecule", MoleculeStrategy())
        self.register("astronomy", AstronomyStrategy())
        self.register("vehicle", VehicleStrategy())
        self.register("architecture", ArchitectureStrategy())
        self.register("engineering", EngineeringStrategy())
        self.register("general", GeneralObjectStrategy())
        self.register("scientific", MoleculeStrategy())  # alias
        self.register("chemistry", MoleculeStrategy())   # alias

    def register(self, category: str, strategy: GenerationStrategy) -> None:
        key = category.lower().strip()
        self._strategies[key] = strategy
        logger.info("Registered strategy %s for category '%s'", strategy.__class__.__name__, key)

    def get(self, category: str) -> Optional[GenerationStrategy]:
        key = category.lower().strip()
        return self._strategies.get(key)

    def get_or_default(self, category: str) -> GenerationStrategy:
        key = category.lower().strip()
        strategy = self._strategies.get(key)
        if strategy is None:
            logger.info("No strategy for category '%s', falling back to general", key)
            strategy = self._strategies["general"]
        return strategy

    def list_categories(self) -> list[str]:
        return sorted(self._strategies.keys())


strategy_registry = StrategyRegistry()
