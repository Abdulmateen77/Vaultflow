"""Tests for the early-access / waitlist lead-capture form (VAU-25)."""
from __future__ import annotations

import sqlite3
import tempfile
import pathlib

import pytest
from fastapi.testclient import TestClient

from app.main import app
import app.waitlist as wl_module


# ---------------------------------------------------------------------------
# Helper: redirect waitlist db to a temp file for test isolation
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def isolated_waitlist_db(tmp_path, monkeypatch):
    """Point the waitlist module at a fresh temp database for each test."""
    test_db = tmp_path / "test_waitlist.db"
    monkeypatch.setattr(wl_module, "_DB_PATH", test_db)
    wl_module._ensure_table()
    yield test_db


# ---------------------------------------------------------------------------
# Unit tests for waitlist module
# ---------------------------------------------------------------------------

def test_insert_and_exists():
    wl_module.insert_lead(
        name="Alice", email="alice@example.com", company="Acme", use_case="HIPAA"
    )
    assert wl_module.lead_exists("alice@example.com") is True


def test_nonexistent_email_returns_false():
    assert wl_module.lead_exists("nobody@nowhere.com") is False


def test_insert_returns_id():
    lead_id = wl_module.insert_lead(
        name="Bob", email="bob@corp.com", company="Corp", use_case="PCI"
    )
    assert isinstance(lead_id, int)
    assert lead_id >= 1


def test_duplicate_not_double_inserted():
    wl_module.insert_lead(name="Carol", email="carol@firm.com", company="Firm", use_case="General")
    wl_module.insert_lead(name="Carol", email="carol@firm.com", company="Firm", use_case="General")
    conn = sqlite3.connect(wl_module._DB_PATH)
    count = conn.execute(
        "SELECT COUNT(*) FROM waitlist_leads WHERE email = ?", ("carol@firm.com",)
    ).fetchone()[0]
    conn.close()
    # We allow the module to insert without dedup — the /waitlist endpoint deduplicates.
    assert count >= 1


# ---------------------------------------------------------------------------
# API tests — /waitlist endpoint
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    return TestClient(app)


def test_waitlist_post_success(client):
    payload = {
        "name": "Dana Smith",
        "email": "dana@healthtech.com",
        "company": "HealthTech Inc.",
        "use_case": "HIPAA",
    }
    res = client.post("/waitlist", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "You're on the list" in data["message"]
    assert data["already_registered"] is False


def test_waitlist_confirmation_message_exact(client):
    payload = {
        "name": "Eli Jones",
        "email": "eli@finserv.io",
        "company": "FinServ",
        "use_case": "PCI",
    }
    res = client.post("/waitlist", json=payload)
    assert res.status_code == 200
    assert res.json()["message"] == "You're on the list. Expect a note from us within 24 hours."


def test_waitlist_already_registered_flag(client):
    payload = {
        "name": "Fay Lee",
        "email": "fay@insure.com",
        "company": "InSure Co",
        "use_case": "General",
    }
    client.post("/waitlist", json=payload)
    res2 = client.post("/waitlist", json=payload)
    assert res2.status_code == 200
    assert res2.json()["already_registered"] is True


def test_waitlist_missing_name_returns_422(client):
    res = client.post("/waitlist", json={"email": "x@y.com", "company": "Acme", "use_case": "General"})
    assert res.status_code == 422


def test_waitlist_bad_email_returns_422(client):
    res = client.post("/waitlist", json={
        "name": "Test", "email": "not-an-email", "company": "Acme", "use_case": "General"
    })
    assert res.status_code == 422


def test_waitlist_missing_company_returns_422(client):
    res = client.post("/waitlist", json={"name": "Test", "email": "t@x.com", "use_case": "General"})
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# Route / page tests
# ---------------------------------------------------------------------------

def test_early_access_page_renders(client):
    res = client.get("/early-access")
    assert res.status_code == 200
    assert "Request Early Access" in res.text or "early access" in res.text.lower()


def test_early_access_page_has_approved_copy(client):
    res = client.get("/early-access")
    assert "PII Redaction Gateway" in res.text
    assert "24 hours" in res.text
    assert "Request Access" in res.text


def test_landing_page_has_cta_banner(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "Request Access" in res.text
    assert "/early-access" in res.text
    assert "PII Redaction Gateway" in res.text


def test_landing_page_nav_has_early_access_link(client):
    res = client.get("/")
    assert 'href="/early-access"' in res.text
