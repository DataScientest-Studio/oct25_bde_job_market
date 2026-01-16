from __future__ import annotations

import csv
import json
import os
import statistics
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


PROJECT_ROOT = Path(__file__).resolve().parent

# Robust: bevorzugt ENV, sonst ../data (dein Setup), sonst ./data (Fallback)
DATA_DIR = Path(os.environ.get("JOB_MARKET_DATA_DIR", "")).expanduser().resolve() if os.environ.get("JOB_MARKET_DATA_DIR") else None
CANDIDATE_DIRS = [d for d in [DATA_DIR, PROJECT_ROOT.parent / "data", PROJECT_ROOT / "data"] if d is not None]

CLEAN_CSV_NAME = "jobs_clean.csv"


def _find_data_file(filename: str) -> Optional[Path]:
    for d in CANDIDATE_DIRS:
        p = d / filename
        if p.exists():
            return p
    return None


def _read_clean_csv(path: Path, limit: int = 5000) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for i, row in enumerate(r):
            rows.append(row)
            if i + 1 >= limit:
                break
    return rows


def _to_float(v: Optional[str]) -> Optional[float]:
    try:
        if v is None:
            return None
        v = str(v).strip()
        if not v:
            return None
        return float(v)
    except Exception:
        return None


def _salary_mid(row: Dict[str, Any]) -> Optional[float]:
    smin = _to_float(row.get("salary_min"))
    smax = _to_float(row.get("salary_max"))
    if smin is None and smax is None:
        return None
    if smin is None:
        return smax
    if smax is None:
        return smin
    return (smin + smax) / 2.0


def _currency_eur(v: float) -> str:
    # ohne locale-Abhängigkeiten, aber sauber formatiert
    return f"€{v:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _top_titles(rows: List[Dict[str, Any]], n: int = 3) -> List[str]:
    titles = [r.get("title") for r in rows if (r.get("title") or "").strip()]
    if not titles:
        return []
    c = Counter(titles)
    return [t for t, _ in c.most_common(n)]


def _call_prediction_api(url: str, payload: Dict[str, Any], timeout_s: int = 10) -> Tuple[Optional[float], str]:
    """
    Erwartet: JSON Response mit z.B. {"predicted_salary": 72500}
    Ist absichtlich tolerant (verschiedene Keys).
    """
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url=url, data=data, method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            obj = json.loads(body)

        # tolerant: mehrere mögliche key-namen
        for k in ["predicted_salary", "salary", "prediction", "y_pred"]:
            if k in obj:
                val = _to_float(str(obj[k]))
                if val is not None:
                    return val, "ok"

        return None, "API antwortete, aber kein Salary-Feld gefunden."
    except urllib.error.HTTPError as e:
        return None, f"API HTTP-Fehler: {e.code}"
    except urllib.error.URLError as e:
        return None, f"API nicht erreichbar: {e.reason}"
    except json.JSONDecodeError:
        return None, "API Antwort war kein gültiges JSON."
    except Exception as e:
        return None, f"API Fehler: {e}"


def _try_import_streamlit():
    try:
        import streamlit as st  # type: ignore
        return st
    except Exception:
        return None


