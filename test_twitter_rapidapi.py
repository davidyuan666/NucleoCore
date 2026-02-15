#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Twitter RapidAPI
"""

import os
import sys
import io
import requests
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()


def test_twitter_rapidapi():
    """测试 Twitter RapidAPI"""
    print("=" * 60)
    print("Twitter RapidAPI 测试")
    print("=" * 60)

    api_key = os.getenv('RAPIDAPI_KEY')
    if not api_key:
        print("❌ 未配置 RAPIDAPI_KEY")
        return

    print(f"\nAPI Key: {api_key[:20]}...")

    # 测试多个 Twitter API 提供商
    apis = [
        {
            "name": "Twitter API v2",
            "host": "twitter-api45.p.rapidapi.com",
            "endpoints": {
                "search": "/search.php",
                "user": "/user.php"
            }
        },
        {
            "name": "Twitter135",
            "host": "twitter135.p.rapidapi.com",
            "endpoints": {
                "search": "/v2/Search/",
                "user": "/v2/UserByScreenName/"
            }
        },
        {
            "name": "Twitter API v1.1",
            "host": "twitter154.p.rapidapi.com",
            "endpoints": {
                "search": "/search/search",
                "user": "/user/details"
            }
        }
    ]

    for api in apis:
        print("\n" + "=" * 60)
        print(f"测试: {api['name']}")
        print("=" * 60)

        headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": api['host']
        }

        # 测试搜索功能
        print(f"\n测试搜索功能...")
        search_url = f"https://{api['host']}{api['endpoints']['search']}"

        try:
            # 不同 API 的参数格式可能不同
            params = {
                "query": "python",
                "q": "python",
                "search": "python"
            }

            response = requests.get(search_url, headers=headers, params=params, timeout=10)
            print(f"状态码: {response.status_code}")

            if response.status_code == 200:
                print(f"✓ {api['name']} 可用！")
                data = response.json()
                print(f"返回数据示例: {json.dumps(data, ensure_ascii=False, indent=2)[:300]}...")
                return api  # 找到可用的 API
            elif response.status_code == 403:
                print(f"❌ 需要订阅")
            elif response.status_code == 404:
                print(f"❌ 端点不存在")
            elif response.status_code == 429:
                print(f"❌ 超过免费额度")
            else:
                print(f"状态: {response.status_code}")
                print(f"响应: {response.text[:200]}")

        except Exception as e:
            print(f"❌ 错误: {e}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


def search_available_twitter_apis():
    """搜索可用的 Twitter API"""
    print("\n" + "=" * 60)
    print("推荐的 Twitter RapidAPI 列表")
    print("=" * 60)

    recommendations = [
        {
            "name": "Twitter API v2",
            "url": "https://rapidapi.com/omarmhaimdat/api/twitter-api45",
            "price": "免费 100 次/月",
            "features": ["搜索推文", "用户信息", "推文详情"]
        },
        {
            "name": "Twitter135",
            "url": "https://rapidapi.com/twitter135/api/twitter135",
            "price": "免费 500 次/月",
            "features": ["搜索", "用户信息", "时间线"]
        },
        {
            "name": "Twitter API v1.1",
            "url": "https://rapidapi.com/Glavier/api/twitter154",
            "price": "$10/月起",
            "features": ["完整功能", "发推文", "高额度"]
        },
        {
            "name": "Twitter Scraper",
            "url": "https://rapidapi.com/omarmhaimdat/api/twitter-scraper-2",
            "price": "免费 100 次/月",
            "features": ["抓取推文", "用户数据", "搜索"]
        }
    ]

    for i, api in enumerate(recommendations, 1):
        print(f"\n{i}. {api['name']}")
        print(f"   价格: {api['price']}")
        print(f"   功能: {', '.join(api['features'])}")
        print(f"   链接: {api['url']}")

    print("\n" + "=" * 60)
    print("使用建议:")
    print("=" * 60)
    print("1. 访问上述链接")
    print("2. 点击 'Subscribe to Test'")
    print("3. 选择免费计划")
    print("4. 测试 API 端点")
    print("5. 告诉我哪个可用，我帮你集成")


if __name__ == "__main__":
    test_twitter_rapidapi()
    search_available_twitter_apis()
