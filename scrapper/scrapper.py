import time
import logging

import pandas as pd

from common.selenium_basics import get_driver, login, scroll, check_two_outputs, wait_element_by_xpath, \
    closing_routine
from config import FULL_POST_DUMP, INSTAGRAM_URL
from secret_config import username_to_scrape

data_dir = "../data"
temp_dir = f"{data_dir}/temp"


def get_info_from_post(dr, number):
    # POST: URL (id)
    # number_post
    # Date
    # Alt image
    # Download image(?)
    # Description
    # Date captured

    # Insights?

    # Likes (id, user, date_captured)
    # Comments (id, user, comment, favs, replies, date_posted)

    if FULL_POST_DUMP:
        pass


def get_post_links(dr, act_username):
    total_posts = int(dr.find_element_by_xpath("//li/span/span").text)
    links = set()
    while total_posts > len(links):
        posts = dr.find_elements_by_xpath("//a[contains(@href,'/p/')]")
        for i, post in enumerate(posts):
            link = post.get_attribute("href")
            links.add(link)
        scroll(dr, True, 1)
        logging.info(f"{len(links)} links found out of {total_posts}")
    logging.info("All links collected successfully")
    pd.DataFrame(list(links), columns=["link"]) \
        .to_csv(f"{temp_dir}/{act_username}_post_links.csv", index=False)
    logging.info("Post links saved")


def get_users_list(dr, act_username, get_followers=True):
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
        total_users = int(element.text)  # TODO: Custom int parser for 2,456

        element.click()
        wait_element_by_xpath(dr, modal_xpath)

        users = set()
        prev_users_found = 0
        count = 0
        while count < 3:
            user_els = dr.find_elements_by_xpath("//a[@title]")
            users_found = len(user_els)
            logging.info(f"{len(user_els)} {to_collect} found out of {total_users} for {act_username}")
            if users_found == prev_users_found:
                count += 1
            else:
                count = 0
            modal_window = dr.find_element_by_xpath(modal_xpath)
            modal_window.click()
            scroll(dr, down=True, intensity=2)
            time.sleep(1)
            prev_users_found = users_found

        for i, user in enumerate(user_els):
            f_username = user.get_attribute("title")
            users.add(f_username)

        logging.info(f"All {to_collect} collected successfully")
        pd.DataFrame(list(users), columns=["follower"]) \
            .to_csv(f"{temp_dir}/{act_username}_{to_collect}_usernames.csv", index=False)
        logging.info(f"{to_collect} list saved")
    else:
        # TODO: private accounts
        logging.warning("Account is private, scrapping not supported yet")

    dr.find_element_by_xpath("//*[@aria-label='Close']").click()


def get_followings_list(dr, act_username):
    get_users_list(dr, act_username, get_followers=False)


extract_from_profile_dict = {
    'post_links': get_post_links,
    'followers_list': get_users_list,
    'following_list': get_followings_list,
}


def go_to_profile(dr, act_username, extract_list: list):
    dr.get(f"{INSTAGRAM_URL}/{act_username}/")
    wait_element_by_xpath(dr, f"//section/div/h2[text() = '{act_username}']")

    for to_extract in extract_list:
        logging.info(f"Extracting {to_extract} from {act_username}...")
        extract_func = extract_from_profile_dict[to_extract]
        extract_func(dr, act_username)
        # TODO: SAVE PROGRESS


def get_from_followers(dr, followers_of_username, extract_list: list):
    followers = pd.read_csv(f"{temp_dir}/{followers_of_username}_followers_usernames.csv")
    total_followers = len(followers)
    logging.info(f"{total_followers} followers found for {followers_of_username}")

    for index, row in followers.iterrows():
        follower = row['follower']
        logging.info(f"Seeing follower {index + 1} out of {total_followers}: {follower}")
        go_to_profile(dr, follower, extract_list)
        # TODO: parallel execution tabs!


if __name__ == "__main__":
    driver = get_driver()
    try:
        login(driver)
        # go_to_profile(driver, username_to_scrape, ['post_links', 'followers_list'])
        get_from_followers(driver, username_to_scrape, ['followers_list', 'following_list'])
        # TODO: Extract from posts

    finally:
        closing_routine(driver)
