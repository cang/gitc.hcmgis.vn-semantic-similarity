# from sentence_transformers import SentenceTransformer
# from services.inference_worker.embedder.embedder import BaseEmbedder
# from typing import List
# import torch
# from FlagEmbedding import BGEM3FlagModel


# ## model nặng quá chưa chạy đc nên chưa test 
# class SentenceFlagEmbeddingTransformer(BaseEmbedder):

#     def __init__(self, model_name: str, device: str = "auto"):
#         self.model_name = model_name
#         self.device = device
#         self.model = None

#     def load(self):

#         if self.device == "auto":
#             self.device = "cuda" if torch.cuda.is_available() else "cpu"

#         print(f"🔄 Loading SentenceTransformer: {self.model_name}", flush=True)

#         self.model = BGEM3FlagModel(self.model_name,  
#                        use_fp16=True) # Setting use_fp16 to True speeds up computation with a slight performance degradation        


#         print(f"✅ Model loaded on {self.device}", flush=True)

#         # warmup
#         with torch.no_grad():
#             self.model.encode(["warmup"])
#             print("✅ warmup", flush=True)
            

#     def encode(self, texts: List[str]) -> List[List[float]]:
#         embeddings_1 = self.model.encode(texts, 
#                             batch_size=len(texts),
#                             max_length=8192, # If you don't need such a long length, you can set a smaller value to speed up the encoding process.
#                             show_progress_bar=False,
#                             convert_to_numpy=True
#                             )['dense_vecs']
#         return embeddings_1.tolist()

    
    