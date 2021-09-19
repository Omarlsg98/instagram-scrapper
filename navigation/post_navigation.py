import logging

import pandas as pd

import data
from common.selenium_basics import wait_element_by_xpath, \
    click_with_retries
from common.utils import safe_str_to_int, append_write_pandas_csv
from config import MASTER_CONFIG

from navigation.main_elements_navigation import UsersModalNavigator


class PostsNavigator:

    def __init__(self, driver):
        self.driver = driver
        self.execute_from_post = {
            'extract/likes': self.get_likes,
            'follow/likes': self.get_likes,
        }

    def get_from_posts(self, execution_list: list):
        posts = pd.read_csv(f"{data.temp_dir}/post_links.csv")
        total_posts = len(posts)
        logging.info(f"{total_posts} posts found for scrapping")

        for index, row in posts.iterrows():
            post = row
            logging.info(f"Seeing post {index + 1} out of {total_posts}: {post['id']}")
            self.go_to_post(post, execution_list)
            # TODO: parallel execution tabs!

    def go_to_post(self, post_info, execution_list):
        dr = self.driver
        dr.get(f"{post_info['link']}")
        post_id = post_info['id']
        wait_element_by_xpath(dr, f"//*[contains(@href,'{post_id}')]")

        for to_do in execution_list:
            logging.info(f"Doing: {to_do} from post {post_id}...")
            exec_func = self.execute_from_post[to_do]
            exec_func(post_id)
            # TODO: SAVE PROGRESS

    def get_likes(self, post_id):
        dr = self.driver
        likes_config = MASTER_CONFIG["from_post"]["extract"]["likes"]
        to_collect = "Likes"
        modal_xpath = "//div[@aria-label='Likes']/div/div[@class]"
        click_xpath = f"//a[@href='/p/{post_id}/liked_by/']/span"
        likes_ele = wait_element_by_xpath(dr, click_xpath, False)
        if likes_ele:
            total_users = safe_str_to_int(likes_ele.text)
            click_with_retries(dr, click_xpath, modal_xpath)

            modal_navigator = UsersModalNavigator(dr, modal_xpath, to_collect, post_id)
            users = modal_navigator.get_users(total_users)
            users_df = pd.DataFrame(list(users), columns=["username"])
            users_df["post_id"] = post_id

            file_path = f"{data.temp_dir}/usernames_of_relevant_likes.csv"
            append_write_pandas_csv(file_path, users_df, likes_config.get("overwrite"))
            logging.info(f"{to_collect} list updated with info from {post_id}")
        else:
            logging.info(f"{to_collect} job SKIPPED for {post_id},"
                         "either the post don't have likes or 'likes' button wasn't found")
