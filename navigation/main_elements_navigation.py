import logging
import time

from common.selenium_basics import scroll, wait_element_by_xpath


class UsersModalNavigator:

    def __init__(self, driver, modal_xpath, to_collect, context):
        self.driver = driver
        self.modal_xpath = modal_xpath
        self.to_collect = to_collect
        self.context = context

    def get_users(self, total_users) -> set:
        """
        Best effort method to retrieve the users of a modal list\n
        Use this to obtain followers list, following list and likes list

        :param total_users: number of expected users
        :return: users set
        """
        dr = self.driver
        modal_xpath = self.modal_xpath
        to_collect = self.to_collect

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
            logging.info(f"{users_found} {to_collect} found out of {total_users} from {self.context}")
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

        logging.info(f"All {to_collect} from {self.context} collected successfully")
        return users
