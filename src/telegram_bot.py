"""Telegram 机器人模块 - 通过 Telegram 控制 Twitter 和邮件"""

import os
import logging
from typing import Dict, Optional
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)


class TelegramBot:
    """Telegram 机器人管理器"""

    def __init__(self, twitter_manager, email_manager, twitter135_manager=None):
        self.logger = logging.getLogger(__name__)
        self.twitter_manager = twitter_manager
        self.email_manager = email_manager
        self.twitter135_manager = twitter135_manager  # RapidAPI Twitter135

        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')

        if not self.bot_token or not self.chat_id:
            raise ValueError("请在 .env 文件中配置 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID")

        self.application = None
        self.pending_tweet = {}  # 存储待发送的推文

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /start 命令"""
        welcome_message = """
🤖 欢迎使用 Social Account Manager Bot！

可用命令：
📱 Twitter 管理
  /tweet - 发送推文
  /mytweets - 查看我的推文
  /twitterinfo - 查看 Twitter 账户信息
  /userinfo - 查看任意用户信息（RapidAPI）

📧 邮件管理
  /checkemail - 检查新邮件
  /sendemail - 发送邮件

ℹ️ 其他
  /help - 显示帮助信息
  /status - 查看系统状态

直接发送文字消息将作为推文发布（需确认）
        """
        await update.message.reply_text(welcome_message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /help 命令"""
        help_text = """
📖 详细帮助

🐦 Twitter 命令：
/tweet - 发送推文
  用法: /tweet 你的推文内容

/mytweets - 查看最近的推文
  显示你最近发布的推文列表

/twitterinfo - Twitter 账户信息
  显示关注者、推文数等统计

📧 邮件命令：
/checkemail - 检查新邮件
  显示未读邮件列表

/sendemail - 发送邮件
  用法: /sendemail 收件人 主题 内容

💡 快捷方式：
直接发送文字 → 将作为推文发布（需确认）
        """
        await update.message.reply_text(help_text)

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /status 命令"""
        try:
            # 获取 Twitter 用户信息
            me = self.twitter_manager.client.get_me(user_fields=['public_metrics'])

            status_text = f"""
📊 系统状态

🐦 Twitter 账户: @{me.data.username}
  - 推文数: {me.data.public_metrics.get('tweet_count', 0)}
  - 关注者: {me.data.public_metrics.get('followers_count', 0)}
  - 正在关注: {me.data.public_metrics.get('following_count', 0)}

📧 邮件账户: {self.email_manager.email_address}
  - 状态: ✅ 已连接

