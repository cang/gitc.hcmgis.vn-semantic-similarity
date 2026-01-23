from sentence_transformers import SentenceTransformer
from services.inference_worker.embedder.embedder import BaseEmbedder
from typing import List
import torch


class SentenceTransformerEmbedder(BaseEmbedder):

    def __init__(self, model_name: str, device: str = "auto"):
        self.model_name = model_name
        self.device = device
        self.model = None

    def load(self):

        if self.device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"🔄 Loading SentenceTransformer: {self.model_name}", flush=True)

        self.model = SentenceTransformer(self.model_name, device=self.device)

        print(f"✅ Model loaded on {self.device}", flush=True)

        # warmup
        with torch.no_grad():
            self.model.encode(["warmup"])
            print("✅ warmup", flush=True)
            

    def encode(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(
            texts,
            batch_size=len(texts),
            show_progress_bar=False,
            convert_to_numpy=True
        ).tolist()
    
    