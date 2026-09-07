import gradio as gr
import pandas as pd
from startup import run as startup_run

# ── startup ────────────────────────────────────────────────────────────────────
startup_run()

from schema_rag import get_relevant_tables
from sql_generator import generate_sql
from sql_executor import execute_sql
from self_corrector import correct_sql

# ── pipeline ───────────────────────────────────────────────────────────────────
def run_query(question):
    if not question.strip():
        return "", "", None, "Please enter a question."

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

    # build status message
    if corrected:
        status = f"✅ Self-corrected on attempt {correction_attempts}"
    elif result["success"]:
        status = f"✅ Success — {len(result['rows'])} rows returned"
    else:
        status = f"❌ Failed: {result.get('error', 'Unknown error')}"

    # build dataframe
    if result["success"] and result["rows"]:
        df = pd.DataFrame(result["rows"], columns=result["columns"])
    else:
        df = pd.DataFrame()

    return sql, status, df, ""


# ── CSS ────────────────────────────────────────────────────────────────────────
css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

body, .gradio-container {
    background: #070B14 !important;
    font-family: 'Inter', sans-serif !important;
}

.gradio-container {
    max-width: 900px !important;
    margin: 0 auto !important;
}

/* hero */
.hero-title {
    text-align: center;
    padding: 48px 0 8px;
}
.hero-title h1 {
    font-size: 48px !important;
    font-weight: 700 !important;
    letter-spacing: -2px !important;
    background: linear-gradient(135deg, #F0F9FF 0%, #7DD3FC 50%, #38BDF8 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    margin: 0 !important;
}
.hero-sub {
    text-align: center;
    color: #64748B !important;
    font-size: 15px !important;
    margin-bottom: 8px !important;
}
.hero-badge {
    text-align: center;
    margin-bottom: 32px !important;
}
.hero-badge span {
    display: inline-block;
    background: rgba(56,189,248,0.07);
    border: 1px solid rgba(56,189,248,0.2);
    color: #38BDF8;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 5px 16px;
    border-radius: 20px;
}

/* input */
.gr-textbox textarea, .gr-textbox input {
    background: #0F1623 !important;
    border: 1px solid #1A2235 !important;
    border-radius: 10px !important;
    color: #CBD5E1 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
}
.gr-textbox textarea:focus, .gr-textbox input:focus {
    border-color: #38BDF8 !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.1) !important;
}

/* button */
.gr-button-primary {
    background: linear-gradient(135deg, #0369A1, #0284C7) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
}
.gr-button-primary:hover {
    background: linear-gradient(135deg, #0284C7, #0EA5E9) !important;
    transform: translateY(-1px) !important;
}

/* sql output */
.sql-output textarea {
    background: #050810 !important;
    border: 1px solid #1A2235 !important;
    border-left: 3px solid #38BDF8 !important;
    border-radius: 10px !important;
    color: #7DD3FC !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
}

/* status */
.status-output textarea {
    background: #0F1623 !important;
    border: 1px solid #1A2235 !important;
    border-radius: 10px !important;
    color: #CBD5E1 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
}

/* dataframe */
.gr-dataframe {
    background: #0F1623 !important;
    border: 1px solid #1A2235 !important;
    border-radius: 10px !important;
}
.gr-dataframe table { background: #0F1623 !important; }
.gr-dataframe th {
    background: #070B14 !important;
    color: #64748B !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 10px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
}
.gr-dataframe td {
    color: #CBD5E1 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    border-bottom: 1px solid #0F1623 !important;
}

/* labels */
label, .gr-block-label {
    color: #475569 !important;
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    font-family: 'Inter', sans-serif !important;
}

/* examples */
.gr-samples-table {
    background: #0F1623 !important;
    border: 1px solid #1A2235 !important;
    border-radius: 10px !important;
}
.gr-samples-table td {
    color: #64748B !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    cursor: pointer !important;
}
.gr-samples-table tr:hover td {
    background: rgba(56,189,248,0.05) !important;
    color: #38BDF8 !important;
}
"""

# ── interface ──────────────────────────────────────────────────────────────────
with gr.Blocks(css=css, title="SQL Agent") as demo:

    gr.HTML("""
    <div class="hero-title"><h1>Ask Your Database</h1></div>
    <div class="hero-sub"><p>Natural language → SQL → Results &nbsp;·&nbsp; Powered by Claude + ChromaDB</p></div>
    <div class="hero-badge"><span>⚡ RAG · LLM · Self-Correction</span></div>
    """)

    with gr.Row():
        question_input = gr.Textbox(
            placeholder="e.g. Show me all orders that haven't been delivered yet...",
            label="Ask a question",
            lines=1,
            scale=5
        )
        run_btn = gr.Button("Run ⚡", variant="primary", scale=1)

    gr.Examples(
        examples=[
            ["Show all pending orders"],
            ["Which products have rating above 4?"],
            ["Top 3 customers by number of orders"],
            ["Show all payments that failed"],
            ["Products with less than 40 items in stock"],
            ["Which orders have been returned?"],
        ],
        inputs=question_input,
        label="Try an example"
    )

    with gr.Row():
        sql_output = gr.Textbox(
            label="Generated SQL",
            lines=4,
            elem_classes=["sql-output"],
            interactive=False
        )
        status_output = gr.Textbox(
            label="Status",
            lines=4,
            elem_classes=["status-output"],
            interactive=False
        )

    results_output = gr.Dataframe(
        label="Query Results",
        interactive=False,
        wrap=True
    )

    error_output = gr.Textbox(visible=False)

    run_btn.click(
        fn=run_query,
        inputs=question_input,
        outputs=[sql_output, status_output, results_output, error_output]
    )

    question_input.submit(
        fn=run_query,
        inputs=question_input,
        outputs=[sql_output, status_output, results_output, error_output]
    )

demo.launch()