"""
taxonomy.py - SPACI 2.0 Space Object Taxonomy & Operational Classifications
============================================================================
Translates raw YOLO class detections into aerospace operational categories,
reusability statuses, and visualization styling attributes.
"""

from dataclasses import dataclass
from typing import Dict, Any

from src.config import (
    CLASS_NAMES,
    CLASS_DISPLAY_NAMES,
    STATE_HAZARDOUS,
    STATE_REUSABLE,
    STATE_ACTIVE,
    STATE_FRAGMENT,
    STATE_COLORS_HEX,
    STATE_COLORS_BGR,
    ACTIVE_SATELLITE_CLASSES,
    INTACT_OBJECT_CLASSES,
)


@dataclass(frozen=True)
class CategoryProfile:
    category_id: str
    name: str
    description: str
    is_trackable: bool
    is_serviceable: bool
    default_base_threat: float
    color_hex: str
    color_bgr: tuple[int, int, int]


# Aerospace Operational Category Taxonomy
OPERATIONAL_CATEGORIES: Dict[str, CategoryProfile] = {
    "TRACKABLE_DEBRIS": CategoryProfile(
        category_id="TRACKABLE_DEBRIS",
        name="Trackable Debris Fragment",
        description="Debris fragment (>10 cm) trackable by SSN radars. High kinetic hazard.",
        is_trackable=True,
        is_serviceable=False,
        default_base_threat=0.68,
        color_hex="#ef4444",
        color_bgr=(68, 68, 239),
    ),
    "SCIENTIFIC_PAYLOAD": CategoryProfile(
        category_id="SCIENTIFIC_PAYLOAD",
        name="Scientific Payload / Active Observatory",
        description="Operational or dormant scientific instrument. High preservation priority.",
        is_trackable=True,
        is_serviceable=True,
        default_base_threat=0.15,
        color_hex="#10b981",
        color_bgr=(129, 185, 16),
    ),
    "DEFUNCT_SATELLITE": CategoryProfile(
        category_id="DEFUNCT_SATELLITE",
        name="Defunct Spacecraft Bus",
        description="Inactive satellite retaining structural integrity. Candidate for on-orbit servicing or deorbiting.",
        is_trackable=True,
        is_serviceable=True,
        default_base_threat=0.35,
        color_hex="#0ea5e9",
        color_bgr=(233, 165, 14),
    ),
    "AMBIGUOUS_OBJECT": CategoryProfile(
        category_id="AMBIGUOUS_OBJECT",
        name="Unresolved / Ambiguous Space Body",
        description="Complex visual signature with undetermined attitude. Requires cautious safety buffer.",
        is_trackable=True,
        is_serviceable=False,
        default_base_threat=0.48,
        color_hex="#f59e0b",
        color_bgr=(11, 158, 245),
    ),
}

# Mapping raw YOLO class to operational category
YOLO_CLASS_TO_CATEGORY: Dict[str, str] = {
    "debris": "TRACKABLE_DEBRIS",
    "cheops": "SCIENTIFIC_PAYLOAD",
    "double_start": "AMBIGUOUS_OBJECT",
    "earth_observation_sat_1": "DEFUNCT_SATELLITE",
    "lisa_pathfinder": "SCIENTIFIC_PAYLOAD",
    "proba_2": "SCIENTIFIC_PAYLOAD",
    "proba_3_csc": "SCIENTIFIC_PAYLOAD",
    "proba_3_ocs": "SCIENTIFIC_PAYLOAD",
    "smart_1": "DEFUNCT_SATELLITE",
    "soho": "SCIENTIFIC_PAYLOAD",
    "xmm_newton": "SCIENTIFIC_PAYLOAD",
}


def get_category_for_class(class_name: str) -> CategoryProfile:
    """Returns the CategoryProfile corresponding to a YOLO class name."""
    cat_id = YOLO_CLASS_TO_CATEGORY.get(class_name.lower().strip(), "TRACKABLE_DEBRIS")
    return OPERATIONAL_CATEGORIES.get(cat_id, OPERATIONAL_CATEGORIES["TRACKABLE_DEBRIS"])


def get_display_name(class_name: str) -> str:
    """Returns formatted human-readable name for a given class."""
    return CLASS_DISPLAY_NAMES.get(class_name.lower().strip(), class_name.replace("_", " ").title())
