import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Audit Service")

# Database Setup
DB_PATH = "logs.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            action_type TEXT NOT NULL,
            user_input JSON,
            search_data JSON,
            model_input TEXT,
            model_output TEXT,
            final_output TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Models
class LogEntry(BaseModel):
    action_type: str
    user_input: Optional[Dict[str, Any]] = None
    search_data: Optional[Any] = None
    model_input: Optional[str] = None
    model_output: Optional[str] = None
    final_output: Optional[str] = None

# Routes
@app.post("/logs")
async def create_log(entry: LogEntry):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        user_input_json = json.dumps(entry.user_input) if entry.user_input else None
        search_data_json = json.dumps(entry.search_data) if entry.search_data else None
        
        cursor.execute('''
            INSERT INTO logs (
                timestamp, action_type, user_input, search_data, 
                model_input, model_output, final_output
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.utcnow(),
            entry.action_type,
            user_input_json,
            search_data_json,
            entry.model_input,
            entry.model_output,
            entry.final_output
        ))
        
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Log entry created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
async def get_logs(limit: int = 10):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        
        logs = [dict(row) for row in rows]
        conn.close()
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
