# Connecting to Notion MCP - Notion Docs

- URL: https://developers.notion.com/guides/mcp/get-started-with-mcp
- source_type: web
- length: 5944 chars
- scraped_at: 2026-05-27 01:04:20
- elapsed: 3s
- ok: True
- error: 

---

This guide walks you through connecting your AI tool to Notion using the Model Context Protocol (MCP). Once connected, your tool can read and write to your Notion workspace based on your access and permissions.## Documentation Index

Fetch the complete documentation index at: https://developers.notion.com/llms.txt

Use this file to discover all available pages before exploring further.


## Claude Code

Run this command in your terminal:`/mcp`

in Claude Code and following the OAuth flow.
Using --scope flag for different installation scopes


Using --scope flag for different installation scopes

`--scope local`

(default): Available only to you in the current project`--scope project`

: Shared with your team via`.mcp.json`

file`--scope user`

: Available to you across all projects

`/mcp`

command to list and manage the MCP servers you have installed, and use the `/context`

command to understand the context token usage of your current session, including the number of tokens used by each MCP server that’s enabled.
## Cursor

Project-level configuration


Project-level configuration

To share the Notion MCP configuration with your team, create a

`.cursor/mcp.json`

file in your project root:## VS Code (GitHub Copilot)

User-level configuration


User-level configuration

To configure Notion MCP across all workspaces, run

**MCP: Open User Configuration**from the Command Palette and add the server configuration there.## Claude Desktop

Remote MCP servers in Claude Desktop are configured through Settings → Connectors, not the

`claude_desktop_config.json`

file. Available on Pro, Max, Team, and Enterprise plans.## Windsurf

## ChatGPT

Go to chatgpt.com/#settings/Connectors (requires login)

## Codex

For more details, see the Codex MCP documentation.Project-level configuration


Project-level configuration

To share the Notion MCP configuration with your team, create a

`.codex/config.toml`

file in your project root with the same server configuration.## Antigravity

We recommend connecting to Notion MCP as a custom server rather than using the pre-configured “Notion” connector in the Antigravity MCP gallery, which uses the deprecated`notion-mcp-server`

package.
Follow the Antigravity instructions for connecting custom MCP servers and add the following to your

`mcp_config.json`

:## Other tools

If your AI tool isn’t listed above but supports MCP, you can connect using one of these URLs:| Transport | URL | Notes |
|---|---|---|
Streamable HTTP (recommended) | `https://mcp.notion.com/mcp` | Modern transport, widely supported |
SSE (Server-Sent Events) | `https://mcp.notion.com/sse` | Legacy transport for older clients |

### JSON configuration format

Most MCP clients accept a JSON configuration. Use the appropriate format for your tool:## Connect through the Notion app

As an alternative to configuring your AI tool directly, you can initiate the connection from within Notion:## Troubleshooting

My tool doesn't support remote MCP servers


My tool doesn't support remote MCP servers

Some MCP clients only support local stdio servers. You can still connect to Notion MCP using the mcp-remote bridge:As a last resort, you can run our open-source MCP server locally, though this package is no longer actively maintained.

Authentication issues


Authentication issues

- Make sure you complete the OAuth flow when prompted
- Try disconnecting and reconnecting: look for a “Clear authentication” or “Disconnect” option in your tool’s MCP settings
- Check that you have the correct permissions in the Notion workspace you’re trying to access

My tool isn't listed here


My tool isn't listed here

Check your tool’s documentation for how to add a remote MCP server. Most tools accept either a URL directly or a JSON configuration. If your tool doesn’t support MCP yet, consider reaching out to the developers to request MCP support.

## FAQ

Can I use Notion MCP without a human in the loop?


Can I use Notion MCP without a human in the loop?

Notion MCP requires user-based OAuth authentication and does not support bearer token authentication. This means a user must complete the OAuth flow to authorize access, which may not be suitable for fully automated workflows or cloud-based coding agents that run without human interaction.If you need headless or fully automated access, you can use the open-source MCP server with a Notion API token, though this package is no longer actively maintained. Notion may explore supporting token-based authentication for remote MCP in the future.For security reasons, we recommend carefully reviewing actions performed by any MCP server before they’re executed.

Does Notion MCP support file uploads?


Does Notion MCP support file uploads?

Image and file uploads are not currently supported in Notion MCP, but this is on our roadmap. In the meantime, you can use the file upload API to upload files such as images and PDFs to your workspace.

What's the difference between Notion MCP and the open-source server?


What's the difference between Notion MCP and the open-source server?

**Notion MCP**(

`https://mcp.notion.com/mcp`

) is our hosted, actively maintained server. It uses OAuth for authentication, requires no infrastructure setup, and includes tools optimized for AI agents.The **open-source server**(

`notion-mcp-server`

) is no longer actively maintained. It supports bearer token authentication and the original JSON-based v1 APIs, which may be useful for automated workflows, but requires you to manage your own connection and deployment.For most users, we recommend Notion MCP.I'm building my own MCP client


I'm building my own MCP client

If you’re integrating Notion MCP into your own application or building a
custom AI tool, see our
MCP client connection guide for
step-by-step instructions on implementing OAuth and connecting to
Notion MCP.

**What’s Next**Learn what you can do with Notion MCP using the tools we provide:
