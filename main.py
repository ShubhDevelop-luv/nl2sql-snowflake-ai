from src.app import query, QueryRequest

query(
    QueryRequest(
        session_id="212", query="Find hospitals and their number of beds in ohio"
    )
)
