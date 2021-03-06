import logging

import data
from common.selenium_basics import get_driver, login, closing_routine
from common.utils import get_execution_list_from_config
from config import MASTER_CONFIG
from navigation.post_navigation import PostsNavigator
from navigation.profile_navigation import ProfilesNavigator
from secret_config import username


def scrap(driver=None, logged=False):
    if not driver:
        driver = get_driver()

    if not logged:
        login(driver)

    jobs = get_execution_list_from_config(MASTER_CONFIG, "")
    for job in jobs:
        job_extract_config = MASTER_CONFIG[job]
        if job_extract_config["enabled"]:
            execution_list = get_execution_list_from_config(job_extract_config, "extract")
            if execution_list:
                if job == "from_profiles":
                    file_with_usernames = f"{data.input_dir}/get_posts_from_users.csv"
                    profiles_navigator = ProfilesNavigator(driver, file_with_usernames, execution_list)
                    profiles_navigator.get_from_profiles()
                elif job == "from_followers":
                    file_with_usernames = f"{data.temp_dir}/{username}_followers_usernames.csv"
                    profiles_navigator = ProfilesNavigator(driver, file_with_usernames, execution_list)
                    profiles_navigator.get_from_profiles()
                elif job == "from_post":
                    posts_navigator = PostsNavigator(driver)
                    posts_navigator.get_from_posts(execution_list)

    logging.info(f"SUCCESSFUL execution, all the scrapping jobs were done")


if __name__ == "__main__":
    scrap()
