INSTAGRAM_URL = "https://www.instagram.com"

TIMEOUT = 30  # in secs
PING = 1  # in secs
HEADLESS = False

SECS_BEFORE_CLOSING = 7

FULL_POST_DUMP = True

EXTRACT_CONFIG = {
    "from_profile": {
        "enabled": True,
        "extract": {
            "post_links": True,
            "followers_list": False,
            "following_list": False,
        }
    },
    "from_followers": {
        "enabled": False,
        "extract": {
            "followers_list": True,
            "following_list": True,
        }
    }
}

POST_LINKS_CONFIG = {
    "first_n_posts": 5,
}