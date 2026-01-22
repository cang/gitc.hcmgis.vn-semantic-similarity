import torch
from sentence_transformers import SentenceTransformer
from shared.core.constants import *

class ModelService:
    def __init__(self, model : SentenceTransformer):
        self.model : SentenceTransformer = model
        
    def encode(self, texts: list):
        return self.model.encode(texts,batch_size=len(texts),convert_to_numpy=True)
    
def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🔄 Loading model={MODEL_NAME} device={device} ...", flush=True)
    model = SentenceTransformer(MODEL_NAME,device=device)
    print("✅ Model loaded", flush=True)

    # warmup
    with torch.no_grad():
        model.encode(["warmup"])
        print("✅ warmup", flush=True)

    return model                

def create_model_service():
    model = load_model()
    return ModelService(model)        


