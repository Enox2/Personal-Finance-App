# Personal-Finanse-App

# Run app
`poetry run uvicorn src.main:app --reload`

# Add migration
`poetry run alembic revision --autogenerate -m "name"`

# Run migration
`poetry run alembic upgrade head`