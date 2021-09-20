import logging
import time
from datetime import datetime

import data
from selenium.common.exceptions import StaleElementReferenceException
from common.selenium_basics import scroll, wait_element_by_xpath
from common.utils import append_to_csv, sleep_random
from common.instagram_context import InstagramContext
from navigation.home_navigator import HomeNavigator
from config import SECS_TO_RE_CLICK, MAX_RETRIES


class UsersModalNavigator:

    def __init__(self, driver, modal_xpath, to_collect, context: InstagramContext, total_users):
        self.driver = driver
        self.modal_xpath = modal_xpath
        self.to_collect = to_collect
        self.context = context

        self.total_users = total_users
        self.users_found = set()

        self.just_followed = set()
        self.confirm_follow = set()

    def main_action(self, follow) -> set:
        """
        Best effort method to retrieve the users of a modal list\n
        Use this to obtain followers list, following list and likes list

        :param follow: follow the users or not
        :return: users set
        """
        dr = self.driver
        to_collect = self.to_collect

        prev_users_found = 0
        count = 0
        while count < 3 and prev_users_found < self.total_users:
            user_els = dr.find_elements_by_xpath("//a[@title]")

            for i, user in enumerate(user_els):
                f_username = user.get_attribute("title")
                self.users_found.add(f_username)

            if follow:
                self.click_follow_users()
                self.check_users_followed()

            n_users_found = len(self.users_found)
            logging.info(f"{n_users_found} {to_collect} found out of {self.total_users} from {self.context.name}")
            # TODO: better logging progress (enlighten)

            if n_users_found == prev_users_found:
                count += 1
            else:
                count = 0

            if self.total_users + 2 > 5:
                self.check_modal()
                scroll(dr, down=True, intensity=2)
                prev_users_found = n_users_found
                sleep_random()
            else:
                break

        logging.info(f"All {to_collect} from {self.context.name} collected successfully")
        return self.users_found

    def click_follow_users(self, try_n=0):
        try:
            follow_buttons = self.driver.find_elements_by_xpath(f"{self.modal_xpath}//button")
            for button in follow_buttons:
                if button.text == "Follow":
                    row_element = button.find_element_by_xpath("./../..")
                    username = row_element.find_element_by_xpath(".//a[@title]").get_attribute("title")

                    if username not in self.just_followed:
                        button.click()
                        self.confirm_follow.add(username)
                        sleep_random()

        except StaleElementReferenceException:
            if try_n < MAX_RETRIES:
                # FIXME!
                logging.warning(f"Stale element exception found. Retrying click_follow_user {try_n + 1} of 3")
                time.sleep(0.3)
                self.click_follow_users(try_n+1)
            else:
                logging.error('Stale Element found 3 consecutive times, omitting error and continuing process')
                scroll(self.driver, down=False, intensity=2)

    def check_users_followed(self, try_n=0):
        try:
            failed_follows = 0
            follow_buttons = self.driver.find_elements_by_xpath(f"{self.modal_xpath}//button")
            for button in follow_buttons:
                row_element = button.find_element_by_xpath("./../..")
                username = row_element.find_element_by_xpath(".//a[@title]").get_attribute("title")
                if username in self.confirm_follow:
                    if button.text != "Follow":
                        self.just_followed.add(username)
                        file_path = f"{data.temp_dir}/users_followed.csv"
                        new_row = f"{datetime.today().strftime('%Y-%m-%d')},{username}"
                        append_to_csv(file_path, new_row, False)
                    else:
                        logging.warning(f"User {username} could not be followed")
                        failed_follows += 1
                        if failed_follows > 5:
                            self.take_a_break()
            self.confirm_follow = set()
        except StaleElementReferenceException:
            if try_n < MAX_RETRIES:
                logging.warning(f"Stale element exception found. Retrying check_users_followed {try_n + 1} of 3")
                time.sleep(0.5)
                self.check_users_followed(try_n + 1)
            else:
                logging.error('Stale Element found 3 consecutive times, omitting error and taking a break')
                self.take_a_break()

    def take_a_break(self):
        home_navigator = HomeNavigator(self.driver, self.context)
        home_navigator.behave_like_human()
        self.context.go_there(self.driver)

    def check_modal(self, try_n=0):
        if try_n < MAX_RETRIES:
            modal = wait_element_by_xpath(self.driver, self.modal_xpath, False, SECS_TO_RE_CLICK)
            if modal:
                try:
                    modal.click()
                    return
                except StaleElementReferenceException:
                    pass
            else:
                if self.driver.current_url == self.context.url:
                    self.driver.find_element_by_xpath(self.context.click_xpath).click()
                else:
                    self.context.go_there(self.driver)

            sleep_random()
            self.check_modal(try_n + 1)
        else:
            raise Exception(f"Max retries to return to the modal exceeded. {str(self.context)}")

    def get_users(self):
        return self.main_action(False)

    def follow_users(self):
        return self.main_action(True)
