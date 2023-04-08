""" Main process of the bot """
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Union

from bot.twitter_controller import TwitterController

logging.basicConfig(level=logging.INFO)


class MainProcess:
    """Main process of the bot"""

    def __init__(
        self, path_to_download: Union[str, Dict[str, str]], **dict_auth_bot
    ) -> None:
        """Create a main process object"""
        self.twitter_handler = TwitterController(**dict_auth_bot)
        logging.info("starting process")
        self.last_id: Optional[str] = None
        self.path_to_download: str = str(path_to_download)

    def run(self):
        """Run the main process"""
        if self.last_id:
            logging.info("Last id: %s Date: %s", self.last_id, datetime.now())
            data_reply = self.twitter_handler.get_mentions(
                count=10, since_id=self.last_id
            )
        else:
            data_reply = self.twitter_handler.get_mentions(count=10)
        time.sleep(2)
        logging.info("Data reply count: %s Date: %s", len(data_reply), datetime.now())
        if len(data_reply) > 0:
            data_reply = self.order_by_date(data_reply)
            self.last_id = data_reply[0]["id"]
            logging.info("Last id set: %s Date: %s", self.last_id, datetime.now())
            self.process_tweets(data_reply=data_reply)
        else:
            logging.info("No new mentions, Date: %s", datetime.now())
        time.sleep(10)

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
            if diff < timedelta(seconds=20):
                logging.info("Tweet id: %s Date: %s", data["id"], datetime.now())
                tweet_id_to_download = data["in_reply_to_status_id"]
                tweet_id = data["id"]
                time.sleep(1)
                self.twitter_handler.download_media_from_tweet(
                    tweet_id=tweet_id_to_download, path=self.path_to_download
                )
                logging.info("Video downloaded. date: %s", datetime.now())
                time.sleep(1)
                self.twitter_handler.reply_in_thread(
                    tweet_id=tweet_id,
                    status="Video downloaded and saved in Downloads folder",
                )
                logging.info("Reply sent date: %s", datetime.now())
                time.sleep(1)
                self.twitter_handler.like(tweet_id=tweet_id)
                logging.info("Tweet favorited date: %s", datetime.now())
                time.sleep(1)
            else:
                logging.info("No new mentions. date: %s", datetime.now())


# @DownloaderBotAP Download bot
