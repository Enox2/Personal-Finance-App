from server.src.csv.models import CSVFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class ProcessFilesApplicationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def start_processing_file(
        self,
        file_id: int,
    ):
        csv_file = await self.get_csv_file(file_id)

    async def get_csv_file(self, file_id: int) -> CSVFile | None:
        get_file_query = select(CSVFile).where(CSVFile.id == file_id)

        result = await self.session.execute(get_file_query)

        return result.scalar_one_or_none()
