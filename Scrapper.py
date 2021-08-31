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


def write_text(element, text):
    element.send_keys(text)
    element.send_keys(Keys.RETURN)


def hover(dr, element_to_hover_over):
    hover_act = ActionChains(dr).move_to_element(element_to_hover_over)
    hover_act.perform()


def scroll(dr, direction, intensity):
    body = dr.find_element_by_xpath("/html/body")
    if intensity == 1:
        if direction:
            body.send_keys(Keys.PAGE_DOWN)
        else:
            body.send_keys(Keys.PAGE_UP)
    else:
        if direction:
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


def get_post_links(dr):
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
        .to_csv(f"data/{username_to_scrape}_post_links.csv", index=False)
    logging.info("Post links saved")


def get_followers_list(dr):
    followers_element = dr.find_element_by_xpath("//a[contains(@href,'followers')]/span")
    total_followers = int(followers_element.text)

    followers_element.click()
    wait_element_by_xpath(dr, "//div[@aria-label='Followers']")

    followers = set()
    while total_followers > len(followers):
        followers_els = dr.find_elements_by_xpath("//a[@title]")
        for i, follower in enumerate(followers_els):
            f_username = follower.get_attribute("title")
            followers.add(f_username)

        followers_window = dr.find_element_by_xpath("//div[@aria-label='Followers']/div/div[@class]")
        followers_window.click()
        scroll(dr, True, 2)

        logging.info(f"{len(followers)} links found out of {total_followers}")

    logging.info("All followers collected successfully")
    pd.DataFrame(list(followers), columns=["follower"]) \
        .to_csv(f"data/{username_to_scrape}_followers_usernames.csv", index=False)
    logging.info("Followers list saved")


def go_to_profile(dr):
    dr.get(f"{instagram_url}/{username_to_scrape}/")
    wait_element_by_xpath(dr, "//button[@title='Change Profile Photo']")

    #get_post_links(dr)
    scroll(dr, False, 2)
    get_followers_list(dr)


if __name__ == "__main__":
    driver = get_driver()
    try:
        login(driver)
        go_to_profile(driver)

    finally:
        time.sleep(4)
        driver.close()
        driver.quit()
