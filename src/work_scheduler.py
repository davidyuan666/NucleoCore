"""工作调度器 - 定时检查邮件并执行任务"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re

from .email_manager import EmailManager
from .telegram_bot import TelegramBot


class WorkScheduler:
    """工作调度器 - 自动检查邮件并执行任务"""

    def __init__(self, email_manager: EmailManager, telegram_bot: TelegramBot):
        self.logger = logging.getLogger(__name__)
        self.email_manager = email_manager
        self.telegram_bot = telegram_bot

        # 你的 Gmail 地址
        self.boss_email = "wu.xiguanghua2014@gmail.com"

        # 检查间隔（分钟）
        self.check_interval = 10  # 每10分钟检查一次邮件
        self.report_interval = 60  # 每60分钟汇报一次状态

        # 任务队列
        self.pending_tasks = []
        self.completed_tasks = []

        # 上次检查时间
        self.last_check_time = None
        self.last_report_time = None

        self.logger.info("工作调度器初始化完成")

    async def check_emails(self):
        """检查新邮件并提取任务"""
        try:
            self.logger.info("检查新邮件...")
            emails = self.email_manager.check_new_emails(max_results=10)

            new_tasks = 0
            for email_data in emails:
                # 只处理来自你的邮件
                if self.boss_email.lower() in email_data['from'].lower():
                    task = self._parse_task_from_email(email_data)
                    if task:
                        self.pending_tasks.append(task)
                        new_tasks += 1
                        self.logger.info(f"新任务: {task['title']}")

            # 不再通过 Telegram 通知新任务，改为邮件确认
            if new_tasks > 0:
                self.logger.info(f"收到 {new_tasks} 个新任务，将通过邮件确认")

            self.last_check_time = datetime.now()
            return new_tasks

        except Exception as e:
            self.logger.error(f"检查邮件失败: {e}")
            return 0

    def _parse_task_from_email(self, email_data: Dict) -> Optional[Dict]:
        """从邮件中解析任务"""
        try:
            subject = email_data['subject']
            body = email_data.get('body', '')

            # 创建任务对象
            task = {
                'id': email_data['id'],
                'title': subject,
                'description': body,
                'from': email_data['from'],
                'received_at': email_data['date'],
                'status': 'pending',
                'created_at': datetime.now()
            }

            return task

        except Exception as e:
            self.logger.error(f"解析任务失败: {e}")
            return None

    async def execute_tasks(self):
        """执行待处理任务"""
        if not self.pending_tasks:
            return

        self.logger.info(f"开始执行 {len(self.pending_tasks)} 个任务")

        for task in self.pending_tasks[:]:  # 复制列表以便安全删除
            try:
                await self._execute_single_task(task)

                # 标记为完成
                task['status'] = 'completed'
                task['completed_at'] = datetime.now()
                self.completed_tasks.append(task)
                self.pending_tasks.remove(task)

            except Exception as e:
                self.logger.error(f"执行任务失败: {task['title']} - {e}")
                task['status'] = 'failed'
                task['error'] = str(e)

    async def _execute_single_task(self, task: Dict):
        """执行单个任务"""
        self.logger.info(f"执行任务: {task['title']}")

        # 通过邮件发送任务开始通知
        try:
            self.email_manager.send_email(
                to=self.boss_email,
                subject=f"任务开始: {task['title']}",
                body=f"任务已开始执行\n\n标题: {task['title']}\n描述: {task['description']}\n开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n我会在完成后通过邮件通知你。\n\n-- NucleoCore Bot",
                dry_run=False
            )
        except Exception as e:
            self.logger.error(f"发送邮件通知失败: {e}")

        # 这里可以根据任务内容执行不同的操作
        # 目前先简单记录
        await asyncio.sleep(1)  # 模拟任务执行

        # 通过邮件发送任务完成通知
        try:
            self.email_manager.send_email(
                to=self.boss_email,
                subject=f"任务完成: {task['title']}",
                body=f"任务已完成\n\n标题: {task['title']}\n描述: {task['description']}\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n如有问题请回复此邮件。\n\n-- NucleoCore Bot",
                dry_run=False
            )
        except Exception as e:
            self.logger.error(f"发送邮件通知失败: {e}")

    async def send_status_report(self):
        """发送工作状态汇报"""
        try:
            now = datetime.now()

            # 统计信息
            total_tasks = len(self.completed_tasks) + len(self.pending_tasks)
            completed = len(self.completed_tasks)
            pending = len(self.pending_tasks)

            # 构建汇报消息
            report = f"""
📊 工作状态汇报

⏰ 时间: {now.strftime('%Y-%m-%d %H:%M:%S')}

📈 任务统计:
  • 总任务数: {total_tasks}
  • 已完成: {completed}
  • 待处理: {pending}

📬 邮箱状态:
  • 工作邮箱: wu.xiguanghua@163.com
  • 上次检查: {self.last_check_time.strftime('%H:%M:%S') if self.last_check_time else '未检查'}

🤖 系统状态:
  • 运行正常 ✅
  • 邮件检查间隔: {self.check_interval} 分钟
  • 汇报间隔: {self.report_interval} 分钟
"""

            # 如果有待处理任务，列出来
            if self.pending_tasks:
                report += "\n📋 待处理任务:\n"
                for i, task in enumerate(self.pending_tasks[:5], 1):
                    report += f"  {i}. {task['title']}\n"

            await self._send_telegram_notification(report)
            self.last_report_time = now

        except Exception as e:
            self.logger.error(f"发送状态汇报失败: {e}")

    async def _send_telegram_notification(self, message: str):
        """发送 Telegram 通知"""
        try:
            await self.telegram_bot.send_notification(message)
        except Exception as e:
            self.logger.error(f"发送 Telegram 通知失败: {e}")

    async def run(self):
        """运行工作调度器"""
        self.logger.info("工作调度器开始运行")

        # 发送启动通知到 Telegram（重要通知）
        await self._send_telegram_notification(
            f"🚀 NucleoCore 工作调度器已启动\n\n"
            f"工作邮箱: wu.xiguanghua@163.com\n"
            f"状态汇报: 每60分钟\n\n"
            f"准备就绪，等待工作安排..."
        )

        while True:
            try:
                # 检查邮件
                await self.check_emails()

                # 执行任务
                await self.execute_tasks()

                # 定时汇报（仅通过 Telegram）
                if (not self.last_report_time or
                    (datetime.now() - self.last_report_time).seconds >= self.report_interval * 60):
                    await self.send_status_report()

                # 等待下次检查
                await asyncio.sleep(self.check_interval * 60)

            except Exception as e:
                self.logger.error(f"工作调度器错误: {e}")
                # 仅在出现异常时通过 Telegram 通知（重要通知）
                await self._send_telegram_notification(
                    f"⚠️ 系统异常\n\n"
                    f"错误: {str(e)[:100]}\n"
                    f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                await asyncio.sleep(60)  # 出错后等待1分钟再继续
