from pathlib import Path
from pandas import DataFrame
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
from src.csv.models import CSVFile


class ProcessFilesApplicationService:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def start_processing_file(
        self,
        file_id: int,
    ):
        file_model = await self.get_csv_file(file_id)

        df = self.prepare_dataframe(file_model)
        pd.set_option("display.max_rows", None)
        pd.set_option("display.max_columns", None)
        print(df.memory_usage(deep=True).sum())

        return df

    async def get_csv_file(self, file_id: int) -> CSVFile | None:
        get_file_query = select(CSVFile).where(CSVFile.id == file_id)

        result = await self.session.execute(get_file_query)

        return result.scalar_one_or_none()

    @staticmethod
    def prepare_dataframe(file_model: CSVFile | None) -> DataFrame:
        df = pd.read_csv(Path(str(file_model.path)), encoding="cp1250")
        unnamed_cols = [col for col in df.columns if col.startswith("Unnamed")]

        df["Opis transakcji"] = df[["Opis transakcji"] + unnamed_cols].astype(str).agg(" ".join, axis=1)

        df = df.drop(columns=[*unnamed_cols, "Saldo po transakcji"])

        df.columns = ["transaction_date", "value_date", "transaction_type", "amount", "currency", "transaction_description"]

        examples = (
            df.groupby("transaction_type", as_index=False)
            .first()[["transaction_type", "transaction_description", "amount"]]
        )

        for _, row in examples.iterrows():
            print(f"{row['transaction_type']}: {row["amount"]}, {row['transaction_description']}\n")

        return df