⏰ 系统时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            await update.message.reply_text(status_text)
        except Exception as e:
            await update.message.reply_text(f"❌ 获取状态失败: {e}")

    async def tweet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /tweet 命令"""
        if not context.args:
            await update.message.reply_text(
                "用法: /tweet 你的推文内容\n"
                "例如: /tweet 今天天气不错 #天气\n\n"
                "💡 提示: 推文会自动添加签名 '— 来自 CC'"
            )
            return

        tweet_text = ' '.join(context.args)

        # 添加签名后检查长度
        signature = "\n\n— 来自 CC"
        full_text = tweet_text + signature

        # 检查推文长度
        if len(full_text) > 280:
            await update.message.reply_text(
                f"❌ 推文过长: {len(full_text)}/280 字符\n"
                f"（包含签名 '{signature}'）"
            )
            return

        # 存储待发送的推文
        user_id = update.effective_user.id
        self.pending_tweet[user_id] = tweet_text

        # 创建确认按钮
        keyboard = [
            [
                InlineKeyboardButton("✅ 确认发送", callback_data="tweet_confirm"),
                InlineKeyboardButton("❌ 取消", callback_data="tweet_cancel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"📝 推文预览:\n\n{full_text}\n\n"
            f"字符数: {len(full_text)}/280\n\n"
            f"确认发送？",
            reply_markup=reply_markup
        )

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理普通文字消息（作为推文）"""
        tweet_text = update.message.text

        # 添加签名后检查长度
        signature = "\n\n— 来自 CC"
        full_text = tweet_text + signature

        # 检查推文长度
        if len(full_text) > 280:
            await update.message.reply_text(
                f"❌ 内容过长: {len(full_text)}/280 字符\n"
                f"（包含签名 '{signature}'）\n"
                f"请缩短内容"
            )
            return

        # 存储待发送的推文
        user_id = update.effective_user.id
        self.pending_tweet[user_id] = tweet_text

        # 创建确认按钮
        keyboard = [
            [
                InlineKeyboardButton("🐦 发送为推文", callback_data="tweet_confirm"),
                InlineKeyboardButton("❌ 取消", callback_data="tweet_cancel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"📝 将以下内容发送为推文？\n\n{full_text}\n\n"
            f"字符数: {len(full_text)}/280",
            reply_markup=reply_markup
        )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理按钮回调"""
        query = update.callback_query
        await query.answer()

        user_id = update.effective_user.id
        callback_data = query.data

        if callback_data == "tweet_confirm":
            # 发送推文
            if user_id not in self.pending_tweet:
                await query.edit_message_text("❌ 推文已过期，请重新发送")
                return

            tweet_text = self.pending_tweet[user_id]

            try:
                success = self.twitter_manager.post_tweet(tweet_text, dry_run=False)

                if success:
                    # 显示实际发送的内容（包含签名）
                    signature = "\n\n— 来自 CC"
                    full_text = tweet_text + signature
                    await query.edit_message_text(
                        f"✅ 推文发送成功！\n\n{full_text}\n\n"
                        f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                else:
                    await query.edit_message_text("❌ 推文发送失败，请稍后重试")

                # 清除待发送推文
                del self.pending_tweet[user_id]

            except Exception as e:
                await query.edit_message_text(f"❌ 发送失败: {e}")

        elif callback_data == "tweet_cancel":
            # 取消发送
            if user_id in self.pending_tweet:
                del self.pending_tweet[user_id]
            await query.edit_message_text("❌ 已取消发送")

    async def mytweets_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /mytweets 命令"""
        try:
            await update.message.reply_text("正在获取推文...")

            tweets = self.twitter_manager.get_recent_tweets(max_results=5)

            if not tweets:
                await update.message.reply_text("没有找到推文")
                return

            response = "📱 最近的推文:\n\n"
            for i, tweet in enumerate(tweets, 1):
                response += f"{i}. {tweet['text'][:100]}...\n"
                response += f"   时间: {tweet['created_at']}\n"
                if 'metrics' in tweet:
                    metrics = tweet['metrics']
                    response += f"   ❤️ {metrics.get('like_count', 0)} | "
                    response += f"🔄 {metrics.get('retweet_count', 0)} | "
                    response += f"💬 {metrics.get('reply_count', 0)}\n"
                response += "\n"

            await update.message.reply_text(response)

        except Exception as e:
            await update.message.reply_text(f"❌ 获取推文失败: {e}")

    async def twitterinfo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /twitterinfo 命令"""
        try:
            # 处理编辑消息的情况
            message = update.edited_message if update.edited_message else update.message
            if not message:
                return

            me = self.twitter_manager.client.get_me(
                user_fields=['description', 'created_at', 'public_metrics']
            )

            if not me.data:
                await message.reply_text("❌ 无法获取账户信息")
                return

            info_text = f"""
🐦 Twitter 账户信息

👤 用户名: @{me.data.username}
📝 显示名称: {me.data.name}
🆔 用户ID: {me.data.id}
"""
            if hasattr(me.data, 'description') and me.data.description:
                info_text += f"📄 简介: {me.data.description}\n"

            if hasattr(me.data, 'created_at'):
                info_text += f"📅 创建时间: {me.data.created_at}\n"

            if hasattr(me.data, 'public_metrics'):
                metrics = me.data.public_metrics
                info_text += f"""
📊 统计数据:
  👥 关注者: {metrics.get('followers_count', 0)}
  ➕ 正在关注: {metrics.get('following_count', 0)}
  📱 推文数: {metrics.get('tweet_count', 0)}
"""

            await update.message.reply_text(info_text)

        except Exception as e:
            await update.message.reply_text(f"❌ 获取信息失败: {e}")

    async def checkemail_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /checkemail 命令"""
        try:
            await update.message.reply_text("正在检查邮件...")

            emails = self.email_manager.check_new_emails(max_results=5)

            if not emails:
                await update.message.reply_text("📭 没有新邮件")
                return

            response = f"📬 发现 {len(emails)} 封新邮件:\n\n"
            for i, email_data in enumerate(emails, 1):
                response += f"{i}. 发件人: {email_data['from']}\n"
                response += f"   主题: {email_data['subject']}\n"
                response += f"   时间: {email_data['date']}\n\n"

            await update.message.reply_text(response)

        except Exception as e:
            await update.message.reply_text(f"❌ 检查邮件失败: {e}")

    async def userinfo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /userinfo 命令 - 使用 RapidAPI 查看任意用户"""
        if not self.twitter135_manager:
            await update.message.reply_text("❌ Twitter135 API 未配置")
            return

        if not context.args:
            await update.message.reply_text(
                "用法: /userinfo 用户名\n"
                "例如: /userinfo elonmusk"
            )
            return

        username = context.args[0].replace('@', '')

        try:
            await update.message.reply_text(f"正在获取 @{username} 的信息...")

            user_info = self.twitter135_manager.get_user_info(username)

            if not user_info:
                await update.message.reply_text(f"❌ 无法获取用户 @{username} 的信息")
                return

            info_text = f"""
🐦 Twitter 用户信息

👤 用户名: @{user_info['username']}
📝 显示名: {user_info['name']}
📄 简介: {user_info['description'][:100]}...

📊 统计数据:
  👥 关注者: {user_info['followers_count']:,}
  ➕ 正在关注: {user_info['following_count']:,}
  📱 推文数: {user_info['tweet_count']:,}
  {'✓ 已认证' if user_info['verified'] else ''}

📅 创建时间: {user_info['created_at']}

💡 数据来源: RapidAPI Twitter135
"""

            await update.message.reply_text(info_text)

        except Exception as e:
            await update.message.reply_text(f"❌ 获取信息失败: {e}")

    async def changename_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /changename 命令 - 修改显示名称"""
        if not context.args:
            await update.message.reply_text(
                "用法: /changename 新名称\n"
                "例如: /changename DavidYuan\n\n"
                "💡 提示: 显示名称最多50个字符，用户名(@ustcer2014)不会改变"
            )
            return

        new_name = ' '.join(context.args)

        # 检查长度
        if len(new_name) > 50:
            await update.message.reply_text(
                f"❌ 名称过长: {len(new_name)}/50 字符\n"
                f"请缩短名称"
            )
            return

        try:
            await update.message.reply_text(f"正在更新显示名称为: {new_name}...")

            success = self.twitter_manager.update_profile_name(new_name)

            if success:
                await update.message.reply_text(
                    f"✅ 显示名称已更新！\n\n"
                    f"新名称: {new_name}\n"
                    f"用户名: @ustcer2014（不变）\n\n"
                    f"使用 /twitterinfo 查看更新后的信息"
                )
            else:
                await update.message.reply_text("❌ 更新失败，请稍后重试")

        except Exception as e:
            await update.message.reply_text(f"❌ 更新失败: {e}")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """错误处理"""
        self.logger.error(f"Update {update} caused error {context.error}")

    def setup_handlers(self):
        """设置命令处理器"""
        # 命令处理器
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("tweet", self.tweet_command))
        self.application.add_handler(CommandHandler("mytweets", self.mytweets_command))
        self.application.add_handler(CommandHandler("twitterinfo", self.twitterinfo_command))
        self.application.add_handler(CommandHandler("userinfo", self.userinfo_command))
        self.application.add_handler(CommandHandler("changename", self.changename_command))
        self.application.add_handler(CommandHandler("checkemail", self.checkemail_command))

        # 按钮回调处理器
        self.application.add_handler(CallbackQueryHandler(self.button_callback))

        # 文字消息处理器（作为推文）
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message)
        )

        # 错误处理器
        self.application.add_error_handler(self.error_handler)

    async def send_notification(self, message: str):
        """发送通知消息"""
        try:
            # 如果 application 未初始化，先初始化
            if not self.application:
                from telegram.ext import Application
                self.application = Application.builder().token(self.bot_token).build()

            await self.application.bot.send_message(
                chat_id=self.chat_id,
                text=message
            )
        except Exception as e:
            self.logger.error(f"发送通知失败: {e}")

    def run(self):
        """运行机器人"""
        self.logger.info("启动 Telegram Bot...")

        # 创建应用
        self.application = Application.builder().token(self.bot_token).build()

        # 设置处理器
        self.setup_handlers()

        self.logger.info("Telegram Bot 已启动")

        # 运行机器人
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
