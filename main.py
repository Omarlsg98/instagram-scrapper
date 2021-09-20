import logging

from common.selenium_basics import get_driver

from scrapper.scrapper import scrap
from marketing_bot.follow_people import follow


if __name__ == "__main__":
    driver = get_driver()
    # scrap(driver)
    follow(driver)

    logging.info(f"SUCCESSFUL execution, ALL jobs were done")
