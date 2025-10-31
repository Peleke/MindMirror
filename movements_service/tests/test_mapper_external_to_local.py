import pytest

from movements.mappers.external_to_local import external_to_local_row


def test_external_to_local_row_minimal():
    ex = {"name": "Bench Press", "externalId": "exr_abc"}
    out = external_to_local_row(ex)
    assert out["name"] == "Bench Press"
    assert out["slug"].startswith("bench-press")
    assert out["externalId"] == "exr_abc"
    assert out["source"] == "exercise-db"


def test_external_to_local_row_rich_fields():
    ex = {
        "name": "Bench Press",
        "externalId": "exr_abc",
        "imageUrl": "img.png",
        "videoUrl": "vid.mp4",
        "equipments": ["Barbell"],
        "targetMuscles": ["Pectoralis Major"],
        "secondaryMuscles": ["Deltoid Anterior"],
        "instructions": ["Do it"],
        "overview": "Chest strength",
        "bodyParts": ["Chest"],
        "keywords": ["barbell", "chest"],
    }
    out = external_to_local_row(ex)
    assert out["gifUrl"] == "img.png"
    assert out["shortVideoUrl"] == "vid.mp4"
    assert out["equipment"] == ["Barbell"]
    assert out["primaryMuscles"] == ["Pectoralis Major"]
    assert out["secondaryMuscles"] == ["Deltoid Anterior"]
    assert out["instructions"] == ["Do it"]
    assert out["overview"] == "Chest strength"
    # tags aggregates bodyParts + keywords
    assert set(out["tags"]) == {"Chest", "barbell", "chest"} 