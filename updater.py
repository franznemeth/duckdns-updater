"""
DuckDNS Updater
---------------
Fetches the current public IPv4 address and updates a DuckDNS subdomain.

Configuration (via environment variables):
  DUCKDNS_TOKEN      - DuckDNS API token  (required, sourced from K8s Secret)
  DUCKDNS_SUBDOMAIN  - DuckDNS subdomain  (required, e.g. "my-home")
"""

import logging
import os
import sys

import requests

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

IPIFY_URL = "https://api4.ipify.org"  # IPv4-only endpoint
DUCKDNS_URL = "https://www.duckdns.org/update"
REQUEST_TIMEOUT = 10  # seconds


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def get_public_ipv4() -> str:
    """Return the current public IPv4 address by querying the ipify API."""
    log.info("Fetching public IPv4 address from %s", IPIFY_URL)
    try:
        response = requests.get(IPIFY_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        log.error("Failed to fetch public IP: %s", exc)
        sys.exit(1)

    ip = response.text.strip()
    log.info("Detected public IPv4: %s", ip)
    return ip


def update_duckdns(subdomain: str, token: str, ip: str) -> None:
    """Update the DuckDNS subdomain record with the given IP address."""
    log.info("Updating DuckDNS subdomain '%s' → %s", subdomain, ip)
    params = {
        "domains": subdomain,
        "token": token,
        "ip": ip,
    }
    try:
        response = requests.get(DUCKDNS_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        log.error("HTTP request to DuckDNS failed: %s", exc)
        sys.exit(1)

    body = response.text.strip()
    if body.startswith("OK"):
        log.info("DuckDNS update successful (response: %s)", body)
    else:
        log.error("DuckDNS update failed (response: %s)", body)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    subdomain = os.environ.get("DUCKDNS_SUBDOMAIN", "").strip()
    token = os.environ.get("DUCKDNS_TOKEN", "").strip()

    if not subdomain:
        log.error("Environment variable DUCKDNS_SUBDOMAIN is not set or empty.")
        sys.exit(1)
    if not token:
        log.error("Environment variable DUCKDNS_TOKEN is not set or empty.")
        sys.exit(1)

    ip = get_public_ipv4()
    update_duckdns(subdomain, token, ip)


if __name__ == "__main__":
    main()

