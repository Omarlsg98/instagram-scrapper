import logging

from common.selenium_basics import get_driver, login, closing_routine
from common.utils import get_execution_list_from_config
from config import MASTER_CONFIG
from navigation.post_navigation import PostsNavigator


def follow(driver=None, logged=False):
    if not driver:
        driver = get_driver()

    try:
        if not logged:
            login(driver)

        jobs = get_execution_list_from_config(MASTER_CONFIG, "")
        for job in jobs:
            job_extract_config = MASTER_CONFIG[job]
            if job_extract_config["enabled"]:
                execution_list = get_execution_list_from_config(job_extract_config, "follow")
                if execution_list:
                    if job == "from_post":
                        posts_navigator = PostsNavigator(driver)
                        posts_navigator.get_from_posts(execution_list)

        logging.info(f"SUCCESSFUL execution, all the follow_people jobs were done")
    finally:
        closing_routine(driver)


if __name__ == "__main__":
    follow()
