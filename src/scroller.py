# Modified from godkingjay/selenium-twitter-scraper
import time


class Scroller:
    DEFAULT_SCROLL: int

    def __init__(self, driver, default_scroll_amount=800) -> None:
        self.driver = driver
        self.DEFAULT_SCROLL = default_scroll_amount

    @property
    def current_position(self):
        return self.driver.execute_script("return window.pageYOffset;")

    def reset(self) -> None:
        self.last_position = self.current_position
        self.scroll_to_top()

    def scroll_to_top(self) -> None:
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

    def scroll_down(self, scroll_by=None) -> None:
        if scroll_by is None:
            scroll_by = self.DEFAULT_SCROLL
        self.driver.execute_script(f"window.scrollBy(0, {scroll_by});")
        time.sleep(1)

    def scroll_up(self, scroll_by=None) -> None:
        if scroll_by is None:
            scroll_by = self.DEFAULT_SCROLL
        self.driver.execute_script(f"window.scrollBy(0, -{scroll_by});")
        time.sleep(1)

    def scroll_to_bottom(self) -> None:
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
