"""Gmail 管理模块 - 使用官方 Gmail API"""

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .utils.rate_limiter import RateLimiter


# Gmail API 权限范围
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.labels']


class GmailManager:
    """Gmail 账户管理器"""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.service = None
        self.rate_limiter = RateLimiter(
            max_requests=config['rate_limit']['max_requests_per_minute'],
            time_window=60
        )
        self._authenticate()

    def _authenticate(self):
        """OAuth 2.0 认证"""
        creds = None
        token_file = self.config['token_file']
        creds_file = self.config['credentials_file']

        # 加载已保存的凭证
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)

        # 如果凭证无效或不存在，重新认证
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(creds_file):
                    self.logger.error(f"凭证文件不存在: {creds_file}")
                    raise FileNotFoundError(f"请先配置 Gmail API 凭证: {creds_file}")

                flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
                creds = flow.run_local_server(port=0)

            # 保存凭证
            os.makedirs(os.path.dirname(token_file), exist_ok=True)
            with open(token_file, 'w') as token:
                token.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info("Gmail API 认证成功")

    def check_new_emails(self, max_results: int = 10) -> List[Dict]:
        """检查新邮件"""
        if not self.rate_limiter.allow_request():
            self.logger.warning("达到速率限制，跳过本次检查")
            return []

        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX'],
                maxResults=max_results,
                q='is:unread'
            ).execute()

            messages = results.get('messages', [])
            self.logger.info(f"发现 {len(messages)} 封未读邮件")

            return [self._get_message_details(msg['id']) for msg in messages]

        except HttpError as error:
            self.logger.error(f"获取邮件失败: {error}")
            return []

    def _get_message_details(self, msg_id: str) -> Dict:
        """获取邮件详情"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()

            headers = {h['name']: h['value'] for h in message['payload']['headers']}

            return {
                'id': msg_id,
                'from': headers.get('From', ''),
                'subject': headers.get('Subject', ''),
                'date': headers.get('Date', ''),
                'snippet': message.get('snippet', '')
            }
        except HttpError as error:
            self.logger.error(f"获取邮件详情失败: {error}")
            return {}

    def send_email(self, to: str, subject: str, body: str, dry_run: bool = True) -> bool:
        """发送邮件（带安全检查）"""
        if dry_run:
            self.logger.info(f"[演练模式] 将发送邮件到 {to}: {subject}")
            return True

        if not self.rate_limiter.allow_request():
            self.logger.warning("达到速率限制，无法发送邮件")
            return False

        try:
            from email.mime.text import MIMEText
            import base64

            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()

            self.logger.info(f"邮件已发送到 {to}")
            return True

        except HttpError as error:
            self.logger.error(f"发送邮件失败: {error}")
            return False

    def backup_emails(self, days: int = 30):
        """备份最近的邮件"""
        self.logger.info(f"开始备份最近 {days} 天的邮件")

        date_filter = (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')

        try:
            results = self.service.users().messages().list(
                userId='me',
                q=f'after:{date_filter}'
            ).execute()

            messages = results.get('messages', [])
            self.logger.info(f"找到 {len(messages)} 封邮件待备份")

            # 这里可以添加实际的备份逻辑

        except HttpError as error:
            self.logger.error(f"备份邮件失败: {error}")
