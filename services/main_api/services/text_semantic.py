import time
import requests
import json
from uuid import uuid4
from fastapi import FastAPI, HTTPException

from shared.core.config import settings
from shared.core.constants import *
import requests
from shared.db.qdrant_client import get_qdrant_client, reset_qdrant_client
from shared.db.redis_client import get_redis, reset_redis
from shared.utils.hashing import cache_key, hash_text
from shared.utils.circuit_breaker import CircuitBreaker
import grpc
from shared.grpc import embed_pb2
from shared.grpc import embed_pb2_grpc
from shared.enum.run_mode import RunMode

EMBED_HOST = settings.EMBED_HOST
EMBED_PORT = settings.EMBED_PORT
TEXTS_VECTOR_COLLECTION = settings.MODEL_VECTOR_COLLECTION

breaker = CircuitBreaker(fail_threshold=3, reset_timeout=10)

def add(text: str):
    vector = _request_embed(text)
    if not vector:
        return False
    
    # Thêm vào vector database
    try:
        qdrant = get_qdrant_client()
        qdrant.upsert(
            collection_name=TEXTS_VECTOR_COLLECTION,
            points=[
                {
                    "id": str(uuid4()),
                    "vector": vector,
                    "payload": { "text": text, # sau này sẽ bõ cái này ra cho nhẹ, vì đã lưu chỗ khác theo hash
                                "hash" : hash_text(text) # hash sừ dụng để tìm lại text 
                                }
                }
            ]
        )
        
        breaker.record_success()
        return True
        
    except Exception as e:
        print(f"Vector Database thất bại: {e}")
        breaker.record_failure()
        reset_qdrant_client()
        return False
    
def search(text: str):

    if not breaker.allow_request():
        raise HTTPException(
            status_code=503,
            detail="Vector DB temporarily unavailable (circuit open)"
        )    

    # cache
    cached = None
    redis_client = None
    try:
        redis_client = get_redis()
        cached = redis_client.get(cache_key(text))
    except Exception as e:
        print(f"Redis thất bại: {e}")
        reset_redis()
        # Redis lỗi → bỏ cache, vẫn cho API chạy
        pass    
      
    vector = None
    if cached:
        vector = json.loads(cached)
    else:
        vector = _request_embed(text)
        # cache lại để lầnn sau khỏi gọi qua embed
        try:
            redis_client = get_redis()
            redis_client.setex(cache_key(text), 300, json.dumps(vector))
        except Exception as e:
            print(f"Redis thất bại: {e}")
            reset_redis()

    if not vector:
        return { "result": 0, "query": text, "results": [] }
    
    # Vector Database
    try:
        start_time = time.time()
        qdrant = get_qdrant_client()
        res = qdrant.query_points(
            collection_name=TEXTS_VECTOR_COLLECTION,
            query=vector,
            limit=3,
            with_payload=True
        )
        print(f"Thời gian thực thi qdrant: {time.time() - start_time} giây")            
        
        breaker.record_success()
        
        hits = res.points
        return {
            "result": 1,
            "query": text,
            "results": [{'hash':h.payload['hash'],'text':h.payload['text'],'score': h.score} for h in hits]
        }
    
    except Exception as e:
        print(f"Vector Database thất bại: {e}")
        breaker.record_failure()
        reset_qdrant_client()    
        return { "result": -1, "query": text, "results": [] }


def _request_embed(text: str):
    if settings.APP_RUN_MODE == RunMode.USE_GRPC:
        return  _request_grpc_embed(text)
    else:
        return  _request_http_embed(text)


def _request_http_embed(text: str):
    try:
        start_time = time.time()

        # gọi embedding
        embed_url = f"http://{EMBED_HOST}:{EMBED_PORT}/embed"
        print(embed_url)
        r = requests.post( embed_url,json={"text": text})
        vector = r.json()["embedding"]

        print(f"Thời gian gọi EMBED: {time.time() - start_time} giây")    
        
        return vector
    except Exception as e:
        print(f"Gọi qua embedding thất bại: {e}")

    return None

def _request_grpc_embed(text: str):
    try:
        start_time = time.time()

        grpc_link = f"{EMBED_HOST}:{EMBED_PORT}"
        print(f"grpc_link = {grpc_link}")
        channel = grpc.insecure_channel(grpc_link)        
        # channel = grpc.insecure_channel(
            # "localhost:50051,localhost:50052,localhost:50053",
            # options=[
                # ("grpc.lb_policy_name", "round_robin")
            # ]
        stub = embed_pb2_grpc.EmbedServiceStub(channel)

        res = stub.EmbedText(
            embed_pb2.EmbedRequest(text=text)
        )        
        
        vector = list(res.vector)        

        print(f"Thời gian gọi EMBED: {time.time() - start_time} giây")    
        
        return vector
    except Exception as e:
        print(f"Gọi qua embedding thất bại: {e}")

    return None


        
        