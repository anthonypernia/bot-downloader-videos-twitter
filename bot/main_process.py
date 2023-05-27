""" Main process of the bot """
import logging
import os
import time
from datetime import datetime, timedelta, timezone
from functools import reduce
from typing import Optional

import pytz
import requests

from bot.dropbox_uploader import DropboxUploader
from bot.twitter_bot import TwitterBot
from bot.util.utils import shorten_link

logging.basicConfig(level=logging.INFO)


class MainProcess:
    """Main process of the bot"""

    def __init__(self, **dict_auth_bot) -> None:
        """Create a main process object"""
        api_key = dict_auth_bot.get("api_key", None)
        api_secret_key = dict_auth_bot.get("api_secret_key", None)
        access_token = dict_auth_bot.get("access_token", None)
        access_token_secret = dict_auth_bot.get("access_token_secret", None)
        dropbox_acess_token = dict_auth_bot.get("dropbox_acess_token", None)
        if (
            not api_key
            or not api_secret_key
            or not access_token
            or not access_token_secret
            or not dropbox_acess_token
        ):
            logging.error("Missing authentication credentials")
            raise ValueError("Missing authentication credentials")
        self.twitter_bot = TwitterBot(
            access_token=access_token,
            access_token_secret=access_token_secret,
            api_key=api_key,
            api_secret_key=api_secret_key,
        )
        self.dropbox_uploader = DropboxUploader(access_token=dropbox_acess_token)
        logging.info("starting process")
        self.last_id: Optional[str] = None

    def run(self):
        """Run the main process"""
        if self.last_id:
            logging.info(f"Last id: {self.last_id} Date: {datetime.now()}")
            data_reply = self.twitter_bot.get_mentions(count=10, since_id=self.last_id)
        else:
            data_reply = self.twitter_bot.get_mentions(count=10)
        time.sleep(2)
        logging.info(f"Data reply count: {len(data_reply)} Date: {datetime.now()}")
        if len(data_reply) > 0:
            data_reply = self.order_by_date(data_reply)
            self.last_id = data_reply[0]["id"]
            logging.info(f"Last id set: {self.last_id} Date: {datetime.now()}")
            self.process_tweets(data_reply=data_reply)
        else:
            logging.info(f"No new mentions, Date: {datetime.now()}")
        time.sleep(10)

    def format_status(self, tweet_id: str, media_links_from_tweet: list) -> str:
        """Format status to reply in thread
        Args:
            tweet_id (str): id of the tweet
            media_links_from_tweet (list): links to download the video

        Returns:
            str: status to reply in thread
        """
        tweet = self.twitter_bot.get_tweet_by_id(tweet_id)
        username = tweet["user"]["screen_name"]
        status_links = ""
        for media_link in media_links_from_tweet:
            status_links += (
                f"{media_link['resolution']}: {shorten_link(media_link['link'])} \n"
            )
        status = f"Hi @{username}! Here are the links to download the video.\n"
        status += status_links
        status += "This files will be available for 1 hour\n"
        # status += f"This bot is open source, code is here: {shorten_link('https://github.com/anthonypernia/bot-downloader-videos-twitter')}"
        # if len(status) < 260:
        #    status += f"\nDeveloped by @AnthonyPerniah"
        return status

    @staticmethod
    def order_by_date(data_tweets: list) -> list:
        """Order tweets by date
        Args:
            data_tweets (list): list of tweets
        Returns:
            list: list of tweets ordered by date
        """
        return sorted(
            data_tweets,
            key=lambda x: datetime.strptime(x["created_at"], "%a %b %d %H:%M:%S %z %Y"),
            reverse=True,
        )

    def clean_media_data(self):
        """Clean media data from dropbox"""
        arg_timezone = pytz.timezone("America/Argentina/Buenos_Aires")
        older_than_60 = (datetime.now() - timedelta(minutes=60)).astimezone(
            arg_timezone
        )
        media_data_cloud = self.dropbox_uploader.list_files_in_dropbox_folder()
        if media_data_cloud:
            for media in media_data_cloud:
                server_modified = media.server_modified
                server_modified = server_modified.replace(
                    tzinfo=timezone.utc
                ).astimezone(arg_timezone)
                if server_modified < older_than_60:
                    logging.info(f"Removing file {media.path_lower}")
                    self.dropbox_uploader.remove_file_from_dropbox(media.path_lower)

    def process_tweets(self, data_reply: list) -> None:
        """Process tweets
        Args:
            data_reply (list): list of tweets
        """
        for data in data_reply:
            created_at = data["created_at"]
            datetime_created_at = datetime.strptime(
                created_at, "%a %b %d %H:%M:%S %z %Y"
            )
            datetime_now = datetime.now(tz=datetime_created_at.tzinfo)
            diff = datetime_now - datetime_created_at
            if diff < timedelta(seconds=100000):
                logging.info(f"Tweet id: { data['id']} Date: {datetime.now()}")
                tweet_id_to_download = data["in_reply_to_status_id"]
                tweet_id = data["id"]
                media_links_from_tweet = self.get_media_from_tweet(
                    tweet_id=tweet_id_to_download
                )
                if media_links_from_tweet:
                    status_to_reply = self.format_status(
                        tweet_id, media_links_from_tweet
                    )
                    self.twitter_bot.reply_in_thread(
                        tweet_id=tweet_id,
                        status=status_to_reply,
                    )
                    self.clean_media_data()
                    logging.info(f"Reply sent date: {datetime.now()}")
                    time.sleep(1)
                    self.twitter_bot.like(tweet_id=tweet_id)
                    logging.info(f"Tweet favorited date: {datetime.now()}")
                    time.sleep(1)
            else:
                logging.info(f"No new mentions. date: {datetime.now()}")

    def get_media_from_tweet(self, tweet_id: str) -> Optional[list]:
        """download media from tweet
        Args:
            tweet_id (str): id of tweet
        """
        try:
            tweet = self.twitter_bot.get_tweet_by_id(tweet_id)
            media_data = tweet["extended_entities"]["media"]
            username = tweet["user"]["screen_name"]
            datetime_str_yyyymmdd = datetime.strptime(
                tweet["created_at"], "%a %b %d %H:%M:%S %z %Y"
            ).strftime("%Y%m%d")
            media_files_from_tweet = []
            for media in media_data:
                video_data = media.get("video_info", None)
                if video_data:
                    variants = video_data["variants"]
                    media_files_from_tweet.append(
                        self.go_through_variants(
                            variants, username, tweet_id, datetime_str_yyyymmdd
                        )
                    )
            media_files_from_tweet = reduce(lambda x, y: x + y, media_files_from_tweet)
            return media_files_from_tweet
        except Exception as error:  # pylint: disable=broad-except
            logging.error(f"Error: {error}")
            return None

    def go_through_variants(
        self, variants: list, username: str, tweet_id: str, datetime_str_yyyymmdd: str
    ) -> list:
        """Go through variants to download the video

        Args:
            variants (list): variants of video from tweet
            username (str): username of tweet
            tweet_id (str): id of tweet
            datetime_str_yyyymmdd (str): date of tweet

        Returns:
            list: list of links to download the video
        """
        links_to_uploaded_media = []
        for variant in variants:
            if variant["content_type"] == "video/mp4":
                url = variant["url"]
                resolution = url.split("/")[-2]
                logging.info(f"video resolution: {resolution}")
                filename = (
                    f"{username}_{datetime_str_yyyymmdd}_{tweet_id}_{resolution}.mp4"
                )
                media_data = self.download_media_data(url)
                if media_data:
                    temporary_link = self.dropbox_uploader.upload_file_to_dropbox(
                        media_data, filename
                    )
                    if temporary_link:
                        links_to_uploaded_media.append(
                            {"resolution": resolution, "link": temporary_link}
                        )
            else:
                logging.info("No video found")
                logging.info(
                    f"Tweet id: %s Content_type: {tweet_id, variant['content_type']}"
                )
                continue
        return links_to_uploaded_media

    def download_media_data(self, url: str) -> Optional[bytes]:
        """download media
        Args:
            url (str): url of media
        """
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            logging.info("Downloading video")
            return response.content
        logging.info(f"Error downloading video. Status code: {response.status_code}")
        return None

    def create_folder_if_not_exists(self, path: str) -> None:
        """Create folder if not exists
        Args:
            path (str): path to create folder
        """
        if not os.path.exists(path):
            os.makedirs(path)
