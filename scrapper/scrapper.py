import re
import time
import logging

import pandas as pd

from common.utils import safe_str_to_int, append_write_pandas_csv
from common.selenium_basics import get_driver, login, scroll, check_two_outputs, wait_element_by_xpath, \
    closing_routine, click_with_retries
from config import INSTAGRAM_URL, EXTRACT_CONFIG

from secret_config import username


data_dir = "../data"
temp_dir = f"{data_dir}/temp"
input_dir = f"{data_dir}/input"


def get_users_from_scroll_modal(dr, modal_xpath, to_collect, total_users, get_from) -> set:
    """
    Best effort method to retrieve the users of a modal list\n
    Use this to obtain followers list, following list and likes list

    :param dr: selenium driver
    :param modal_xpath: xpath of the modal
    :param to_collect: name of the list of users
    :param total_users: number of expected users
    :param get_from: context of source of information
    :return: users set
    """
    users = set()
    prev_users_found = 0
    count = 0
    wait_element_by_xpath(dr, modal_xpath)
    while count < 3 and prev_users_found < total_users:
        user_els = dr.find_elements_by_xpath("//a[@title]")

        for i, user in enumerate(user_els):
            f_username = user.get_attribute("title")
            users.add(f_username)

        users_found = len(users)
        logging.info(f"{users_found} {to_collect} found out of {total_users} from {get_from}")
        # TODO: better logging progress (enlighten)
        # TODO: instagram generates a blink of this modal when is a bot, make a bot capable of return to the modal
        # TODO: instagram stop displaying the users names if detects is a bot, reload page/give likes until works (?)
        
        if users_found == prev_users_found:
            count += 1
        else:
            count = 0

        if total_users + 2 > 5:
            modal_window = wait_element_by_xpath(dr, modal_xpath)
            modal_window.click()
            scroll(dr, down=True, intensity=2)
            time.sleep(1)
            prev_users_found = users_found
        else:
            break

    logging.info(f"All {to_collect} from {get_from} collected successfully")
    return users


def get_likes(dr, post_id):
    likes_config = EXTRACT_CONFIG["from_post"]["extract"]["likes"]
    to_collect = "Likes"
    modal_xpath = "//div[@aria-label='Likes']/div/div[@class]"
    click_xpath = f"//a[@href='/p/{post_id}/liked_by/']/span"
    likes_ele = wait_element_by_xpath(dr, click_xpath, False)
    if likes_ele:
        total_users = safe_str_to_int(likes_ele.text)
        click_with_retries(dr, click_xpath, modal_xpath)

        users = get_users_from_scroll_modal(dr, modal_xpath, to_collect, total_users, post_id)
        users_df = pd.DataFrame(list(users), columns=["username"])
        users_df["post_id"] = post_id

        file_path = f"{temp_dir}/usernames_of_relevant_likes.csv"
        append_write_pandas_csv(file_path, users_df, likes_config.get("overwrite"))
        logging.info(f"{to_collect} list updated with info from {post_id}")
    else:
        logging.info(f"{to_collect} job SKIPPED for {post_id}," 
                     "either the post don't have likes or 'likes' button wasn't found")


extract_from_post = {
    'likes': get_likes,
}


def go_to_post(dr, post_info, extract_list):
    dr.get(f"{post_info['link']}")
    post_id = post_info['id']
    wait_element_by_xpath(dr, f"//*[contains(@href,'{post_id}')]")

    for to_extract in extract_list:
        logging.info(f"Extracting {to_extract} from {post_id}...")
        extract_func = extract_from_post[to_extract]
        extract_func(dr, post_id)
        # TODO: SAVE PROGRESS


def get_from_posts(dr, extract_list: list):
    posts = pd.read_csv(f"{temp_dir}/post_links.csv")
    total_posts = len(posts)
    logging.info(f"{total_posts} posts found for scrapping")

    for index, row in posts.iterrows():
        post = row
        logging.info(f"Seeing post {index + 1} out of {total_posts}: {post['id']}")
        go_to_post(dr, post, extract_list)
        # TODO: parallel execution tabs!


def get_post_links(dr, act_username):
    posts_config = EXTRACT_CONFIG["from_profiles"]["extract"]["post_links"]
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

    append_write_pandas_csv(f"{temp_dir}/post_links.csv", links_df, posts_config["overwrite"])
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
        total_users = safe_str_to_int(element.text)

        element.click()
        wait_element_by_xpath(dr, modal_xpath)

        users = get_users_from_scroll_modal(dr, modal_xpath, to_collect, total_users, act_username)

        users_pd = pd.DataFrame(list(users), columns=["username"])
        users_pd.to_csv(f"{temp_dir}/{act_username}_{to_collect}_usernames.csv", index=False)
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


def get_from_profiles(dr, file_with_users, extract_list: list):
    users_list = pd.read_csv(file_with_users)
    total_users = len(users_list)
    logging.info(f"{total_users} followers found in {file_with_users}")

    for index, row in users_list.iterrows():
        act_user = row['username']
        logging.info(f"Seeing user {index + 1} out of {total_users}: {act_user}")
        go_to_profile(dr, act_user, extract_list)
        # TODO: parallel execution tabs!


def get_execution_list_from_config(extract_dict: dict):
    extract_list = []
    for key, value in extract_dict.items():
        if value:
            extract_list.append(key)
        elif type(value) is dict and value.get("enabled"):
            extract_list.append(key)
    return extract_list


def main():
    driver = get_driver()

    try:
        login(driver)
        from_users = pd.read_csv(f"{input_dir}/get_posts_from_users.csv")
        user_to_scrape = from_users["username"][0]  # TODO: THIS

        jobs = get_execution_list_from_config(EXTRACT_CONFIG)
        for job in jobs:
            job_extract_config = EXTRACT_CONFIG[job]
            if job_extract_config["enabled"]:
                extract_list_ = get_execution_list_from_config(job_extract_config["extract"])
                if job == "from_profiles":
                    file_with_usernames = f"{input_dir}/get_posts_from_users.csv"
                    get_from_profiles(driver, file_with_usernames, extract_list_)
                elif job == "from_followers":
                    file_with_usernames = f"{temp_dir}/{username}_followers_usernames.csv"
                    get_from_profiles(driver, file_with_usernames, extract_list_)
                elif job == "from_post":
                    get_from_posts(driver, extract_list_)

        logging.info(f"SUCCESSFUL execution, all the scrapping jobs were done")
    finally:
        closing_routine(driver)


if __name__ == "__main__":
    main()
