import dotenv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
import pandas as pd
import hashlib
from datetime import datetime


from scroller import Scroller

dotenv.load_dotenv()

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_PATH = DATA_DIR / "twitter_data.csv"
DATA = pd.read_csv(DATA_PATH) if DATA_PATH.exists() else pd.DataFrame()


class Tweet:
    def __init__(
        self,
        username: str,
        handle: str,
        datetime: datetime,
        content: str,
        n_likes: int,
        n_comments: int,
        n_reposts: int,
        n_bookmarks: int,
        n_views: int,
    ) -> None:
        # Note: tweet_id is not same as Twitter tweet ID
        self.tweet_id = self.get_tweet_id(content)
        self.username = username
        self.handle = handle
        self.datetime = datetime
        self.content = content
        self.likes = n_likes
        self.comments = n_comments
        self.reposts = n_reposts
        self.bookmarks = n_bookmarks
        self.views = n_views

    @classmethod
    def get_tweet_id(cls, content: str):
        return hashlib.md5(content.encode()).hexdigest()[:8]

    def to_dict(self):
        return {
            "tweet_id": self.tweet_id,
            "username": self.username,
            "handle": self.handle,
            "datetime": self.datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "content": self.content,
            "likes": self.likes,
            "comments": self.comments,
            "reposts": self.reposts,
            "bookmarks": self.bookmarks,
            "views": self.views,
        }

    def __str__(self) -> str:
        return f"Tweet(tweet_id={self.tweet_id}, username={self.username}, handle={self.handle}, datetime={self.datetime.strftime('%Y-%m-%d %H:%M:%S')}, content={self.content}, likes={self.likes}, comments={self.comments}, reposts={self.reposts}, bookmarks={self.bookmarks}, views={self.views})"

    def __repr__(self) -> str:
        return self.__str__()


class TwitterScraper:
    BASE_URL = "https://twitter.com/"

    def __init__(self, driver=webdriver.Chrome()) -> None:
        self.driver = driver
        self.scroller = Scroller(self.driver)

    def _login(self):
        if os.environ.get("TWITTER_USERNAME") is None:
            raise Exception("TWITTER_USERNAME not found in .env")
        if os.environ.get("TWITTER_PASSWORD") is None:
            raise Exception("TWITTER_PASSWORD not found in .env")
        # Input username
        self.driver.find_element(By.NAME, "text").send_keys(
            os.environ.get("TWITTER_USERNAME")
        )
        # Click next
        self.driver.find_element(By.XPATH, "//*[text()='Next']").click()
        # Input password
        self.driver.find_element(By.NAME, "password").send_keys(
            os.environ.get("TWITTER_PASSWORD")
        )
        # Click login
        self.driver.find_element(By.XPATH, "//*[text()='Log in']").click()

    def go_to_profile(self, username):
        self.driver.get(f"https://twitter.com/{username}")
        time.sleep(3)
        try:
            self._login()
        except:
            print("Error logging in. Potentially already logged in.")
        time.sleep(3)

    def get_post(self):
        return self.driver.find_element(By.XPATH, '//div[@data-testid="cellInnerDiv"]')

    def get_cards(self):
        return self.driver.find_elements(
            By.XPATH, '//article[@data-testid="tweet" and not(@disabled)]'
        )

    def browse(self, username, num_scrolls=10):
        """Browse a Twitter profile by just scrolling down"""
        self.go_to_profile(username)
        for _ in range(num_scrolls):
            self.scroller.scroll_down()

    def parse_card(self, card) -> Tweet:
        user = card.find_element("xpath", './/div[@data-testid="User-Name"]//span').text
        handle = card.find_element("xpath", './/span[contains(text(), "@")]').text
        # TODO: Fix datetime
        # dt = card.find_element("xpath", ".//time").get_attribute("datetime")
        dt = datetime.now()
        content = card.find_element("xpath", './/div[@data-testid="tweetText"]')
        like_element = card.find_element("xpath", './/div[@role="group"]')
        engagement = like_element.get_attribute("aria-label")
        if engagement is None:
            raise Exception("Engagement is None")
        comments, likes, reposts, bookmarks, views = self._parse_engagement(engagement)

        return Tweet(
            username=user,
            handle=handle,
            datetime=dt,
            content=content.text.strip(),
            n_likes=likes,
            n_comments=comments,
            n_reposts=reposts,
            n_bookmarks=bookmarks,
            n_views=views,
        )

    def _parse_engagement(self, engagement):
        engagement = engagement.split(",")
        engagement = list(map(lambda x: x.split(), engagement))
        engagement = {v: int(k) for k, v in engagement}
        return (
            engagement.get("comments", 0),
            engagement.get("likes", 0),
            engagement.get("reposts", 0),
            engagement.get("bookmarks", 0),
            engagement.get("views", 0),
        )

    def scrape_posts(self, username, num_posts=250):
        self.go_to_profile(username)
        data = {}  # Tweet ID: Tweet

        while len(data) < num_posts:
            self.scroller.scroll_down()
            cards = self.get_cards()
            # Parse only the last 10 cards found
            for card in cards[-10:]:
                try:
                    tweet = self.parse_card(card)
                except Exception as e:
                    print("Error parsing card")
                    print(e)
                    continue
                if tweet.tweet_id in data:
                    continue
                data[tweet.tweet_id] = tweet
        return data


def main():
    # Set up the Selenium WebDriver
    profile = "_bubblyabby_"
    twitter_scraper = TwitterScraper()
    data = twitter_scraper.scrape_posts(profile, 10)
    print(data)


if __name__ == "__main__":
    main()
    input()
