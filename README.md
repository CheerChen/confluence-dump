# Confluence Dump

Export Confluence pages to Markdown (optionally HTML/JSON) and download images for LLM context.

## Requirements

- [uv](https://github.com/astral-sh/uv) installed locally
- Confluence Cloud base URL, email, and API token

## Quickstart

1) export variables:

   ```bash
   export CONFLUENCE_BASE_URL="https://your-site.atlassian.net"
   export CONFLUENCE_EMAIL="xxx"
   export CONFLUENCE_API_TOKEN="xxx"
   ```
   
2) Run with uv:

   ```bash
   uv run confluence-dump "https://your-site.atlassian.net/wiki/pages/viewpage.action?pageId=123456" -o ./output
   ```

   Or use Homebrew-installed script:

   ```bash
   brew tap cheerchen/tap
   brew install confluence-dump
   confluence-dump "https://your-site.atlassian.net/wiki/pages/viewpage.action?pageId=123456"
   ```

## Common options

- `-o, --output` output directory (default `./output`)
- `-r/--recursive` include descendants (default on; disable with `--no-recursive`)
- `-f/--format` `md` / `html` / `json`
- `-i/--include-images` download and rewrite image links (default on)
- `--all-attachments` download all attachments (default: only referenced images)
- `--debug` enable debug mode (saves raw HTML for inspection)
- `-v/--verbose` verbose logs
- `--version` show version

## Development

- Entry point: `src/confluence_dump/main.py`
