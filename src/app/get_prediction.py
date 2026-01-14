from src.models.predict_model import predict_salary

predict_salary(
        job_title="Senior Python Developer",
        job_description="""
    We are looking for a Senior Python Developer with 5+ years experience.
    Skills required: Python, AWS, Machine Learning.
    Remote work possible.
    """,
        contract_type='permanent',
        contract_time='full_time',
        city='Berlin',
        country='Deutschland',
        latitude=52.52,
        longitude=13.405
    )

print(predict_salary)