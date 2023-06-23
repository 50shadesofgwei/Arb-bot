
import requests 
import threading
import json
import time
import hmac
import hashlib
import schedule
from queue import Queue
from multiprocessing import Process
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import http.client
from binance.client import Client
from requests.exceptions import RequestException
from binance.exceptions import BinanceAPIException, BinanceOrderException



# All coinbase vars/defs
class Coinbase:
    BASE_URL = "https://api.coinbase.com"
    secretKey = "YhgPlByvWIGeNUP4lgkumniGao7usjha"
    accessKey = "DFtojCm1QzzWWCXp"
    timestamp = str(int(time.time()))

    def __init__(self, secretKey, accessKey):
        self.secretKey = secretKey
        self.accessKey = accessKey

    def get_signature(self, timestamp: str, method: str, url_path: str, body: str) -> bytes:
        message = timestamp + method + url_path + body
        signature = hmac.new(self.secretKey.encode(
          "utf-8"), message.encode("utf-8"), digestmod=hashlib.sha256).digest()
        return signature

    def get_headers(self, method: str, url_path: str, body: str) -> str:
        signature = self.get_signature(self.timestamp, method, url_path, body)
        headers = {
            "CB-ACCESS-KEY": self.accessKey,
            "CB-ACCESS-SIGN": signature.hex(),
            "CB-ACCESS-TIMESTAMP": self.timestamp,
        }
        return headers

    def get_btc_usd_price(self) -> float:
        method = "GET"
        url_path = "/v2/prices/BTC-USD/buy"
        body = ""
        headers = self.get_headers(method, url_path, body)
        try:
            response = requests.get(self.BASE_URL + url_path, headers=headers)
        except Exception as err:
            print(f"An error occurred when calling BTC price from Coinbase: {err}")
            return None
        else:
          coinbaseAPI = response.json()
          BTCcoinString = str(coinbaseAPI)
          BTCcoinString = BTCcoinString[55:]
          btc_filtered_string = ''.join(char for char in BTCcoinString if char.isdigit() or char == '.')
          BTCPriceFloat = float(btc_filtered_string)  
          return BTCPriceFloat

    def get_eth_usd_price(self) -> float:
        method = "GET"
        url_path = "/v2/prices/ETH-USD/buy"
        body = ""
        headers = self.get_headers(method, url_path, body)
        try:
            response = requests.get(self.BASE_URL + url_path, headers=headers)
        except Exception as err:
            print(f"An error occurred when calling price ETH from Coinbase: {err}")
            return None
        else:
          coinbaseAPI = response.json()
          ETHCoinString = str(coinbaseAPI)
          ETHCoinString = ETHCoinString[55:]
          eth_filtered_string = ''.join(char for char in ETHCoinString if char.isdigit() or char == '.')
          ETHPriceFloat = float(eth_filtered_string)  
          return ETHPriceFloat
    
    def get_link_usd_price(self) -> float:
        method = "GET"
        url_path = "/v2/prices/LINK-USD/buy"
        body = ""
        headers = self.get_headers(method, url_path, body)
        try:
            response = requests.get(self.BASE_URL + url_path, headers=headers)
        except Exception as err:
            print(f"An error occurred when calling LINK price from Coinbase: {err}")
            return None
        else:
          coinbaseAPI = response.json()
          LINKCoinString = str(coinbaseAPI)
          LINKCoinString = LINKCoinString[55:]
          link_filtered_string = ''.join(char for char in LINKCoinString if char.isdigit() or char == '.')
          LINKPriceFloat = float(link_filtered_string)  
          return LINKPriceFloat

    
    def buy_order(self, productID: str):
        conn = http.client.HTTPSConnection("api.coinbase.com")
        method = "POST"
        url_path = "/api/v3/brokerage/orders"
        int_order_id = np.random.randint(2**62)
        str_order_id = str(int_order_id)
        payload = json.dumps({
            "client_order_id": str_order_id,
            "product_id": productID,
            "side": "BUY",
            "order_configuration": {
            "market_market_ioc": {
            "quote_size": "1000"
        }
        }
    })
        headers = self.get_headers(method, url_path, payload)
        try:
            conn.request(method, url_path, payload, headers=headers)
            res = conn.getresponse()
            data = res.read()
            if res.status != 200:
                print(f"Request failed with status {res.status}: {data.decode('utf-8')}")
            else:
                print(data.decode("utf-8"))
        except http.client.HTTPException as err:
            print(f"A HTTP client error occurred when submitting {productID} buy order: {err}")
        except Exception as err:
            print(f"A client error occurred when submitting {productID} buy order: {err}")

    def sell_order(self, productID: str, priceCall):
            conn = http.client.HTTPSConnection("api.coinbase.com")
            method = "POST"
            url_path = "/api/v3/brokerage/orders"
            int_order_id = np.random.randint(2**63)
            coinFloat = priceCall
            baseSize = 1/(coinFloat/1000)
            baseSize = str(baseSize)
            payload = json.dumps({
                "client_order_id": str(int_order_id),
                "product_id": productID,
                "side": "SELL",
                "order_configuration": {
                "market_market_ioc": {
                "base_size": baseSize
            }
        }
        })
            headers = self.get_headers(method, url_path, payload)
            try:
                conn.request(method, url_path, payload, headers=headers)
                res = conn.getresponse()
                data = res.read()
                if res.status != 200:
                    print(f"Request failed with status {res.status}: {data.decode('utf-8')}")
                else:
                    print(data.decode("utf-8"))
            except http.client.HTTPException as err:
                print(f"A HTTP client error occurred when submitting a {productID} sell order: {err}")
            except Exception as err:
                print(f"A client error occurred when submitting a {productID} sell order: {err}")
        

