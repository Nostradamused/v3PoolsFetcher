import json
from web3 import Web3
import asyncio
import time
import requests




class V3Pools:
    def __init__(self, fromBlock, toBlock, dex="uniswap"):
        self.config = json.load(open("config.json"))
        self.provider = Web3(Web3.WebsocketProvider(self.config["wss"]))
        self.fromBlock = fromBlock
        self.toBlock = toBlock
        if dex == "uniswap":
            self.contractFactory = self.provider.eth.contract(address=self.config["factoryAddress"],abi=json.load(open("./abis/factories/UniV3FactoryABI.json")))
            self.contractPool = self.provider.eth.contract(address=self.config["poolAddress"],abi=json.load(open("./abis/pools/UniV3PoolABI.json")))
        elif dex == "traderjoe":
            self.contractFactory = self.provider.eth.contract(address=self.config["factoryAddress"],abi=json.load(open("./abis/factories/TJoeV3FactoryABI.json")))
            self.contractPool = self.provider.eth.contract(address=self.config["poolAddress"],abi=json.load(open("./abis/pools/TJoeV3PoolABI.json")))

    async def log_loop_pool_creation(self,event_filter, poll_interval):
        for poolCreated in event_filter.get_all_entries():
            self.handle_event_pool_creation(poolCreated)
            
        await asyncio.sleep(poll_interval)


    def handle_event_pool_creation(self,event):
        print("====================================")
        eventData = event.args
        print(eventData)
        

    def fetch_created_pool(self):
        event_filter =  self.contractFactory.events.LBPairCreated.create_filter(fromBlock=self.fromBlock, toBlock=self.toBlock)
        loop = asyncio.get_event_loop()
        try:
            print("Starting fetch created pools")
            loop.run_until_complete(
                asyncio.gather(
                    self.log_loop_pool_creation(event_filter, 0.2)
                    )
                )
        finally:
                # close loop to free up system resources
            loop.close()

    def main(self):
        self.fetch_created_pool()



v3pools = V3Pools(fromBlock=42727000, toBlock=42728000, dex="traderjoe")
v3pools.main()