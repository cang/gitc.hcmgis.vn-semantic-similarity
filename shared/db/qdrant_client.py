from qdrant_client import QdrantClient, models
from shared.core.config import settings
from shared.core.constants import *
import threading

QDRAN_HOST = settings.QDRAN_HOST
QDRAN_PORT = settings.QDRAN_PORT

_client = None
_lock = threading.Lock()

def get_qdrant_client():
    global _client
    if _client is None:
        with _lock:
            if _client is None:
            
                print(f"Connect to QdrantClient {QDRAN_HOST}:{QDRAN_PORT}")
                _client = QdrantClient(
                    host=QDRAN_HOST, 
                    port=QDRAN_PORT,
                    timeout=1.5
                )
			
                #ENSURE TEXTS_VECTOR_COLLECTION
                ensure_collection(_client)
	
    return _client

def reset_qdrant_client():
    global _client
    print(f"RESET QdrantClient {QDRAN_HOST}:{QDRAN_PORT}")
    _client = None
	
def ensure_collection(client):
    #collections = client.get_collections().collections
    #if TEXTS_VECTOR_COLLECTION not in [c.name for c in collections]:
	try:
		if not client.collection_exists(TEXTS_VECTOR_COLLECTION):
			client.create_collection(
				collection_name=TEXTS_VECTOR_COLLECTION,
				vectors_config=models.VectorParams(
					size=TEXTS_VECTOR_SIZE,
					distance=models.Distance.COSINE
				)
			)	
	except Exception:
		pass

