"""163 邮箱管理模块 - 使用 SMTP/IMAP 协议"""

import os
import logging
import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from .utils.rate_limiter import RateLimiter


class EmailManager:
    """163 邮箱管理器"""

    # 163 邮箱服务器配置
    IMAP_SERVER = 'imap.163.com'
    IMAP_PORT = 993
    SMTP_SERVER = 'smtp.163.com'
    SMTP_PORT = 465

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_PASSWORD')  # 这是授权码，不是登录密码
        self.rate_limiter = RateLimiter(
            max_requests=config['rate_limit']['max_emails_per_day'],
            time_window=86400
        )
        self._validate_credentials()

    def _validate_credentials(self):
        """验证邮箱凭证"""
        if not self.email_address or not self.email_password:
            self.logger.error("邮箱凭证未配置")
            raise ValueError("请在 .env 文件中配置 EMAIL_ADDRESS 和 EMAIL_PASSWORD")

        self.logger.info(f"邮箱账户: {self.email_address}")

    def _connect_imap(self) -> Optional[imaplib.IMAP4_SSL]:
        """连接到 IMAP 服务器"""
        try:
            mail = imaplib.IMAP4_SSL(self.IMAP_SERVER, self.IMAP_PORT)
            mail.login(self.email_address, self.email_password)
            self.logger.info("IMAP 连接成功")
            return mail
        except imaplib.IMAP4.error as e:
            self.logger.error(f"IMAP 连接失败: {e}")
            self.logger.error("请确保使用的是授权码，不是登录密码")
            return None
        except Exception as e:
            self.logger.error(f"IMAP 连接异常: {e}")
            return None

    def _decode_header(self, header_value: str) -> str:
        """解码邮件头"""
        if not header_value:
            return ""

        decoded_parts = decode_header(header_value)
        result = []

        for content, encoding in decoded_parts:
            if isinstance(content, bytes):
                try:
                    result.append(content.decode(encoding or 'utf-8'))
                except:
                    result.append(content.decode('utf-8', errors='ignore'))
            else:
                result.append(str(content))

        return ''.join(result)

    def check_new_emails(self, max_results: int = 10) -> List[Dict]:
        """检查新邮件"""
        mail = self._connect_imap()
        if not mail:
            return []

        try:
            # 选择收件箱
            mail.select('INBOX')

            # 搜索未读邮件
            status, messages = mail.search(None, 'UNSEEN')

            if status != 'OK':
                self.logger.error("搜索邮件失败")
                return []

            email_ids = messages[0].split()
            email_ids = email_ids[-max_results:]  # 只取最新的几封

            self.logger.info(f"发现 {len(email_ids)} 封未读邮件")

            emails = []
            for email_id in email_ids:
                email_data = self._fetch_email(mail, email_id)
                if email_data:
                    emails.append(email_data)

            return emails

        except Exception as e:
            self.logger.error(f"检查邮件失败: {e}")
            return []
        finally:
            try:
                mail.close()
                mail.logout()
            except:
                pass

    def _fetch_email(self, mail: imaplib.IMAP4_SSL, email_id: bytes) -> Optional[Dict]:
        """获取邮件详情"""
        try:
            status, msg_data = mail.fetch(email_id, '(RFC822)')

            if status != 'OK':
                return None

            # 解析邮件
            msg = email.message_from_bytes(msg_data[0][1])

            # 提取邮件信息
            subject = self._decode_header(msg.get('Subject', ''))
            from_addr = self._decode_header(msg.get('From', ''))
            date = msg.get('Date', '')

            # 获取邮件正文
            body = self._get_email_body(msg)

            return {
                'id': email_id.decode(),
                'from': from_addr,
                'subject': subject,
                'date': date,
                'body': body[:200] + '...' if len(body) > 200 else body
            }

        except Exception as e:
            self.logger.error(f"获取邮件详情失败: {e}")
            return None

    def _get_email_body(self, msg: email.message.Message) -> str:
        """提取邮件正文"""
        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                pass

        return body.strip()

    def send_email(self, to: str, subject: str, body: str, dry_run: bool = True) -> bool:
        """发送邮件（带安全检查）"""
        if dry_run:
            self.logger.info(f"[演练模式] 将发送邮件到 {to}: {subject}")
            return True

        if not self.rate_limiter.allow_request():
            self.logger.warning("达到每日邮件发送限制")
            return False

        try:
            # 创建邮件对象
            msg = MIMEText(body, 'plain', 'utf-8')
            msg['Subject'] = subject
            msg['From'] = self.email_address
            msg['To'] = to

            # 连接 SMTP 服务器 - 使用固定的本地主机名避免空格问题
            server = smtplib.SMTP_SSL(self.SMTP_SERVER, self.SMTP_PORT, timeout=10, local_hostname='localhost')
            server.login(self.email_address, self.email_password)

            # 发送邮件
            server.sendmail(self.email_address, [to], msg.as_string())
            server.quit()

            self.logger.info(f"邮件已发送到 {to}")
            return True

        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP 发送失败: {e}")
            return False
        except Exception as e:
            self.logger.error(f"发送邮件失败: {e}")
            return False

    def backup_emails(self, days: int = 30):
        """备份最近的邮件"""
        self.logger.info(f"开始备份最近 {days} 天的邮件")

        mail = self._connect_imap()
        if not mail:
            return

        try:
            mail.select('INBOX')

            # 计算日期
            since_date = (datetime.now() - timedelta(days=days)).strftime('%d-%b-%Y')

            # 搜索指定日期后的邮件
            status, messages = mail.search(None, f'SINCE {since_date}')

            if status != 'OK':
                self.logger.error("搜索邮件失败")
                return

            email_ids = messages[0].split()
            self.logger.info(f"找到 {len(email_ids)} 封邮件待备份")

            # 创建备份目录
            backup_dir = 'backups/email'
            os.makedirs(backup_dir, exist_ok=True)

            # 备份邮件
            backup_data = []
            for email_id in email_ids[:100]:  # 限制备份数量
                email_data = self._fetch_email(mail, email_id)
                if email_data:
                    backup_data.append(email_data)

            # 保存到文件
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{backup_dir}/emails_{timestamp}.json"

            import json
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"邮件已备份到 {backup_file}")

        except Exception as e:
            self.logger.error(f"备份邮件失败: {e}")
        finally:
            try:
                mail.close()
                mail.logout()
            except:
                pass

    def mark_as_read(self, email_id: str) -> bool:
        """标记邮件为已读"""
        mail = self._connect_imap()
        if not mail:
            return False

        try:
            mail.select('INBOX')
            mail.store(email_id.encode(), '+FLAGS', '\\Seen')
            self.logger.info(f"邮件 {email_id} 已标记为已读")
            return True
        except Exception as e:
            self.logger.error(f"标记邮件失败: {e}")
            return False
        finally:
            try:
                mail.close()
                mail.logout()
            except:
                pass
