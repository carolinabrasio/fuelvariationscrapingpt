"""Provide minimal Home Assistant imports for parser-only tests."""

import importlib.util
import sys
from types import ModuleType
from typing import Any


if importlib.util.find_spec("homeassistant") is None:
    homeassistant = ModuleType("homeassistant")
    components = ModuleType("homeassistant.components")
    sensor = ModuleType("homeassistant.components.sensor")
    helpers = ModuleType("homeassistant.helpers")
    entity_platform = ModuleType("homeassistant.helpers.entity_platform")

    sensor.SensorEntity = object
    entity_platform.AddEntitiesCallback = Any
    homeassistant.components = components
    homeassistant.helpers = helpers
    components.sensor = sensor
    helpers.entity_platform = entity_platform

    sys.modules.update(
        {
            "homeassistant": homeassistant,
            "homeassistant.components": components,
            "homeassistant.components.sensor": sensor,
            "homeassistant.helpers": helpers,
            "homeassistant.helpers.entity_platform": entity_platform,
        }
    )