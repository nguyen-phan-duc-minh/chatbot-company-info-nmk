import logging
from typing import List

from core.schema import RetrievedDocument

logger = logging.getLogger("context_builder")

class ContextBuilder:
    def __init__(self, max_documents: int = 5, max_context_length: int = 3000, separator: str = "\n\n---\n\n"):
        self.max_documents = max_documents
        self.max_context_length = max_context_length
        self.separator = separator

    def build(self, documents: List[RetrievedDocument]) -> str:
        if not documents:
            logger.warning("No documents provided to context builder.")
            return ""

        context_parts = []
        current_length = 0

        for doc in documents[: self.max_documents]:
            text = doc.text.strip()
            if not text:
                continue

            if current_length + len(text) > self.max_context_length:
                remaining = self.max_context_length - current_length
                if remaining <= 0:
                    break
                text = text[:remaining]

            context_parts.append(text)
            current_length += len(text)

        context = self.separator.join(context_parts)

        logger.info(
            f"Built context with {len(context_parts)} documents, "
            f"total length {len(context)} characters."
        )

        return context
