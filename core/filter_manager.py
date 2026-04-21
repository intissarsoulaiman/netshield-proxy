def load_file(path):
    try:
        with open(path, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

blacklist = load_file("data/blacklist.txt")
whitelist = load_file("data/whitelist.txt")

def is_blocked(url):
    # whitelist overrides blacklist if not empty
    if whitelist:
        return not any(site in url for site in whitelist)

    return any(site in url for site in blacklist)