from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import sqlite3
import json
from datetime import datetime, timezone

app = FastAPI()
DB_PATH = "analytics.db"


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
