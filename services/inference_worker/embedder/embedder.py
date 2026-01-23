from abc import ABC, abstractmethod
from typing import List


class BaseEmbedder(ABC):
    @abstractmethod
    def load(self):
        """Load model vào memory (GPU/CPU)"""
        pass

    @abstractmethod
    def encode(self, texts: List[str]) -> List[List[float]]:
        pass
