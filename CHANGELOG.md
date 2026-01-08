# Changelog

## [0.2.1]
- **Feature**: Support Confluence code macros conversion to Markdown code blocks
- **Feature**: Support drawio macro image extraction (converts to PNG preview)
- **Feature**: Global attachment pool for cross-page image sharing
- **Fix**: Improved attachment fetch error handling (graceful 400/404 warnings)
- **Fix**: Image download now falls back to global pool when not found in current page

## [0.2.0]
- **Feature**: Skip exporting empty pages (pages with no content)
- **Feature**: Only download images referenced in the content by default (reduce size)
- **Feature**: Add `--all-attachments` flag to force downloading all attachments
- **Feature**: Add `--debug` flag to save raw HTML content for inspection
- **Fix**: Correctly sanitize folder names (preserving dates and numbers)
- **Fix**: Handle attachment download errors gracefully (continue export on 400/error)
- **Improvement**: Folder naming now includes Page ID: `{page_id}_{title}`
- **Improvement**: Prepend Page Title as H1 header in Markdown output

## [0.1.0]
- Initial release: recursive export of Confluence pages to Markdown/HTML/JSON
- Download attachments and rewrite image links
- Add uv wrapper script for local and Homebrew-style usage
