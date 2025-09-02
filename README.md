## **Running the app**

1. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**  
   Copy `.env.example` → `.env` and fill in your Snowflake + LLM credentials.

3. **Index your schema**  
   ```bash
   python scripts/index_schema.py
   ```

4. **Run the API**  
   ```bash
   uvicorn src.app:app --reload --port 8000
   ```

---

## **Example request**

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc123",
    "query": "Show me the top 5 customers by revenue last quarter"
  }'
```

**Example response:**
```json
{
  "session_id": "abc123",
  "intent": "simple_query",
  "sql": "SELECT customer_id, SUM(revenue) AS total_revenue FROM SALES.PUBLIC.ORDERS WHERE order_date >= DATEADD(quarter, -1, CURRENT_DATE) GROUP BY customer_id ORDER BY total_revenue DESC LIMIT 5",
  "columns": ["CUSTOMER_ID", "TOTAL_REVENUE"],
  "rows": [
    ["CUST001", 120000],
    ["CUST045", 115000]
  ],
  "error": null,
  "clarifying_question": null,
  "awaiting_clarification": false,
  "metadata": {"reason": "Direct aggregation query"}
}
```