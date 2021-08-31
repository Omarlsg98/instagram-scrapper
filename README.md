# Instagram-scrapper
A web scrapping tool to get important and relevant information about your followers on Instagram.

With this you can get:
* Followers list
* Followers activity on your page
* Followers connections

## Install
1. Install Google Chrome if you don't have it
2. Download the correct selenium WebDriver for your version of chrome and os
3. Unzip the selenium WebDriver and paste it on the ./driver folder
4. Create a file in the root path called secret_config.py and put the following:
```python
username = "{username to login}"
password = "{password for the username}"
username_to_scrape = "{username to scrape}"
```
5. Install the requirements.txt
6. Run Scrapper.py