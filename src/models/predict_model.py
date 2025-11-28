import pandas as pd
import numpy as np
import joblib
import re

# ============================================================================
# FEATURE EXTRACTION (same as training)
# ============================================================================

def extract_simple_features(df):
    """Extract simple features from job descriptions"""
    df['desc_lower'] = df['job_description'].str.lower()
    
    # Keyword groups same as training
    keyword_groups = {
        'seniority': ['senior', 'lead', 'principal', 'staff', 'junior', 'entry', 
                      'experienced', 'expert', 'chief', 'head of', 'director', 'vp',
                      'leitend', 'erfahren', 'anfänger', 'einsteiger', 'fachlich', 
                      'leiter', 'direktor'],
        'languages': ['python', 'java', 'javascript', 'typescript', 'c\\+\\+', 'c#', 
                      'ruby', 'go', 'rust', 'scala', 'kotlin', 'swift', 'php', 'r'],
        'frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'spring', 
                       'node\\.js', 'express', '\\.net', 'tensorflow', 'pytorch', 'keras'],
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
                       'teamleitung', 'führung', 'kommunikation', 'projektleitung', 'architekt'],
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

    # Create has_* features
    for category, keywords in keyword_groups.items():
        pattern = r'\b(?:' + '|'.join(keywords) + r')\b'
        df[f'has_{category}'] = df['desc_lower'].str.contains(pattern, regex=True, na=False).astype(int)

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
# PREDICTION FUNCTIONS
# ============================================================================

def prepare_features(df, model_data):
    """Prepare features for prediction"""
    X = df.copy()

    # Fill missing numeric/categorical using training values
    for col, val in model_data['median_values'].items():
        if col in X.columns:
            X[col] = X[col].fillna(val)
    for col, val in model_data['mode_values'].items():
        if col in X.columns:
            X[col] = X[col].fillna(val)
    
    # Encode categorical variables
    cat_cols = ['contract_type', 'contract_time', 'city', 'country']
    X = pd.get_dummies(X, columns=cat_cols)

    # Encode title
    le_title = model_data['label_encoder']
    X['title_encoded'] = X['title'].apply(
        lambda x: le_title.transform([str(x)])[0] if str(x) in le_title.classes_ else -1
    )
    X = X.drop('title', axis=1)

    # Align columns with training
    for col in model_data['feature_columns']:
        if col not in X.columns:
            X[col] = 0
    X = X[model_data['feature_columns']]
    return X

def predict_salary(job_title, job_description, contract_type='permanent', 
                   contract_time='full_time', city='Berlin', country='Deutschland',
                   latitude=None, longitude=None):
    """Predict salary for a single job"""
    model_data = joblib.load('salary_model.pkl')
    model = model_data['model']
    train_median_values = model_data['median_values']
    
    # Use median values from training if latitude/longitude not provided
    if latitude is None:
        latitude = train_median_values.get('latitude', 52.52)  # fallback default
    if longitude is None:
        longitude = train_median_values.get('longitude', 13.405)
    
    # Build dataframe
    df = pd.DataFrame([{
        'title': job_title,
        'job_description': job_description,
        'contract_type': contract_type,
        'contract_time': contract_time,
        'city': city,
        'country': country,
        'latitude': latitude,
        'longitude': longitude
    }])
    
    df = extract_simple_features(df)
    X = prepare_features(df, model_data)
    prediction = model.predict(X)[0]
    return prediction

def predict_batch(jobs_df):
    """Predict salaries for multiple jobs"""
    model_data = joblib.load('salary_model.pkl')
    model = model_data['model']

    if 'latitude' not in jobs_df or jobs_df['latitude'].isna().any():
        jobs_df['latitude'] = jobs_df['latitude'].fillna(train_median_values.get('latitude', 52.52))
    
    if 'longitude' not in jobs_df or jobs_df['longitude'].isna().any():
        jobs_df['longitude'] = jobs_df['longitude'].fillna(train_median_values.get('longitude', 13.405))

    df = extract_simple_features(jobs_df.copy())
    X = prepare_features(df, model_data)
    predictions = model.predict(X)
    return predictions

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("SINGLE PREDICTION EXAMPLE")
    print("="*70)

    job_title = "Senior Python Developer"
    job_description = """
    We are looking for a Senior Python Developer with 5+ years experience.
    Skills required: Python, AWS, Machine Learning.
    Remote work possible.
    """

    predicted_salary = predict_salary(
        job_title=job_title,
        job_description=job_description,
        contract_type='permanent',
        contract_time='full_time',
        city='Berlin',
        country='Deutschland',
        latitude=52.52,
        longitude=13.405
    )

    print(f"\nJob Title: {job_title}")
    print(f"Location: Berlin, Deutschland")
    print(f"Predicted Salary: €{predicted_salary:,.2f}")

    # --------------------------
    print("\n" + "="*70)
    print("BATCH PREDICTION EXAMPLE")
    print("="*70)

    jobs = pd.DataFrame([
        {
            'title': 'Junior Data Analyst',
            'job_description': 'Entry level. Python and SQL required.',
            'contract_type': 'permanent',
            'contract_time': 'full_time',
            'city': 'Munich',
            'country': 'Deutschland',
            'latitude': 48.1351,
            'longitude': 11.5820
        },
        {
            'title': 'Lead Java Developer',
            'job_description': 'Leading team. Java, AWS, 8+ years experience.',
            'contract_type': 'contract',
            'contract_time': 'full_time',
            'city': 'Frankfurt',
            'country': 'Deutschland',
            'latitude': 50.1109,
            'longitude': 8.6821
        }
    ])

    predictions = predict_batch(jobs)

    for i, pred in enumerate(predictions):
        print(f"\n{jobs.iloc[i]['title']} ({jobs.iloc[i]['city']})")
        print(f"  Predicted Salary: €{pred:,.2f}")


# How to se it to make predictions:

#    from predict_model import predict_salary
   
#    salary = predict_salary(
#        "Senior Python Developer",
#        "5+ years Python, AWS, Machine Learning"
#    )
#    print(f"Predicted: €{salary:,.2f}")