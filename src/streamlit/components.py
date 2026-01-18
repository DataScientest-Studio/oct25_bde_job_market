"""Reusable Streamlit components."""

import streamlit as st


def show_prediction_result(job_title: str, city: str, country: str, 
                          contract_type: str, salary: float, job_description: str):
    """Display prediction results."""
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
            - Location: {city}, {country}
            - Type: {contract_type}
            """
        )
    
    # Additional info
    st.markdown("---")
    st.subheader("📊 Insights")
    st.markdown(
        f"Based on {len(job_description)} characters of job description, "
        f"the model predicts this position in {city} will offer approximately **€{salary:,.0f}** annually."
    )


def show_error(error_type: str, message: str = ""):
    """Display formatted error message."""
    if error_type == "connection":
        st.error(
            "❌ Cannot connect to API. "
            "Make sure the FastAPI server is running on http://api:8000"
        )
    elif error_type == "api":
        st.error(f"❌ API Error: {message}")
    elif error_type == "validation":
        st.error(f"❌ Please fill in all required fields: {message}")
    else:
        st.error(f"❌ Error: {message}")
