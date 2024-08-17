from utils.core import create_sessions
from utils.telegram import Accounts
from utils.starter import start, stats
import asyncio
import sys
import os


async def main():
    action = get_action()

    if not os.path.exists('sessions'): os.mkdir('sessions')
    if not os.path.exists('statistics'): os.mkdir('statistics')
    if not os.path.exists('sessions/accounts.json'):
        with open("sessions/accounts.json", 'w') as f:
            f.write("[]")

    match action:
        case 3: await create_sessions()
        case 2: await stats()
        case 1: 
            accounts = await Accounts().get_accounts()
            tasks = []
            for thread, account in enumerate(accounts):
                tasks.append(asyncio.create_task(start(session_name=account["session_name"], phone_number=account["phone_number"], 
                                                       thread=thread, proxy=account["proxy"], play_game=account["play_game"])))

            await asyncio.gather(*tasks)

def get_action():
    if len(sys.argv) == 2: action = sys.argv[1]
    else: action = input("Select action:\n1. Start soft\n2. Get statistics\n3. Create sessions\n\n> ")
    
    if action in ["1", "2", "3"]: return int(action)
    else: 
        print("Wrong value! Try again...\n")
        return get_action()

if __name__ == '__main__':
    asyncio.run(main())
