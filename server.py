from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

from schema_rag import get_relevant_tables
from sql_generator import generate_sql
from sql_executor import execute_sql
from self_corrector import correct_sql
from startup import run as startup_run

startup_run()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def serve_ui():
    return FileResponse("index.html")

@app.post("/query")
def run_query(req: QueryRequest):
    question = req.question

    # step 1 - RAG
    relevant_tables = get_relevant_tables(question)

    # step 2 - generate SQL
    sql = generate_sql(question, relevant_tables)

    # step 3 - execute
    result = execute_sql(sql)
    corrected = False
    correction_attempts = 0

    # step 4 - self correct if needed
    if not result["success"]:
        fixed_sql, correction_attempts = correct_sql(
            question, sql, result["error"], relevant_tables
        )
        if fixed_sql:
            sql = fixed_sql
            result = execute_sql(sql)
            corrected = True

    if result["success"]:
        return {
            "success": True,
            "sql": sql,
            "columns": result["columns"],
            "rows": result["rows"],
            "corrected": corrected,
            "correction_attempts": correction_attempts,
            "tables_used": [t["table"] for t in relevant_tables]
        }
    else:
        return {
            "success": False,
            "sql": sql,
            "error": result.get("error", "Unknown error"),
            "corrected": corrected
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)