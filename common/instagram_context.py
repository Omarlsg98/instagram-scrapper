from common.selenium_basics import wait_element_by_xpath
from config import SECS_TO_RE_CLICK, TIMEOUT


class InstagramContext:
    def __init__(self, name, url, wait_xpath, parent=None, click_xpath=None):
        if not url and not click_xpath:
            raise Exception(f"Incorrect instantiation of an InstagramContext")
        self.name = name
        self.url = url
        self.click_xpath = click_xpath
        self.wait_xpath = wait_xpath
        self.parent = parent

    def clone(self, name=None, url=None, wait_xpath=None, parent=None, click_xpath=None):
        return InstagramContext(
            name=name if name else self.name,
            url=url if url else self.url,
            click_xpath=click_xpath if click_xpath else self.click_xpath,
            wait_xpath=wait_xpath if wait_xpath else self.wait_xpath,
            parent=parent if parent else self,
        )

    def go_there(self, driver):
        context_chain = self.get_context_chain()
        for node in context_chain:
            if node.click_xpath:
                driver.find_element_by_xpath(node.click_xpath).click()
                wait_element_by_xpath(driver, node.wait_xpath, False, SECS_TO_RE_CLICK)
            else:
                driver.get(node.url)
                wait_element_by_xpath(driver, node.wait_xpath)

    def get_context_chain(self):
        """
        Get context chain of actual node
        :return: context_chain organized from upmost parent to actual node
        """
        context_chain = [self]
        actual_node = self
        while actual_node.parent:
            actual_node = actual_node.parent
            context_chain.insert(0, actual_node)
        return context_chain

    def __str__(self):
        return f"InstagramContext(url={self.url}, name={self.name}," \
               f"click_xpath:{self.click_xpath}, parent:{self.parent.name})"
