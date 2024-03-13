import json
from web3 import Web3
import asyncio
import time
import requests


class V3Pools:
    def __init__(self, fromBlock, toBlock, chain="avalanche", dex="traderjoe"):
        self.config = json.load(open("config.json"))
        self.provider = Web3(Web3.HTTPProvider(self.config["http"]))
        self.fromBlock = fromBlock
        self.toBlock = toBlock
        self.addresses = json.load(open("addresses.json"))
        self.contractFactory = self.provider.eth.contract(address=self.addresses[chain][dex]["factoryAddress"],abi=json.load(open(f"./abis/{dex}/V3FactoryABI.json")))
        self.contractPool = self.provider.eth.contract(address=self.addresses[chain][dex]["poolAddress"],abi=json.load(open(f"./abis/{dex}/V3PoolABI.json")))


    def log_loop_pool_creation(self, event_filter):
        for poolCreated in event_filter.get_all_entries():
            self.handle_event_pool_creation(poolCreated)

    def handle_event_pool_creation(self,event):
        print("====================================")
        eventData = event.args
        print(eventData)


    def fetch_created_pool(self):
        event_filter =  self.contractFactory.events.LBPairCreated.create_filter(fromBlock=self.fromBlock, toBlock=self.toBlock)
        try:
            print(f"Starting fetch created pools: {self.fromBlock} to {self.toBlock}")
            self.log_loop_pool_creation(event_filter)
        except Exception as e:
            print(f"Error: {e}")

    def main(self):
        self.fetch_created_pool()



fromBlock = 42700000
toBlock = 42728000


while fromBlock+2000 <= toBlock:
    v3pools = V3Pools(fromBlock=fromBlock, toBlock=fromBlock+2000, dex="traderjoe")
    v3pools.main()
    
    time.sleep(.2)
    fromBlock+=2000