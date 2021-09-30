import logging

import pandas as pd

from common.selenium_basics import get_driver, login, wait_element_by_xpath, \
     write_text, wait_any_element_to_have_text, skip_notifications_dialog
from common.utils import beautify_list, get_execution_list_from_config

from config import INSTAGRAM_URL, MASTER_CONFIG
from secret_config import username

import data


def send_message(dr, to_username, message):
    new_message_button = wait_element_by_xpath(dr, "//*[@aria-label='New Message']")
    new_message_button.click()

    search_user_input = dr.find_element_by_xpath("//input[@name='queryBox']")
    write_text(dr, search_user_input, to_username)

    first_user = wait_element_by_xpath(dr, "//div[@aria-disabled='false']")
    first_user.click()

    next_button = wait_element_by_xpath(dr, "//button/div[text()='Next']")
    next_button.click()

    wait_any_element_to_have_text(dr, "//button/div/div/div", to_username)

    text_area = wait_element_by_xpath(dr, "//textarea[@placeholder]")
    write_text(dr, text_area, message)


def send_message_from_template(dr, template, to_username, likes):
    b_likes = beautify_list(likes)
    final_message = template.format(username=to_username, like=b_likes)
    send_message(dr, to_username, final_message)


def go_to_direct(dr, act_username, action_list: list):
    dr.get(f"{INSTAGRAM_URL}/direct/inbox/")
    wait_element_by_xpath(dr, "//*[@aria-label='New Message']")

    skip_notifications_dialog(dr)

    if 'send_message_from_template' in action_list:
        with open(f"{data.input_dir}/message.txt", 'r') as temp:
            template = temp.read()

        destinations = pd.read_csv(f"{data.input_dir}/send_message_to.csv")
        total_destinations = len(destinations)
        for index, row in destinations.iterrows():
            destination = row['username']
            likes = row['likes'].split('|')
            logging.info(f"{index + 1} of {total_destinations}, Sending message to {destination} " +
                         f"from {act_username} using template...")
            send_message_from_template(dr, template, destination, likes)


def direct_sender(driver=None, logged=False):
    if not driver:
        driver = get_driver()

    if not logged:
        login(driver)

    if "send_message_from_template" in get_execution_list_from_config(MASTER_CONFIG, ""):
        go_to_direct(driver, username, ["send_message_from_template"])
        logging.info("All message sent SUCCESSFULLY")
    else:
        logging.info("Send messages from template option disabled!")


if __name__ == "__main__":
    direct_sender()
