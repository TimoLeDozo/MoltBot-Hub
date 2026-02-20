# Google Doc Sync (Native Google API)

This skill is native and standalone (no third-party SaaS wrapper).
It uses a Google Service Account key mounted in Docker at:

- `/app/config/google_service_account.json`

## Behavior

1. Accept a local Markdown file path.
2. Authenticate with Service Account (`from_service_account_file`).
3. Create a new Google Doc.
4. Insert the Markdown text content as document text.
5. Print the created Google Doc URL to stdout.

## Dependencies

The skill uses only:

- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

Install command:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Usage

```bash
python /app/skills/google-doc-sync/sync_google_doc.py \
  /app/workspace/RELAIS_SOIR.md \
  --service-account /app/config/google_service_account.json \
  --title "Night Shift Report"
```
