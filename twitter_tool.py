#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter 交互式发推工具
"""

import os
import sys
import io

# 设置标准输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
from datetime import datetime

# 加载环境变量
load_dotenv()

from src.twitter_manager import TwitterManager


def post_tweet_interactive():
    """交互式发布推文"""
    print("=" * 60)
    print("Twitter 发推工具")
    print("=" * 60)

    config = {
        'rate_limit': {
            'max_tweets_per_day': 50,
            'min_interval_seconds': 300
        }
    }

    try:
        twitter_manager = TwitterManager(config)

        # 获取用户信息
        me = twitter_manager.client.get_me()
        if me.data:
            print(f"\n当前账户: @{me.data.username}")

        print("\n请输入推文内容（最多 280 字符）:")
        print("提示: 输入 'q' 退出\n")

        tweet_text = input("> ").strip()

        if tweet_text.lower() == 'q':
            print("已取消")
            return

        if not tweet_text:
            print("❌ 推文内容不能为空")
            return

        if len(tweet_text) > 280:
            print(f"❌ 推文过长: {len(tweet_text)} 字符（最大 280）")
            return

        # 显示预览
        print("\n" + "-" * 60)
        print("推文预览:")
        print(tweet_text)
        print("-" * 60)

        print(f"\n字符数: {len(tweet_text)}/280")
        print("\n确认发布？(y/n): ", end='')

        confirm = input().strip().lower()

        if confirm != 'y':
            print("已取消")
            return

        # 发布推文
        print("\n正在发布...")
        success = twitter_manager.post_tweet(tweet_text, dry_run=False)

        if success:
            print("\n✓ 推文发布成功！")
            print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\n查看推文: https://twitter.com/{me.data.username}")
        else:
            print("\n❌ 推文发布失败")

    except Exception as e:
        print(f"\n❌ 错误: {e}")


def backup_tweets():
    """备份推文"""
    print("=" * 60)
    print("备份推文")
    print("=" * 60)

    config = {
        'rate_limit': {
            'max_tweets_per_day': 50,
            'min_interval_seconds': 300
        }
    }

    try:
        twitter_manager = TwitterManager(config)

        print("\n正在备份推文...")
        twitter_manager.backup_tweets()

        print("\n✓ 备份完成")
        print("备份文件保存在: backups/twitter/")

    except Exception as e:
        print(f"\n❌ 错误: {e}")


def show_menu():
    """显示菜单"""
    print("\n" + "=" * 60)
    print("Twitter 管理工具")
    print("=" * 60)
    print("\n请选择操作:")
    print("1. 发布推文")
    print("2. 备份推文")
    print("3. 查看账户信息")
    print("4. 退出")
    print("\n选择 (1-4): ", end='')


def show_account_info():
    """显示账户信息"""
    print("=" * 60)
    print("账户信息")
    print("=" * 60)

    config = {
        'rate_limit': {
            'max_tweets_per_day': 50,
            'min_interval_seconds': 300
        }
    }

    try:
        twitter_manager = TwitterManager(config)

        me = twitter_manager.client.get_me(
            user_fields=['description', 'created_at', 'public_metrics']
        )

        if me.data:
            print(f"\n用户名: @{me.data.username}")
            print(f"显示名称: {me.data.name}")
            print(f"用户ID: {me.data.id}")

            if hasattr(me.data, 'description') and me.data.description:
                print(f"简介: {me.data.description}")

            if hasattr(me.data, 'created_at'):
                print(f"创建时间: {me.data.created_at}")

            if hasattr(me.data, 'public_metrics'):
                metrics = me.data.public_metrics
                print(f"\n统计数据:")
                print(f"  关注者: {metrics.get('followers_count', 0)}")
                print(f"  正在关注: {metrics.get('following_count', 0)}")
                print(f"  推文数: {metrics.get('tweet_count', 0)}")

    except Exception as e:
        print(f"\n❌ 错误: {e}")


def main():
    """主函数"""
    # 检查配置
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    if not access_token or access_token == 'your_access_token_here':
        print("❌ 错误: 未配置 Access Token")
        print("请在 .env 文件中配置 TWITTER_ACCESS_TOKEN")
        return

    while True:
        show_menu()
        choice = input().strip()

        if choice == '1':
            post_tweet_interactive()
        elif choice == '2':
            backup_tweets()
        elif choice == '3':
            show_account_info()
        elif choice == '4':
            print("\n再见！")
            break
        else:
            print("\n❌ 无效选择，请输入 1-4")

        input("\n按 Enter 继续...")


if __name__ == "__main__":
    main()
