import os 
import anthropic
from dotenv import load_dotenv
from sql_executor import execute_sql

load_dotenv() # Parse a .env file and then load all the variables found as environment variables.

client = anthropic.Anthropic(api_key = os.getenv("ANTHROPIC_API_KEY"))


def correct_sql(question, failed_sql, error_message, relevant_tables, max_attempts = 3): #retry limit to prevent infinite loops, and escalation to a human when all attempts are exhausted. max_attempts
    # building schema context same way as before
    schema_context = ""
    for table in relevant_tables:
        schema_context += f"Table: {table['table']}\n"
        schema_context += f"Description: {table['description']}\n\n"

    # build conversation history with the failure included
    messages = [
        {
            "role": "user",
            "content": f"""You are a SQL expert working with an e-commerce database.
Schema Context:
{schema_context}
Question: {question}

Rules:
- Return only SQL query, no explanation
- Use standard SQL syntax
- Use proper table and column names from the schema

SQL Query:"""
        },
        {
            "role": "assistant",
            "content": failed_sql
        },
        {
            "role": "user",
            "content": f"""That query failed with this error:
{error_message}
Please fix the SQL query. Return ONLY the corrected SQL, nothing else."""
        }
    ]

    # retry loop
    for attempt in range(max_attempts):
        response = client.messages.create(
            model = "claude-sonnet-4-6",
            max_tokens = 1024,
            messages = messages
        )

        corrected_sql = response.content[0].text.strip()
        corrected_sql = corrected_sql.replace("```sql", "").replace("```","").strip()

        # actually test if the corrected SQL works

        test_result = execute_sql(corrected_sql)
        if test_result["success"]:
            return corrected_sql, attempt + 1

        # if it still fails, add this attempt to the conversation and retry
        messages.append({"role": "assistant", "content": corrected_sql})
        messages.append({
            "role": "user",
            "content": f"""Still failing with: {test_result['error']}
                    Please fix it again. Return ONLY the SQL."""
        })

    return None, max_attempts


if __name__ == "__main__":
    from schema_rag import get_relevant_tables
    from sql_executor import execute_sql

    question = "Show me all orders that haven't been delivered yet"

    # get relevant tables
    relevant_tables = get_relevant_tables(question)

    # deliberately broken SQL to test self-correction
    broken_sql = "SELECT * FROM orders WHERE stats = 'pending'"

    print(f"Broken SQL: {broken_sql}")

    # execute the broken SQL - should fail
    result = execute_sql(broken_sql)
    print(f"Error: {result['error']}")

    # now self-correct
    corrected_sql, attempts = correct_sql(question, broken_sql, result['error'], relevant_tables)

    print(f"\nCorrected SQL (attempt {attempts}):")
    print(corrected_sql)

    # execute the corrected SQL
    final_result = execute_sql(corrected_sql)
    print(f"\nColumns: {final_result['columns']}")
    print(f"Rows:")
    for row in final_result['rows']:
        print(row)