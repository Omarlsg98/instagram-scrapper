import logging

from common.selenium_basics import get_driver, closing_routine

from scrapper.scrapper import scrap
from marketing_bot.follow_people import follow
from marketing_bot.direct_sender import direct_sender


if __name__ == "__main__":
    driver = get_driver()
    try:
        scrap(driver)
        direct_sender(driver, True)
        follow(driver, True)
        logging.info(f"SUCCESSFUL execution, ALL jobs were done")
    finally:
        closing_routine(driver)
