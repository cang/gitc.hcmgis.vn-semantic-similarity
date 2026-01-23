from embedder.sentence_transformer import SentenceTransformerEmbedder
#from embedder.flag_embedding_transformer import SentenceFlagEmbeddingTransformer

MODEL_REGISTRY = {
    "sentence_transformer": SentenceTransformerEmbedder,
    #"sentence_fe_transformer": SentenceFlagEmbeddingTransformer,
    # "openai": OpenAIEmbedder (sau này thêm)
}

def create_embedder(model_type: str, **kwargs):
    if model_type not in MODEL_REGISTRY:
        raise ValueError(f"Unsupported model_type: {model_type}")
    return MODEL_REGISTRY[model_type](**kwargs)
