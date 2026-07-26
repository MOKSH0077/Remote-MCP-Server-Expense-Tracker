# ============================================================
# REMOTE MCP SERVER — EXPENSE TRACKER
# ============================================================
#
# WHAT IS A REMOTE MCP SERVER?
# A Remote MCP Server is an MCP server that runs on a DIFFERENT machine
# (i.e., on the internet/cloud), not on your local computer.
#
# HOW IS IT DIFFERENT FROM A LOCAL MCP SERVER?
#
#   LOCAL MCP SERVER:
#   - Runs on YOUR machine (same computer as Claude/AI client)
#   - Transport used: stdio (Standard Input/Output)
#   - Claude launches your server as a subprocess and talks to it via stdio pipes
#   - Only YOU can use it (single user, your machine only)
#   - Faster (no network involved)
#   - Example: expense_tracker.py in LOCAL MCP SERVERS 2
#
#   REMOTE MCP SERVER:
#   - Runs on a CLOUD server (e.g., FastMCP Cloud, Render, Railway, etc.)
#   - Transport used: HTTP (Streamable HTTP)
#   - Claude connects to it via a URL: https://your-server.com/mcp
#   - ANYONE with the URL can use it (multi-user, internet accessible)
#   - Slightly slower (network involved) but scalable
#   - Example: THIS file (main.py)
#
# HOW DOES TESTING WORK? (Inspector confusion cleared)
#
#   When you run: uv run fastmcp dev main.py
#   The MCP Inspector opens in your browser and connects via STDIO.
#   This does NOT mean your server is a local server!
#   Inspector always uses STDIO for local testing — it just launches
#   your file as a subprocess to test tools. It is a DEVELOPMENT tool only.
#
#   In PRODUCTION:
#   - Local server  → Claude uses stdio (subprocess)
#   - Remote server → Claude uses HTTP URL (network)
#
# ============================================================
# UNDERSTANDING: transport="http", host="0.0.0.0", port=8000
# ============================================================
#
# TRANSPORT TYPES IN MCP:
#
#   1. stdio (Standard Input/Output)
#      - Used for LOCAL servers
#      - Claude spawns the server as a child process
#      - Communication happens via stdin/stdout pipes (text streams)
#      - No network involved — fast, simple, single user
#      - Example: mcp.run() or mcp.run(transport="stdio")
#
#   2. SSE — Server-Sent Events (DEPRECATED / OLD)
#      - Old way of doing HTTP-based MCP
#      - Used two separate endpoints: POST (client→server) + SSE stream (server→client)
#      - Complex, hard to scale, now replaced by Streamable HTTP
#      - Avoid using this
#
#   3. HTTP — Streamable HTTP (MODERN STANDARD ✅)
#      - Used for REMOTE servers (this file!)
#      - Single unified endpoint: /mcp
#      - Client sends requests via HTTP POST
#      - Server responds via the same connection (can stream responses)
#      - Scalable, load-balancer friendly, stateless-capable
#      - In FastMCP: transport="http" = transport="streamable-http" (same thing)
#      - Example: mcp.run(transport="http", host="0.0.0.0", port=8000)
#
# PARAMETERS EXPLAINED:
#
#   transport="http"
#   → Tells FastMCP to use Streamable HTTP protocol (the modern MCP standard)
#   → Your server will expose an endpoint at: http://host:port/mcp
#   → Any MCP client (Claude, Inspector, etc.) connects to this URL
#
#   host="0.0.0.0"
#   → Means: "listen on ALL available network interfaces"
#   → 0.0.0.0 = accept connections from EVERYWHERE (your machine, LAN, internet)
#   → If you used "127.0.0.1" instead → only YOUR machine could connect (localhost only)
#   → For a remote/cloud server you MUST use "0.0.0.0" so the cloud can route traffic to it
#
#   port=8000
#   → The port number your server listens on
#   → Think of it like a door number in a building (IP = building, port = door)
#   → HTTP default = 80, HTTPS default = 443, FastMCP convention = 8000
#   → On cloud platforms, the platform usually assigns the port via an env variable
#     (e.g., PORT=8080) — so production code often does: port=int(os.environ.get("PORT", 8000))
#
# FINAL FLOW (Local Dev → Cloud Deploy):
#
#   DEV:    uv run python main.py → server at http://localhost:8000/mcp (your machine)
#   DEPLOY: push to GitHub → FastMCP Cloud → server at https://xxx.fastmcp.app/mcp (internet)
#   CLAUDE: connects via that URL → tools available to anyone
#
# ============================================================

from fastmcp import FastMCP
import sqlite3
import os

# WHY DB_PATH LIKE THIS?
# os.path.dirname(__file__) gives the folder where this script lives.
# We store Expense.db in the same folder so it's always found relative to the script.
# NOTE: On cloud platforms, this file will reset on every redeploy (ephemeral storage).
# For production, use a persistent DB like PostgreSQL or Supabase instead.
DB_PATH=os.path.join(os.path.dirname(__file__),"Expense.db")

# WHY FastMCP(name='expense-tracker')?
# Creates the MCP server instance with a display name.
# This name appears in MCP Inspector and MCP client listings.
mcp=FastMCP(name='expense-tracker')


