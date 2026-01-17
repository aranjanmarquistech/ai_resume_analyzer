import pytest

from resume_analyzer.ml.role_predictor import RolePredictor


def test_role_predictor_missing_model():
    with pytest.raises(FileNotFoundError):
        RolePredictor("models/nope.joblib")
