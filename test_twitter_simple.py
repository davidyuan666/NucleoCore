#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter 功能演示 - 适配免费版 API
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


def show_api_limits():
    """显示 Twitter API 限制说明"""
    print("\n" + "=" * 60)
    print("Twitter API 免费版限制说明")
    print("=" * 60)
    print("""
当前你的 Twitter 账户遇到 402 错误，这表示：

1. 免费版 API 额度限制：
   - 每月最多 1,500 条推文读取
   - 每月最多 50 条推文发布
   - 搜索功能需要付费订阅

2. 可用的免费功能：
   - 获取自己的推文（需要 Access Token）
   - 发布推文（需要 Access Token）
   - 基础用户信息查询

3. 需要付费的功能：
   - 搜索推文（search_recent_tweets）
   - 获取其他用户的推文（部分限制）
   - 高级过滤和分析

4. 解决方案：
   a) 升级到 Basic 计划（$100/月）
   b) 使用替代方案：
      - 只管理自己的推文
      - 使用 RSS 订阅获取公开内容
      - 使用第三方工具（如 Nitter）

5. 当前可以做的：
   - 配置 Access Token 后发布推文
   - 获取和备份自己的推文
   - 定时发布内容
    """)


def test_basic_features():
    """测试基础功能（不需要额外额度）"""
    print("\n" + "=" * 60)
    print("测试基础功能")
    print("=" * 60)

    config = {
        'rate_limit': {
            'max_tweets_per_day': 50,
            'min_interval_seconds': 300
        }
    }

    try:
        twitter_manager = TwitterManager(config)
        print("\n✓ Twitter API 连接成功")

        # 测试发布推文（演练模式）
        print("\n测试发布推文（演练模式）...")
        test_content = "这是一条测试推文 #test"
        success = twitter_manager.post_tweet(test_content, dry_run=True)

        if success:
            print(f"✓ 推文内容: {test_content}")
            print("✓ 演练模式测试通过")
        else:
            print("❌ 发布失败")

        # 检查 Access Token 配置
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        if access_token and access_token != 'your_access_token_here':
            print("\n✓ 已配置 Access Token，可以发布真实推文")
            print("  提示: 将 config.json 中的 dry_run_mode 设为 false 即可")
        else:
            print("\n⚠ 未配置 Access Token")
            print("  需要配置才能发布推文和获取自己的推文")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False


def show_alternative_solutions():
    """显示替代方案"""
    print("\n" + "=" * 60)
    print("推荐的替代方案")
    print("=" * 60)
    print("""
由于 Twitter API 免费版限制较多，建议：

方案 1: 专注于内容发布
- 使用本工具定时发布推文
- 设置发布计划和内容队列
- 自动备份已发布的推文

方案 2: 结合其他工具
- 使用 RSS 订阅关注的账号
- 使用 Nitter (nitter.net) 查看推文
- 使用浏览器插件导出数据

方案 3: 升级 API 计划
- Basic: $100/月，适合个人开发者
- Pro: $5,000/月，适合企业应用

当前项目配置建议：
1. 配置 Access Token（在 Twitter Developer Portal 获取）
2. 使用定时发布功能
3. 定期备份自己的推文
4. 监控 API 使用量
    """)


def main():
    """主函数"""
    print("=" * 60)
    print("Twitter 功能测试（免费版适配）")
    print("=" * 60)

    # 检查配置
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    if not bearer_token or bearer_token == 'your_bearer_token_here':
        print("\n❌ 错误: 未配置 Twitter Bearer Token")
        return

    print(f"\nBearer Token: {bearer_token[:30]}...")

    # 显示 API 限制
    show_api_limits()

    # 测试基础功能
    test_basic_features()

    # 显示替代方案
    show_alternative_solutions()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print("\n下一步:")
    print("1. 在 Twitter Developer Portal 获取 Access Token")
    print("2. 更新 .env 文件中的 TWITTER_ACCESS_TOKEN")
    print("3. 使用本工具定时发布推文")
    print("4. 查看 docs/setup.md 了解详细配置")


if __name__ == "__main__":
    main()
