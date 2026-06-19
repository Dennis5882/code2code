import math

import pytest

from src.building_classifier import (
    BuildingGeometry,
    BuildingType,
    StructuralType,
    calculate_effective_area,
    classify_building_type,
    classify_structural_type,
)


def test_classifies_open_building_from_explicit_wall_ratios() -> None:
    geometry = BuildingGeometry(
        windward_area=100.0,
        windward_opening_area=10.0,
        leeward_area=200.0,
        leeward_opening_area=20.0,
        fundamental_frequency_hz=2.0,
        wall_opening_ratios=(0.85, 0.82, 0.10, 0.05),
    )

    assert classify_building_type(geometry) is BuildingType.OPEN


def test_classifies_partially_enclosed_building() -> None:
    geometry = BuildingGeometry(
        windward_area=100.0,
        windward_opening_area=20.0,
        leeward_area=300.0,
        leeward_opening_area=10.0,
        fundamental_frequency_hz=0.8,
    )

    assert classify_building_type(geometry) is BuildingType.PARTIALLY_ENCLOSED


def test_classifies_enclosed_building() -> None:
    geometry = BuildingGeometry(
        windward_area=100.0,
        windward_opening_area=5.0,
        leeward_area=300.0,
        leeward_opening_area=10.0,
        fundamental_frequency_hz=2.0,
    )

    assert classify_building_type(geometry) is BuildingType.ENCLOSED


def test_classifies_structural_flexibility() -> None:
    flexible = BuildingGeometry(
        windward_area=100.0,
        windward_opening_area=5.0,
        leeward_area=100.0,
        leeward_opening_area=5.0,
        fundamental_frequency_hz=0.9,
    )
    rigid = BuildingGeometry(
        windward_area=100.0,
        windward_opening_area=5.0,
        leeward_area=100.0,
        leeward_opening_area=5.0,
        fundamental_frequency_hz=1.2,
    )

    assert classify_structural_type(flexible) is StructuralType.FLEXIBLE
    assert classify_structural_type(rigid) is StructuralType.RIGID


def test_effective_area_uses_one_third_span_lower_bound() -> None:
    assert math.isclose(calculate_effective_area(5.0, 1.0), 25.0 / 3.0, rel_tol=1e-9)


def test_invalid_geometry_is_rejected() -> None:
    with pytest.raises(ValueError):
        BuildingGeometry(
            windward_area=-1.0,
            windward_opening_area=0.0,
            leeward_area=100.0,
            leeward_opening_area=0.0,
            fundamental_frequency_hz=1.0,
        )
