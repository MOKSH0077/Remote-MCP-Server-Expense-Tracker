# 🧾 Remote MCP Server — Expense Tracker

A **Remote MCP Server** built with [FastMCP](https://gofastmcp.com) that lets you track expenses directly through Claude AI — from any device, anywhere in the world. Just connect and use!

> 🔗 **Live Server URL**: `https://remote-mcp-server-expense-tracker-k4gb.onrender.com/mcp`

---

## ⚡ How to Connect (Any Device, Anyone)

This server uses **Google OAuth** — so you just need a Gmail account. No JSON files, no API keys, no technical setup!

---

### 📱 Option 1: Claude Mobile App (iPhone / Android)

1. Open **Claude App** on your phone
2. Go to **Settings → Connectors** (or tap the plug 🔌 icon)
3. Tap **"Add Custom Connector"** or **"+"**
4. Paste this URL:
   ```
   https://remote-mcp-server-expense-tracker-k4gb.onrender.com/mcp
   ```
5. A **"Sign in with Google"** popup will appear
6. Select your Gmail account → Tap **Allow**
7. Done! ✅ Now just ask Claude anything about expenses!

---

### 💻 Option 2: Claude Web App (Browser — claude.ai)

1. Go to [claude.ai](https://claude.ai) in your browser
2. Click the **plug icon 🔌** or go to **Settings → Integrations**
3. Click **"Add Integration"** or **"Connect MCP Server"**
4. Paste this URL:
   ```
   https://remote-mcp-server-expense-tracker-k4gb.onrender.com/mcp
   ```
5. A **"Sign in with Google"** popup will appear
6. Select your Gmail → Click **Allow**
7. Done! ✅

---

### 🖥️ Option 3: Claude Desktop App (Windows / Mac)

1. Close Claude Desktop App completely (including from system tray)
2. Open this file in Notepad / VS Code:
   - **Windows**: `C:\Users\<YourName>\AppData\Roaming\Claude\claude_desktop_config.json`
   - **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
3. Paste this config:
   ```json
   {
     "mcpServers": {
       "expense-tracker": {
         "command": "npx",
         "args": [
           "-y",
           "mcp-remote",
           "https://remote-mcp-server-expense-tracker-k4gb.onrender.com/mcp"
         ]
       }
     }
   }
   ```
4. Save the file → Reopen Claude Desktop
5. A **Google login popup** will appear in your browser
6. Sign in → Done! ✅

> **Note**: `npx` requires [Node.js](https://nodejs.org) to be installed. If you have Python/uv installed, replace `"command": "npx"` with `"command": "uvx"` and `"args": ["-y", "mcp-remote", "URL"]` with `"args": ["fastmcp", "run", "URL"]`.

---

## 💬 How to Use (Ask Claude Anything!)

Once connected, just chat naturally with Claude:

| What you want | What to say |
|---|---|
| Add expense | *"Add ₹500 for groceries on 27 July"* |
| View all expenses | *"Show me all my expenses"* |
| Edit an expense | *"Edit expense ID 3, change amount to ₹200"* |
| Delete an expense | *"Delete expense ID 5"* |

---

## 🛠️ Tools Available

| Tool | Description |
|---|---|
| `add_expense` | Add a new expense (amount, category, date, description) |
| `list_expenses` | View all your recorded expenses |
| `edit_expense` | Update an existing expense by ID |
| `delete_expense` | Remove an expense by ID |

---

## ⚠️ Important Notes

- **First connection may take 30-60 seconds** — Render's free tier "sleeps" after inactivity. After the first request wakes it up, everything is fast!
- **After reconnecting Google OAuth, you don't need to reconnect** — Even if the server redeploys, your Google token stays saved in Claude. Just keep using it!
- **Data resets on server restart** — Expenses are stored in `/tmp/Expense.db` on the cloud server. This is demo/learning storage. For permanent data, a cloud database (PostgreSQL/Supabase) would be needed.
- **Google account required** — Any Gmail account works. No GitHub, no API keys, no technical knowledge needed!

---

## 🚀 Deploy Your Own Copy (Optional)

Want to host your own instance? Fork this repo and follow these steps.

### Step 1 — Google Cloud Console (Free OAuth App)
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project → **APIs & Services → Credentials**
3. Click **"Create Credentials" → "OAuth 2.0 Client ID"**
4. Application type: **Web Application**
5. Add Authorized redirect URI:
   ```
   https://YOUR-RENDER-URL.onrender.com/auth/callback
   ```
6. Copy your **Client ID** and **Client Secret**

### Step 2 — Deploy to Render.com (Free)
1. Go to [render.com](https://render.com) → **New → Web Service**
2. Connect your GitHub forked repo
3. Settings:
   - **Language**: Python 3
   - **Build Command**: `pip install uv && uv sync`
   - **Start Command**: `uv run python main.py`
4. Add Environment Variables:
   | Key | Value |
   |---|---|
   | `GOOGLE_CLIENT_ID` | From Google Console |
   | `GOOGLE_CLIENT_SECRET` | From Google Console |
   | `SERVER_BASE_URL` | `https://YOUR-RENDER-URL.onrender.com` |
5. Click **Deploy!**

---

## 📁 Project Structure

```
├── main.py          # MCP server — async tools + Google OAuth + detailed comments
├── pyproject.toml   # Dependencies (fastmcp, aiosqlite)
├── uv.lock          # Locked dependency versions
├── render.yaml      # Render.com deployment blueprint
├── .python-version  # Python 3.12
└── .gitignore       # Excludes .venv, .db, .env files
```
