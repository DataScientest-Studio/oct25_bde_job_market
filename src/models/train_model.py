import pandas as pd
import numpy as np
import joblib
import re
import warnings
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

warnings.filterwarnings('ignore')

"""
Train the salary prediction model and save it for later use.
Run this script to retrain the model when there is new data.
"""
### Configuration
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = 'adzuna'
COLLECTION_NAME = 'jobs'
PG_CONN = os.getenv("PG_CONN")
OUTPUT_MODEL = Path(__file__).parent.parent.parent / 'models/salary_model.pkl'
TEST_SIZE = 0.2
RANDOM_STATE = 42

### Feature engineering

def extract_simple_features(df):
    """Extract simple features from job descriptions"""
    df['desc_lower'] = df['job_description'].str.lower()
    

# Keyword groups
    keyword_groups = {
        'seniority': ['senior', 'lead', 'principal', 'staff', 'junior', 'entry', 
                    'experienced', 'expert', 'chief', 'head of', 'director', 'vp',
                    'leitend', 'erfahren', 'anfänger', 'einsteiger', 'fachlich', 
                    'leiter', 'direktor'],

        'languages': ['python', 'java', 'javascript', 'typescript', 'c\\+\\+', 'c#', 
                    'ruby', 'go', 'rust', 'scala', 'kotlin', 'swift', 'php', 'r'],

        'frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'spring', 
                    'node\\.js', 'express', '\\.net', 'tensorflow', 'pytorch', 
                    'keras'],

        'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'redis', 
                    'elasticsearch', 'cassandra', 'dynamodb', 'neo4j'],

        'cloud': ['aws', 'azure', 'gcp', 'cloud', 'docker', 'kubernetes', 'k8s',
                'terraform', 'ansible', 'jenkins', 'gitlab', 'ci/cd', 'devops'],

        'data_ai': ['machine learning', 'deep learning', 'ai', 'data science', 
                    'analytics', 'big data', 'etl', 'data warehouse', 'spark', 
                    'hadoop', 'tableau', 'power bi', 'künstliche intelligenz',
                    'datenwissenschaft', 'datenanalyse', 'datenlager'],

        'methodologies': ['agile', 'scrum', 'kanban', 'waterfall', 'test-driven',
                        'microservices', 'rest', 'api', 'graphql'],

        'management': ['team lead', 'leadership', 'management', 'communication',
                    'project management', 'stakeholder', 'mentor', 'architect',
                    'teamleitung', 'führung', 'kommunikation', 'projektleitung', 
                    'architekt'],

        'education': ['bachelor', 'master', 'phd', 'doctorate', 'degree', 
                    'university', 'certification', 'certified',
                    'bachelorabschluss', 'masterabschluss', 'doktor', 'abschluss', 
                    'universität', 'zertifizierung', 'zertifiziert'],

        'experience': ['years of experience', 'year experience', 'experience in',
                    'proven track record', 'extensive experience', 
                    'jahre erfahrung', 'erfahrung in', 
                    'nachweisliche erfahrung', 'umfangreiche erfahrung'],

        'domains': ['finance', 'fintech', 'healthcare', 'e-commerce', 'automotive',
                    'telecommunications', 'gaming', 'security', 'blockchain', 'iot',
                    'finanzen', 'gesundheitswesen', 'handel', 'automobil', 
                    'telekommunikation', 'sicherheit', 'internet der dinge'],

        'company_type': ['startup', 'enterprise', 'corporation', 'sme', 'scale-up',
                        'fortune 500', 'multinational'],

        'benefits': ['remote', 'flexible', 'home office', 'relocation', 'visa',
                    'bonus', 'stock options', 'equity', '30 days vacation',
                    'flexibel', 'heimarbeit', 'umzug', 'urlaub', 'aktienoptionen']
    }

    # Create columns
    for category, keywords in keyword_groups.items():
        # Build pattern e.g. r'\b(senior|lead|principal)\b'
        pattern = r'\b(?:' + '|'.join(keywords) + r')\b'

        df[f'has_{category}'] = (
            df['desc_lower'].str.contains(pattern, regex=True, na=False).astype(int)
        )

    
    # Extract years of experience
    def extract_years(text):
        if pd.isna(text):
            return 0
        matches = re.findall(r'(\d+)\+?\s*(?:years?|jahr)', text.lower())
        return max([int(m) for m in matches]) if matches else 0
    
    df['years_required'] = df['job_description'].apply(extract_years)
    
    # Text length features
    df['desc_length'] = df['job_description'].str.len()
    df['title_length'] = df['title'].str.len()
    
    return df

### Model training

