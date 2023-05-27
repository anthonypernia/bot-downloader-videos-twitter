""" Twitter Controller Module """
from typing import Optional

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

    def like(self, tweet_id: str) -> None:
        """like
        Args:
            tweet_id (str): id of tweet
        Returns:
            dict: tweet
        """
        try:
            self.api.create_favorite(tweet_id)
        except Exception as error:  # pylint: disable=broad-except
            print(error)

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
