#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Twitter135 API
"""

import os
import sys
import io
import requests
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()


def test_twitter135():
    """测试 Twitter135 API"""
    print("=" * 60)
    print("Twitter135 API 测试")
    print("=" * 60)

    api_key = os.getenv('RAPIDAPI_KEY')
    print(f"\nAPI Key: {api_key[:20]}...")

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "twitter135.p.rapidapi.com"
    }

    # 测试 1: 搜索推文
    print("\n" + "-" * 60)
    print("测试 1: 搜索推文")
    print("-" * 60)

    url = "https://twitter135.p.rapidapi.com/v2/Search/"
    querystring = {"q": "python", "count": "5"}

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            print("✓ 搜索功能可用！")
            data = response.json()

            if 'timeline' in data:
                tweets = data['timeline']
                print(f"\n找到 {len(tweets)} 条推文:\n")

                for i, tweet in enumerate(tweets[:3], 1):
                    print(f"{i}. {tweet.get('text', '')[:100]}...")
                    print(f"   作者: @{tweet.get('user', {}).get('screen_name', 'unknown')}")
                    print(f"   点赞: {tweet.get('favorites', 0)}")
                    print()
            else:
                print(f"数据格式: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")

        else:
            print(f"❌ 请求失败: {response.text[:200]}")

    except Exception as e:
        print(f"❌ 错误: {e}")

    # 测试 2: 获取用户信息
    print("\n" + "-" * 60)
    print("测试 2: 获取用户信息")
    print("-" * 60)

    url_user = "https://twitter135.p.rapidapi.com/v2/UserByScreenName/"
    querystring_user = {"username": "elonmusk"}

    try:
        response = requests.get(url_user, headers=headers, params=querystring_user, timeout=10)
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            print("✓ 用户信息功能可用！")
            data = response.json()

            if 'user' in data:
                user = data['user']
                print(f"\n用户名: @{user.get('screen_name', '')}")
                print(f"显示名: {user.get('name', '')}")
                print(f"关注者: {user.get('followers_count', 0)}")
                print(f"推文数: {user.get('statuses_count', 0)}")
            else:
                print(f"数据: {json.dumps(data, ensure_ascii=False, indent=2)[:300]}")

        else:
            print(f"请求失败: {response.text[:200]}")

    except Exception as e:
        print(f"❌ 错误: {e}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_twitter135()
