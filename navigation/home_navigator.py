import logging
import random
import time

from common.instagram_context import InstagramContext
from common.selenium_basics import scroll, skip_notifications_dialog
from common.utils import sleep_random
from config import INSTAGRAM_URL, SECS_RANGE_TO_BEHAVE_LIKE_HUMAN


class HomeNavigator:

    def __init__(self, driver, previous_context):
        self.driver = driver
        self.previous_context = previous_context
        self.context = InstagramContext(name="Home",
                                        url=INSTAGRAM_URL,
                                        wait_xpath="//a[@href='/explore/people/']")

    def behave_like_human(self, for_n_secs=None):
        self.context.go_there(self.driver)
        start = time.time()
        skip_notifications_dialog(self.driver)

        for_n_secs = for_n_secs if for_n_secs else random.uniform(*SECS_RANGE_TO_BEHAVE_LIKE_HUMAN)
        time_passed = 0
        logging.info(f"Behaving like a human for {int(for_n_secs)} secs to avoid instagram bot detection ...")
        while time_passed < for_n_secs:
            sleep_random((1, 5))
            rand_dir = random.random() < 0.93
            rand_intensity = 1 if random.random() < 0.98 else 2
            scroll(self.driver, down=rand_dir, intensity=rand_intensity)
            time_passed = time.time() - start
        logging.info(f"Returning to task at hand at context: {str(self.previous_context)}")
