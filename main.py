# ============================================================
# REMOTE MCP SERVER — EXPENSE TRACKER (ASYNC VERSION)
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
# ============================================================
# ⚡ WHY ASYNC CODE INSTEAD OF SYNC? (SYNC vs ASYNC EXPLAINED)
# ============================================================
#
# PEHLE KYA THA (Synchronous):
# - Standard `import sqlite3` & `def add_expense(...)`
# - Synchronous code executes linearly. Jab ek query run hoti hai, tab tak baki requests block rehti hain.
# - Remote Server pe jab multiple users ya AI agents ek saath tool call karenge, toh Sync code se server slow ho jaata hai.
#
# AB KYA HAI (Asynchronous):
# - `import aiosqlite` & `async def add_expense(...)` & `await conn.execute(...)`
# - Async (Non-Blocking) code Python Event Loop ka use karta hai. Jab SQLite DB disk operation kar raha hota hai,
#   tab server freeze hone ki jagah doosre user ki incoming HTTP request ko process kar sakta hai!
#
# KYUN ZAROORI HAI?
# - FastMCP ka underlying server (Uvicorn/Starlette) Async-first hai.
# - High concurrency aur production-grade Remote MCP Servers ke liye ASYNC best practice hoti hai!
# ============================================================

from fastmcp import FastMCP
import aiosqlite
import os

# WHY DB_PATH LIKE THIS?
# On Cloud platforms (Linux), the directory containing the code is read-only!
# Writing to code directory causes "sqlite3.OperationalError: attempt to write a readonly database".
# Therefore, on Linux/Cloud (os.name == 'posix'), we store the database in the writable '/tmp' directory.
# On Windows (Local), it stores it next to the script as usual.
if os.name == 'posix':
    DB_PATH = "/tmp/Expense.db"
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "Expense.db")

# WHY FastMCP(name='expense-tracker')?
# Creates the MCP server instance with a display name.
# This name appears in MCP Inspector and MCP client listings.
mcp=FastMCP(name='expense-tracker')


# WHY THIS FUNCTION IS ASYNC?
# 1. PEHLE: `def initdb()` with `sqlite3.connect()`. Blocking execution!
# 2. AB: `async def initdb()` with `async with aiosqlite.connect()`.
# 3. KYUN: Server startup par table asynchronously non-blocking way mein initialize hoga.
#
# HOW IT WORKS (LINE-BY-LINE):
# - "async with aiosqlite.connect(DB_PATH) as conn:": Asynchronously opens connection.
# - "await conn.execute(...)": Awaits SQL query execution without blocking the main event loop.
# - "await conn.commit()": Awaits writing changes to disk.
async def initdb():
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date DATE NOT NULL,
            description TEXT
        )
        """)
        await conn.commit()


# WHY THIS TOOL IS ASYNC?
# PEHLE: `def add_expense(...)` (Sync / Blocking)
# AB: `async def add_expense(...)` (Async / Non-blocking)
# KYUN: Multiple users simultaneously expense add kar sakte hain without waiting for DB locks!
#
# HOW IT WORKS (LINE-BY-LINE):
# - "@mcp.tool": Exposes function as MCP tool. FastMCP natively supports async functions!
# - "async with aiosqlite.connect(DB_PATH) as conn:": Non-blocking DB connection.
# - "cursor = await conn.cursor()": Asynchronously creates cursor.
# - "await cursor.execute(...)": Non-blocking insert operation.
# - "await conn.commit()": Commits transaction to database.
# - "cursor.lastrowid": Returns inserted ID.
@mcp.tool
async def add_expense(amount: float, category: str, date: str, description: str) -> dict:
    """Add expense to database"""
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                "INSERT INTO expenses (amount,category,date,description) VALUES (?,?,?,?)",
                (amount, category, date, description)
            )
            await conn.commit()
            return {"status": "ok", "id": cursor.lastrowid}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# WHY THIS TOOL IS ASYNC?
# PEHLE: `def list_expenses()` (Sync fetch)
# AB: `async def list_expenses()` (Async fetch)
# KYUN: DB reading IO operation hai. Await karne par doosri HTTP requests block nahi honge.
#
# HOW IT WORKS (LINE-BY-LINE):
# - "async with aiosqlite.connect(DB_PATH) as conn:": Non-blocking connection.
# - "cursor = await conn.cursor()": Asynchronously prepares cursor.
# - "await cursor.execute("SELECT * FROM expenses")": Non-blocking query execution.
# - "rows = await cursor.fetchall()": Asynchronously retrieves all fetched rows.
@mcp.tool
async def list_expenses() -> list:
    """Get all expenses from database"""
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.cursor()
        await cursor.execute("SELECT * FROM expenses")
        rows = await cursor.fetchall()
        return rows


# WHY THIS TOOL IS ASYNC?
# PEHLE: `def edit_expense(...)` (Sync update)
# AB: `async def edit_expense(...)` (Async update)
# KYUN: Non-blocking UPDATE operation.
#
# HOW IT WORKS (LINE-BY-LINE):
# - "await cursor.execute(...)": Runs non-blocking UPDATE query.
# - "await conn.commit()": Commits the update asynchronously.
# - "cursor.rowcount": Checks modified rows count.
@mcp.tool
async def edit_expense(id: int, amount: float, category: str, date: str, description: str) -> dict:
    """Edit expense in database"""
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            cursor = await conn.cursor()
            await cursor.execute(
                "UPDATE expenses SET amount = ?, category = ?, date = ?, description = ? WHERE id = ?",
                (amount, category, date, description, id)
            )
            await conn.commit()
            if cursor.rowcount == 0:
                return {"status": "error", "message": "Expense ID not found"}
            return {"status": "ok", "id": id}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# WHY THIS TOOL IS ASYNC?
# PEHLE: `def delete_expense(...)` (Sync delete)
# AB: `async def delete_expense(...)` (Async delete)
# KYUN: Non-blocking DELETE operation.
#
# HOW IT WORKS (LINE-BY-LINE):
# - "await cursor.execute(...)": Runs non-blocking DELETE query.
# - "await conn.commit()": Commits row deletion asynchronously.
@mcp.tool
async def delete_expense(id: int) -> dict:
    """Delete expense from database"""
    try:
        async with aiosqlite.connect(DB_PATH) as conn:
            cursor = await conn.cursor()
            await cursor.execute("DELETE FROM expenses WHERE id = ?", (id,))
            await conn.commit()
            if cursor.rowcount == 0:
                return {"status": "error", "message": "Expense ID not found"}
            return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# FastMCP Server startup handling async initdb before running HTTP server
if __name__ == "__main__":
    import asyncio
    asyncio.run(initdb())
    mcp.run(transport="http", host="0.0.0.0", port=8000)