# WHY THIS FUNCTION?
# 1. This function initializes our database. When the app starts, we must ensure
#    the "expenses" table exists so we can read/write data without errors.
# 2. SQLite automatically creates the "Expense.db" file if it doesn't exist,
#    but we still need to create the table inside it.
#
# HOW IT WORKS (LINE-BY-LINE):
# - "with sqlite3.connect(DB_PATH) as conn:": Opens a connection to the database file.
#   The "with" block ensures the connection closes automatically when done.
# - "conn.execute(...)": Runs the SQL command to create the table.
# - "CREATE TABLE IF NOT EXISTS expenses": Creates the table only if it doesn't
#   already exist, preventing errors on subsequent runs.
# - Columns defined:
#    * id: Unique ID for each expense (auto-increments).
#    * amount: Decimal value for the expense amount (cannot be empty).
#    * category: Category name (cannot be empty).
#    * date: The date of the expense (cannot be empty).
#    * description: Optional notes about the expense.
def initdb():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date DATE NOT NULL,
            description TEXT
        )
        """)

initdb()


# WHY THIS TOOL?
# This tool allows the MCP client to add a new expense entry into the SQLite database.
#
# HOW IT WORKS (LINE-BY-LINE):
# - "@mcp.tool": Exposes this Python function as an MCP tool so that any MCP
#   client/agent (Claude, Inspector, etc.) can call it.
# - "try...except": Catches any database/execution errors to avoid crashing the server.
# - "with sqlite3.connect(DB_PATH) as conn:": Opens a connection to the database file.
# - "cursor = conn.cursor()": Creates a cursor object to execute SQL commands.
# - "cursor.execute(...)": Safely inserts the expense data into the table.
#   The "?" placeholders prevent SQL injection attacks.
# - "return {"status":"ok","id":cursor.lastrowid}": Returns success + the new record's ID.
@mcp.tool
def add_expense(amount:float,category:str,date:str,description:str)->dict:
    """Add expense to database"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO expenses (amount,category,date,description) VALUES (?,?,?,?)",(amount,category,date,description))
            return {"status":"ok","id":cursor.lastrowid}
    except Exception as e:
        return {"status":"error","message":str(e)}


# WHY THIS TOOL?
# This tool retrieves all recorded expenses from the database so the user/agent can view them.
#
# HOW IT WORKS (LINE-BY-LINE):
# - "@mcp.tool": Exposes this function as an MCP tool.
# - "with sqlite3.connect(DB_PATH) as conn:": Opens a connection to the database file.
# - "cursor = conn.cursor()": Prepares a cursor to execute SQL commands.
# - "cursor.execute("SELECT * FROM expenses")": Fetches all rows from the expenses table.
# - "rows=cursor.fetchall()": Gathers all query results as a list of tuples.
# - "return rows": Returns the full list of expenses.
@mcp.tool
def list_expenses()->list:
    """Get all expenses from database"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses")
        rows=cursor.fetchall()
        return rows


# WHY THIS TOOL?
# This tool modifies an existing expense record in the database using its unique integer ID.
#
# HOW IT WORKS (LINE-BY-LINE):
# - "@mcp.tool": Exposes this function as an MCP tool.
# - "try...except": Catches potential database errors so the server doesn't crash.
# - "with sqlite3.connect(DB_PATH) as conn:": Opens a connection to the database file.
# - "cursor = conn.cursor()": Prepares a cursor to execute SQL commands.
# - "cursor.execute(...)": Runs the UPDATE SQL query to change fields where the ID matches.
# - "cursor.rowcount": Checks how many rows were updated. If 0, the ID was not found.
@mcp.tool
def edit_expense(id:int,amount:float,category:str,date:str,description:str)->dict:
    """Edit expense in database"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE expenses SET amount = ?, category = ?, date = ?, description = ? WHERE id = ?",(amount,category,date,description,id))
            if cursor.rowcount == 0:
                return {"status":"error","message":"Expense ID not found"}
            return {"status":"ok","id":id}
    except Exception as e:
        return {"status":"error","message":str(e)}


# WHY THIS TOOL?
# This tool deletes a specific expense record from the database based on its unique integer ID.
#
# HOW IT WORKS (LINE-BY-LINE):
# - "@mcp.tool": Exposes this function as an MCP tool.
# - "try...except": Safeguards the server from crashing on database errors.
# - "with sqlite3.connect(DB_PATH) as conn:": Opens a connection to the database file.
# - "cursor = conn.cursor()": Prepares a cursor to execute SQL commands.
# - "cursor.execute(...)": Runs the DELETE SQL query for the given ID.
# - "cursor.rowcount": Checks if a row was actually deleted. If 0, the ID was not found.
@mcp.tool
def delete_expense(id:int)->dict:
    """Delete expense from database"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE id = ?",(id,))
            if cursor.rowcount == 0:
                return {"status":"error","message":"Expense ID not found"}
            return {"status":"ok"}
    except Exception as e:
        return {"status":"error","message":str(e)}

# WHY if __name__ == "__main__"?
# This ensures mcp.run() is only called when YOU run this file directly
# (e.g., uv run python main.py).
# When FastMCP Cloud or another platform imports this file to get the "mcp"
# object, it does NOT trigger this block — preventing accidental server starts.
#
# WHAT mcp.run() DOES:
# Starts the HTTP server using uvicorn (a fast async Python web server).
# Your server becomes accessible at: http://0.0.0.0:8000/mcp
# Locally: http://localhost:8000/mcp
# On cloud: https://your-deployment-url/mcp
if __name__=="__main__":
    mcp.run(transport="http",host="0.0.0.0",port=8000)