"""Twitter135 RapidAPI 管理模块"""

import os
import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime


class Twitter135Manager:
    """Twitter135 RapidAPI 管理器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.base_url = "https://twitter135.p.rapidapi.com"

        if not self.api_key:
            raise ValueError("请在 .env 文件中配置 RAPIDAPI_KEY")

        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "twitter135.p.rapidapi.com"
        }

        self.logger.info("Twitter135 API 初始化成功")

    def get_user_info(self, username: str) -> Optional[Dict]:
        """获取用户信息"""
        try:
            url = f"{self.base_url}/v2/UserByScreenName/"
            params = {"username": username}

            response = requests.get(url, headers=self.headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # 解析用户数据
                if 'data' in data and 'user' in data['data']:
                    user_result = data['data']['user']['result']
                    legacy = user_result.get('legacy', {})

                    return {
                        'username': legacy.get('screen_name', username),
                        'name': legacy.get('name', ''),
                        'description': legacy.get('description', ''),
                        'followers_count': legacy.get('followers_count', 0),
                        'following_count': legacy.get('friends_count', 0),
                        'tweet_count': legacy.get('statuses_count', 0),
                        'verified': user_result.get('is_blue_verified', False),
                        'created_at': legacy.get('created_at', '')
                    }

                self.logger.warning(f"用户数据格式异常: {username}")
                return None

            elif response.status_code == 429:
                self.logger.error("API 额度已用完")
                return None
            else:
                self.logger.error(f"获取用户信息失败: {response.status_code}")
                return None

        except Exception as e:
            self.logger.error(f"获取用户信息异常: {e}")
            return None

    def get_user_tweets(self, username: str, count: int = 10) -> List[Dict]:
        """获取用户推文"""
        try:
            url = f"{self.base_url}/v2/UserTweets/"
            params = {
                "username": username,
                "count": str(count)
            }

            response = requests.get(url, headers=self.headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                tweets = []

                # 解析推文数据
                if 'data' in data and 'user' in data['data']:
                    timeline = data['data']['user']['result'].get('timeline_v2', {})
                    instructions = timeline.get('timeline', {}).get('instructions', [])

                    for instruction in instructions:
                        if instruction.get('type') == 'TimelineAddEntries':
                            entries = instruction.get('entries', [])

                            for entry in entries:
                                content = entry.get('content', {})
                                if content.get('entryType') == 'TimelineTimelineItem':
                                    item_content = content.get('itemContent', {})
                                    tweet_result = item_content.get('tweet_results', {}).get('result', {})

                                    if tweet_result.get('__typename') == 'Tweet':
                                        legacy = tweet_result.get('legacy', {})

                                        tweets.append({
                                            'id': tweet_result.get('rest_id', ''),
                                            'text': legacy.get('full_text', ''),
                                            'created_at': legacy.get('created_at', ''),
                                            'favorite_count': legacy.get('favorite_count', 0),
                                            'retweet_count': legacy.get('retweet_count', 0),
                                            'reply_count': legacy.get('reply_count', 0),
                                            'view_count': tweet_result.get('views', {}).get('count', 0)
                                        })

                self.logger.info(f"获取到 {len(tweets)} 条推文")
                return tweets

            elif response.status_code == 429:
                self.logger.error("API 额度已用完")
                return []
            else:
                self.logger.error(f"获取推文失败: {response.status_code}")
                return []

        except Exception as e:
            self.logger.error(f"获取推文异常: {e}")
            return []

    def search_tweets(self, query: str, count: int = 10) -> List[Dict]:
        """搜索推文"""
        try:
            url = f"{self.base_url}/v2/Search/"
            params = {
                "q": query,
                "count": str(count)
            }

            response = requests.get(url, headers=self.headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                tweets = []

                # 解析搜索结果
                if 'data' in data and 'search_by_raw_query' in data['data']:
                    search_timeline = data['data']['search_by_raw_query'].get('search_timeline', {})
                    instructions = search_timeline.get('timeline', {}).get('instructions', [])

                    for instruction in instructions:
                        if instruction.get('type') == 'TimelineAddEntries':
                            entries = instruction.get('entries', [])

                            for entry in entries:
                                content = entry.get('content', {})
                                if content.get('entryType') == 'TimelineTimelineItem':
                                    item_content = content.get('itemContent', {})
                                    tweet_result = item_content.get('tweet_results', {}).get('result', {})

                                    if tweet_result.get('__typename') == 'Tweet':
                                        legacy = tweet_result.get('legacy', {})
                                        user_result = tweet_result.get('core', {}).get('user_results', {}).get('result', {})
                                        user_legacy = user_result.get('legacy', {})

                                        tweets.append({
                                            'id': tweet_result.get('rest_id', ''),
                                            'text': legacy.get('full_text', ''),
                                            'created_at': legacy.get('created_at', ''),
                                            'favorite_count': legacy.get('favorite_count', 0),
                                            'retweet_count': legacy.get('retweet_count', 0),
                                            'author_username': user_legacy.get('screen_name', ''),
                                            'author_name': user_legacy.get('name', '')
                                        })

                self.logger.info(f"搜索到 {len(tweets)} 条推文")
                return tweets

            elif response.status_code == 429:
                self.logger.error("API 额度已用完")
                return []
            else:
                self.logger.error(f"搜索失败: {response.status_code}")
                return []

        except Exception as e:
            self.logger.error(f"搜索异常: {e}")
            return []

    def get_tweet_detail(self, tweet_id: str) -> Optional[Dict]:
        """获取推文详情"""
        try:
            url = f"{self.base_url}/v2/TweetDetail/"
            params = {"id": tweet_id}

            response = requests.get(url, headers=self.headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # 解析推文详情
                if 'data' in data and 'threaded_conversation_with_injections_v2' in data['data']:
                    instructions = data['data']['threaded_conversation_with_injections_v2'].get('instructions', [])

                    for instruction in instructions:
                        if instruction.get('type') == 'TimelineAddEntries':
                            entries = instruction.get('entries', [])

                            for entry in entries:
                                if entry.get('entryId', '').startswith('tweet-'):
                                    content = entry.get('content', {})
                                    item_content = content.get('itemContent', {})
                                    tweet_result = item_content.get('tweet_results', {}).get('result', {})

                                    if tweet_result.get('__typename') == 'Tweet':
                                        legacy = tweet_result.get('legacy', {})

                                        return {
                                            'id': tweet_result.get('rest_id', ''),
                                            'text': legacy.get('full_text', ''),
                                            'created_at': legacy.get('created_at', ''),
                                            'favorite_count': legacy.get('favorite_count', 0),
                                            'retweet_count': legacy.get('retweet_count', 0),
                                            'reply_count': legacy.get('reply_count', 0)
                                        }

                return None

            else:
                self.logger.error(f"获取推文详情失败: {response.status_code}")
                return None

        except Exception as e:
            self.logger.error(f"获取推文详情异常: {e}")
            return None
