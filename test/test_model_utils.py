# -*- coding: utf-8 -*-
import pytest
import pandas as pd
from model_utils import make_inference, load_model
from sklearn.pipeline import Pipeline
from pickle import dumps


@pytest.fixture
def create_data() -> dict[str, int | float]:
    return {
        "longitude": -122.23,
        "latitude": 37.88,
        "housing_median_age": 41.0,
        "total_rooms": 880.0,
        "total_bedrooms": 129.0,
        "population": 322.0,
        "households": 126.0,
        "median_income": 8.3252
    }


def test_make_inference(monkeypatch, create_data):
    def mock_get_predictions(_, data: pd.DataFrame) -> list[list[float]]:
        assert create_data == {
            key: value[0] for key, value in data.to_dict("list").items()
        }
        return [452600.0]

    in_model = Pipeline([])
    monkeypatch.setattr(Pipeline, "predict", mock_get_predictions)

    result = make_inference(in_model, create_data)
    assert result == {"median_house_value": 452600.0}


@pytest.fixture()
def filepath_and_data(tmpdir):
    p = tmpdir.mkdir("datadir").join("fakedmodel.pkl")
    example: str = "Test message!"
    p.write_binary(dumps(example))
    return str(p), example


def test_load_model(filepath_and_data):
    assert filepath_and_data[1] == load_model(filepath_and_data[0])
