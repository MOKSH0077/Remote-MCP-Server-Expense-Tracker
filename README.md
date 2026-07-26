# 🧾 Remote MCP Server — Expense Tracker

A **Remote MCP Server** built with [FastMCP](https://gofastmcp.com) that exposes an expense tracking tool over HTTP. Multiple users/AI clients can connect to this server via URL — no local setup needed.

## 🛠️ Tools Available

| Tool | Description |
|---|---|
| `add_expense` | Add a new expense (amount, category, date, description) |
| `list_expenses` | Get all expenses from the database |
| `edit_expense` | Edit an existing expense by ID |
| `delete_expense` | Delete an expense by ID |

## 📁 Project Structure

```
REMOTE SERVERS/
├── main.py          # MCP server with all tools
├── pyproject.toml   # Dependencies (fastmcp)
├── uv.lock          # Locked dependency versions
├── .python-version  # Python 3.12
└── .gitignore       # Excludes .venv, .db, .env files
```

---

## 🚀 Deploy to FastMCP Cloud (Horizon)

Follow these steps to deploy this server to the internet for free.

### Step 1 — Push to GitHub
Make sure your latest code is pushed:
```bash
git add .
git commit -m "your message"
git push origin main
```

### Step 2 — Create an account on FastMCP Cloud
Go to: [https://horizon.prefect.io](https://horizon.prefect.io)
- Sign up / Log in with your GitHub account

### Step 3 — Connect your GitHub repo
- Click **"New Server"** or **"Deploy"**
- Select **"GitHub"** as the source
- Authorize FastMCP to access your repos
- Choose your repo: `Remote-MCP-Server-Expense-Tracker`

### Step 4 — Configure the deployment
Fill in the following settings:

| Field | Value |
|---|---|
| **Branch** | `main` |
| **Entry point** | `main.py` (or `main.py:mcp`) |
| **Runtime** | `uv` (auto-detected from `pyproject.toml`) |
| **Python version** | `3.12` (from `.python-version`) |

> **No environment variables needed** for this project (no API keys or secrets used).
> If you add secrets in future, add them in the "Environment Variables" section of the dashboard — **never** hardcode them in code.

### Step 5 — Deploy
- Click **"Deploy"**
- Wait ~1-2 minutes for the build to complete
- You'll get a public URL like:
  ```
  https://your-server-name.fastmcp.app/mcp
  ```

### Step 6 — Connect Claude to your Remote Server
In Claude Desktop's `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "expense-tracker-remote": {
      "url": "https://your-server-name.fastmcp.app/mcp"
    }
  }
}
```
Restart Claude → your tools are now available via the internet! 🎉

---

## 💻 Run Locally (for development)

```bash
# 1. Create virtual environment
uv venv

# 2. Activate it
.venv\Scripts\Activate.ps1        # Windows
source .venv/bin/activate          # Mac/Linux

# 3. Install dependencies
uv sync

# 4. Run the server
uv run python main.py
# Server starts at: http://localhost:8000/mcp

# 5. Test with MCP Inspector
uv run fastmcp dev main.py
# Opens Inspector at: http://localhost:6274
```

---

## ⚠️ Important Notes

- **SQLite resets on redeploy** — data is stored in `Expense.db` which is ephemeral on cloud. For persistent data, use PostgreSQL/Supabase.
- **`.db` files are gitignored** — your expense data is never pushed to GitHub.
- **Never push `.env` files** — they are gitignored by default in this project.
