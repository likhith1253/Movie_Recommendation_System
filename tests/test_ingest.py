"""Pure-function tests for the ingestion helpers (no ChromaDB or model download needed)."""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import ingest_data  # noqa: E402

GENRES = "[{'id': 28, 'name': 'Action'}, {'id': 878, 'name': 'Science Fiction'}]"
CREW = "[{'job': 'Producer', 'name': 'P'}, {'job': 'Director', 'name': 'Jane Doe'}]"
CAST = "[" + ", ".join(f"{{'name': 'Actor {i}'}}" for i in range(8)) + "]"


def test_parse_json_column_extracts_names_and_survives_bad_rows():
    df = pd.DataFrame({"genres": [GENRES, "not json", None]})
    assert ingest_data.parse_json_column(df, "genres") == [["Action", "Science Fiction"], [], []]


def test_get_cast_keeps_top_five():
    cast = ingest_data.get_cast(pd.DataFrame({"cast": [CAST, "oops"]}), "cast")
    assert cast[0] == [f"Actor {i}" for i in range(5)]
    assert cast[1] == []


def test_get_director_defaults_to_unknown():
    df = pd.DataFrame({"crew": [CREW, "[{'job': 'Editor', 'name': 'E'}]", "broken"]})
    assert ingest_data.get_director(df, "crew") == ["Jane Doe", "Unknown", "Unknown"]


def test_create_rich_document_contains_all_fields():
    doc = ingest_data.create_rich_document(
        {"title_x": "Alien", "overview": "In space.", "genres_list": ["Horror", "Sci-Fi"],
         "cast_list": ["Sigourney Weaver"], "director": "Ridley Scott"})
    assert doc == ("Title: Alien. Overview: In space.. Genres: Horror, Sci-Fi. "
                   "Cast: Sigourney Weaver. Director: Ridley Scott.")


def test_ingest_reports_missing_csv(monkeypatch):
    monkeypatch.setattr(ingest_data, "MOVIES_CSV_FILE_PATH", "does_not_exist.csv")
    ok, count, err = ingest_data.ingest_data()
    assert not ok and count == 0 and "CSV files not found" in err
