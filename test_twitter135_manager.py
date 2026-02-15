#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Twitter135 管理器
"""

import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

from src.twitter135_manager import Twitter135Manager


def test_twitter135_manager():
    """测试 Twitter135 管理器"""
    print("=" * 60)
    print("Twitter135 管理器测试")
    print("=" * 60)

    try:
        manager = Twitter135Manager()

        # 测试 1: 获取用户信息
        print("\n" + "-" * 60)
        print("测试 1: 获取用户信息")
        print("-" * 60)

        usernames = ["elonmusk", "OpenAI", "ustcer2014"]

        for username in usernames:
            print(f"\n获取用户 @{username} 的信息...")
            user_info = manager.get_user_info(username)

            if user_info:
                print(f"✓ 成功获取用户信息")
                print(f"  用户名: @{user_info['username']}")
                print(f"  显示名: {user_info['name']}")
                print(f"  简介: {user_info['description'][:50]}...")
                print(f"  关注者: {user_info['followers_count']}")
                print(f"  推文数: {user_info['tweet_count']}")
                print(f"  认证: {'是' if user_info['verified'] else '否'}")
            else:
                print(f"❌ 获取失败")

        # 测试 2: 获取用户推文
        print("\n" + "-" * 60)
        print("测试 2: 获取用户推文")
        print("-" * 60)

        username = "elonmusk"
        print(f"\n获取 @{username} 的推文...")
        tweets = manager.get_user_tweets(username, count=5)

        if tweets:
            print(f"✓ 成功获取 {len(tweets)} 条推文\n")
            for i, tweet in enumerate(tweets, 1):
                print(f"{i}. {tweet['text'][:80]}...")
                print(f"   时间: {tweet['created_at']}")
                print(f"   互动: ❤️ {tweet['favorite_count']} | 🔄 {tweet['retweet_count']}")
                print()
        else:
            print("❌ 获取推文失败")

        # 测试 3: 搜索推文
        print("\n" + "-" * 60)
        print("测试 3: 搜索推文")
        print("-" * 60)

        keywords = ["Python", "AI"]

        for keyword in keywords:
            print(f"\n搜索关键词: {keyword}")
            tweets = manager.search_tweets(keyword, count=3)

            if tweets:
                print(f"✓ 找到 {len(tweets)} 条推文\n")
                for i, tweet in enumerate(tweets, 1):
                    print(f"{i}. @{tweet['author_username']}: {tweet['text'][:60]}...")
                    print(f"   ❤️ {tweet['favorite_count']} | 🔄 {tweet['retweet_count']}")
                    print()
            else:
                print("❌ 搜索失败")

        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)

        print("\n✓ Twitter135 API 可用功能:")
        print("  - 获取用户信息")
        print("  - 获取用户推文")
        print("  - 搜索推文")
        print("  - 获取推文详情")

        print("\n⚠️ 限制:")
        print("  - 免费版: 500 次请求/月")
        print("  - 只读功能，不能发推文")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")


if __name__ == "__main__":
    test_twitter135_manager()
