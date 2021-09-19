import logging
import re

import pandas as pd

import data
from common.selenium_basics import scroll, check_two_outputs, wait_element_by_xpath
from common.utils import safe_str_to_int, append_write_pandas_csv
from config import INSTAGRAM_URL, MASTER_CONFIG
from navigation.main_elements_navigation import UsersModalNavigator


class ProfilesNavigator:

    def __init__(self, driver, file_with_users):
        self.driver = driver
        self.file_with_users = file_with_users
        self.execute_from_profile = {
            'extract/post_links': self.get_post_links,
            'extract/followers_list': self.get_users_list,
            'extract/following_list': self.get_followings_list,
        }

    def get_from_profiles(self, file_with_users, execute_list: list):
        users_list = pd.read_csv(file_with_users)
        total_users = len(users_list)
        logging.info(f"{total_users} followers found in {file_with_users}")

        for index, row in users_list.iterrows():
            act_user = row['username']
            logging.info(f"Seeing user {index + 1} out of {total_users}: {act_user}")
            self.go_to_profile(act_user, execute_list)
            # TODO: parallel execution tabs!

    def go_to_profile(self, act_username, execute_list: list):
        dr = self.driver
        dr.get(f"{INSTAGRAM_URL}/{act_username}/")
        wait_element_by_xpath(dr, f"//section/div/h2[text() = '{act_username}']")

        for to_do in execute_list:
            logging.info(f"Doing: {to_do} from {act_username}...")
            exec_func = self.execute_from_profile[to_do]
            exec_func(act_username)
            # TODO: SAVE PROGRESS

    def get_post_links(self, act_username):
        dr = self.driver
        posts_config = MASTER_CONFIG["from_profiles"]["extract"]["post_links"]
        max_posts = posts_config["first_n_posts"]

        total_posts = int(dr.find_element_by_xpath("//li/span/span").text)
        links = set()
        continue_scrolling = True
        while total_posts > len(links) and continue_scrolling:
            posts = dr.find_elements_by_xpath("//a[contains(@href,'/p/')]")
            for i, post in enumerate(posts):
                link = post.get_attribute("href")
                if len(links) < max_posts:
                    links.add(link)
                else:
                    continue_scrolling = False
                    break

            scroll(dr, True, 1)
            logging.info(f"{len(links)} links found out of {total_posts}")

        logging.info("All links collected successfully")
        links_df = pd.DataFrame(list(links), columns=["link"])
        links_df["username"] = act_username
        links_df["id"] = links_df["link"].apply(lambda x: re.search('.*/p/(.+?)/$', x).group(1))

        append_write_pandas_csv(f"{data.temp_dir}/post_links.csv", links_df, posts_config["overwrite"])
        logging.info("Post links saved")

    def get_users_list(self, act_username, get_followers=True):
        dr = self.driver
        scroll(dr, False, 2)
        is_public, _ = check_two_outputs(dr,
                                         "//div[@role='tablist']",
                                         "//article//h2")
        if is_public:
            if get_followers:
                to_collect = "followers"
                modal_xpath = "//div[@aria-label='Followers']/div/div[@class]"
            else:
                to_collect = "following"
                modal_xpath = "//div[contains(@aria-label,'Following')]/div/div[@class and not(@role)]"

            element = dr.find_element_by_xpath(f"//a[contains(@href,'{to_collect}')]/span")
            total_users = safe_str_to_int(element.text)

            element.click()
            wait_element_by_xpath(dr, modal_xpath)

            modal_navigator = UsersModalNavigator(dr, modal_xpath, to_collect, act_username)
            users = modal_navigator.get_users(total_users)

            users_pd = pd.DataFrame(list(users), columns=["username"])
            users_pd.to_csv(f"{data.temp_dir}/{act_username}_{to_collect}_usernames.csv", index=False)
            logging.info(f"{to_collect} list saved")
        else:
            # TODO: private accounts
            logging.warning("Account is private, scrapping not supported yet")

        dr.find_element_by_xpath("//*[@aria-label='Close']").click()

    def get_followings_list(self, act_username):
        self.get_users_list(act_username, get_followers=False)
