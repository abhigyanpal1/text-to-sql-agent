import sqlite3

def execute_sql(sql_query):
    try:
        # connect to the database
        conn = sqlite3.connect("ecommerce.db")
        cursor = conn.cursor()

        # execute the generated SQL 
        cursor.execute(sql_query)

        # fetch all results
        results = cursor.fetchall()

        # get column names from the cursor
        columns = [description[0] for description in cursor.description]

        conn.close()
        return {"success": True, "columns": columns, "rows": results}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    from sql_generator import generate_sql
    from schema_rag import get_relevant_tables

    question = "Show me all the orders that haven't been delivered yet"

    relevant_tables = get_relevant_tables(question)
    sql = generate_sql(question, relevant_tables)
    result = execute_sql(sql)

    print(f"Question: {question}")
    print(f"\nSQL:\n{sql}")
    print(f"\nColumns: {result['columns']}")
    print(f"\nRows:")
    for row in result['rows']:
        print(row)
        