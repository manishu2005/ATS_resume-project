
from typing import Any, Dict, List
import os

import requests
import streamlit as st


def _backend_url() -> str:
    """Get the configured FastAPI backend URL."""
    try:
        url = st.secrets["backend"]["url"]
    except (KeyError, FileNotFoundError):
        url = os.getenv("BACKEND_URL", "").strip()

    url = str(url).strip().rstrip("/")

    if not url:
        raise RuntimeError(
            "Backend URL is missing. Configure [backend].url "
            "in Streamlit Secrets or set BACKEND_URL."
        )

    if not url.startswith(("https://", "http://")):
        raise RuntimeError(
            "Invalid backend URL. Use an http:// or https:// URL."
        )

    return url


def _auth_headers(access_token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def health_check() -> Dict[str, Any]:
    response = requests.get(
        f"{_backend_url()}/api/v1/health",
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def analyze_resume(
    resume_file,
    access_token: str,
    job_description: str = "",
) -> Dict[str, Any]:
    files = {
        "resume": (
            resume_file.name,
            resume_file.getvalue(),
            resume_file.type or "application/pdf",
        ),
    }

    data = {"job_description": job_description}

    response = requests.post(
        f"{_backend_url()}/api/v1/analyze-resume",
        files=files,
        data=data,
        headers=_auth_headers(access_token),
        timeout=180,
    )

    response.raise_for_status()
    return response.json()


def get_history(access_token: str) -> List[Dict[str, Any]]:
    response = requests.get(
        f"{_backend_url()}/api/v1/history",
        headers=_auth_headers(access_token),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def delete_history_entry(
    analysis_id: str,
    access_token: str,
) -> None:
    response = requests.delete(
        f"{_backend_url()}/api/v1/history/{analysis_id}",
        headers=_auth_headers(access_token),
        timeout=30,
    )
    response.raise_for_status()


def generate_pdf(
    analysis_data: Dict[str, Any],
    access_token: str,
) -> bytes:
    response = requests.post(
        f"{_backend_url()}/api/v1/generate-pdf",
        json=analysis_data,
        headers=_auth_headers(access_token),
        timeout=60,
    )
    response.raise_for_status()
    return response.content


def get_history_pdf(
    analysis_id: str,
    access_token: str,
) -> bytes:
    response = requests.get(
        f"{_backend_url()}/api/v1/history/{analysis_id}/pdf",
        headers=_auth_headers(access_token),
        timeout=60,
    )
    response.raise_for_status()
    return response.content
