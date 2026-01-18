"""
Streamlit app for salary prediction.
Main entry point for the Streamlit application.
"""

import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Page config
st.set_page_config(
    page_title="Salary Predictor",
    page_icon="💰",
    layout="wide"
)

st.title("💰 IT Jobs Salary Predictor")
st.markdown("Predict your salary based on job information")

# API endpoint
API_URL = os.getenv("API_URL", "http://api:8000")

st.sidebar.header("About")
st.sidebar.info(
    "This app predicts salaries based on IT job information using machine learning (Germany only at the moment). "
    "Enter job details and get an instant prediction!"
)

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Job Information")
    
    job_title = st.text_input(
        "Job Title",
        placeholder="e.g., Senior Python Developer",
        value=""
    )
    
    job_description = st.text_area(
        "Job Description",
        placeholder="Paste the full job description here...",
        height=150
    )
    
    city = st.text_input(
        "City",
        placeholder="e.g., Berlin",
        value=""
    )

with col2:
    st.subheader("Job Details")
    
    country = st.text_input(
        "Country",
        placeholder="e.g., Deutschland",
        value="Deutschland"
    )
    
    contract_type = st.selectbox(
        "Contract Type",
        ["permanent", "contract", "temporary", "apprenticeship"],
        index=0
    )
    
    contract_time = st.selectbox(
        "Contract Time",
        ["full_time", "part_time", "temporary", "freelance"],
        index=0
    )

# Prediction button
if st.button("🔮 Predict Salary", use_container_width=True, type="primary"):
    if not job_title or not job_description or not city:
        st.error("Please fill in all required fields: Job Title, Description, and City")
    else:
        with st.spinner("Predicting salary..."):
            try:
                # Call API
                params = {
                    "job_title": job_title,
                    "job_description": job_description,
                    "city": city,
                    "country": country,
                    "contract_time": contract_time,
                    "contract_type": contract_type
                }
                
                response = requests.get(
                    f"{API_URL}/data/predictions",
                    params=params,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    salary = data.get("Predicted Salary")
                    
                    if salary is None:
                        st.error("❌ No salary prediction received from API")
                    else:
                        st.success("✅ Prediction complete!")
                        
                        # Display result
                        col_result1, col_result2 = st.columns([1, 1])
                        with col_result1:
                            st.metric(
                                label="Predicted Annual Salary",
                                value=f"€{salary:,.0f}",
                                delta=None
                            )
                        
                        with col_result2:
                            st.info(
                                f"""
                                **Job Details:**
                                - Title: {job_title}
                                - Location: {city}
                                - Type: {contract_type}
                                - Time: {contract_time}
                                """
                            )
                        
                        # Additional info
                        st.markdown("---")
                        st.subheader("📊 Insights")
                        st.markdown(
                            f"Based on {len(job_description)} characters of job description, "
                            f"the model predicts this position in {city} will offer approximately **€{salary:,.0f}** annually."
                        )
                
                else:
                    st.error(f"❌ API Error: {response.status_code}")
                    try:
                        st.write(response.json())
                    except:
                        st.write(response.text)
                    
            except requests.exceptions.ConnectionError:
                st.error(
                    "❌ Cannot connect to API. "
                    "Make sure the FastAPI server is running on http://api:8000"
                )
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
    <small>DST DE 2025/2026 | Data from Adzuna Job Market API</small>
    </div>
    """,
    unsafe_allow_html=True
)
