# Ingestion Service Refinement Design

## Objective
Enhance the Excel ingestion process to be production-ready, handling large files, preventing duplicates, and managing errors gracefully.

## Key Strategies

### 1. Chunking (Memory Management)
Instead of loading the entire Excel file into memory:
- Use `pandas.read_excel(chunksize=N)` if compatible, or more likely for Excel, read fully but process in batches if file size permits (Excel is usually not streaming friendly like CSV).
- **Strategy**: Since `read_excel` with `chunksize` works but isn't always efficient for parsing, we will stream the file if possible or stick to row-wise iteration with batch commits.
- **Batch Size**: 1000 records per database commit to balance memory vs I/O.

### 2. Idempotency (Data Integrity)
- **Problem**: Re-running the task shouldn't duplicate valid records.
- **Solution**: 
    - Use `bulk_create(ignore_conflicts=True)` with proper `unique` constraints on models.
    - `Customer.phone_number` is already unique.
    - `Loan.loan_id` is the primary key provided in data.
    - If a record exists, we skip it (idempotent).
    - *Advanced*: Update existing if changed (Upsert)? Requirement implies "Ingest ... data", usually implied strictly adding history. We will stick to "Skip Existing".

### 3. Error Handling (Resilience)
- **Problem**: One bad row shouldn't fail the whole file.
- **Solution**:
    - Wrap individual row parsing in `try-except`.
    - Collect invalid rows in a list.
    - Log entry for every failure with valid reason (e.g., "Missing Salary").
    - **Report**: Return a summary `{"total": 100, "success": 95, "failed": 5, "errors": [...]}`.

## Flow Diagram
1. **Trigger**: User calls Celery task with file path.
2. **Setup**: Initialize counters (success=0, fail=0).
3. **Loop**: Iterate rows.
    - **Validate**: Check required fields.
    - **Transform**: Convert dates, types.
    - **Batch**: Add to batch list.
    - **Commit**: If batch >= 1000, `bulk_create`.
4. **Finalize**: Commit remaining batch.
5. **Report**: Log/Return summary.

## Implementation Changes
- Modify `apps/ingestion/tasks.py`.
- Add validation helper functions.
- Update `bulk_create` usage.
