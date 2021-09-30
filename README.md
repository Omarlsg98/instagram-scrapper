# Instagram-scrapper (and bot)
A web scrapping tool to get important and relevant information about your followers on Instagram.
Initially it was just a scrapper, but then I decided to add some other bot like features.

####Web scrapping functionality:
* Post list (urls)
* Followers list
* Followers activity on your page
* Followers connections

####Bot functionality:
* Send direct messages using a template to a list of users
* Follow the people who like the first N posts of certain accounts


## Install
1. Install Google Chrome if you don't have it
2. Download the correct selenium WebDriver for your version of chrome and os
3. Execute setup.sh
4. Unzip the selenium WebDriver and paste it on the ./driver folder
5. Install the requirements.txt

##Usage
This thing barely works. Instagram is really hardcore with the measures to prevent bots
and scrappers.
>NOTE: Using this program may cause your account to be banned, so used it with precaution and/or
> with disposable accounts

To use it:
1. Change the content in secret_config.py and put the instagram credentials
   you want to use:
```python
username = "{username to login}"
password = "{password for the username}"
```
2. Configure the files in data/input according to you want to use:
* **get_posts_from_user.csv**: allows you to specify what users the scrapper must get 
the post links (useful for enabling follow with likes option. See below)
*  **message.txt**: allows you to configure the basic message template to send when sending direct messages ....  
   The {words} surrounded with brackets will be replaced on execution. 
*  **send_message_to.csv**: allows you to put the list of users that you want to send the message and also
specify the "likes" you identified on them (maybe that's useful ...)
   
3. Change the config.py file.
* Change **INSTALLATION_DIR** with your installation directory
* Change the **MASTER_CONFIG** variable:  
**example)**  
  ```python
     MASTER_CONFIG = {
        "from_profiles": {
            "enabled": True,
            "extract": {
                "post_links": {
                    "enabled": True,
                    "overwrite": True,
                    "first_n_posts": 5,
                },
                "followers_list": False,
                "following_list": False,
            },
        },
        "from_followers": {
            "enabled": False,
            "extract": {
                "followers_list": True,
                "following_list": True,
            },
        },
        "from_post": {
            "enabled": True,
            "extract": {
                "likes": {
                    "enabled": False,
                    "overwrite": False,
                },
            },
            "follow": {
                "likes": True,
            },
        },
        "send_message_from_template": {
            "enabled": False,
        }
     }
  ````
    In this example,  the program will first scrap the first 5 post links
of the get_post_from_users.csv users and then will follow all the people
who liked those extracted posts (from_post/follow/likes is true, hence enabled).  
It will not send direct messages from the template, nor extract any information from 
the followers of you account, nor any other information from your profile.

4. See results under the data/ folder.
