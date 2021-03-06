import time
import logging

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from secret_config import username, password
from config import HEADLESS, TIMEOUT, PING, INSTAGRAM_URL, SECS_BEFORE_CLOSING, MAX_RETRIES, \
    SECS_TO_RE_CLICK, INSTALLATION_DIR

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)s - #%(levelname)s - %(message)s')


def write_text(dr, element, text):
    for part in text.split('\n'):
        element.send_keys(part)
        ActionChains(dr).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()
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
    elif intensity == 2:
        if down:
            body.send_keys(Keys.END)
        else:
            body.send_keys(Keys.HOME)
    else:
        raise Exception("Invalid intensity")


def click_with_retries(dr, xpath_click, xpath_confirmation):
    tries = 0
    while tries < MAX_RETRIES:
        element_to_click = dr.find_element_by_xpath(xpath_click)
        element_to_click.click()
        tries = tries + 1
        if wait_element_by_xpath(dr, xpath_confirmation, False, SECS_TO_RE_CLICK):
            return
        else:
            logging.info(f"Retrying click for xpath {xpath_click}. Try {tries} out of {MAX_RETRIES}")
    logging.error(f"Element with xpath {xpath_confirmation} not found after {tries} clicks to {xpath_click}")
    raise TimeoutError()


def wait_element_by_xpath(dr, xpath, error_on_timeout=True, wait_time=TIMEOUT):
    secs_passed = 0
    while secs_passed < wait_time:
        elements_found = dr.find_elements_by_xpath(xpath)
        if len(elements_found) > 0:
            logging.debug(f"########### element found {xpath}")
            return elements_found[0]
        time.sleep(PING)
        secs_passed += PING
    if error_on_timeout:
        logging.error(f"Element with xpath {xpath} not found after {wait_time} seconds")
        raise TimeoutError()
    else:
        return False


def wait_any_element_to_have_text(dr, xpath, text):
    secs_passed = 0
    while secs_passed < TIMEOUT:
        elements_found = dr.find_elements_by_xpath(xpath)
        for element in elements_found:
            if element.text == text:
                return element
        time.sleep(PING)
        secs_passed += PING
    logging.error(f"Element with xpath {xpath} and text {text} not found after {TIMEOUT} seconds")
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
    driver_ = webdriver.Chrome(f"{INSTALLATION_DIR}/driver/chromedriver.exe",
                               options=opts)
    return driver_


def login(dr):
    dr.get(INSTAGRAM_URL)
    user_elem = wait_element_by_xpath(dr, "//input[@name='username']")
    write_text(dr, user_elem, username)
    pass_elem = dr.find_element_by_xpath("//input[@name='password']")
    write_text(dr, pass_elem, password)

    first_path, elements = check_two_outputs(dr,
                                             "//img[@alt='Instagram']",
                                             "//p[@id='slfErrorAlert']")
    if first_path:
        logging.info("Logged successfully")
    else:
        logging.error(f"Login error: {elements[0].text}")
        raise Exception()


def skip_notifications_dialog(dr):
    notifications_dialog = dr.find_elements_by_xpath("//div[@role='dialog']")
    if notifications_dialog:
        buttons = notifications_dialog[0].find_elements_by_xpath(".//button")
        for button in buttons:
            if button.text == "Not Now":
                button.click()


def closing_routine(dr):
    logging.info(f"Waiting {SECS_BEFORE_CLOSING} secs before closing...")
    time.sleep(SECS_BEFORE_CLOSING)
    dr.close()
    dr.quit()
    logging.info("Driver closed successfully")
