#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Twitter 获取推文功能
"""

import os
import sys
import io

# 设置标准输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from src.twitter_manager import TwitterManager


def test_search_tweets():
    """测试搜索推文功能"""
    print("\n" + "=" * 60)
    print("测试 1: 搜索公开推文")
    print("=" * 60)

    config = {
        'rate_limit': {
            'max_tweets_per_day': 50,
            'min_interval_seconds': 300
        }
    }

    try:
        twitter_manager = TwitterManager(config)

        # 搜索关键词
        keywords = ["Python", "AI", "机器学习"]

        for keyword in keywords:
            print(f"\n搜索关键词: {keyword}")
            print("-" * 60)

            tweets = twitter_manager.search_recent_tweets(keyword, max_results=5)

            if tweets:
                print(f"找到 {len(tweets)} 条推文:\n")
                for i, tweet in enumerate(tweets, 1):
                    print(f"{i}. @{tweet['author_username']} ({tweet['author_name']})")
                    print(f"   内容: {tweet['text'][:80]}...")
                    print(f"   时间: {tweet['created_at']}")
                    metrics = tweet['metrics']
                    print(f"   互动: ❤️ {metrics['like_count']} | "
                          f"🔄 {metrics['retweet_count']} | "
                          f"💬 {metrics['reply_count']}")
                    print()
            else:
                print("没有找到相关推文\n")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_get_user_tweets():
    """测试获取指定用户推文"""
    print("\n" + "=" * 60)
    print("测试 2: 获取指定用户的推文")
    print("=" * 60)

    config = {
        'rate_limit': {
            'max_tweets_per_day': 50,
            'min_interval_seconds': 300
        }
    }

    try:
        twitter_manager = TwitterManager(config)

        # 测试获取知名用户的推文
        usernames = ["elonmusk", "OpenAI", "github"]

        for username in usernames:
            print(f"\n获取用户 @{username} 的推文")
            print("-" * 60)

            tweets = twitter_manager.get_user_tweets(username, max_results=3)

            if tweets:
                print(f"找到 {len(tweets)} 条推文:\n")
                for i, tweet in enumerate(tweets, 1):
                    print(f"{i}. 内容: {tweet['text'][:100]}...")
                    print(f"   时间: {tweet['created_at']}")
                    metrics = tweet['metrics']
                    print(f"   互动: ❤️ {metrics['like_count']} | "
                          f"🔄 {metrics['retweet_count']} | "
                          f"💬 {metrics['reply_count']}")
                    print()
            else:
                print("没有找到推文\n")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_backup_tweets():
    """测试备份推文功能"""
    print("\n" + "=" * 60)
    print("测试 3: 备份推文")
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

        print("✓ 备份测试完成")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("Twitter 获取推文功能测试")
    print("=" * 60)

    # 检查环境变量
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    if not bearer_token or bearer_token == 'your_bearer_token_here':
        print("\n❌ 错误: 未配置 Twitter Bearer Token")
        print("请在 .env 文件中配置 TWITTER_BEARER_TOKEN")
        return

    print(f"\nBearer Token: {bearer_token[:30]}...")
    print("\n开始测试...\n")

    # 运行测试
    results = []

    results.append(("搜索公开推文", test_search_tweets()))
    results.append(("获取用户推文", test_get_user_tweets()))
    results.append(("备份推文", test_backup_tweets()))

    # 显示测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    for test_name, result in results:
        status = "✓ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\n总计: {passed}/{total} 个测试通过")
    print("=" * 60)


if __name__ == "__main__":
    main()
