# Zotero import workflow

Use this when a generated or modified PDF must be inspected inside Zotero desktop on this Mac.

## Hard rule

Do **not** try to import a PDF with:

- `open -a Zotero /path/to/file.pdf`

On macOS, Zotero.app is not registered as a general PDF document opener/importer in the way we need here. This can produce:

- `The selected file is not in a supported format.`

## Reliable order of operations

1. **Ensure Zotero desktop is running**
2. **Ping the local connector** at `http://127.0.0.1:23119/connector/ping`
3. **Check the current save target** with `/connector/getSelectedCollection`
4. **Import the PDF as a standalone attachment** via `/connector/saveStandaloneAttachment`
5. **Resolve the imported attachment key**
   - Prefer the helper script for this
   - If the Local API is disabled and SQLite is locked, resolve by matching the newest copied PDF under `~/Zotero/storage/*/*.pdf`
6. **Open the imported PDF** with:
   - `zotero://open-pdf/library/items/<ATTACHMENT_KEY>`

## Preferred path

Use the bundled helper script:

```bash
python3 /Users/apple/.openclaw/workspace/skills/zotero-paper-coach/scripts/import_pdf_to_zotero.py \
  /path/to/file.pdf \
  --title "My annotated PDF" \
  --open
```

## Why this is the preferred path

- Connector import is stable with Zotero desktop
- It imports into the currently selected library/collection
- It avoids relying on the Local API, which may be disabled
- It avoids touching `zotero.sqlite`, which may be locked while Zotero is running

## Manual connector import

If you need the raw flow, send a POST request to:

- `http://127.0.0.1:23119/connector/saveStandaloneAttachment`

With headers:

- `Content-Type: application/pdf`
- `X-Zotero-Connector-API-Version: 3`
- `X-Metadata: {"sessionID":"...","url":"file:///...pdf","title":"..."}`

And send the PDF bytes as the request body.

## Opening the imported attachment

If the helper script prints an `attachmentKey`, open it with:

```bash
open 'zotero://open-pdf/library/items/<ATTACHMENT_KEY>'
```

## Notes

- The Local API may return `Local API is not enabled`
- Direct SQLite inspection may fail with `database is locked`
- Connector import is the stable route for one-shot testing and review
