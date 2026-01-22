'''
🔌 CIRCUIT BREAKER (CHỐNG SPAM DB KHI DOWN)
🎯 Vấn đề nếu không có Circuit Breaker
Qdrant down
1k RPS search
Mỗi request đều timeout
❌ API bị nghẽn
'''

import time
import threading

class CircuitBreaker:
    def __init__(self, fail_threshold=5, reset_timeout=10):
        self.fail_threshold = fail_threshold
        self.reset_timeout = reset_timeout

        self.fail_count = 0
        self.last_fail_time = None
        self.lock = threading.Lock()

    def allow_request(self):
        with self.lock:
            if self.fail_count < self.fail_threshold:
                return True

            if time.time() - self.last_fail_time > self.reset_timeout:
                # cho thử lại
                self.fail_count = 0
                return True

            return False

    def record_success(self):
        with self.lock:
            self.fail_count = 0
            self.last_fail_time = None

    def record_failure(self):
        with self.lock:
            self.fail_count += 1
            self.last_fail_time = time.time()
