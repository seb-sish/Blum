import pyrogram
from loguru import logger
from config import Config
from utils.core.file_manager import save_to_json
import phonenumbers
from langcodes import Language


def lang_code_by_phone(phone_number: str):
    try:
        country_code = phonenumbers.region_code_for_number(phonenumbers.parse(phone_number))
        if country_code: return Language.get(country_code).language
        else: return "en"
    except: return "en"


async def create_sessions():
    while True:
        session_name = input('\nInput the name of the session (press Enter to exit): ')
        if not session_name: return

        proxy = input("Input the proxy in the format login:password@ip:port (press Enter to use without proxy): ")
        if proxy:
            client_proxy = {
                "scheme": Config.PROXY_TYPE,
                "hostname": proxy.split(":")[1].split("@")[1],
                "port": int(proxy.split(":")[2]),
                "username": proxy.split(":")[0],
                "password": proxy.split(":")[1].split("@")[0]
            }
        else:
            client_proxy, proxy = None, None

        phone_number = (input("Input the phone number of the account: ")).replace(' ', '')
        phone_number = '+' + phone_number if not phone_number.startswith('+') else phone_number

        client = pyrogram.Client(
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            name=session_name,
            workdir=Config.WORKDIR,
            phone_number=phone_number,
            proxy=client_proxy,
            ipv6=Config.IPV6
        )

        async with client:
            me = await client.get_me()

        play_game = ''
        while play_game == '':
            play_game = input("Play game on the account(Y/n): ")
            if play_game.lower() in ['y', '']:
                play_game = True
                break
            elif play_game.lower() == 'n':
                play_game = False
                break
            else: 
                print("Wrong answer, try again")

        save_to_json('sessions/accounts.json', dict_={
            "session_name": session_name,
            "phone_number": phone_number,
            "play_game": play_game,
            "proxy": proxy
        })
        logger.success(f'Added a account {me.username} ({me.first_name}) | {me.phone_number}')
