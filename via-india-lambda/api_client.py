"""
API client for the Via India FastAPI backend (via API Gateway).
All calls go through the deployed API Gateway URL stored in st.secrets.
"""

import streamlit as st
import requests
from typing import Optional


def _base_url() -> str:
    """Get the API base URL from Streamlit secrets."""
    return st.secrets["api"]["base_url"].rstrip("/")


def _headers() -> dict:
    """Return common headers including the API key."""
    return {"x-api-key": st.secrets["api"]["api_key"]}


def _handle_response(resp: requests.Response) -> dict | list | None:
    """Raise a readable error or return JSON."""
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise Exception(f"API error {resp.status_code}: {detail}")
    return resp.json()


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def health_check() -> dict:
    resp = requests.get(f"{_base_url()}/health", headers=_headers(), timeout=10)
    return _handle_response(resp)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def create_user(name: str, email: str, phone: str = "") -> dict:
    payload = {"name": name, "email": email}
    if phone:
        payload["phone"] = phone
    resp = requests.post(f"{_base_url()}/users", json=payload, headers=_headers(), timeout=10)
    return _handle_response(resp)


def get_user(user_id: str) -> dict:
    resp = requests.get(f"{_base_url()}/users/{user_id}", headers=_headers(), timeout=10)
    return _handle_response(resp)


def verify_user(email: str) -> dict:
    resp = requests.post(
        f"{_base_url()}/users/verify",
        params={"email": email},
        headers=_headers(),
        timeout=10,
    )
    return _handle_response(resp)


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------

def create_request(
    user_id: str,
    request_type: str,
    origin: str,
    destination: str,
    departure: str,
    return_date: Optional[str] = None,
    flexible: bool = False,
    passenger_details: Optional[dict] = None,
    helper_details: Optional[dict] = None,
) -> dict:
    payload = {
        "user_id": user_id,
        "type": request_type,
        "route": {"origin": origin, "destination": destination},
        "travel_dates": {
            "departure": departure,
            "flexible": flexible,
        },
    }
    if return_date:
        payload["travel_dates"]["return_date"] = return_date
    if passenger_details:
        payload["passenger_details"] = passenger_details
    if helper_details:
        payload["helper_details"] = helper_details

    resp = requests.post(f"{_base_url()}/requests", json=payload, headers=_headers(), timeout=10)
    return _handle_response(resp)


def get_request(request_id: str) -> dict:
    resp = requests.get(f"{_base_url()}/requests/{request_id}", headers=_headers(), timeout=10)
    return _handle_response(resp)


def get_user_requests(user_id: str) -> list:
    resp = requests.get(f"{_base_url()}/users/{user_id}/requests", headers=_headers(), timeout=10)
    return _handle_response(resp)


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------

def find_matches(request_id: str) -> dict:
    resp = requests.get(f"{_base_url()}/requests/{request_id}/matches", headers=_headers(), timeout=10)
    return _handle_response(resp)
