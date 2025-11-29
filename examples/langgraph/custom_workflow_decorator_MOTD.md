---
messages:
  - "ETL pipeline ready to process! 🔄"
  - "Extracting, transforming, loading... Let's go! 🚀"
  - "Data transformation engines online! ⚙️"
  - "Ready to move data through the pipeline! 📦"
  - "ETL workflow standing by! 💪"
  - "Time to extract some value from data! 💎"
  - "Pipeline activated - let the data flow! 🌊"
---

# Custom Workflow - ETL Pipeline

{message}

## Workflow Steps

1. **extract** - Read data from source file
2. **transform** - Apply business transformations
3. **load** - Store results in database

## Configuration

- **Queue:** etl-pipeline
- **Timeout:** 600s (10 minutes)
- **Checkpointing:** Enabled
- **State:** Custom ETLState

## State Structure

### Required fields
- `source_path`: str
- `load_status`: str
- `errors`: list[str] (accumulates)

### Optional fields
- `extracted_data`: dict
- `transformed_data`: dict
- `row_count`: int
- `metadata`: dict

## Example Jobs

### 1. Process CSV file

```bash
aimq send etl-pipeline '{
  "source_path": "data/sales_2024.csv",
  "load_status": "",
  "errors": []
}'
```

### 2. Process JSON data

```bash
aimq send etl-pipeline '{
  "source_path": "exports/user_data.json",
  "load_status": "",
  "errors": []
}'
```

### 3. Process text file

```bash
aimq send etl-pipeline '{
  "source_path": "logs/application.log",
  "load_status": "",
  "errors": []
}'
```

### 4. Resumable ETL (with thread_id)

```bash
aimq send etl-pipeline '{
  "source_path": "large_files/yearly_data.csv",
  "thread_id": "etl-batch-2024-10",
  "load_status": "",
  "errors": []
}'
```

## Error Handling

Errors accumulate in state['errors'] using the add reducer.
This allows all steps to report errors without overwriting.
Final state contains complete error history for debugging.

## Decorator Benefits

- Custom state definition (ETLState)
- Type safety with TypedDict
- Automatic checkpointing
- Error accumulation pattern
- Clean separation of extract/transform/load logic
