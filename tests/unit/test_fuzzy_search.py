"""Unit tests for the FuzzySearchEngine, including per-field search selection."""

# pylint: disable=redefined-outer-name
from types import SimpleNamespace

import pytest

from ina_ground_control.utils.fuzzy_search import FuzzySearchEngine


def _task(name="", instruction="", documentation=""):
    return SimpleNamespace(
        name=name, instruction=instruction, documentation=documentation
    )


@pytest.fixture()
def tasks():
    # Each searchable keyword lives in a single, distinct field.
    return [
        _task(name="Segmentation video"),
        _task(instruction="annotate named entities"),
        _task(documentation="transcription guidelines"),
    ]


@pytest.fixture()
def engine():
    return FuzzySearchEngine(min_score=70)


def test_default_searches_all_fields(engine, tasks):
    # name
    assert [r.matched_field for r in engine.search_tasks(tasks, "segmentation")] == [
        "name"
    ]
    # instruction
    assert [r.matched_field for r in engine.search_tasks(tasks, "entities")] == [
        "instruction"
    ]
    # documentation
    assert [r.matched_field for r in engine.search_tasks(tasks, "transcription")] == [
        "documentation"
    ]


def test_search_single_field_only(engine, tasks):
    # Restricting to "name" ignores matches living in other fields.
    assert engine.search_tasks(tasks, "entities", search_fields=["name"]) == []
    assert engine.search_tasks(tasks, "transcription", search_fields=["name"]) == []

    results = engine.search_tasks(tasks, "segmentation", search_fields=["name"])
    assert [r.matched_field for r in results] == ["name"]


def test_search_multiple_fields(engine, tasks):
    fields = ["name", "documentation"]

    # A "documentation" hit is found ...
    assert [
        r.matched_field
        for r in engine.search_tasks(tasks, "transcription", search_fields=fields)
    ] == ["documentation"]
    # ... a "name" hit too ...
    assert [
        r.matched_field
        for r in engine.search_tasks(tasks, "segmentation", search_fields=fields)
    ] == ["name"]
    # ... but an "instruction" hit is excluded.
    assert engine.search_tasks(tasks, "entities", search_fields=fields) == []


def test_omitting_search_fields_preserves_default_behavior(engine, tasks):
    explicit = engine.search_tasks(
        tasks, "entities", search_fields=["name", "instruction", "documentation"]
    )
    default = engine.search_tasks(tasks, "entities")

    assert [r.matched_field for r in explicit] == [r.matched_field for r in default]


def test_invalid_field_names_are_rejected(engine, tasks):
    with pytest.raises(ValueError, match="Invalid search field"):
        engine.search_tasks(tasks, "segmentation", search_fields=["title"])

    # Rejection happens even when mixed with valid fields.
    with pytest.raises(ValueError):
        engine.search_tasks(tasks, "segmentation", search_fields=["name", "bogus"])


def test_empty_search_fields_searches_nothing(engine, tasks):
    assert engine.search_tasks(tasks, "segmentation", search_fields=[]) == []
