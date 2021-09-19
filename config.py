INSTAGRAM_URL = "https://www.instagram.com"
INSTALLATION_DIR = "C:\\repos\\instagram-scrapper"

TIMEOUT = 30  # in secs
PING = 1  # in secs
HEADLESS = False

CLICKS_RETRIES = 3
SECS_TO_RE_CLICK = 5

SECS_BEFORE_CLOSING = 5

MASTER_CONFIG = {
    "from_profiles": {
        "enabled": False,
        "extract": {
            "post_links": {
                "enabled": True,
                "overwrite": True,
                "first_n_posts": 2,
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
                "enabled": True,
                "overwrite": False,
            },
        },
        "follow": {
            "likes": True,
        },
    },
}
