import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from config import headless


def get_driver() -> webdriver:
    opts = Options()
    if headless:
        opts.add_argument("--headless")
    opts.add_argument("--start-maximized")
    driver_ = webdriver.Chrome("./driver/chromedriver.exe",
                               options=opts)
    return driver_


def func(dr):

    dr.get("http://www.python.org")
    assert "Python" in dr.title
    elem = dr.find_element_by_name("q")
    elem.clear()
    elem.send_keys("pycon")
    elem.send_keys(Keys.RETURN)


if __name__ == "__main__":
    driver = get_driver()
    try:
        func(driver)
    finally:
        time.sleep(4)
        driver.close()
        driver.quit()
