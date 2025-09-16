from src.app import query, QueryRequest

print(
    query(
        QueryRequest(
            session_id="214",
            query="find me hospitals in ohio and number of beds in them",
        )
    )
)
