import pandas as pd
from app.utils.query_parser import parse_and_filter

# Global in-memory DataFrame
csv_df = pd.DataFrame()

def ingest_and_index_doc(file) -> bool:
    try:
        global csv_df
        file.file.seek(0)  # Just in case pointer isn't at start
        csv_df = pd.read_csv(file.file)
        print("✅ Uploaded file indexed:", file.filename)
        return True
    except Exception as e:
        print("❌ Failed to ingest file:", e)
        return False

def query_structured_data(user_query: str) -> str:
    global csv_df
    if csv_df.empty:
        return "No data loaded yet."

    filtered_df = parse_and_filter(csv_df, user_query)
    if filtered_df is None or filtered_df.empty:
        return ""

    return "\n\n".join(
        filtered_df.astype(str).apply(
            lambda row: "\n".join([f"{k}: {v}" for k, v in row.items()]), axis=1
        )
    )

def query_rag_context(user_query: str) -> str:
    return query_structured_data(user_query)

