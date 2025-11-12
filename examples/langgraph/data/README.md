# Test Data for LangGraph Examples

This directory contains sample data files for testing the LangGraph examples.

## Available Test Files

### 1. sample_sales.json
A comprehensive Q4 2024 sales report with:
- Report metadata (period, department, region)
- Summary statistics (revenue, orders, growth)
- Monthly breakdowns
- Top products analysis
- Sales team performance metrics
- Customer segmentation data
- Anomaly detection highlights

**Test with:**
```bash
# Terminal 1: Start the worker
uv run python examples/langgraph/custom_agent_decorator.py

# Terminal 2: Send analysis job
aimq send data-processor '{
  "messages": [
    {"role": "user", "content": "examples/langgraph/data/sample_sales.json"}
  ],
  "tools": [],
  "iteration": 0,
  "errors": []
}'
```

### 2. sample_sales.csv
Transaction-level sales data with columns:
- date, sales_rep, product, category
- quantity, unit_price, total_amount
- region, customer_segment

**Test with:**
```bash
# Terminal 1: Start the worker
uv run python examples/langgraph/custom_agent_decorator.py

# Terminal 2: Send analysis job
aimq send data-processor '{
  "messages": [
    {"role": "user", "content": "examples/langgraph/data/sample_sales.csv"}
  ],
  "tools": [],
  "iteration": 0,
  "errors": []
}'
```

## What the Agent Will Analyze

The data processor agent (custom_agent_decorator.py) will:

### For JSON files:
1. Parse the JSON structure
2. Validate the schema
3. Extract important fields
4. Identify key insights and patterns
5. Flag any anomalies or notable trends

### For CSV files:
1. Identify column structure
2. Summarize data trends
3. Calculate statistics (totals, averages, etc.)
4. Flag any anomalies
5. Provide actionable insights

## Expected Output

The agent will:
1. Read the file from local storage (or Supabase if configured)
2. Analyze the data using Mistral AI (mistral-large-latest)
3. Store results in the `analysis_results` table
4. Return a comprehensive analysis with insights

## Database Setup

Before testing, ensure the analysis_results table exists:

```sql
CREATE TABLE analysis_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  analysis TEXT NOT NULL,
  source_file TEXT NOT NULL,
  processed_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Tips for Testing

1. **Local File Testing**: These files are in the repository, so the agent can read them directly from the file system
2. **Custom Data**: Create your own JSON/CSV files following these formats
3. **Resumable Jobs**: Use `thread_id` for long-running analyses that might need to be resumed
4. **Error Handling**: Try invalid paths or malformed data to test error handling

## Example Analysis Questions

When creating test files, the agent can help answer:
- What are the key trends in this data?
- Which metrics show unusual patterns?
- What actionable insights can be derived?
- Are there any data quality issues?
- What correlations exist between variables?
