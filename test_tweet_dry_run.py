#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试模式 - 模拟发推文（不消耗 API 额度）
"""

import os
import sys
import io
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

from src.twitter_manager import TwitterManager

def test_post_tweet():
    """测试发推文（演练模式）"""
    print("=" * 60)
    print("Twitter 发推测试（演练模式 - 不消耗 API 额度）")
    print("=" * 60)

    config = {
        'rate_limit': {
            'max_tweets_per_day': 50,
            'min_interval_seconds': 300
        }
    }

    twitter_manager = TwitterManager(config)

    # 测试推文
    test_tweets = [
        "测试推文 1",
        "今天天气不错 #天气",
        "通过 Telegram Bot 发送推文测试 🚀"
    ]

    print("\n测试推文列表:")
    for i, tweet in enumerate(test_tweets, 1):
        print(f"{i}. {tweet}")

    print("\n开始测试（演练模式）...\n")

    for i, tweet in enumerate(test_tweets, 1):
        print(f"推文 {i}:")
        print(f"  原文: {tweet}")

        # 添加签名
        signature = "\n\n— 来自 CC"
        full_text = tweet + signature
        print(f"  完整内容: {full_text}")
        print(f"  字符数: {len(full_text)}/280")

        # 演练模式发送
        success = twitter_manager.post_tweet(tweet, dry_run=True)

        if success:
            print(f"  ✅ 演练成功")
        else:
            print(f"  ❌ 演练失败")
        print()

    print("=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n说明:")
    print("- 演练模式不会真实发送推文")
    print("- 不消耗 API 额度")
    print("- 可以验证推文格式和长度")
    print("\n当前问题:")
    print("❌ Twitter API 额度不足（402 错误）")
    print("💡 解决方案:")
    print("  1. 等待下月额度重置")
    print("  2. 升级到 Basic 计划（$100/月）")
    print("  3. 使用新的开发者账号")

if __name__ == "__main__":
    test_post_tweet()
