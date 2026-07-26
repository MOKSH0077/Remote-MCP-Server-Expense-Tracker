# 🧾 Remote MCP Server — Expense Tracker

A **Remote MCP Server** built with [FastMCP](https://gofastmcp.com) that lets you track expenses directly through Claude AI — no local setup needed. Just connect and use.

---

## ⚡ How to Use This Server (Connect Claude to it)

This server is hosted on the internet. You just need to add the URL to your Claude config — no installation, no code.

### Step 1 — Open Claude Desktop config file

**Windows:**
```
C:\Users\<YourName>\AppData\Roaming\Claude\claude_desktop_config.json
```
**Mac:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Step 2 — Add this server to the config

```json
{
  "mcpServers": {
    "expense-tracker": {
      "url": "https://moksh-expense-tracker.fastmcp.app/mcp"
    }
  }
}
```

> 🔗 **Server URL**: `https://moksh-expense-tracker.fastmcp.app/mcp`

### Step 3 — Restart Claude

Close and reopen Claude Desktop. The expense tracker tools will now be available!

### Step 4 — Start using it

Ask Claude things like:
- *"Add an expense of ₹500 for food today"*
- *"Show me all my expenses"*
- *"Edit expense ID 3, change amount to ₹200"*
- *"Delete expense ID 5"*

---

## 🛠️ Tools Available

| Tool | What it does |
|---|---|
| `add_expense` | Add a new expense (amount, category, date, description) |
| `list_expenses` | View all your recorded expenses |
| `edit_expense` | Update an existing expense by ID |
| `delete_expense` | Remove an expense by ID |

---

## 🚀 Deploy Your Own Copy (Optional)

Want to host your own instance? Follow these steps.

### Step 1 — Fork this repo
Click **Fork** on the top right of this page.

### Step 2 — Create an account on FastMCP Cloud
Go to: [https://horizon.prefect.io](https://horizon.prefect.io)
Sign up / Log in with GitHub.

### Step 3 — Connect your forked repo
- Click **"New Server"** → Select **GitHub**
- Choose your forked repo

### Step 4 — Configure deployment

| Field | Value |
|---|---|
| **Branch** | `main` |
| **Entry point** | `main.py` |
| **Runtime** | `uv` |
| **Python version** | `3.12` |

> No environment variables needed for this project.

### Step 5 — Deploy
Click **Deploy** → Wait ~1-2 minutes → Get your public URL:
```
https://your-server-name.fastmcp.app/mcp
```
Use this URL in Step 2 of the usage guide above.

---

## 📁 Project Structure

```
├── main.py          # MCP server with all tools + detailed comments
├── pyproject.toml   # Dependencies (fastmcp)
├── uv.lock          # Locked dependency versions
├── .python-version  # Python 3.12
└── .gitignore       # Excludes .venv, .db, .env files
```

> ⚠️ **Note:** SQLite data resets on every redeploy (ephemeral cloud storage). For persistent data in production, replace SQLite with PostgreSQL or Supabase.
