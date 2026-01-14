import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pydantic
from pymongo import MongoClient

load_dotenv()
engine = create_engine(os.getenv("PG_CONN"))

# def get_jobs(indicators:str):
#     """
#     Combines data from SQL and NoSQL Databases and returns
#     """
#     #retrieve SQL
#     if "description" in indicators:
#         #retrieve NoSQl
# # PG_CONN = os.getenv("PG_CONN")

# engine = create_engine(os.getenv("PG_CONN"))

def retrieve_sql(columns = list[str]):
    df_main = pd.read_sql("""
                          SELECT * 
                          FROM job 
                          LEFT JOIN company USING(company_id)
                          LEFT JOIN location USING(location_id)
                          LEFT JOIN category USING(category_id)
                          """, engine)

    job_postings = df_main[columns]
    return job_postings

retrieve_sql(columns=["job_id", "longitude", "company_name"])

# MONGO_URI = os.getenv("MONGO_URI")
# DATABASE_NAME = 'admin'
# COLLECTION_NAME = 'jobs'
# def retrieve_mongo():
#     # client = MongoClient(
#     # host="127.0.0.1",
#     # port = 27017,
#     # username = "datascientest",
#     # password = "dst123"
#     # )
#     client = MongoClient(MONGO_URI)
#     db = client[DATABASE_NAME]
#     collection = db[COLLECTION_NAME]
#     client.list_database_names()
#     print(collection.find_one())

#     cursor = collection.find( # extract only job id and description from mongo
#         {},
#         {"_id": 0, "id": 1, "description": 1}
#     )

#     df_mongo = pd.DataFrame(list(cursor))
#     df_mongo = df_mongo.rename(columns={"id": "job_id", "description": "job_description"})
#     df_mongo['job_id'] = df_mongo['job_id'].astype(int)
#     return df_mongo

# retrieve_mongo()



# ============================================================================
# CLEAN DATA
# ============================================================================

print("\nCleaning data...")

# Handle missing values
df['job_description'] = df['job_description'].fillna('')
# df['latitude'] = df['latitude'].fillna(df['latitude'].median())
# df['longitude'] = df['longitude'].fillna(df['longitude'].median())
# df['city'] = df['city'].fillna('Unknown')
# df['country'] = df['country'].fillna('Deutschland')

# Remove rows with missing salary
df = df.dropna(subset=['salary_min', 'salary_max'])
df = df[df['salary_max'] >= df['salary_min']]

# Create target variable
df['salary_avg'] = (df['salary_min'] + df['salary_max']) / 2

# Remove hourly salaries
df = df[df['salary_min'] > 100]

print(f"After cleaning: {len(df)} records")
predict_salary

    # how import SQL and MongoDB?
