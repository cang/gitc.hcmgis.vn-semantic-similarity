# Trung gian sử dụng queue đề truyền qua worker xử lý
import grpc
import uuid
import time
import json
import hashlib
from concurrent import futures
from shared.grpc import embed_pb2
from shared.grpc import embed_pb2_grpc
from shared.db.redis_client import get_redis
from shared.core.constants import *
from shared.utils.text_normalize import preprocess_vi
from shared.utils.hashing import hash_text

class EmbedService(embed_pb2_grpc.EmbedServiceServicer):
    def EmbedText(self, request, context):
        text = request.text
        if not text:
            raise Exception(detail="Empty text")
        
        text = preprocess_vi(request.text)
        if not text:
            raise Exception(detail="Empty text")
        
        # 1️⃣ check cache : cái này có thể không chạy vì , nó đã đc cache ở tầng 1 trước vô tới tầng 2 này
        text_hash = hash_text(text)
        cache_key = f"embed:cache:{text_hash}"
        
        redis_client = None
        try:
            redis_client = get_redis()
            cached = redis_client.get(cache_key)
            if cached:
                return embed_pb2.EmbedResponse(vector=json.loads(cached))
        except Exception as e:
            print(f"Redis thất bại: {e}")
            raise Exception(detail="Cannot connect to Redis") 

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
                
                # cache lại
                redis_client.setex(
                    cache_key,
                    CACHE_EXPIRE_SECONDS,
                    json.dumps(embedding)
                )

                redis_client.delete(result_key)
                return embed_pb2.EmbedResponse(vector=embedding)

            time.sleep(0.05)

        raise Exception("Inference timeout")
       

def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=8)
    )
    embed_pb2_grpc.add_EmbedServiceServicer_to_server(
        EmbedService(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    print("gRpc server start on port 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()