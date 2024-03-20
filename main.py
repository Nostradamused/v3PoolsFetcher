import json
from web3 import Web3
import asyncio
import time
import requests
import pandas as pd


class V3Pools:
    def __init__(
        self, fromBlock, toBlock, blockMaxWindow, chain="avalanche", dex="traderjoe"
    ):
        self.config = json.load(open("config.json"))
        self.provider = Web3(Web3.HTTPProvider(self.config["http"]))
        self.fromBlock = fromBlock
        self.toBlock = toBlock
        self.blockMaxWindow = blockMaxWindow
        self.addresses = json.load(open("addresses.json"))
        self.dex = dex
        self.contractFactory = self.provider.eth.contract(
            address=self.addresses[chain][dex]["factoryAddress"],
            abi=json.load(open(f"./abis/{dex}/V3FactoryABI.json")),
        )
        self.contractPool = self.provider.eth.contract(
            address=self.addresses[chain][dex]["poolAddress"],
            abi=json.load(open(f"./abis/{dex}/V3PoolABI.json")),
        )
        self.pools = pd.read_csv("data/pools.csv", index_col=0)

    def log_loop_pool_creation(self, event_filter):
        for poolCreated in event_filter.get_all_entries():
            self.handle_event_pool_creation(poolCreated)

    def handle_event_pool_creation(self, event):
        print("====================================")
        eventData = event
        print(eventData)
        currentEvent = pd.DataFrame(
            {
                "token0": eventData["args"]["tokenX"],
                "token1": eventData["args"]["tokenY"],
                "poolAddress": eventData["args"]["LBPair"],
                "binStep": eventData["args"]["binStep"],
                "protocol": self.dex,
                "blockNumber": eventData["blockNumber"],
            },
            index=[0],
        )
        self.pools = pd.concat([self.pools, currentEvent], ignore_index=True)

    def fetch_created_pool(self, fromBlock, toBlock):
        event_filter = self.contractFactory.events.LBPairCreated.create_filter(
            fromBlock=fromBlock, toBlock=toBlock
        )
        try:
            print(f"Starting fetch created pools: {fromBlock} to {toBlock}")
            self.log_loop_pool_creation(event_filter)
        except Exception as e:
            print(f"Error: {e}")

    def main(self):
        while self.fromBlock < self.toBlock:
            self.fetch_created_pool(
                self.fromBlock, self.fromBlock + self.blockMaxWindow
            )
            self.fromBlock += self.blockMaxWindow
            time.sleep(0.2)

        self.pools = self.pools.drop_duplicates(ignore_index=True)
        self.pools = self.pools.reset_index()
        self.pools.to_csv("data/pools.csv", index=False)


v3pools = V3Pools(
    fromBlock=40000000, toBlock=43158000, blockMaxWindow=2000, dex="traderjoe"
)
v3pools.main()
