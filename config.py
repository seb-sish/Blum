from dotenv import load_dotenv
import os

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
   # api id, hash 
    API_ID = os.environ.get('API_ID')
    API_HASH = os.environ.get('API_HASH')

    DELAYS = {
        'ACCOUNT': [5, 15],  # delay between connections to accounts (the more accounts, the longer the delay)
        'PLAY': [5, 15],   # delay between play in seconds
        'ERROR_PLAY': [60, 180],    # delay between errors in the game in seconds
    }

    # points with each play game; max 280
    POINTS = [230, 270]

    # proxy type
    PROXY_TYPE = "socks5"  # "socks4", "socks5" and "http" are supported
    IPV6 = False

    # title blacklist tasks (do not change)
    BLACKLIST_TASKS = ["Farm", "Invite", "Summer Quest"]

    # session folder (do not change)
    WORKDIR = "sessions/"
