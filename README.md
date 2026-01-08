# Confluence Dump

Export Confluence pages to Markdown (optionally HTML/JSON) and download images for LLM context.

## Requirements
- [uv](https://github.com/astral-sh/uv) installed locally
- Confluence Cloud base URL, email, and API token (stored in `.env`)

## Quickstart
1) Create `.env`:
   ```bash
   CONFLUENCE_BASE_URL=https://your-site.atlassian.net
   CONFLUENCE_EMAIL=you@example.com
   CONFLUENCE_API_TOKEN=your_api_token
   ```
2) Run with locked dependencies:
   ```bash
   uv run confluence-dump "https://your-site.atlassian.net/wiki/pages/viewpage.action?pageId=123456" -o ./output
   ```
   Or use the bundled wrapper:
   ```bash
   ./confluence-dump.sh "https://...pageId=123456" -o ./output
   ```

## Common options
- `-o, --output` output directory (default `./output`)
- `-r/--recursive` include descendants (default on; disable with `--no-recursive`)
- `-f/--format` `md` / `html` / `json`
- `-i/--include-images` download and rewrite image links (default on)
- `-v/--verbose` verbose logs
- `--version` show version

## Development
- Smoke check: `uv run confluence-dump --version`
- Entry point: `src/confluence_dump/main.py`