def train_salary_model():
    """Main function to train and save the model"""
    print("="*70)
    print("TRAINING SALARY PREDICTION MODEL")
    print("="*70)
    
    # 1. Load data
    print("\n[1/5] Loading data...")

    ## Mongo

    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    cursor = collection.find( # extract only job id and description from mongo
        {},
        {"_id": 0, "id": 1, "description": 1}
    )

    df_mongo = pd.DataFrame(list(cursor))
    df_mongo = df_mongo.rename(columns={"id": "job_id", "description": "job_description"})
    df_mongo['job_id'] = df_mongo['job_id'].astype(int)

    ## Postgres
    engine = create_engine(os.getenv("PG_CONN"))

    jobs = pd.read_sql("SELECT * FROM job", engine)
    locs = pd.read_sql("SELECT * FROM location", engine)
    
    ## Merge the two
    df = jobs.merge(locs)
    df = df.merge(df_mongo)
    print(f"   Loaded {len(df)} records")
    
    # 2. Clean data
    print("\n[2/5] Cleaning data...")
    df['job_description'] = df['job_description'].fillna('')

    # Remove rows with missing salary
    df = df.dropna(subset=['salary_min', 'salary_max'])
    df = df[df['salary_max'] >= df['salary_min']]

    # Create target variable
    df['salary_avg'] = (df['salary_min'] + df['salary_max']) / 2

    # Remove hourly salaries
    df = df[df['salary_min'] > 100]

    df = df.reset_index(drop=True)

    print(f"After cleaning: {len(df)} records")
    
    # 3. Feature engineering
    print("\n[3/5] Engineering features...")

    df = extract_simple_features(df)
    
    # 4. Prepare features
    print("\n[4/5] Preparing features...")
    y = df['salary_avg']

    # Automatically select all columns beginning with "has_"
    keyword_features = [col for col in df.columns if col.startswith('has_')]

    # Your existing numeric features
    numeric_features = ['latitude', 'longitude', 
                        'years_required', 'desc_length', 'title_length']

    categorical_columns = ['title', 'contract_type', 'contract_time', 'city', 'country']

    # Combine everything
    X = df[numeric_features + keyword_features + categorical_columns]

    # Separation of training and test data sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    # Reset index (important for proper handling)
    X_train = X_train.reset_index(drop=True)
    X_test = X_test.reset_index(drop=True)
    y_train = y_train.reset_index(drop=True)
    y_test = y_test.reset_index(drop=True)

    # Handling missing values - replacement (AFTER train/test split)
    print("\nHandling missing values in train/test sets...")

    mode_values = {col: X_train[col].mode()[0] for col in categorical_columns}
    median_values = {col: X_train[col].median() for col in numeric_features}

    # Numerical columns - fill with median from training set
    for col in numeric_features:
        X_train[col] = X_train[col].fillna(median_values[col])
        X_test[col] = X_test[col].fillna(median_values[col])

    # Categorical columns - fill with mode from training set
    for col in categorical_columns:
        X_train[col] = X_train[col].fillna(mode_values[col])
        X_test[col] = X_test[col].fillna(mode_values[col])

    # Encoding text variables using get_dummies (like in course example)
    print("\nEncoding categorical variables...")

    # Use get_dummies for categorical variables
    X_train = pd.get_dummies(X_train, columns=['contract_type', 'contract_time', 'city', 'country'])
    X_test = pd.get_dummies(X_test, columns=['contract_type', 'contract_time', 'city', 'country'])

    # Handle title separately (too many unique values - use label encoding)
    le_title = LabelEncoder()
    X_train['title_encoded'] = le_title.fit_transform(X_train['title'].astype(str))
    X_test['title_encoded'] = X_test['title'].apply(
        lambda x: le_title.transform([x])[0] if x in le_title.classes_ else -1
    )

    # Drop original title columns
    X_train = X_train.drop(['title'], axis=1, errors='ignore')
    X_test = X_test.drop(['title'], axis=1, errors='ignore')

    # Align train and test columns (important when using get_dummies)
    X_train, X_test = X_train.align(X_test, join='left', axis=1, fill_value=0)

    print(f"\nTraining set: {X_train.shape}")
    print(f"Test set: {X_test.shape}")
    
    # 5. Train model
    print("\n[5/5] Training Random Forest model...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred_test = model.predict(X_test)
    
    # Evaluate model
    mae = mean_absolute_error(y_test, y_pred_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    r2 = r2_score(y_test, y_pred_test)
    
    print("\n" + "="*70)
    print("MODEL PERFORMANCE")
    print("="*70)
    print(f"MAE:  €{mae:,.2f}")
    print(f"RMSE: €{rmse:,.2f}")
    print(f"R²:   {r2:.4f}")
    
    # Feature importance
    print("\n" + "="*70)
    print("TOP 15 MOST IMPORTANT FEATURES")
    print("="*70)
    feature_importance = pd.DataFrame({
        'Feature': X_train.columns,
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=False)
    print(feature_importance.head(15).to_string(index=False))
    
    # Save model using joblib
    print(f"\nSaving model to {OUTPUT_MODEL}...")
    
    joblib.dump({
        'model': model,
        'feature_columns': X_train.columns.tolist(),
        'label_encoder': le_title,
        'mode_values': mode_values,
        'median_values': median_values,
        'metrics': {'mae': mae, 'rmse': rmse, 'r2': r2}
    }, OUTPUT_MODEL)
    
    print("\n" + "="*70)
    print("TRAINING COMPLETE!")
    print("="*70)
    
    return model

if __name__ == "__main__":
    train_salary_model()