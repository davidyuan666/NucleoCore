"""速率限制器 - 防止超过 API 限制"""

import time
from collections import deque
from typing import Optional


class RateLimiter:
    """滑动窗口速率限制器"""

    def __init__(self, max_requests: int, time_window: int):
        """
        初始化速率限制器

        Args:
            max_requests: 时间窗口内最大请求数
            time_window: 时间窗口（秒）
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()

    def allow_request(self) -> bool:
        """检查是否允许新请求"""
        current_time = time.time()

        # 移除过期的请求记录
        while self.requests and self.requests[0] < current_time - self.time_window:
            self.requests.popleft()

        # 检查是否超过限制
        if len(self.requests) >= self.max_requests:
            return False

        # 记录新请求
        self.requests.append(current_time)
        return True

    def get_wait_time(self) -> Optional[float]:
        """获取需要等待的时间（秒）"""
        if len(self.requests) < self.max_requests:
            return 0

        current_time = time.time()
        oldest_request = self.requests[0]
        wait_time = self.time_window - (current_time - oldest_request)

        return max(0, wait_time)
