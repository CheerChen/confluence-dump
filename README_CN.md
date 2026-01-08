# Confluence Dump

导出 Confluence 页面为 Markdown（可选 HTML/JSON），并下载图片，便于作为 LLM 上下文。

## 前置
- 安装 [uv](https://github.com/astral-sh/uv)
- `.env` 提供账号信息：
  ```bash
  CONFLUENCE_BASE_URL=https://your-site.atlassian.net
  CONFLUENCE_EMAIL=you@example.com
  CONFLUENCE_API_TOKEN=your_api_token
  ```

## 使用
- 直接运行（依赖锁定在 `uv.lock`）：
  ```bash
  uv run confluence-dump "https://...pageId=123456" -o ./output
  ```
- 或使用 brew 安装之后（自动 `uv run --project`）：
  ```bash
  confluence-dump "https://...pageId=123456" -o ./output
  ```

常用参数：
- `-o, --output` 指定输出目录（默认 `./output`）
- `--no-recursive` 仅导出单页
- `-f/--format` `md` / `html` / `json`
- `--no-include-images` 跳过图片下载
- `-v/--verbose` 详细日志
- `--version` 查看版本

## 开发
- 入口：`src/confluence_dump/main.py`
