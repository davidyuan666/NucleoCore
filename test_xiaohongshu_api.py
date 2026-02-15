#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试小红书 RapidAPI
"""

import os
import sys
import io
import requests
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()


def test_xiaohongshu_api():
    """测试小红书 API"""
    print("=" * 60)
    print("小红书 RapidAPI 测试")
    print("=" * 60)

    api_key = os.getenv('RAPIDAPI_KEY')
    if not api_key:
        print("❌ 未配置 RAPIDAPI_KEY")
        return

    print(f"\nAPI Key: {api_key[:20]}...")

    # 测试 1: 搜索笔记
    print("\n" + "-" * 60)
    print("测试 1: 搜索笔记")
    print("-" * 60)

    url = "https://xiaohongshu-all-api.p.rapidapi.com/api/search/notes"

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "xiaohongshu-all-api.p.rapidapi.com"
    }

    # 搜索关键词
    keywords = ["美食", "旅游", "科技"]

    for keyword in keywords:
        print(f"\n搜索关键词: {keyword}")

        querystring = {
            "keyword": keyword,
            "page": "1",
            "page_size": "5"
        }

        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            print(f"状态码: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"✓ 请求成功")
                print(f"返回数据: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")

                # 解析笔记
                if 'data' in data and 'items' in data['data']:
                    notes = data['data']['items']
                    print(f"\n找到 {len(notes)} 条笔记:")
                    for i, note in enumerate(notes[:3], 1):
                        print(f"{i}. {note.get('title', '无标题')}")
                        print(f"   作者: {note.get('user', {}).get('nickname', '未知')}")
                        print(f"   点赞: {note.get('liked_count', 0)}")
                else:
                    print("数据格式:", data)

            elif response.status_code == 429:
                print("❌ 超过免费额度限制")
                print("提示: 免费版每月只有少量请求")
            elif response.status_code == 403:
                print("❌ API Key 无效或未订阅")
            else:
                print(f"❌ 请求失败: {response.text[:200]}")

        except requests.exceptions.Timeout:
            print("❌ 请求超时")
        except Exception as e:
            print(f"❌ 错误: {e}")

    # 测试 2: 获取用户信息
    print("\n" + "-" * 60)
    print("测试 2: 获取用户信息")
    print("-" * 60)

    url_user = "https://xiaohongshu-all-api.p.rapidapi.com/api/user/info"

    querystring_user = {
        "user_id": "5ff0e6410000000001001274"  # 示例用户ID
    }

    try:
        response = requests.get(url_user, headers=headers, params=querystring_user, timeout=10)
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✓ 请求成功")
            print(f"返回数据: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
        else:
            print(f"请求失败: {response.text[:200]}")

    except Exception as e:
        print(f"❌ 错误: {e}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

    print("\n小红书 API 功能:")
    print("✓ 搜索笔记")
    print("✓ 获取用户信息")
    print("✓ 获取笔记详情")
    print("✓ 获取评论")
    print("\n免费额度:")
    print("- 每月 100 次请求（免费版）")
    print("- 升级后可获得更多额度")


if __name__ == "__main__":
    test_xiaohongshu_api()
