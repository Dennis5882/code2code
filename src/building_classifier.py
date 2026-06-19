"""Building envelope classification helpers for wind design code workflows."""

from dataclasses import dataclass
from enum import Enum


class BuildingType(Enum):
    """Building enclosure category derived from clause 1.3 style definitions."""

    OPEN = "OPEN"
    PARTIALLY_ENCLOSED = "PARTIALLY_ENCLOSED"
    ENCLOSED = "ENCLOSED"


class StructuralType(Enum):
    """Dynamic behavior category derived from the fundamental frequency threshold."""

    RIGID = "RIGID"
    FLEXIBLE = "FLEXIBLE"


@dataclass(frozen=True)
class BuildingGeometry:
    """Input geometry needed for the chapter-1 classification logic."""

    windward_area: float
    windward_opening_area: float
    leeward_area: float
    leeward_opening_area: float
    fundamental_frequency_hz: float
    wall_opening_ratios: tuple[float, ...] = ()

    def __post_init__(self) -> None:
        for name, value in (
            ("windward_area", self.windward_area),
            ("windward_opening_area", self.windward_opening_area),
            ("leeward_area", self.leeward_area),
            ("leeward_opening_area", self.leeward_opening_area),
        ):
            if value < 0:
                raise ValueError(f"{name} cannot be negative")

        if self.fundamental_frequency_hz <= 0:
            raise ValueError("fundamental_frequency_hz must be positive")

        for ratio in self.wall_opening_ratios:
            if ratio < 0 or ratio > 1:
                raise ValueError("wall_opening_ratios must stay between 0 and 1")


def classify_building_type(geometry: BuildingGeometry) -> BuildingType:
    """Classify the building enclosure using clause 1.3 style logic."""
    if _is_open_building(geometry):
        return BuildingType.OPEN

    if _is_partially_enclosed_building(geometry):
        return BuildingType.PARTIALLY_ENCLOSED

    return BuildingType.ENCLOSED


def classify_structural_type(geometry: BuildingGeometry) -> StructuralType:
    """Classify the structure by the 1 Hz flexible-building threshold."""
    if geometry.fundamental_frequency_hz < 1.0:
        return StructuralType.FLEXIBLE
    return StructuralType.RIGID


def calculate_effective_area(span: float, effective_width: float) -> float:
    """Calculate effective wind area with the one-third span lower bound."""
    if span <= 0:
        raise ValueError("span must be positive")
    if effective_width < 0:
        raise ValueError("effective_width cannot be negative")

    adjusted_width = max(effective_width, span / 3.0)
    return span * adjusted_width


def _is_open_building(geometry: BuildingGeometry) -> bool:
    """Prefer explicit wall ratios; otherwise use a conservative two-face fallback."""
    if geometry.wall_opening_ratios:
        open_faces = sum(1 for ratio in geometry.wall_opening_ratios if ratio >= 0.8)
        return open_faces >= 2

    windward_ratio = (
        geometry.windward_opening_area / geometry.windward_area
        if geometry.windward_area > 0
        else 0.0
    )
    leeward_ratio = (
        geometry.leeward_opening_area / geometry.leeward_area
        if geometry.leeward_area > 0
        else 0.0
    )
    return windward_ratio >= 0.8 and leeward_ratio >= 0.8


def _is_partially_enclosed_building(geometry: BuildingGeometry) -> bool:
    """Apply the three-condition partially enclosed definition."""
    dominant_opening = geometry.windward_opening_area > 1.10 * geometry.leeward_opening_area
    minimum_opening = geometry.windward_opening_area > min(0.37, 0.01 * geometry.windward_area)

    if geometry.leeward_area <= 0:
        return False

    background_opening_ratio = geometry.leeward_opening_area / geometry.leeward_area
    return dominant_opening and minimum_opening and background_opening_ratio <= 0.20
