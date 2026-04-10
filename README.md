# duckdns-updater

A minimal Python tool that runs as a Kubernetes **CronJob** and keeps a [DuckDNS](https://www.duckdns.org) subdomain in sync with the cluster's public IPv4 address.

---

## How it works

1. Queries `https://api4.ipify.org` to discover the current public IPv4 address.
2. Calls the DuckDNS update API with the subdomain, token, and detected IP.
3. Logs the outcome and exits `0` on success, `1` on any failure.

---

## Configuration

| Environment variable | Source              | Description                                      |
|----------------------|---------------------|--------------------------------------------------|
| `DUCKDNS_SUBDOMAIN`  | CronJob `env`       | Subdomain name only — e.g. `my-home` for `my-home.duckdns.org` |
| `DUCKDNS_TOKEN`      | Kubernetes Secret   | DuckDNS API token (keep this secret!)            |

---

## Deployment

### 1 — Create the Kubernetes Secret

```bash
# Option A: from the template (fill in your token, then apply)
cp k8s/secret.yaml.template k8s/secret.yaml
# edit k8s/secret.yaml — set the real token
kubectl apply -f k8s/secret.yaml

# Option B: one-liner (token never written to disk)
kubectl create secret generic duckdns-secret \
  --namespace=default \
  --from-literal=token='<YOUR_DUCKDNS_TOKEN>'
```

> `k8s/secret.yaml` is listed in `.gitignore` — never commit a real token.

### 2 — Deploy the CronJob

Edit `k8s/cronjob.yaml`:
- Replace `<OWNER>` with your GitHub username / organisation.
- Replace `<YOUR_SUBDOMAIN>` with your DuckDNS subdomain (e.g. `my-home`).
- Adjust the `schedule` if needed (default: every 5 minutes).

```bash
kubectl apply -f k8s/cronjob.yaml
```

---

## Local development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Run manually (set real or dummy values)
export DUCKDNS_SUBDOMAIN=my-home
export DUCKDNS_TOKEN=your-token-here
python updater.py
```

---

## CI/CD

A GitHub Actions workflow (`.github/workflows/docker-publish.yml`) triggers on:
- **Push to `main`** — runs tests, builds, and pushes with `latest` + `sha-<short-sha>` tags.
- **Push of a `vX.Y.Z` tag** — runs tests, builds, and pushes with the full semver tag set.

| Tag | Example | When |
|---|---|---|
| `latest` | `…:latest` | Every merge to `main` |
| `sha-<short-sha>` | `…:sha-a1b2c3d` | Every build (immutable) |
| `vX.Y.Z` | `…:v1.2.3` | On Git tag push |
| `vX.Y` | `…:v1.2` | On Git tag push |
| `vX` | `…:v1` | On Git tag push |

To release a new version:
```bash
git tag v1.0.0 && git push origin v1.0.0
```

No additional secrets are required — the workflow uses the built-in `GITHUB_TOKEN`.

