from decimal import Decimal
from math import isnan
from typing import cast

from pandas import DataFrame
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.csv.models import CSVFile
from src.domains.processing.parsers.categoriser import RuleLike, categorise_transactions
from src.domains.processing.parsers.pkobp_csv import prepare_dataframe
from src.domains.rules.service import RulesService
from src.domains.transactions.models import Transaction


class ProcessingService:
    def __init__(self, session: AsyncSession, rules_service: RulesService):
        self.session = session
        self.rules_service = rules_service

    async def start_processing_file(self, file_id: int) -> dict[str, int]:
        file_model = await self.get_csv_file(file_id)
        if file_model is None:
            raise ValueError("CSV file not found")

        df = prepare_dataframe(file_model)
        rules = await self.rules_service.list_rules()
        df = categorise_transactions(df, cast(list[RuleLike], cast(object, rules)))

        await self.replace_transactions(file_model.id, df)

        uncategorised = int(df["category_id"].isna().sum())
        return {"processed": len(df), "uncategorised": uncategorised}

    async def get_csv_file(self, file_id: int) -> CSVFile | None:
        result = await self.session.execute(select(CSVFile).where(CSVFile.id == file_id))
        return result.scalar_one_or_none()

    async def replace_transactions(self, csv_file_id: int, df: DataFrame) -> None:
        await self.session.execute(
            delete(Transaction).where(Transaction.csv_file_id == csv_file_id)
        )

        transactions = [
            Transaction(
                csv_file_id=csv_file_id,
                transaction_date=row["transaction_date"],
                value_date=row["value_date"],
                transaction_type=row["transaction_type"],
                amount=Decimal(str(row["amount"])),
                currency=row["currency"],
                merchant=row.get("merchant", "") or "",
                category_id=self._parse_category_id(row.get("category_id")),
                transaction_description=row["transaction_description"],
            )
            for _, row in df.iterrows()
        ]

        self.session.add_all(transactions)
        await self.session.commit()

    @staticmethod
    def prepare_dataframe(file_model: CSVFile | None) -> DataFrame:
        return prepare_dataframe(file_model)

    @staticmethod
    def _parse_category_id(value: int | float | str | None) -> int | None:
        if value is None:
            return None
        if isinstance(value, float) and isnan(value):
            return None
        return int(value)
