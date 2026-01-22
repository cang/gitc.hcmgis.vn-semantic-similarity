# Embedding System – Demo & Architecture

## I. Chạy test demo trên Docker

### Các chế độ chạy
Hệ thống hỗ trợ **gRPC** và **HTTP**. Trước khi chạy, cần đổi cấu hình tương ứng.

### 1. Chế độ gRPC
Thay đổi các file sau:
- `docker-compose.yml.grpc` → `docker-compose.yml`
- `services/embedding/Dockerfile.grpc` → `services/embedding/Dockerfile`
- `.env.grpc` → `.env`

Trong file `.env`, chỉ cần đảm bảo:
```env
APP_RUN_MODE=USE_GRPC
```

### 2. Chế độ HTTP
Thay đổi các file sau:
- `docker-compose.http` → `docker-compose.yml`
- `services/embedding/Dockerfile.http` → `services/embedding/Dockerfile`
- `.env.http` → `.env`

Trong file `.env`, chỉ cần đảm bảo:
```env
APP_RUN_MODE=DEFAULT
```

### Lệnh chạy Docker
```bash
docker compose up --build
```

Sau khi chạy xong, truy cập:
```
http://localhost:8080/docs
```
để test API.

---

## II. Kiến trúc hệ thống

### Tổng quan
- Kí hiệu **N**: cho phép scale ngang nhiều instance / nhiều máy.
- **Vector Database**: Qdrant.
- **Text gốc**: lưu PostgreSQL (đủ mạnh, có thể tách server theo hash).
- **Cache & chia sẻ nội bộ**: Redis.

---

## Kiến trúc 4 tầng qua HTTP

```
Load Balancer
   |
FastAPI x N (nhẹ)
   |
HTTP (chậm)
   |
Embedding API x N (nhẹ)
   |
Redis (cache + giao tiếp worker)
   |
Embedding Workers (GPU) x N (batch, nặng)
   |
Vector Database
```

---

## Kiến trúc 4 tầng qua gRPC (khuyến nghị)

```
Load Balancer
   |
FastAPI x N (nhẹ)
   |
gRPC (nhanh)
   |
Embedding gRPC x N (nhẹ)
   |
Redis (cache + giao tiếp worker)
   |
Embedding Workers (GPU) x N (batch, nặng)
   |
Vector Database
```

---

## 1️⃣ Logical Architecture (Sơ đồ tổng thể)

```
Client
  |
  | HTTP
  v
API Gateway / Load Balancer (Layer 0)
  |
  v
Client API x N (Layer 1 – nhẹ)
  - auth / rate limit
  - orchestration
  |
  | gRPC
  v
Embedding Process x N (Layer 2 – nhẹ)
  - preprocessing
  - cache Redis
  - enqueue request
  |
  | Redis Queue
  v
Embedding Worker x N (Layer 3 – GPU, nặng)
  - batch inference
  - write result
  |
  v
Redis Result KV
  |
  v
Client API
  - read embedding
  - vector search
  |
  v
Vector Database (Qdrant / Milvus / PG)
```

---

## 2️⃣ Chi tiết luồng xử lý theo request

```
1. Client gửi request(text)
2. API Gateway → Client API
3. Client API gọi Embed(text) qua gRPC
4. Embedding Process:
   - preprocess
   - check cache
     - HIT → trả kết quả
     - MISS → push request vào Redis Queue
5. Embedding Worker:
   - batch pull
   - GPU inference
   - ghi kết quả vào Redis
6. Embedding Process poll kết quả
7. Client API thực hiện vector search
8. Trả response cho Client
```

---

## 3️⃣ Process & Scaling View (Rất quan trọng)

```
API Gateway (stateless)
        |
Client API x N (CPU nhẹ)
        |
Embedding Process x N (CPU nhẹ, không load model)
        |
   +----+-------------------+
   |                        |
Redis Queue           Redis Cache
   |
Embedding Worker x N (GPU, batch)
   |
Redis Result
```

---

## Ghi chú thiết kế
- Embedding Process **không load model** → scale nhanh.
- Worker GPU **1 process / 1 GPU** để tránh tranh chấp VRAM.
- Redis đóng vai trò:
  - Queue
  - Cache embedding
  - Result KV async

---

## License
Internal / Only Demo Project 

