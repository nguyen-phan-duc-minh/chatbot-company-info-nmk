from typing import List
from core.schema import RetrievedDocument

class BaseReranker:
    def rerank(self, query: str, documents: List[RetrievedDocument], top_k: int | None = None) -> List[RetrievedDocument]:
        raise NotImplementedError