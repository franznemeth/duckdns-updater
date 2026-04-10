"""Unit tests for updater.py."""

import pytest
import requests
import responses as resp

import updater


FAKE_IP = "1.2.3.4"
FAKE_TOKEN = "test-token-abc123"
FAKE_SUBDOMAIN = "my-home"


# ---------------------------------------------------------------------------
# get_public_ipv4
# ---------------------------------------------------------------------------


@resp.activate
def test_get_public_ipv4_success():
    resp.add(resp.GET, updater.IPIFY_URL, body=FAKE_IP, status=200)
    ip = updater.get_public_ipv4()
    assert ip == FAKE_IP


@resp.activate
def test_get_public_ipv4_http_error(capsys):
    resp.add(resp.GET, updater.IPIFY_URL, status=500)
    with pytest.raises(SystemExit) as exc_info:
        updater.get_public_ipv4()
    assert exc_info.value.code == 1


@resp.activate
def test_get_public_ipv4_connection_error(capsys):
    resp.add(resp.GET, updater.IPIFY_URL, body=requests.ConnectionError("connection refused"))
    with pytest.raises(SystemExit) as exc_info:
        updater.get_public_ipv4()
    assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# update_duckdns
# ---------------------------------------------------------------------------


@resp.activate
def test_update_duckdns_success():
    resp.add(resp.GET, updater.DUCKDNS_URL, body="OK", status=200)
    # Should not raise
    updater.update_duckdns(FAKE_SUBDOMAIN, FAKE_TOKEN, FAKE_IP)
    assert len(resp.calls) == 1
    sent_params = resp.calls[0].request.url
    assert f"domains={FAKE_SUBDOMAIN}" in sent_params
    assert f"ip={FAKE_IP}" in sent_params
    # Token must be present in the URL, but we only check key existence
    assert "token=" in sent_params


@resp.activate
def test_update_duckdns_ko_response():
    resp.add(resp.GET, updater.DUCKDNS_URL, body="KO", status=200)
    with pytest.raises(SystemExit) as exc_info:
        updater.update_duckdns(FAKE_SUBDOMAIN, FAKE_TOKEN, FAKE_IP)
    assert exc_info.value.code == 1


@resp.activate
def test_update_duckdns_http_error():
    resp.add(resp.GET, updater.DUCKDNS_URL, status=503)
    with pytest.raises(SystemExit) as exc_info:
        updater.update_duckdns(FAKE_SUBDOMAIN, FAKE_TOKEN, FAKE_IP)
    assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# main – env var validation
# ---------------------------------------------------------------------------


@resp.activate
def test_main_missing_subdomain(monkeypatch):
    monkeypatch.delenv("DUCKDNS_SUBDOMAIN", raising=False)
    monkeypatch.delenv("DUCKDNS_TOKEN", raising=False)
    with pytest.raises(SystemExit) as exc_info:
        updater.main()
    assert exc_info.value.code == 1


@resp.activate
def test_main_missing_token(monkeypatch):
    monkeypatch.setenv("DUCKDNS_SUBDOMAIN", FAKE_SUBDOMAIN)
    monkeypatch.delenv("DUCKDNS_TOKEN", raising=False)
    with pytest.raises(SystemExit) as exc_info:
        updater.main()
    assert exc_info.value.code == 1


@resp.activate
def test_main_success(monkeypatch):
    monkeypatch.setenv("DUCKDNS_SUBDOMAIN", FAKE_SUBDOMAIN)
    monkeypatch.setenv("DUCKDNS_TOKEN", FAKE_TOKEN)
    resp.add(resp.GET, updater.IPIFY_URL, body=FAKE_IP, status=200)
    resp.add(resp.GET, updater.DUCKDNS_URL, body="OK", status=200)
    # Should complete without error
    updater.main()



