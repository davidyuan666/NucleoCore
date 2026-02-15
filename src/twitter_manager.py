"""Twitter 管理模块 - 使用官方 Twitter API v2"""

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

import tweepy

from .utils.rate_limiter import RateLimiter


class TwitterManager:
    """Twitter 账户管理器"""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.rate_limiter = RateLimiter(
            max_requests=config['rate_limit']['max_tweets_per_day'],
            time_window=86400  # 24小时
        )
        self.min_interval = config['rate_limit']['min_interval_seconds']
        self.last_tweet_time = None
        self._authenticate()

    def _authenticate(self):
        """OAuth 认证"""
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

        if not bearer_token:
            self.logger.error("Twitter Bearer Token 未配置")
            raise ValueError("请在 .env 文件中配置 TWITTER_BEARER_TOKEN")

        # 使用 Bearer Token 进行认证（只读操作）
        # 如果有 Access Token，则使用完整认证（可读写）
        if access_token and access_token_secret and access_token != 'your_access_token_here':
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret
            )
            self.logger.info("Twitter API 认证成功（完整权限）")
        else:
            self.client = tweepy.Client(bearer_token=bearer_token)
            self.logger.info("Twitter API 认证成功（只读模式）")

    def search_recent_tweets(self, query: str, max_results: int = 10) -> List[Dict]:
        """搜索最近的公开推文"""
        try:
            self.logger.info(f"搜索推文: {query}")

            # 搜索推文
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'author_id'],
                expansions=['author_id'],
                user_fields=['username', 'name']
            )

            if not tweets.data:
                self.logger.info("没有找到匹配的推文")
                return []

            # 构建用户信息映射
            users = {}
            if tweets.includes and 'users' in tweets.includes:
                for user in tweets.includes['users']:
                    users[user.id] = {
                        'username': user.username,
                        'name': user.name
                    }

            result = []
            for tweet in tweets.data:
                user_info = users.get(tweet.author_id, {})
                result.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'author_id': tweet.author_id,
                    'author_username': user_info.get('username', 'Unknown'),
                    'author_name': user_info.get('name', 'Unknown'),
                    'metrics': {
                        'like_count': tweet.public_metrics.get('like_count', 0),
                        'retweet_count': tweet.public_metrics.get('retweet_count', 0),
                        'reply_count': tweet.public_metrics.get('reply_count', 0),
                        'quote_count': tweet.public_metrics.get('quote_count', 0)
                    }
                })

            self.logger.info(f"找到 {len(result)} 条推文")
            return result

        except tweepy.TweepyException as error:
            self.logger.error(f"搜索推文失败: {error}")
            return []

    def get_user_tweets(self, username: str, max_results: int = 10) -> List[Dict]:
        """获取指定用户的推文"""
        try:
            self.logger.info(f"获取用户 @{username} 的推文")

            # 先获取用户信息
            user = self.client.get_user(username=username)
            if not user.data:
                self.logger.error(f"用户 @{username} 不存在")
                return []

            user_id = user.data.id

            # 获取用户推文
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics']
            )

            if not tweets.data:
                self.logger.info(f"用户 @{username} 没有推文")
                return []

            result = []
            for tweet in tweets.data:
                result.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'author_username': username,
                    'metrics': {
                        'like_count': tweet.public_metrics.get('like_count', 0),
                        'retweet_count': tweet.public_metrics.get('retweet_count', 0),
                        'reply_count': tweet.public_metrics.get('reply_count', 0),
                        'quote_count': tweet.public_metrics.get('quote_count', 0)
                    }
                })

            self.logger.info(f"获取到 {len(result)} 条推文")
            return result

        except tweepy.TweepyException as error:
            self.logger.error(f"获取用户推文失败: {error}")
            return []

    def update_profile_name(self, new_name: str) -> bool:
        """更新 Twitter 显示名称（Display Name）

        Args:
            new_name: 新的显示名称，最多50个字符

        Returns:
            bool: 是否成功
        """
        try:
            if len(new_name) > 50:
                self.logger.error(f"显示名称过长: {len(new_name)}/50 字符")
                return False

            if not new_name.strip():
                self.logger.error("显示名称不能为空")
                return False

            self.logger.info(f"更新显示名称为: {new_name}")

            # 使用 Twitter API v2 更新用户资料
            # 注意：需要使用 OAuth 1.0a User Context
            response = self.client.update_me(name=new_name)

            if response:
                self.logger.info(f"✓ 显示名称已更新为: {new_name}")
                return True
            else:
                self.logger.error("更新显示名称失败")
                return False

        except tweepy.TweepyException as error:
            self.logger.error(f"更新显示名称失败: {error}")
            return False

    def get_recent_tweets(self, max_results: int = 10) -> List[Dict]:
        """获取当前认证用户的最近推文"""
        try:
            # 获取当前用户信息
            me = self.client.get_me()
            if not me.data:
                self.logger.warning("无法获取当前用户信息，可能需要配置 Access Token")
                return []

            user_id = me.data.id

            # 获取用户推文
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics']
            )

            if not tweets.data:
                self.logger.info("没有找到推文")
                return []

            result = []
            for tweet in tweets.data:
                result.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'metrics': tweet.public_metrics
                })

            self.logger.info(f"获取到 {len(result)} 条推文")
            return result

        except tweepy.TweepyException as error:
            self.logger.error(f"获取推文失败: {error}")
            return []

    def post_tweet(self, text: str, dry_run: bool = True, add_signature: bool = True) -> bool:
        """发布推文（带安全检查）"""
        # 添加签名
        signature = "\n\n— 来自 CC"
        if add_signature and not text.endswith(signature):
            tweet_text = text + signature
        else:
            tweet_text = text

        # 检查推文长度
        if len(tweet_text) > 280:
            self.logger.error(f"推文过长: {len(tweet_text)} 字符（最大 280）")
            return False

        # 演练模式
        if dry_run:
            self.logger.info(f"[演练模式] 将发布推文: {tweet_text[:50]}...")
            return True

        # 速率限制检查
        if not self.rate_limiter.allow_request():
            self.logger.warning("达到每日推文限制")
            return False

        # 最小间隔检查
        if self.last_tweet_time:
            elapsed = (datetime.now() - self.last_tweet_time).total_seconds()
            if elapsed < self.min_interval:
                self.logger.warning(f"距离上次发推不足 {self.min_interval} 秒")
                return False

        try:
            response = self.client.create_tweet(text=tweet_text)
            self.last_tweet_time = datetime.now()
            self.logger.info(f"推文已发布，ID: {response.data['id']}")
            return True

        except tweepy.TweepyException as error:
            self.logger.error(f"发布推文失败: {error}")
            return False

    def get_trending_topics(self, location_id: int = 1) -> List[Dict]:
        """获取热门话题（需要 API v1.1）"""
        # 注意：Twitter API v2 暂不支持获取热门话题
        # 这里保留接口，未来可能会支持
        self.logger.warning("Twitter API v2 暂不支持获取热门话题")
        return []

    def backup_tweets(self):
        """备份推文"""
        self.logger.info("开始备份推文")

        try:
            tweets = self.get_recent_tweets(max_results=100)

            if not tweets:
                self.logger.info("没有推文需要备份")
                return

            # 创建备份目录
            backup_dir = 'backups/twitter'
            os.makedirs(backup_dir, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{backup_dir}/tweets_{timestamp}.json"

            import json
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(tweets, f, ensure_ascii=False, indent=2, default=str)

            self.logger.info(f"推文已备份到 {backup_file}")

        except Exception as error:
            self.logger.error(f"备份推文失败: {error}")

    def schedule_tweet(self, text: str, scheduled_time: datetime) -> bool:
        """计划发布推文"""
        self.logger.info(f"计划在 {scheduled_time} 发布推文")

        # 注意：Twitter API v2 免费版不支持计划推文
        # 这里需要使用本地调度器实现

        return True
