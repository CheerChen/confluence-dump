# Confluence Dump

导出 Confluence 页面为 Markdown（可选 HTML/JSON），并下载图片，便于作为 LLM 上下文。

## 前置要求

- 本地安装 [uv](https://github.com/astral-sh/uv)
- Confluence Cloud 基础 URL、电子邮件和 API Token

## 快速上手

1) 设置环境变量：

   ```bash
   export CONFLUENCE_BASE_URL="https://your-site.atlassian.net"
   export CONFLUENCE_EMAIL="xxx"
   export CONFLUENCE_API_TOKEN="xxx"
   ```

2) 使用 uv 运行：

   ```bash
   uv run confluence-dump "https://your-site.atlassian.net/wiki/pages/viewpage.action?pageId=123456" -o ./output
   ```

   或者使用 Homebrew 安装脚本：

   ```bash
   brew tap cheerchen/tap
   brew install confluence-dump
   confluence-dump "https://your-site.atlassian.net/wiki/pages/viewpage.action?pageId=123456"
   ```

## 常用参数

- `-o, --output` 指定输出目录（默认 `./output`）
- `-r/--recursive` 包含子页面（默认开启；使用 `--no-recursive` 禁用）
- `-f/--format` 输出格式 `md` / `html` / `json`
- `-i/--include-images` 下载并重写图片链接（默认开启）
- `--all-attachments` 下载所有附件（默认仅下载文中引用的图片）
- `--debug` 开启调试模式（保存原始 HTML 以供检查）
- `-v/--verbose` 详细日志
- `--version` 显示版本

## 开发

- 入口文件：`src/confluence_dump/main.py`