#!/usr/bin/env python3
"""
演示模式启动脚本 - 无需真实 API 凭证
"""

import os
import sys
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger('demo')


def demo_email():
    """演示 163 邮箱功能"""
    logger.info("=== 163 邮箱管理演示 ===")
    logger.info("[演练模式] 检查新邮件...")
    logger.info("发现 3 封未读邮件:")
    logger.info("  1. From: friend@163.com - Subject: 周末聚会")
    logger.info("  2. From: newsletter@company.com - Subject: 每周简报")
    logger.info("  3. From: support@service.com - Subject: 账户更新")
    logger.info("")
    logger.info("[演练模式] 发送邮件...")
    logger.info("将发送邮件到: recipient@163.com")
    logger.info("主题: 测试邮件")
    logger.info("邮件发送成功（演练模式）")
    logger.info("")


def demo_twitter():
    """演示 Twitter 功能"""
    logger.info("=== Twitter 管理演示 ===")
    logger.info("[演练模式] 获取最近推文...")
    logger.info("找到 5 条最近推文:")
    logger.info("  1. 今天天气不错 (10 likes, 2 retweets)")
    logger.info("  2. 分享一篇技术文章 (25 likes, 8 retweets)")
    logger.info("  3. 项目更新通知 (15 likes, 3 retweets)")
    logger.info("")
    logger.info("[演练模式] 发布新推文...")
    logger.info("推文内容: 这是一条测试推文 #demo")
    logger.info("推文发布成功（演练模式）")
    logger.info("")


def demo_scheduler():
    """演示调度器功能"""
    logger.info("=== 任务调度演示 ===")
    logger.info("已注册的定时任务:")
    logger.info("  - 检查邮件: 每 30 分钟执行一次")
    logger.info("  - 备份数据: 每天凌晨 2:00 执行")
    logger.info("  - 清理日志: 每周日执行")
    logger.info("")


def demo_safety_features():
    """演示安全特性"""
    logger.info("=== 安全特性演示 ===")
    logger.info("✓ 授权码认证 - 不存储登录密码")
    logger.info("✓ 速率限制器 - 防止超过平台限制")
    logger.info("  - 163邮箱: 每天最多 200 封邮件")
    logger.info("  - Twitter: 每天最多 50 条推文，最小间隔 5 分钟")
    logger.info("✓ 演练模式 - 默认不执行实际操作")
    logger.info("✓ 人工审核 - 重要操作需要确认")
    logger.info("✓ 本地加密存储 - 保护敏感数据")
    logger.info("")


def show_next_steps():
    """显示后续步骤"""
    logger.info("=== 配置真实服务的步骤 ===")
    logger.info("")
    logger.info("1. 163 邮箱配置:")
    logger.info("   - 登录 163 邮箱网页版 (mail.163.com)")
    logger.info("   - 进入 设置 -> POP3/SMTP/IMAP")
    logger.info("   - 开启 IMAP/SMTP 服务")
    logger.info("   - 获取授权码（16位字符）")
    logger.info("   - 在 .env 文件中填入邮箱地址和授权码")
    logger.info("")
    logger.info("2. Twitter API 配置:")
    logger.info("   - 访问 https://developer.twitter.com/")
    logger.info("   - 申请开发者账号并创建应用")
    logger.info("   - 获取 API Key, API Secret, Access Token 等")
    logger.info("   - 在 .env 文件中填入凭证")
    logger.info("")
    logger.info("3. 测试邮箱连接:")
    logger.info("   - 运行: python test_email.py")
    logger.info("")
    logger.info("4. 启动真实服务:")
    logger.info("   - 编辑 config.json，设置 \"dry_run_mode\": false")
    logger.info("   - 运行: python main.py")
    logger.info("")
    logger.info("详细配置指南请查看: docs/setup.md")
    logger.info("")


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("Social Account Manager - 演示模式")
    logger.info("安全合规的 163 邮箱和 Twitter 账户管理工具")
    logger.info("=" * 60)
    logger.info("")

    demo_safety_features()
    demo_email()
    demo_twitter()
    demo_scheduler()
    show_next_steps()

    logger.info("=" * 60)
    logger.info("演示完成！")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
