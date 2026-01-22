#gunicorn -w 4 -k uvicorn.workers.UvicornWorker embed:app
import time
import json
import torch
from redis.exceptions import RedisError
from sentence_transformers import SentenceTransformer
from shared.db.redis_client import get_redis
from shared.core.constants import *
from services.inference_worker.model_service import *

def start_worker(model_service: ModelService):
    print("Worker loop started", flush=True)
    redis_client = None
    while True:
        try:
            if redis_client is None:
                redis_client = get_redis()
                redis_client.ping()
                
            jobs = []
            for _ in range(BATCH_SIZE):
                job = redis_client.lpop(EMBED_QUEUE_KEY)    
                if not job:
                    break
                jobs.append(json.loads(job))
                
            if not jobs:
                time.sleep(0.05)
                continue
                
            #texts = [tokenize(j["text"]) for j in jobs]
            texts = [j["text"] for j in jobs]

            with torch.no_grad():
                embeddings = model_service.encode(texts)
                
            print(f"> đã xử lý {jobs}", flush=True)
            for job, vector in zip(jobs, embeddings):
                redis_client.set(
                    f"{EMBED_RESULT}:{job['job_id']}",
                    json.dumps(vector.tolist()),
                    ex=30
                )
                
        except RedisError as e:
            print(f"[REDIS ERROR] {EMBED_QUEUE_KEY} EXCEPT: {e}", flush=True)
            redis_client = None
            time.sleep(1)        
            
        except Exception as e:
            print(f"[WORKER ERROR] {e}", flush=True)
            time.sleep(1)    

def main():
    model_service = create_model_service()
    start_worker(model_service)

if __name__ == "__main__":
    main()            