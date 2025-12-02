from src.models.predict_model import predict_salary

def test_predict_salary_runs():
    result = predict_salary(
        job_title="Python Developer",
        job_description="Strong Python skills",
        city="Berlin",
        country="Deutschland"
    )
    assert isinstance(result, float)
