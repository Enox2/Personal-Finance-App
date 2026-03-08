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
- `POST /rules` create regex-based categorisation rule (`pattern`, `category_id`, `priority`).
- `GET /rules` list all rules.
- `PUT /rules/{rule_id}` update a rule.
- `DELETE /rules/{rule_id}` delete a rule.
- Invalid `category_id` in rule create/update returns `400 Bad Request`.

# Transactions
- `GET /transactions/uncategorised` list transactions where `category_id` is null.

# Processing
- `POST /processing/process/{file_id}` parse uploaded CSV and apply rules.

# Seeded categories
- Migration seeds: `groceries`, `subscriptions`, `transport`, `utilities`, `housing`, `salary`, `other`.

# Demo categoriser script
`poetry run python scripts/etl_categoriser_demo.py`
