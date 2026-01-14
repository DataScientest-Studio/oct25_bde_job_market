import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import re

# ============================================================================
# CONFIGURATION
# ============================================================================

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = 'adzuna'
COLLECTION_NAME = 'jobs'
PG_CONN = os.getenv("PG_CONN")

# ============================================================================
# SIMPLE FEATURE EXTRACTION
# ============================================================================

def extract_simple_features(df):
    """Extract simple features from job descriptions"""
    df['desc_lower'] = df['job_description'].str.lower()
    
    # Count important keywords
    # df['has_senior'] = df['desc_lower'].str.contains('senior|lead|principal', na=False).astype(int)
    # df['has_python'] = df['desc_lower'].str.contains('python', na=False).astype(int)
    # df['has_java'] = df['desc_lower'].str.contains('java', na=False).astype(int)
    # df['has_aws'] = df['desc_lower'].str.contains('aws|azure|cloud', na=False).astype(int)
    # df['has_ml'] = df['desc_lower'].str.contains('machine learning|ai|data science', na=False).astype(int)
    # df['has_remote'] = df['desc_lower'].str.contains('remote|home office', na=False).astype(int)


# Your keyword groups
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

# ============================================================================
# LOAD AND PREPARE DATA
# ============================================================================

print("Loading data...")
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
# com = pd.read_sql("SELECT * FROM company", engine)
# cat = pd.read_sql("SELECT * FROM category", engine)
locs = pd.read_sql("SELECT * FROM location", engine)

## Merge the two
df = jobs.merge(locs)
df = df.merge(df_mongo)
print(f"   Loaded {len(df)} records")

# ============================================================================
# CLEAN DATA
# ============================================================================

print("\nCleaning data...")

# Handle missing values
df['job_description'] = df['job_description'].fillna('')

# Remove rows with missing salary
df = df.dropna(subset=['salary_min', 'salary_max'])
df = df[df['salary_max'] >= df['salary_min']]

# Create target variable
df['salary_avg'] = (df['salary_min'] + df['salary_max']) / 2

# Remove hourly salaries
df = df[df['salary_min'] > 100]

print(f"After cleaning: {len(df)} records")

# ============================================================================
# FEATURE ENGINEERING
# ============================================================================

print("\nExtracting features...")
df = extract_simple_features(df)

# ============================================================================
# PREPARE FOR MODELING
# ============================================================================

# Separation of target and explanatory variables
y = df['salary_avg']

# Automatically select all columns beginning with "has_"
keyword_features = [col for col in df.columns if col.startswith('has_')]

# Your existing numeric features
numeric_features = ['years_required', 'desc_length', 'title_length']

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

# Numerical columns - fill with median from training set
numerical_columns = ['desc_length', 'years_required']
for col in numerical_columns:
    X_train[col] = X_train[col].fillna(X_train[col].median())
    X_test[col] = X_test[col].fillna(X_train[col].median())

# Categorical columns - fill with mode from training set
for col in categorical_columns:
    mode_value = X_train[col].mode()[0] if len(X_train[col].mode()) > 0 else 'Unknown'
    X_train[col] = X_train[col].fillna(mode_value)
    X_test[col] = X_test[col].fillna(mode_value)

# Encoding text variables using get_dummies (like in course example)
print("\nEncoding categorical variables...")

# Use get_dummies for categorical variables
X_train = pd.get_dummies(X_train, columns=['contract_type', 'contract_time', 'city', 'country'])
X_test = pd.get_dummies(X_test, columns=['contract_type', 'contract_time', 'city', 'country'])

# Handle title separately (too many unique values - use label encoding)
from sklearn.preprocessing import LabelEncoder
le_title = LabelEncoder()
X_train['title_encoded'] = le_title.fit_transform(X_train['title'].astype(str))
X_test['title_encoded'] = X_test['title'].apply(
    lambda x: le_title.transform([str(x)])[0] if str(x) in le_title.classes_ else -1
)

# Drop original categorical columns
X_train = X_train.drop(['title', 'contract_type', 'contract_time', 'city', 'country'], axis=1, errors='ignore')
X_test = X_test.drop(['title', 'contract_type', 'contract_time', 'city', 'country'], axis=1, errors='ignore')

# Align train and test columns (important when using get_dummies)
X_train, X_test = X_train.align(X_test, join='left', axis=1, fill_value=0)

# Scaling features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"\nTraining set: {X_train.shape}")
print(f"Test set: {X_test.shape}")

# ============================================================================
# TEST DIFFERENT MODELS
# ============================================================================

print("\n" + "="*70)
print("TESTING DIFFERENT MODELS")
print("="*70)

models = {
    'Linear Regression': LinearRegression(),
    'Ridge Regression': Ridge(alpha=1.0),
    'Decision Tree': DecisionTreeRegressor(max_depth=10, random_state=42),
    'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42),
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
}

results = []

for name, model in models.items():
    print(f"\nTraining {name}...")
    
    # Train model
    if name in ['Linear Regression', 'Ridge Regression']:
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
    else:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
    
    # Calculate metrics
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    results.append({
        'Model': name,
        'MAE': mae,
        'RMSE': rmse,
        'R²': r2
    })
    
    print(f"  MAE:  €{mae:,.2f}")
    print(f"  RMSE: €{rmse:,.2f}")
    print(f"  R²:   {r2:.4f}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*70)
print("MODEL COMPARISON SUMMARY")
print("="*70)

results_df = pd.DataFrame(results)
results_df = results_df.sort_values('R²', ascending=False)
print(results_df.to_string(index=False))

best_model = results_df.iloc[0]['Model']
print(f"\n🏆 Best Model: {best_model}")
print(f"   R² Score: {results_df.iloc[0]['R²']:.4f}")
print(f"   MAE: €{results_df.iloc[0]['MAE']:,.2f}")

print("\n" + "="*70)
print("RECOMMENDATION:")
print("="*70)
print("Random Forest is recommended because:")
print("  ✓ Good balance between accuracy and interpretability")
print("  ✓ Handles non-linear relationships well")
print("  ✓ Less prone to overfitting than single trees")
print("  ✓ Provides feature importance")
print("  ✓ No need for feature scaling")