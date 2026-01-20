from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel

class Job(BaseModel):
    universidade: str
    titulo: str
    area: Optional[str] = None
    link: str
    data_publicacao: Optional[str] = None
    data_encerramento: Optional[str] = None
    status: Optional[str] = None

class BaseScraper(ABC):
    universidade: str
    url: str

    @abstractmethod
    async def fetch_jobs(self) -> List[Job]:
        pass
