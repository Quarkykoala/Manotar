import pytest
import os
from app import (
    generate_access_code, 
    generate_trend, 
    generate_risk_level, 
    generate_mental_health_score,
    model
)

def test_generate_access_code():
    code = generate_access_code()
    assert len(code) == 8
    has_letter = any(c.isalpha() for c in code)
    has_number = any(c.isdigit() for c in code)
    assert has_letter and has_number, "Code should contain both letters and numbers"
    another_code = generate_access_code()
    assert code != another_code, "Generated codes should be unique"

def test_generate_trend():
    trend = generate_trend()
    assert trend.startswith(('+', '-'))
    assert trend.endswith('%')
    value = int(trend[1:-1])
    assert 1 <= value <= 20

def test_generate_risk_level():
    risk_level = generate_risk_level()
    assert risk_level in ["Low", "Medium", "High"]

def test_generate_mental_health_score():
    score = generate_mental_health_score()
    assert isinstance(score, float)
    assert 5.0 <= score <= 9.0

@pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="No API key provided")
def test_gemini_model():
    assert model is not None
    try:
        response = model.generate_content("Hello")
        assert response is not None
    except Exception as e:
        pytest.skip(f"Skipping model test due to API error: {str(e)}")