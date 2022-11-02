import aiohttp
import asyncio
import json
import yaml

async def get_Etherscan_Key():
    config = ''

    with open("Resources/Config.yaml") as file:
        config = yaml.safe_load(file)

    key = config["etherscan"]["API_Key"]
    return key

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={await get_Etherscan_Key()}') as response:
            
            gas_prices_content = await response.content.read()
            gas_prices_object = json.loads(gas_prices_content.decode("utf-8"))
            safe_gas_price = gas_prices_object['result']['SafeGasPrice']
            propose_gas_price = gas_prices_object['result']['ProposeGasPrice']
            fast_gas_price = gas_prices_object['result']['FastGasPrice']

            slow = (f'🐢 {safe_gas_price}|')
            medium = (f'🚌 {propose_gas_price}|')
            fast = (f'🚀 {fast_gas_price} (gwei)')
            
            print(f'{slow} {medium} {fast}')

asyncio.run(main())