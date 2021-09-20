import logging
import pandas as pd

import data
from common.instagram_context import InstagramContext
from common.selenium_basics import wait_element_by_xpath, click_with_retries
from common.utils import safe_str_to_int, append_write_pandas_csv, create_csv_headers
from config import MASTER_CONFIG
from navigation.user_modal_navigation import UsersModalNavigator


class PostsNavigator:

    def __init__(self, driver):
        self.driver = driver
        self.execute_from_post = {
            'extract/likes': self.get_likes,
            'follow/likes': self.follow_likes,
        }
        self.extract_likes_config = MASTER_CONFIG["from_post"]["extract"]["likes"]
        self.context = None

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
        post_id = post_info['id']
        url = post_info['link']
        wait_xpath = f"//*[contains(@href,'{post_id}')]"
        self.context = InstagramContext(name=post_id, url=url, wait_xpath=wait_xpath)
        self.context.go_there(self.driver)

        for to_do in execution_list:
            logging.info(f"Doing: {to_do} from post {post_id}...")
            exec_func = self.execute_from_post[to_do]
            exec_func()
            # TODO: SAVE PROGRESS

    def do_with_likes(self, action):
        dr = self.driver
        post_id = self.context.name
        to_collect = "Likes"
        modal_xpath = "//div[@aria-label='Likes']/div/div[@class]"
        click_xpath = f"//a[@href='/p/{post_id}/liked_by/']/span"
        likes_ele = wait_element_by_xpath(dr, click_xpath, False)
        if likes_ele:
            total_users = safe_str_to_int(likes_ele.text)
            click_with_retries(dr, click_xpath, modal_xpath)

            modal_context = self.context.clone(click_xpath=click_xpath, wait_xpath=modal_xpath)
            modal_navigator = UsersModalNavigator(dr, modal_xpath, to_collect, modal_context, total_users)
            if action == "extract":
                users = modal_navigator.get_users()
                users_df = pd.DataFrame(list(users), columns=["username"])
                users_df["post_id"] = post_id

                file_path = f"{data.temp_dir}/usernames_of_relevant_likes.csv"
                append_write_pandas_csv(file_path, users_df, self.extract_likes_config.get("overwrite"))
                logging.info(f"{to_collect} list updated with info from {post_id}")

            elif action == "follow":
                file_path = f"{data.temp_dir}/users_followed.csv"
                create_csv_headers(file_path, "date,username")
                modal_navigator.follow_users()

        else:
            logging.info(f"{to_collect} job SKIPPED for {post_id},"
                         "either the post doesn't have likes or 'likes' button wasn't found")

    def get_likes(self):
        self.do_with_likes("extract")

    def follow_likes(self):
        self.do_with_likes("follow")
