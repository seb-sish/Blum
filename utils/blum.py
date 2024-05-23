import random
from utils.core import logger
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView, GetMessagesViews
import asyncio
from urllib.parse import unquote
from data import config
import aiohttp
from fake_useragent import UserAgent


class Start:
    def __init__(self, thread: int, account: str, proxy: [str, None]):
        self.proxy = f"http://{proxy}" if proxy is not None else None
        self.thread = thread

        if proxy:
            proxy = {
                "scheme": "http",
                "hostname": proxy.split(":")[1].split("@")[1],
                "port": int(proxy.split(":")[2]),
                "username": proxy.split(":")[0],
                "password": proxy.split(":")[1].split("@")[0]
            }

        self.client = Client(name=account, api_id=config.API_ID, api_hash=config.API_HASH, workdir=config.WORKDIR, proxy=proxy)

        headers = {'User-Agent': UserAgent(os='android').random}
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True)
        self.refresh_token = ''

    async def main(self):
        await asyncio.sleep(random.uniform(config.ACC_DELAY[0], config.ACC_DELAY[1]))
        await self.login()

        while True:
            try:
                msg = await self.claim_daily_reward()
                if isinstance(msg, bool) and msg:
                    logger.success(f"Thread {self.thread} | Claimed daily reward!")

                timestamp, start_time, end_time, play_passes = await self.balance()

                while play_passes:
                    game_id = await self.start_game()
                    if not game_id:
                        logger.error(f"Thread {self.thread} | Couldn't start play in game!")
                        continue

                    logger.info(f"Thread {self.thread} | Start play in game! GameId: {game_id}")

                    msg, points = await self.claim_game(game_id)
                    if isinstance(msg, bool) and msg:
                        logger.success(f"Thread {self.thread} | Finish play in game!; reward: {points}")
                    else:
                        logger.error(f"Thread {self.thread} | Couldn't play game; msg: {msg}")

                    await asyncio.sleep(random.uniform(5, 10))
                    timestamp, start_time, end_time, play_passes = await self.balance()

                if start_time is None and end_time is None:
                    await self.start()
                    logger.info(f"Thread {self.thread} | Start farming!")

                elif start_time is not None and end_time is not None and timestamp >= end_time:
                    await self.refresh()
                    timestamp, balance = await self.claim()
                    logger.success(f"Thread {self.thread} | Claimed reward! Balance: {balance}")

                else:
                    logger.info(f"Thread {self.thread} | Sleep {end_time-timestamp} seconds!")
                    await asyncio.sleep(end_time-timestamp)

                await asyncio.sleep(10)
            except Exception as e:
                logger.error(f"Thread {self.thread} | Error: {e}")

    async def claim_daily_reward(self):
        resp = await self.session.post("https://game-domain.blum.codes/api/v1/daily-reward?offset=-180", proxy=self.proxy)
        txt = await resp.text()
        await asyncio.sleep(1)
        return True if txt == 'OK' else txt

    async def refresh(self):
        json_data = {'refresh': self.refresh_token}
        resp = await self.session.post("https://gateway.blum.codes/v1/auth/refresh", json=json_data, proxy=self.proxy)
        resp_json = await resp.json()

        self.session.headers['Authorization'] =  "Bearer " + resp_json.get('access')
        self.refresh_token = resp_json.get('refresh')

    async def start_game(self):
        await asyncio.sleep(random.uniform(config.PLAY_DELAY[0], config.PLAY_DELAY[1]))
        resp = await self.session.post("https://game-domain.blum.codes/api/v1/game/play", proxy=self.proxy)
        resp_json = await resp.json()

        return (resp_json).get("gameId")

    async def claim_game(self, game_id: str):
        await asyncio.sleep(random.uniform(60, 65))
        points = random.randint(config.POINTS[0], config.POINTS[1])
        json_data = {"gameId": game_id, "points": points}
        resp = await self.session.post("https://game-domain.blum.codes/api/v1/game/claim", json=json_data, proxy=self.proxy)
        txt = await resp.text()

        return True if txt == 'OK' else txt, points

    async def claim(self):
        resp = await self.session.post("https://game-domain.blum.codes/api/v1/farming/claim", proxy=self.proxy)
        resp_json = await resp.json()

        return int(resp_json.get("timestamp")/1000), resp_json.get("availableBalance")

    async def start(self):
        resp = await self.session.post("https://game-domain.blum.codes/api/v1/farming/start", proxy=self.proxy)

    async def balance(self):
        resp = await self.session.get("https://game-domain.blum.codes/api/v1/user/balance", proxy=self.proxy)
        resp_json = await resp.json()
        await asyncio.sleep(1)

        timestamp = resp_json.get("timestamp")
        if resp_json.get("farming"):
            start_time = resp_json.get("farming").get("startTime")
            end_time = resp_json.get("farming").get("endTime")

            return int(timestamp/1000), int(start_time/1000), int(end_time/1000), resp_json.get("playPasses")
        return int(timestamp/1000), None, None, resp_json.get("playPasses")

    async def login(self):
        json_data = {"query": await self.get_tg_web_data()}

        resp = await self.session.post("https://gateway.blum.codes/v1/auth/provider/PROVIDER_TELEGRAM_MINI_APP", json=json_data, proxy=self.proxy)
        resp_json = await resp.json()

        self.session.headers['Authorization'] = "Bearer " + resp_json.get("token").get("access")
        self.refresh_token = resp_json.get("token").get("refresh")

    async def get_tg_web_data(self):
        await self.client.connect()

        try:
            try:
                await self.client.join_chat("https://t.me/+3I58kRjC8uU4NTIy")
            except: pass

            async for msg in self.client.get_chat_history(-1002136959923, limit=1):
                msg_id = msg.id
            await self.client.invoke(GetMessagesViews(
                peer=await self.client.resolve_peer(-1002136959923),
                id=list(range(msg_id-random.randint(50, 100), msg_id + 1)),
                increment=True
            ))

        except: pass

        web_view = await self.client.invoke(RequestWebView(
            peer=await self.client.resolve_peer('BlumCryptoBot'),
            bot=await self.client.resolve_peer('BlumCryptoBot'),
            platform='android',
            from_bot_menu=False,
            url='https://telegram.blum.codes/'
        ))

        auth_url = web_view.url
        await self.client.disconnect()
        return unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))