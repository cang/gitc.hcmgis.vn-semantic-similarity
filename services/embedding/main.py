#uvicorn main:app --port 9000
import uuid
import time
import json
from fastapi import FastAPI, HTTPException
from shared.db.redis_client import get_redis
from shared.schemas.embedding import EmbedRequest, EmbedResponse
from shared.core.constants import *
from shared.utils.text_normalize import preprocess_vi
from shared.utils.hashing import hash_text

app = FastAPI(title="Embedding API")

@app.post("/embed", response_model=EmbedResponse)
def embed(req: EmbedRequest):
    text = req.text
    if not text:
        raise HTTPException(status_code=400, detail="Empty text")
    
    text = preprocess_vi(text)

    # 1️⃣ check cache : cái này có thể không chạy vì , nó đã đc cache ở tầng 1 trước vô tới tầng 2 này
    text_hash = hash_text(text)
    cache_key = f"embed:cache:{text_hash}"
    
    redis_client = None
    try:
        redis_client = get_redis()
        cached = redis_client.get(cache_key)
        if cached:
            return {"embedding": json.loads(cached)}
    except Exception as e:
        print(f"Redis thất bại: {e}")
        raise HTTPException(status_code=504, detail="Cannot connect to Redis")
        
    # 2️⃣ tạo job
    job_id = str(uuid.uuid4())
    job_payload = {
        "job_id": job_id,
        "text": text
    }

    # 3️⃣ push vào queue
    redis_client.rpush(EMBED_QUEUE_KEY, json.dumps(job_payload))
    print(f"push vào queue: {json.dumps(job_payload)}")

    # 4️⃣ đợi kết quả (poll)
    result_key = f"{EMBED_RESULT}:{job_id}"
    start = time.time()

    while time.time() - start < RESULT_EXPIRE_SECONDS:
        result = redis_client.get(result_key)
        if result:
            embedding = json.loads(result)

            #print(f"vector của text {text} là {embedding}")

            # cache lại
            redis_client.setex(
                cache_key,
                CACHE_EXPIRE_SECONDS,
                json.dumps(embedding)
            )

            redis_client.delete(result_key)
            return {"embedding": embedding}

        time.sleep(0.05)

    raise HTTPException(status_code=504, detail="Inference timeout")
