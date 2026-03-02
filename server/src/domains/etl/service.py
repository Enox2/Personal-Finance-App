import pandas as pd
from pandas import DataFrame
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.csv.models import CSVFile
from src.domains.etl.parsers.pkobp_csv import prepare_dataframe


class ProcessFilesApplicationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def start_processing_file(
        self,
        file_id: int,
    ):
        file_model = await self.get_csv_file(file_id)

        df = prepare_dataframe(file_model)
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
        return prepare_dataframe(file_model)
