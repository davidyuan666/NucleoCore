#!/usr/bin/env python3
"""
测试 163 邮箱连接
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from src.email_manager import EmailManager

def test_email_connection():
    """测试邮箱连接"""
    print("=" * 60)
    print("163 邮箱连接测试")
    print("=" * 60)
    print()

    # 检查环境变量
    email_address = os.getenv('EMAIL_ADDRESS')
    email_password = os.getenv('EMAIL_PASSWORD')

    if not email_address or not email_password:
        print("❌ 错误: 未配置邮箱凭证")
        print()
        print("请按以下步骤配置:")
        print("1. 复制 .env.example 到 .env")
        print("2. 编辑 .env 文件")
        print("3. 填入你的 163 邮箱地址和授权码")
        print()
        print("注意: EMAIL_PASSWORD 是授权码，不是登录密码")
        return False

    print(f"邮箱地址: {email_address}")
    print(f"授权码: {'*' * len(email_password)}")
    print()

    # 创建配置
    config = {
        'rate_limit': {
            'max_emails_per_day': 200
        }
    }

    try:
        # 初始化邮件管理器
        print("正在连接到 163 邮箱...")
        email_manager = EmailManager(config)

        # 测试读取邮件
        print("正在检查未读邮件...")
        emails = email_manager.check_new_emails(max_results=5)

        print()
        print("✓ 连接成功！")
        print(f"✓ 找到 {len(emails)} 封未读邮件")
        print()

        if emails:
            print("最近的未读邮件:")
            for i, email_data in enumerate(emails, 1):
                print(f"{i}. 发件人: {email_data['from']}")
                print(f"   主题: {email_data['subject']}")
                print(f"   日期: {email_data['date']}")
                print()

        # 测试发送邮件（演练模式）
        print("测试发送邮件（演练模式）...")
        success = email_manager.send_email(
            to=email_address,  # 发送给自己
            subject="测试邮件",
            body="这是一封测试邮件，用于验证 163 邮箱配置是否正确。",
            dry_run=True
        )

        if success:
            print("✓ 发送测试通过（演练模式）")

        print()
        print("=" * 60)
        print("测试完成！邮箱配置正确。")
        print("=" * 60)
        return True

    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print()
        print("可能的原因:")
        print("1. 未开启 IMAP/SMTP 服务")
        print("2. 授权码不正确")
        print("3. 网络连接问题")
        print()
        print("请查看 docs/setup.md 了解详细配置步骤")
        return False


if __name__ == "__main__":
    test_email_connection()
