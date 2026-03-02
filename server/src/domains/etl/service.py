from decimal import Decimal

import pandas as pd
from pandas import DataFrame
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.csv.models import CSVFile
from src.domains.etl.models import CategoryRule, Transaction
from src.domains.etl.parsers.categoriser import categorise_transactions
from src.domains.etl.parsers.pkobp_csv import prepare_dataframe
from src.domains.etl.schemas import CategoryRuleCreate, CategoryRuleUpdate


class ProcessFilesApplicationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def start_processing_file(self, file_id: int) -> dict[str, int]:
        file_model = await self.get_csv_file(file_id)
        if file_model is None:
            raise ValueError("CSV file not found")

        df = prepare_dataframe(file_model)
        rules = await self.list_rules()
        df = categorise_transactions(df, rules)

        await self.replace_transactions(file_model.id, df)

        uncategorised = int(df["category"].isna().sum())
        return {"processed": len(df), "uncategorised": uncategorised}

    async def get_csv_file(self, file_id: int) -> CSVFile | None:
        get_file_query = select(CSVFile).where(CSVFile.id == file_id)

        result = await self.session.execute(get_file_query)

        return result.scalar_one_or_none()

    async def list_rules(self) -> list[CategoryRule]:
        result = await self.session.execute(
            select(CategoryRule).order_by(CategoryRule.priority.desc(), CategoryRule.id)
        )
        return list(result.scalars().all())

    async def create_rule(self, rule: CategoryRuleCreate) -> CategoryRule:
        rule_model = CategoryRule(
            pattern=rule.pattern,
            category=rule.category,
            priority=rule.priority,
        )
        self.session.add(rule_model)
        await self.session.commit()
        await self.session.refresh(rule_model)
        return rule_model

    async def update_rule(
        self, rule_id: int, rule_update: CategoryRuleUpdate
    ) -> CategoryRule | None:
        result = await self.session.execute(
            select(CategoryRule).where(CategoryRule.id == rule_id)
        )
        rule = result.scalar_one_or_none()
        if rule is None:
            return None

        update_data = rule_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)

        await self.session.commit()
        await self.session.refresh(rule)
        return rule

    async def delete_rule(self, rule_id: int) -> bool:
        result = await self.session.execute(
            delete(CategoryRule).where(CategoryRule.id == rule_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def list_uncategorised(self, limit: int = 100) -> list[Transaction]:
        result = await self.session.execute(
            select(Transaction)
            .where(Transaction.category.is_(None))
            .order_by(Transaction.transaction_date.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def recategorise_transactions(self) -> int:
        rules = await self.list_rules()
        result = await self.session.execute(select(Transaction))
        transactions = list(result.scalars().all())

        if not transactions:
            return 0

        df = pd.DataFrame(
            [
                {
                    "id": tx.id,
                    "merchant": tx.merchant,
                    "transaction_description": tx.transaction_description,
                    "category": tx.category,
                }
                for tx in transactions
            ]
        )

        df = categorise_transactions(df, rules)

        updated = 0
        for tx in transactions:
            new_category = df.loc[df["id"] == tx.id, "category"].iloc[0]
            if tx.category != new_category:
                tx.category = new_category
                updated += 1

        await self.session.commit()
        return updated

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
                category=row.get("category"),
                transaction_description=row["transaction_description"],
            )
            for _, row in df.iterrows()
        ]

        self.session.add_all(transactions)
        await self.session.commit()

    @staticmethod
    def prepare_dataframe(file_model: CSVFile | None) -> DataFrame:
        return prepare_dataframe(file_model)
