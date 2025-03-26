import re

CUSTOM_HEADER = {
    'Host': 'api.spotidownloader.com',
    'Referer': 'https://spotidownloader.com/',
    'Origin': 'https://spotidownloader.com',
}

PURR_HEADER = {
    'Host': 'simba.purr.rip',
    'Referer': 'https://spotidownloader.com/',
    'Origin': 'https://spotidownloader.com',
}

NAME_SANITIZE_REGEX = re.compile(r"[<>:\"\/\\|?*]")
