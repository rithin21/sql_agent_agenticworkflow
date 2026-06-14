import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from pydantic import BaseModel
from db import get_engine, set_connection
from sqlalchemy import inspect
from agno.agent import Agent
from agno.models.groq import Groq
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class connection(BaseModel):
    connection_link: str

class QueryRequest(BaseModel):
    prompt: str
    connectionString: str

CURRENT_ENGINE = None


LATEST_SQL_RESULT = None


def _patch_agno_null_tool_arguments():
    """Agno 2.6 can pass the literal string "null" for no-arg tool calls."""
    import agno.utils.functions as agno_functions
    import agno.utils.tools as agno_tools

    original_get_function_call = agno_functions.get_function_call

    def patched_get_function_call(name, arguments=None, call_id=None, functions=None):
        if arguments in (None, "", "null", "None"):
            arguments = "{}"
        return original_get_function_call(name, arguments, call_id, functions)

    agno_functions.get_function_call = patched_get_function_call
    agno_tools.get_function_call = patched_get_function_call


_patch_agno_null_tool_arguments()




def list_tables():
    """
    List all tables in the connected database along with their column names and types.

    Returns:
        A dictionary mapping each table name to its list of columns.
    """
    if CURRENT_ENGINE is None:
        raise Exception("No database connection established.")

    inspector = inspect(CURRENT_ENGINE)
    schema = {}
    for table in inspector.get_table_names():
        schema[table] = [
            {"name": col["name"], "type": str(col["type"])}
            for col in inspector.get_columns(table)
        ]
    return schema


def get_table_schema(table_name: str):
    """
    Get the column names and types for a specific table.

    Args:
        table_name: The exact name of the table to inspect.

    Returns:
        Table name and its column definitions.
    """
    if CURRENT_ENGINE is None:
        raise Exception("No database connection established.")

    inspector = inspect(CURRENT_ENGINE)
    columns = inspector.get_columns(table_name)
    return {
        "table": table_name,
        "columns": [
            {"name": col["name"], "type": str(col["type"])}
            for col in columns
        ]
    }


def execute_sql(query: str):
    """
    Execute a SQL query against the connected database.

    Args:
        query: A valid SQL query string.

    Returns:
        Query results as a list of JSON rows, or a success message for non-SELECT queries.
    """
    print("EXECUTING:", query)
    global LATEST_SQL_RESULT
    if CURRENT_ENGINE is None:
        raise Exception("No database connection established.")

    with CURRENT_ENGINE.begin() as conn:
        result = conn.execute(text(query))

        if result.returns_rows:
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            LATEST_SQL_RESULT = rows
            return {"type": "table", "data": rows}

    return {"type": "message", "data": "Query executed successfully"}




def _make_agent() -> Agent:
    """Create a fresh Agent instance (new session) for each request."""
    return Agent(
        model=Groq(
            id="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.0,
        ),
        tools=[list_tables, get_table_schema, execute_sql],
        markdown=False,
        instructions="""
You are a SQL assistant with three tools: list_tables, get_table_schema, and execute_sql.

Workflow you MUST follow for every user question:
1. Call list_tables() with no arguments to discover all available tables and their columns.
2. If you need more column detail for a specific table, call get_table_schema(table_name).
3. Write a SQL query based on the schema and call execute_sql(query) to run it.
4. Summarise the results clearly in plain text.

NEVER guess table or column names. NEVER skip tool calls.
""",
    )



agent = _make_agent()




@app.post("/verifyconnection")
def verifyconnection(connect: connection):
    try:
        global CURRENT_ENGINE
        CURRENT_ENGINE = create_engine(connect.connection_link)
        with CURRENT_ENGINE.connect() as conn:
            conn.execute(text("SELECT 1"))

        set_connection(connect.connection_link)

        return {
            "connection_name": CURRENT_ENGINE.url.database,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/process_query")
def query(req: QueryRequest):
    global LATEST_SQL_RESULT, CURRENT_ENGINE
    LATEST_SQL_RESULT = None

    if req.connectionString:
        try:
            CURRENT_ENGINE = create_engine(req.connectionString)
            with CURRENT_ENGINE.connect() as conn:
                conn.execute(text("SELECT 1"))
            set_connection(req.connectionString)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Database connection failed: {str(e)}"
            )

    if CURRENT_ENGINE is None:
        raise HTTPException(status_code=400, detail="No database connection established.")


    global agent
    agent = _make_agent()
    try:
        run_output = agent.run(req.prompt)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent failed to process query: {str(e)}"
        )

    answer = run_output.get_content_as_string() if run_output.content is None else run_output.content

    res_data = {"answer": answer or "Done."}
    if LATEST_SQL_RESULT is not None:
        res_data["data"] = LATEST_SQL_RESULT

    return res_data


# db_url="postgresql://postgres:21wdspvabd@localhost:5432/sql_agent_demo"