# All binance vars/defs
class Binance:
    secretKey = 'EplcH4b00prUTAN4PRs2cAHO88kYGztwjZn7Ezi1BjrfNHItvidHKIBPebPRMmCw'
    accessKey = 'umg6kwhTo2le1RNYWridgkSmy7e2R7RN904HTBc4cex1XMULQnXWPdsGXVFf3PVe'
    client = Client(secretKey, accessKey)

    def __init__(self, client):
        self.client = client
    
    def get_BTCUSDT_price(self) -> float:
        try:
            binancePrice = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT')
        except Exception as err:
            print(f"An error occurred when calling BTC price from Binance: {err}")
            return None
        binancePrice = binancePrice.json()
        bistring = str(binancePrice)
        bistring = bistring[32:]
        biFilString = ''.join(char for char in bistring if char.isdigit() or char == '.')
        biFloat = float(biFilString)
        return biFloat

    def get_ETHUSDT_price(self) -> float:
        try:
            binancePrice = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT')
        except Exception as err:
            print(f"An error occurred when calling ETH price from Binance: {err}")
            return None
        binancePrice = binancePrice.json()
        bistring = str(binancePrice)
        bistring = bistring[32:]
        biFilString = ''.join(char for char in bistring if char.isdigit() or char == '.')
        biFloat = float(biFilString)
        return biFloat

    def get_LINKUSDT_price(self) -> float:
        try:
            binancePrice = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=LINKUSDT')
        except Exception as err:
            print(f"An error occurred when calling LINK price from Binance: {err}")
            return None
        binancePrice = binancePrice.json()
        bistring = str(binancePrice)
        bistring = bistring[32:]
        biFilString = ''.join(char for char in bistring if char.isdigit() or char == '.')
        biFloat = float(biFilString)
        return biFloat

    def buy_order(self, symbol: str, side):
      try:
          self.order = self.client.create_order(
              symbol = symbol,
              side = side,
              type = self.client.ORDER_TYPE_MARKET,
              quoteOrderQty=1000
          )
      except BinanceAPIException as e:
        print(f"Binance API returned an error when submitting {symbol} buy order. Error code: {e.status_code}, Error message: {e.message}")
      except BinanceOrderException as e:
        print(f"{symbol} buy order failed. Error message: {e.message}")
      except Exception as e:
        print(f"An unknown error occurred with {symbol} buy order. Error message: {e}")
    
    def sell_order(self, symbol: str, side):
      try:
          self.order = self.client.create_order(
            symbol = symbol,
            side = side,
            type = self.client.ORDER_TYPE_MARKET,
            quoteOrderQty = 1000
          )
      except BinanceAPIException as e:
        print(f"Binance API returned an error when sumbitting {symbol} sell order. Error code: {e.status_code}, Error message: {e.message}")
      except BinanceOrderException as e:
        print(f"{symbol} sell order failed. Error message: {e.message}")
      except Exception as e:
        print(f"An unknown error occurred with {symbol} sell order. Error message: {e}")
    

