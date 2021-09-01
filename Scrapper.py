import sys
import time
import logging

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
import pandas as pd

from config import HEADLESS, TIMEOUT, PING, FULL_POST_DUMP
from secret_config import username, password, username_to_scrape

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)s - #%(levelname)s - %(message)s')

instagram_url = "https://www.instagram.com"
data_dir = "data"
temp_dir = f"{data_dir}/temp"


def write_text(element, text):
    element.send_keys(text)
    element.send_keys(Keys.RETURN)


def hover(dr, element_to_hover_over):
    hover_act = ActionChains(dr).move_to_element(element_to_hover_over)
    hover_act.perform()


def scroll(dr, down, intensity):
    body = dr.find_element_by_xpath("/html/body")
    if intensity == 1:
        if down:
            body.send_keys(Keys.PAGE_DOWN)
        else:
            body.send_keys(Keys.PAGE_UP)
    else:
        if down:
            body.send_keys(Keys.END)
        else:
            body.send_keys(Keys.HOME)


def wait_element_by_xpath(dr, xpath):
    secs_passed = 0
    while secs_passed < TIMEOUT:
        elements_found = dr.find_elements_by_xpath(xpath)
        if len(elements_found) > 0:
            return elements_found[0]
        time.sleep(PING)
        secs_passed += PING
    logging.error(f"Element with xpath {xpath} not found after {TIMEOUT} seconds")
    raise TimeoutError()


def check_two_outputs(dr, xpath1, xpath2):
    """
    Check two possible outcomes given two xpaths
    :param dr: reference to the driver
    :param xpath1: global xpath identifier for path 1
    :param xpath2: global xpath identifier for path 2
    :return: A tuple (first_path, elements) where the first is a boolean indicating that the first path was found
    """
    secs_passed = 0
    while secs_passed < TIMEOUT:
        elements1_found = dr.find_elements_by_xpath(xpath1)
        elements2_found = dr.find_elements_by_xpath(xpath2)
        if len(elements1_found) > 0:
            return True, elements1_found
        if len(elements2_found) > 0:
            return False, elements2_found
        time.sleep(PING)
        secs_passed += PING
    logging.error(f"The element with xpath {xpath1} nor the {xpath2} were found after {TIMEOUT} seconds")
    raise TimeoutError()


def get_driver() -> webdriver:
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless")
    opts.add_argument("--start-maximized")
    driver_ = webdriver.Chrome("./driver/chromedriver.exe",
                               options=opts)
    return driver_


def login(dr):
    dr.get(instagram_url)
    user_elem = wait_element_by_xpath(dr, "//input[@name='username']")
    write_text(user_elem, username)
    pass_elem = dr.find_element_by_xpath("//input[@name='password']")
    write_text(pass_elem, password)

    first_path, elements = check_two_outputs(dr,
                                             "//img[@alt='Instagram']",
                                             "//p[@id='slfErrorAlert']")
    if first_path:
        logging.info("Logged successfully")
    else:
        logging.error(f"Login error: {elements[0].text}")
        raise Exception()


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
        total_users = int(element.text)     # TODO: Custom int parser for 2,456

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
    dr.get(f"{instagram_url}/{act_username}/")
    wait_element_by_xpath(dr, f"//section/div/h2[text() = '{act_username}']")

    for to_extract in extract_list:
        logging.info(f"Extracting {to_extract} from {act_username}...")
        extract_func = extract_from_profile_dict[to_extract]
        extract_func(dr, act_username)
        #TODO: SAVE PROGRESS


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
    finally:
        secs_before_closing = 7
        logging.info(f"Waiting {secs_before_closing} secs before closing...")
        time.sleep(secs_before_closing)
        driver.close()
        driver.quit()
        logging.info("Driver closed successfully")
