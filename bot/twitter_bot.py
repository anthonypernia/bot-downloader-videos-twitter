""" Twitter Controller Module """
from datetime import datetime
from typing import Optional

import requests
import tweepy


class TwitterBot:
    """Twitter Controller"""

    def __init__(
        self,
        api_key: str,
        api_secret_key: str,
        access_token: str,
        access_token_secret: str,
    ):
        """Create a Twitter Controller object

        Args:
            api_key (str): api key
            api_secret_key (str): api secret key
            access_token (str): access token
            access_token_secret (str): access token secret
            bearer_token (str): bearer token
        """
        self.api_key = api_key
        self.api_secret_key = api_secret_key
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.auth = tweepy.OAuthHandler(self.api_key, self.api_secret_key)
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth)

    def get_tweets(self, query: str, count: int = 10) -> list:
        """get tweets from twitter
        Args:
            query (str): query to search
            count (int, optional): number of tweets to return. Defaults to 10.
        Returns:
            list: list of tweets
        """
        response = self.api.search_tweets(query, count=count)
        tweets = [tweet._json for tweet in response]  # pylint: disable=protected-access
        return tweets

    def get_tweet_by_id(self, id_tweet: str) -> dict:
        """get tweet by id
        Args:
            id (str): id of tweet
        Returns:
            dict: tweet
        """
        response = self.api.get_status(id_tweet)
        tweet = response._json  # pylint: disable=protected-access
        return tweet

    def tweet(self, status: str) -> dict:
        """tweet
        Args:
            status (str): text of tweet
        Returns:
            dict: tweet
        """
        response = self.api.update_status(status)
        tweet = response._json  # pylint: disable=protected-access
        return tweet

    def tweet_with_media(self, status: str, path_media: str) -> dict:
        """tweet with media
        Args:
            status (str): text of tweet
            path_media (str): path of media
        Returns:
            dict: tweet
        """
        response = self.api.update_status_with_media(status=status, filename=path_media)
        tweet = response._json  # pylint: disable=protected-access
        return tweet

    def reply_in_thread(self, tweet_id: str, status: str) -> dict:
        """reply in thread
        Args:
            tweet_id (str): id of tweet to reply
            status (str): text of reply
        Returns:
            dict: tweet
        """
        response = self.api.update_status(
            status, in_reply_to_status_id=tweet_id, auto_populate_reply_metadata=True
        )
        tweet = response._json  # pylint: disable=protected-access
        return tweet

    def get_mentions(self, count: int = 50, since_id: Optional[str] = None) -> list:
        """get mentions
        Args:
            count (int, optional): number of mentions to return. Defaults to 50.
            since_id (str, optional): id of last mention. Defaults to None.
        Returns:
            list: list of mentions
        """
        response = self.api.mentions_timeline(count=count, since_id=since_id)
        mentions = [
            mention._json for mention in response  # pylint: disable=protected-access
        ]
        return mentions

    def delete_tweet(self, tweet_id: str) -> dict:
        """delete tweet
        Args:
            tweet_id (str): id of tweet
        Returns:
            dict: tweet
        """
        response = self.api.destroy_status(tweet_id)
        tweet = response._json  # pylint: disable=protected-access
        return tweet

    def retweet(self, tweet_id: str) -> dict:
        """retweet
        Args:
            tweet_id (str): id of tweet
        Returns:
            dict: tweet
        """
        response = self.api.retweet(tweet_id)
        tweet = response._json  # pylint: disable=protected-access
        return tweet

    def like(self, tweet_id: str) -> dict:
        """like
        Args:
            tweet_id (str): id of tweet
        Returns:
            dict: tweet
        """
        response = self.api.create_favorite(tweet_id)
        tweet = response._json  # pylint: disable=protected-access
        return tweet

    def follow(self, username: str) -> dict:
        """follow
        Args:
            username (str): id of user
        Returns:
            dict: user
        """
        response = self.api.create_friendship(screen_name=username)
        user = response._json  # pylint: disable=protected-access
        return user

    def get_user(self, username: str) -> dict:
        """get user
        Args:
            username (str): username of user
        Returns:
            dict: user
        """
        response = self.api.get_user(screen_name=username)
        user = response._json  # pylint: disable=protected-access
        return user

    def unfollow(self, username: str) -> dict:
        """unfollow
        Args:
            username (str): username of user
        Returns:
            dict: user
        """
        response = self.api.destroy_friendship(screen_name=username)
        user = response._json  # pylint: disable=protected-access
        return user

    def download_media_from_tweet(self, tweet_id: str, path: str) -> None:
        """download media from tweet
        Args:
            tweet_id (str): id of tweet
            path (str): path to save media
        """
        tweet = self.get_tweet_by_id(tweet_id)
        media_data = tweet["extended_entities"]["media"]
        username = tweet["user"]["screen_name"]
        datetime_str_yyyymmdd = datetime.strptime(
            tweet["created_at"], "%a %b %d %H:%M:%S %z %Y"
        ).strftime("%Y%m%d")
        for media in media_data:
            video_data = media.get("video_info", None)
            if video_data:
                variants = video_data["variants"]
                for variant in variants:
                    if variant["content_type"] == "video/mp4":
                        url = variant["url"]
                        resolution = url.split("/")[-2]
                        print(f"video resolution: {resolution}")
                        filename = f"{username}_{datetime_str_yyyymmdd}_{tweet_id}_{resolution}.mp4"
                        self.download_media(url, path, filename)

    def download_media(self, url: str, path: str, filename: str) -> None:
        """download media
        Args:
            url (str): url of media
            path (str): path to save media
            filename (str): filename of media
        """
        response = requests.get(url, timeout=5)
        with open(f"{path}/{filename}", "wb") as file:
            file.write(response.content)
            file.close()