def _render_streamlit_app(st) -> None:
    st.set_page_config(page_title="Job Market", layout="wide")

    # Minimal-CSS für „professioneller“, ohne Theme/Host-Anpassung
    st.markdown(
        """
        <style>
          .jm-card {
            border: 1px solid rgba(49, 51, 63, 0.2);
            border-radius: 10px;
            padding: 14px 16px;
            background: rgba(255,255,255,0.02);
          }
          .jm-label { font-size: 0.9rem; opacity: 0.75; margin-bottom: 4px; }
          .jm-big { font-size: 2.2rem; font-weight: 700; margin: 0; }
          .jm-sub { font-size: 1.0rem; opacity: 0.75; margin-top: 6px; }
          div.stButton > button {
            background: #d62828 !important;
            border: 1px solid #d62828 !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 0.55rem 1.05rem !important;
            border-radius: 8px !important;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Job Market – Artefakt-basiertes UI")
    st.caption("Dieses UI konsumiert ausschließlich die Artefakte (jobs_clean.csv). Optional kann eine externe Prediction-API angebunden werden.")

    clean_path = _find_data_file(CLEAN_CSV_NAME)
    if not clean_path:
        st.error("jobs_clean.csv wurde nicht gefunden.")
        st.info(
            "Erwartete Pfade:\n"
            f"- {PROJECT_ROOT.parent / 'data' / CLEAN_CSV_NAME}\n"
            f"- {PROJECT_ROOT / 'data' / CLEAN_CSV_NAME}\n\n"
            "Tipp: Du kannst den Pfad auch via ENV JOB_MARKET_DATA_DIR setzen."
        )
        return

    rows = _read_clean_csv(clean_path, limit=100000)
    if not rows:
        st.warning("jobs_clean.csv ist leer oder konnte nicht gelesen werden.")
        return

    left, right = st.columns([1.35, 1.0], gap="large")

    # ---------------- LEFT: INPUT FORM ----------------
    with left:
        st.subheader("Job Details Input")

        with st.form("job_input_form", clear_on_submit=False):
            job_title = st.text_input("Job Title", value="Senior Python Developer")
            job_description = st.text_area(
                "Job Description",
                value="We are looking for a Senior Python Developer with 5+ years experience.\nSkills required: Python, AWS, Machine Learning.\nRemote work possible.",
                height=120,
            )

            c1, c2 = st.columns(2)
            with c1:
                contract_type = st.selectbox("Contract Type", ["Permanent", "Contract", "Internship", "Temporary"], index=0)
            with c2:
                contract_time = st.selectbox("Contract Time", ["Full Time", "Part Time"], index=0)

            st.markdown("**Location**")
            l1, l2 = st.columns([1.0, 1.0])
            with l1:
                city = st.text_input("City", value="Berlin")
            with l2:
                country = st.selectbox("Country", ["Deutschland", "Austria", "Switzerland", "Other"], index=0)

            g1, g2 = st.columns(2)
            with g1:
                lat = st.text_input("Latitude", value="52.52")
            with g2:
                lon = st.text_input("Longitude", value="13.405")

            predict_clicked = st.form_submit_button("Predict Salary")

        st.markdown("")

        predicted_salary: Optional[float] = None
        pred_msg: Optional[str] = None

        if predict_clicked:
            api_url = os.environ.get("PREDICTION_API_URL", "").strip()
            if not api_url:
                pred_msg = "Prediction ist nicht konfiguriert (ENV PREDICTION_API_URL fehlt)."
            else:
                payload = {
                    "job_title": job_title,
                    "job_description": job_description,
                    "contract_type": contract_type,
                    "contract_time": contract_time,
                    "city": city,
                    "country": country,
                    "latitude": lat,
                    "longitude": lon,
                }
                predicted_salary, status = _call_prediction_api(api_url, payload)
                if predicted_salary is None:
                    pred_msg = status

        # Predicted salary card
        st.markdown('<div class="jm-card">', unsafe_allow_html=True)
        st.markdown('<div class="jm-label">Predicted Salary:</div>', unsafe_allow_html=True)

        if predicted_salary is not None:
            st.markdown(f'<p class="jm-big">{_currency_eur(predicted_salary)} <span class="jm-sub">per year</span></p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="jm-big">—</p>', unsafe_allow_html=True)
            if pred_msg:
                st.warning(pred_msg)
            else:
                st.caption("Klicke auf „Predict Salary“, um optional die externe API zu nutzen.")

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- RIGHT: INSIGHTS ----------------
    with right:
        st.subheader("Data Insights")

        # Salary average (best-effort)
        mids = [m for m in (_salary_mid(r) for r in rows) if m is not None]
        avg_salary = statistics.mean(mids) if mids else None

        # Total job listings
        total_jobs = len(rows)

        # Top titles
        top3 = _top_titles(rows, n=3)

        # Card: Average Salary
        st.markdown('<div class="jm-card">', unsafe_allow_html=True)
        st.markdown('<div class="jm-label">Average Salary:</div>', unsafe_allow_html=True)
        st.markdown(f'<p class="jm-big">{_currency_eur(avg_salary) if avg_salary is not None else "—"}</p>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("")

        # Card: Total Jobs
        st.markdown('<div class="jm-card">', unsafe_allow_html=True)
        st.markdown('<div class="jm-label">Total Job Listings:</div>', unsafe_allow_html=True)
        st.markdown(f'<p class="jm-big">{total_jobs:,}'.replace(",", ".") + ' <span class="jm-sub">Jobs</span></p>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("")

        # Card: Top Titles
        st.markdown('<div class="jm-card">', unsafe_allow_html=True)
        st.markdown('<div class="jm-label">Top Job Titles:</div>', unsafe_allow_html=True)
        if top3:
            st.markdown("\n".join([f"- {t}" for t in top3]))
        else:
            st.markdown("—")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("")
        with st.expander("Preview: jobs_clean.csv (first 50 rows)"):
            preview = rows[:50]
            st.dataframe(preview, use_container_width=True)


def _cli_fallback() -> None:
    print("Streamlit is not installed in this environment.")
    print("This file is meant to be run via Streamlit.")
    print("")
    print("Expected artifacts:")
    for d in CANDIDATE_DIRS:
        print(f" - {d / CLEAN_CSV_NAME}")


def main() -> None:
    st = _try_import_streamlit()
    if st is None:
        _cli_fallback()
        return
    _render_streamlit_app(st)


if __name__ == "__main__":
    main()