class Trade:
    coinSecretKey = "YhgPlByvWIGeNUP4lgkumniGao7usjha"
    coinAccessKey = "DFtojCm1QzzWWCXp"
    biSecretKey = 'EplcH4b00prUTAN4PRs2cAHO88kYGztwjZn7Ezi1BjrfNHItvidHKIBPebPRMmCw'
    biAccessKey = 'umg6kwhTo2le1RNYWridgkSmy7e2R7RN904HTBc4cex1XMULQnXWPdsGXVFf3PVe'
    client = Client(biSecretKey, biAccessKey)

    def __init__(self):
        self.coinbaseInstance = Coinbase(self.coinAccessKey, self.coinSecretKey)
        self.binanceInstance = Binance(self.client)
        

    def callCoinbaseBTCPrice(self) -> float:
        coinPrice = self.coinbaseInstance.get_btc_usd_price()
        return coinPrice
    
    def callBinanceBTCPrice(self) -> float:
        biPrice = self.binanceInstance.get_BTCUSDT_price()
        return biPrice

    def callCoinbaseETHPrice(self) -> float:
        coinPrice = self.coinbaseInstance.get_eth_usd_price()
        return coinPrice
    
    def callBinanceETHPrice(self) -> float:
        biPrice = self.binanceInstance.get_ETHUSDT_price()
        return biPrice
    
    def callCoinbaseLINKPrice(self) -> float:
        coinPrice = self.coinbaseInstance.get_link_usd_price()
        return coinPrice

    def callBinanceLINKPrice(self) -> float:
        biPrice = self.binanceInstance.get_LINKUSDT_price()
        return biPrice
    
    def isBTCPriceHigherOnBinance(self, biPrice, coinPrice) -> bool:
        biPrice = self.callBinanceBTCPrice()
        coinPrice = self.callCoinbaseBTCPrice()
        result = biPrice - coinPrice
        # Returns true if price is higher on Binance
        if result > 0:
            return True
        else: return False

    def isBTCPriceHigherOnCoinbase(self, biPrice, coinPrice) -> bool:
        biPrice = self.callBinanceBTCPrice()
        coinPrice = self.callCoinbaseBTCPrice()
        result = coinPrice - biPrice
        # Returns true if price is higher on Coinbase
        if result > 0:
            return True
        else: return False
    
    def isETHPriceHigherOnBinance(self, biPrice, coinPrice) -> bool:
        biPrice = self.callBinanceETHPrice()
        coinPrice = self.callCoinbaseETHPrice()
        result = biPrice - coinPrice
        # Returns true if price is higher on Binance
        if result > 0:
            return True
        else: return False

    def isETHPriceHigherOnCoinbase(self, biPrice, coinPrice) -> bool:
        biPrice = self.callBinanceETHPrice()
        coinPrice = self.callCoinbaseETHPrice()
        result = coinPrice - biPrice
        # Returns true if price is higher on Coinbase
        if result > 0:
            return True
        else: return False
    
    def isETHPriceHigherOnBinance(self, biPrice, coinPrice) -> bool:
        biPrice = self.callBinanceETHPrice()
        coinPrice = self.callCoinbaseETHPrice()
        result = biPrice - coinPrice
        # Returns true if price is higher on Binance
        if result > 0:
            return True
        else: return False
    
    def isLINKPriceHigherOnBinance(self, biPrice, coinPrice) -> bool:
        biPrice = self.callBinanceLINKPrice()
        coinPrice = self.callCoinbaseLINKPrice()
        result = biPrice - coinPrice
        # Returns true if price is higher on Binance
        if result > 0:
            return True
        else: return False

    def isLINKPriceHigherOnCoinbase(self, biPrice, coinPrice) -> bool:
        biPrice = self.callBinanceLINKPrice()
        coinPrice = self.callCoinbaseLINKPrice()
        result = coinPrice - biPrice
        # Returns true if price is higher on Coinbase
        if result > 0:
            return True
        else: return False

    def process_btc(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(self.callCoinbaseBTCPrice)
            future2 = executor.submit(self.callBinanceBTCPrice)
        
            coinbaseBTCPrice = future1.result()
            binanceBTCPrice = future2.result()

        if self.isBTCPriceHigherOnBinance(binanceBTCPrice, coinbaseBTCPrice):
         productID = 'BTC-USD'
         symbol = 'BTCUSDT'
         self.coinbaseInstance.buy_order(productID=productID)
         self.binanceInstance.sell_order(symbol=symbol, side=self.client.SIDE_SELL)
        elif self.isBTCPriceHigherOnCoinbase(binanceBTCPrice, coinbaseBTCPrice):
            self.binanceInstance.buy_order(symbol=symbol, side=self.client.SIDE_BUY)
            self.coinbaseInstance.sell_order(productID=productID, priceCall=coinbaseBTCPrice)

    def process_eth(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(self.callCoinbaseETHPrice)
            future2 = executor.submit(self.callBinanceETHPrice)

            coinbaseETHPrice = future1.result()
            binanceETHPrice = future2.result()

        if self.isETHPriceHigherOnBinance(binanceETHPrice, coinbaseETHPrice):
            productID = 'ETH-USD'
            symbol = 'ETHUSDT'
            self.coinbaseInstance.buy_order(productID=productID)
            self.binanceInstance.sell_order(symbol=symbol, side=self.client.SIDE_SELL)
        elif self.isETHPriceHigherOnCoinbase(binanceETHPrice, coinbaseETHPrice):
            self.binanceInstance.buy_order(symbol=symbol, side=self.client.SIDE_BUY)
            self.coinbaseInstance.sell_order(productID=productID, priceCall=coinbaseETHPrice)

    def process_link(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(self.callCoinbaseLINKPrice)
            future2 = executor.submit(self.callBinanceLINKPrice)

            coinbaseLINKPrice = future1.result()
            binanceLINKPrice = future2.result()

        if self.isLINKPriceHigherOnBinance(binanceLINKPrice, coinbaseLINKPrice):
            productID = 'LINK-USD'
            symbol = 'LINKUSDT'
            self.coinbaseInstance.buy_order(productID=productID)
            self.binanceInstance.sell_order(symbol=symbol, side=self.client.SIDE_SELL)
        elif self.isLINKPriceHigherOnCoinbase(binanceLINKPrice, coinbaseLINKPrice):
            self.binanceInstance.buy_order(symbol=symbol, side=self.client.SIDE_BUY)
            self.coinbaseInstance.sell_order(productID=productID, priceCall=coinbaseLINKPrice)

    def run(self):
        # Process each coin type concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.submit(self.process_btc)
            executor.submit(self.process_eth)
            executor.submit(self.process_link)


execution = Trade()
schedule.every(30).seconds.do(execution.run)

while True:
    schedule.run_pending()
    time.sleep(1)
