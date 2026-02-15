"""任务调度器"""

import logging
import time
from typing import Dict, Callable
import schedule


class TaskScheduler:
    """任务调度管理器"""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.tasks = {}

    def register_task(self, name: str, func: Callable):
        """注册定时任务"""
        self.tasks[name] = func
        self.logger.info(f"已注册任务: {name}")

    def run(self):
        """运行调度器"""
        # 设置邮件检查任务（每30分钟）
        schedule.every(30).minutes.do(self._safe_run, 'check_email')

        # 设置备份任务（每天凌晨2点）
        schedule.every().day.at("02:00").do(self._safe_run, 'backup')

        self.logger.info("调度器已启动")

        while True:
            schedule.run_pending()
            time.sleep(60)

    def _safe_run(self, task_name: str):
        """安全执行任务"""
        if task_name not in self.tasks:
            self.logger.error(f"任务不存在: {task_name}")
            return

        try:
            self.logger.info(f"开始执行任务: {task_name}")
            self.tasks[task_name]()
            self.logger.info(f"任务完成: {task_name}")
        except Exception as e:
            self.logger.error(f"任务执行失败 {task_name}: {e}")
