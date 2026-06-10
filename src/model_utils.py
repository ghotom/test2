# -*- coding: utf-8 -*-
import pandas as pd
from sklearn.pipeline import Pipeline
from pickle import load


def make_inference(in_model: Pipeline, in_data: dict) -> dict[str, float]:
    prediction = in_model.predict(pd.DataFrame(in_data, index=[0]))[0]
    return {"median_house_value": round(prediction, 3)}


def load_model(path: str) -> Pipeline:
    """Return the model being read which stored on the path."""
    with open(path, "rb") as file:
        model: Pipeline = load(file)

    return model
