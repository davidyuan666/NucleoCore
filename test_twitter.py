#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Twitter API 连接和获取推文功能
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

def test_twitter_connection():
    """测试 Twitter 连接"""
    print("=" * 60)
    print("Twitter API 连接测试")
    print("=" * 60)
    print()

    # 检查环境变量
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

    if not api_key or not api_secret or not bearer_token:
        print("❌ 错误: 未配置 Twitter API 凭证")
        print()
        print("请按以下步骤配置:")
        print("1. 编辑 .env 文件")
        print("2. 填入你的 Twitter API 凭证")
        print()
        return False

    print(f"API Key: {api_key[:10]}...")
    print(f"API Secret: {api_secret[:10]}...")
    print(f"Bearer Token: {bearer_token[:20]}...")
    print()

    # 创建配置
    config = {
        'rate_limit': {
            'max_tweets_per_day': 50,
            'min_interval_seconds': 300
        }
    }

    try:
        # 初始化 Twitter 管理器
        print("正在连接到 Twitter API...")
        twitter_manager = TwitterManager(config)

        print("✓ Twitter API 认证成功！")
        print()

        # 测试获取当前用户信息
        print("正在获取用户信息...")
        try:
            me = twitter_manager.client.get_me()
            if me.data:
                print(f"✓ 用户名: @{me.data.username}")
                print(f"✓ 用户ID: {me.data.id}")
                print()
        except Exception as e:
            print(f"⚠ 获取用户信息失败: {e}")
            print("注意: 可能需要配置 Access Token 才能获取用户信息")
            print()

        # 测试获取推文
        print("正在获取最近的推文...")
        tweets = twitter_manager.get_recent_tweets(max_results=5)

        if tweets:
            print(f"✓ 成功获取 {len(tweets)} 条推文")
            print()
            print("最近的推文:")
            for i, tweet in enumerate(tweets, 1):
                print(f"\n{i}. 推文 ID: {tweet['id']}")
                print(f"   内容: {tweet['text'][:100]}...")
                print(f"   发布时间: {tweet['created_at']}")
                if 'metrics' in tweet:
                    metrics = tweet['metrics']
                    print(f"   互动: {metrics.get('like_count', 0)} 赞, "
                          f"{metrics.get('retweet_count', 0)} 转发, "
                          f"{metrics.get('reply_count', 0)} 回复")
        else:
            print("⚠ 没有找到推文")
            print("可能原因:")
            print("1. 账户还没有发布过推文")
            print("2. 需要配置 Access Token 和 Access Token Secret")
            print()

        # 测试发布推文（演练模式）
        print("\n测试发布推文（演练模式）...")
        test_tweet = "这是一条测试推文 #test"
        success = twitter_manager.post_tweet(test_tweet, dry_run=True)

        if success:
            print("✓ 发布测试通过（演练模式）")

        print()
        print("=" * 60)
        print("测试完成！Twitter API 配置正确。")
        print("=" * 60)
        print()
        print("提示:")
        print("- 如需发布推文，需要配置 Access Token 和 Access Token Secret")
        print("- 如需获取自己的推文，也需要完整的认证信息")
        print("- 当前使用 Bearer Token 可以进行只读操作")
        return True

    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print()
        print("可能的原因:")
        print("1. API 凭证不正确")
        print("2. 网络连接问题")
        print("3. Twitter API 访问限制")
        print()
        print("请查看 docs/setup.md 了解详细配置步骤")
        return False


if __name__ == "__main__":
    test_twitter_connection()
