# Personal-Finanse-App

# Run app
`poetry run uvicorn src.main:app --reload`

# Add migration
`poetry run alembic revision --autogenerate -m "name"`

# Run migration
`poetry run alembic upgrade head`

# Environment
- `UPLOAD_DIR` (optional): upload directory path; defaults to `data/uploads` under the project root.

# ETL rules
- `POST /etl/rules` create regex-based categorisation rule.
- `GET /etl/rules` list all rules.
- `PUT /etl/rules/{rule_id}` update a rule.
- `DELETE /etl/rules/{rule_id}` delete a rule.
- `GET /etl/transactions/uncategorised` list uncategorised transactions.
- `POST /etl/transactions/recategorise` reapply rules to existing transactions.

# Demo categoriser script
`poetry run python scripts/etl_categoriser_demo.py`
