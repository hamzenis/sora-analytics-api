from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
import sqlite3
import json
from datetime import datetime, timezone

app = FastAPI()
DB_PATH = "./analytics.db"


# Initialize database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            device TEXT,
            app_version TEXT,
            module_name TEXT,
            module_version TEXT,
            data TEXT
        )
    """
    )
    conn.commit()
    conn.close()


init_db()


@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sora Analytics API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            p { font-size: 1.2em; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>Welcome to the Sora Analytics API</h1>
        <p>Please visit <a href="/docs">/docs</a> for API documentation.</p>
        <p>For more information, please visit the <a href="https://github.com/hamzenis/sora-analytics-api">GitHub repository</a>.</p>
        <p>Analytics API: <a href="http://151.106.3.14:47474/analytics">http://151.106.3.14:47474/analytics</a></p>
        <p>Analytics API (HTML): <a href="http://151.106.3.14:47474/analytics?format=html">http://151.106.3.14:47474/analytics?format=html</a></p>
    </body>
    </html>
    """


@app.post("/analytics")
async def receive_analytics(request: Request):
    try:
        data = await request.json()

        event = data.get("event", "unknown_event")
        timestamp = datetime.utcnow().isoformat() # Maybe use datetime.now(timezone.utc).isoformat() instead, cuz deprecated
        device = data.get("device", "unknown_device")
        app_version = data.get("app_version", "unknown_version")
        module_name = data.get("module_name", "unknown_module")
        module_version = data.get("module_version", "unknown_version")

        # Store additional flexible data in JSON field
        extra_data = json.dumps(data.get("data", {}))

        # Insert into SQLite
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO analytics (event, timestamp, device, app_version, module_name, module_version, data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                event,
                timestamp,
                device,
                app_version,
                module_name,
                module_version,
                extra_data,
            ),
        )

        conn.commit()
        conn.close()

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Analytics data saved successfully",
                "event": event,
                "timestamp": timestamp,
            },
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Failed to save analytics data",
                "error": str(e),
            },
        )


@app.get("/analytics")
async def get_analytics(format: str = "json", filter: str = None, search: str = None):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        query = "SELECT * FROM analytics"
        conditions = []
        params = []

        if filter == "errors":
            conditions.append("event LIKE ?")
            params.append("%error%")
        elif filter == "watch":
            conditions.append("event LIKE ?")
            params.append("%watch%")
        elif filter == "search":
            conditions.append("event LIKE ?")
            params.append("%search%")
        
        if search:
            conditions.append("(event LIKE ? OR device LIKE ? OR app_version LIKE ? OR module_name LIKE ? OR module_version LIKE ? OR data LIKE ?)")
            search_param = f"%{search}%"
            params.extend([search_param] * 6)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY timestamp DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        # Convert rows to list of dictionaries
        analytics_data = [
            {
                "id": row[0],
                "event": row[1],
                "timestamp": row[2],
                "device": row[3],
                "app_version": row[4],
                "module_name": row[5],
                "module_version": row[6],
                "data": json.loads(row[7]) if row[7] else {}
            }
            for row in rows
        ]

        if format == "html":
            # Generate HTML table
            html_content = """
            <html>
            <head>
                <title>Analytics Data</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    table { width: 100%; border-collapse: collapse; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
                    th { background-color: #f2f2f2; }
                    tr:nth-child(even) { background-color: #f9f9f9; }
                    tr:hover { background-color: #ddd; }
                    .button { padding: 10px 20px; margin: 5px; text-decoration: none; color: white; background-color: #007bff; border: none; border-radius: 5px; cursor: pointer; }
                    .button:hover { background-color: #0056b3; }
                </style>
            </head>
            <body>
                <h1>Analytics Data</h1>
                <div>
                    <button class="button" onclick="window.location.href='/analytics?format=html&filter=errors'">Filter Errors</button>
                    <button class="button" onclick="window.location.href='/analytics?format=html&filter=watch'">Filter Watch</button>
                    <button class="button" onclick="window.location.href='/analytics?format=html&filter=search'">Filter Search</button>
                    <button class="button" onclick="window.location.href='/analytics?format=html'">Clear Filters/Search</button>
                    <input type="text" id="searchField" placeholder="Search...">
                    <button class="button" onclick="searchAnalytics()">Search</button>
                </div>
                <script>
                    function searchAnalytics() {
                        const searchValue = document.getElementById('searchField').value;
                        window.location.href = `/analytics?format=html&search=${searchValue}`;
                    }
                </script>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Event</th>
                        <th>Timestamp</th>
                        <th>Device</th>
                        <th>App Version</th>
                        <th>Module Name</th>
                        <th>Module Version</th>
                        <th>Data</th>
                    </tr>
            """
            for data in analytics_data:
                row_color = "#FFCCCC" if "error" in data['event'].lower() else "#FFFFFF"
                html_content += f"""
                    <tr style="background-color: {row_color};">
                        <td style="text-align: center;">{data['id']}</td>
                        <td style="text-align: center;">{data['event']}</td>
                        <td style="text-align: center;">{datetime.fromisoformat(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}</td>
                        <td style="text-align: center;">{data['device']}</td>
                        <td style="text-align: center;">{data['app_version']}</td>
                        <td style="text-align: center;">{data['module_name']}</td>
                        <td style="text-align: center;">{data['module_version']}</td>
                        <td style="text-align: center;">{json.dumps(data['data'])}</td>
                    </tr>
                """
            html_content += """
                </table>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)

        return JSONResponse(
            status_code=200,
            content=analytics_data
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Failed to retrieve analytics data",
                "error": str(e),
            },
        )