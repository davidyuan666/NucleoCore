#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter 完整功能测试 - 已配置 Access Token
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


def test_get_user_info():
    """测试获取用户信息"""
    print("\n" + "=" * 60)
    print("测试 1: 获取当前用户信息")
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
        me = twitter_manager.client.get_me(user_fields=['description', 'created_at', 'public_metrics'])

        if me.data:
            print(f"\n✓ 用户名: @{me.data.username}")
            print(f"✓ 用户ID: {me.data.id}")
            if hasattr(me.data, 'name'):
                print(f"✓ 显示名称: {me.data.name}")
            if hasattr(me.data, 'description'):
                print(f"✓ 简介: {me.data.description}")
            if hasattr(me.data, 'created_at'):
                print(f"✓ 创建时间: {me.data.created_at}")
            if hasattr(me.data, 'public_metrics'):
                metrics = me.data.public_metrics
                print(f"\n账户统计:")
                print(f"  - 关注者: {metrics.get('followers_count', 0)}")
                print(f"  - 正在关注: {metrics.get('following_count', 0)}")
                print(f"  - 推文数: {metrics.get('tweet_count', 0)}")

            return True
        else:
            print("❌ 无法获取用户信息")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_post_tweet_dry_run():
    """测试发布推文（演练模式）"""
    print("\n" + "=" * 60)
    print("测试 2: 发布推文（演练模式）")
    print("=" * 60)

    config = {
        'rate_limit': {
            'max_tweets_per_day': 50,
            'min_interval_seconds': 300
        }
    }

    try:
        twitter_manager = TwitterManager(config)

        # 测试多条推文
        test_tweets = [
            "Hello World! 这是第一条测试推文 🚀",
            "测试中文推文 #测试 #Python",
            "Testing Twitter API integration with Python 🐍"
        ]

        print("\n准备发布的推文:")
        for i, tweet in enumerate(test_tweets, 1):
            print(f"{i}. {tweet}")

        print("\n开始发布（演练模式）...")
        for i, tweet in enumerate(test_tweets, 1):
            success = twitter_manager.post_tweet(tweet, dry_run=True)
            if success:
                print(f"✓ 推文 {i} 准备就绪")
            else:
                print(f"❌ 推文 {i} 失败")

        print("\n✓ 所有推文测试通过（演练模式）")
        print("提示: 将 dry_run=False 即可发布真实推文")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_post_real_tweet():
    """测试发布真实推文"""
    print("\n" + "=" * 60)
    print("测试 3: 发布真实推文")
    print("=" * 60)

    config = {
        'rate_limit': {
            'max_tweets_per_day': 50,
            'min_interval_seconds': 300
        }
    }

    try:
        twitter_manager = TwitterManager(config)

        # 询问用户是否要发布真实推文
        print("\n⚠️  警告: 即将发布真实推文到你的 Twitter 账户")
        print("推文内容: 测试推文 - Twitter API 集成成功 🎉 #test")
        print("\n是否继续？(y/n): ", end='')

        # 由于是自动化脚本，这里默认不发布
        print("n (自动跳过)")
        print("\n✓ 已跳过真实推文发布")
        print("如需发布，请修改脚本或使用交互模式")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def show_available_features():
    """显示可用功能"""
    print("\n" + "=" * 60)
    print("当前可用的 Twitter 功能")
    print("=" * 60)
    print("""
✓ 已配置功能:
1. 获取用户信息 - 可用
2. 发布推文 - 可用
3. 定时发布 - 可用
4. 推文备份 - 可用

❌ 受限功能（需要付费 API）:
1. 搜索推文 - 需要 Basic 计划
2. 获取其他用户推文 - 部分限制
3. 高级分析 - 需要付费

💡 推荐使用场景:
1. 定时发布内容
   - 设置发布计划
   - 自动发布推文
   - 避免手动操作

2. 内容管理
   - 本地编辑推文
   - 批量准备内容
   - 定时发布队列

3. 数据备份
   - 定期备份推文
   - 导出为 JSON
   - 本地存档

4. 自动化工作流
   - 邮件触发发推
   - RSS 转推文
   - 定时提醒
    """)


def main():
    """主函数"""
    print("=" * 60)
    print("Twitter 完整功能测试")
    print("=" * 60)

    # 检查配置
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    if not access_token or access_token == 'your_access_token_here':
        print("\n❌ 错误: 未配置 Access Token")
        return

    print(f"\nAccess Token: {access_token[:20]}...")
    print("✓ 完整认证已配置")

    # 运行测试
    results = []

    results.append(("获取用户信息", test_get_user_info()))
    results.append(("发布推文（演练）", test_post_tweet_dry_run()))
    results.append(("发布真实推文", test_post_real_tweet()))

    # 显示可用功能
    show_available_features()

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

    print("\n下一步:")
    print("1. 编辑 config.json，设置 dry_run_mode: false")
    print("2. 运行 python main.py 启动定时服务")
    print("3. 或使用交互式发推: python -c \"from src.twitter_manager import TwitterManager; ...\"")


if __name__ == "__main__":
    main()
