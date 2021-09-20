HEADLESS = False

INSTAGRAM_URL = "https://www.instagram.com"
INSTALLATION_DIR = "C:\\repos\\instagram-scrapper"

TIMEOUT = 30  # in secs
PING = 1  # in secs

MAX_RETRIES = 3
SECS_TO_RE_CLICK = 5

SECS_RANGE_FOR_CLICKS = (0.7, 1.5)
SECS_RANGE_TO_BEHAVE_LIKE_HUMAN = (50, 70)

SECS_BEFORE_CLOSING = 5

MASTER_CONFIG = {
    "from_profiles": {
        "enabled": True,
        "extract": {
            "post_links": {
                "enabled": True,
                "overwrite": True,
                "first_n_posts": 4,
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
