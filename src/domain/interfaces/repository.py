from abc import ABC, abstractmethod
from typing import List, Optional, Any
from domain.entities.article import Article

class IRepository(ABC):
    @abstractmethod
    def save(self, article: Article) -> None:
        pass

    @abstractmethod
    def get_by_id(self, article_id: str) -> Optional[Article]:
        pass

    @abstractmethod
    def get_all(self) -> List[Article]:
        pass

    @abstractmethod
    def delete(self, article_id: str) -> None:
        pass
