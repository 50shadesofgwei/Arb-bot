
import requests 
import json
import time
import hmac
import hashlib
import schedule
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

    def get_signature(self, timestamp, method, url_path, body):
        message = timestamp + method + url_path + body
        signature = hmac.new(self.secretKey.encode(
          "utf-8"), message.encode("utf-8"), digestmod=hashlib.sha256).digest()
        return signature

    def get_headers(self, method, url_path, body):
        signature = self.get_signature(self.timestamp, method, url_path, body)
        headers = {
            "CB-ACCESS-KEY": self.accessKey,
            "CB-ACCESS-SIGN": signature.hex(),
            "CB-ACCESS-TIMESTAMP": self.timestamp,
        }
        return headers

    def get_btc_usd_price(self):
        method = "GET"
        url_path = "/v2/prices/BTC-USD/buy"
        body = ""
        headers = self.get_headers(method, url_path, body)
        try:
            response = requests.get(self.BASE_URL + url_path, headers=headers)
        except Exception as err:
            print(f"An error occurred when calling price from Coinbase: {err}")
            return None
        else:
          coinbaseAPI = response.json()
          coinstring = str(coinbaseAPI)
          coinstring = coinstring[55:]
          filtered_string = ''.join(char for char in coinstring if char.isdigit() or char == '.')
          coinFloat = float(filtered_string)  
          return coinFloat
    
    def buy_order(self):
        conn = http.client.HTTPSConnection("api.coinbase.com")
        method = "POST"
        url_path = "/api/v3/brokerage/orders"
        int_order_id = np.random.randint(2**62)
        str_order_id = str(int_order_id)
        payload = json.dumps({
            "client_order_id": str_order_id,
            "product_id": "BTC-USD",
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
            print(f"A HTTP error occurred: {err}")
        except Exception as err:
            print(f"An error occurred: {err}")

    def sell_order(self):
        conn = http.client.HTTPSConnection("api.coinbase.com")
        method = "POST"
        url_path = "/api/v3/brokerage/orders"
        int_order_id = np.random.randint(2**63)
        coinFloat = self.get_btc_usd_price()
        baseSize = 1/(coinFloat/1000)
        baseSize = str(baseSize)
        payload = json.dumps({
            "client_order_id": str(int_order_id),
            "product_id": "BTC-USD",
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
            print(f"A HTTP error occurred with the Coinbase client: {err}")
        except Exception as err:
            print(f"An error occurred with the Coinbase client: {err}")
        

# All binance vars/defs
class Binance:
    secretKey = 'EplcH4b00prUTAN4PRs2cAHO88kYGztwjZn7Ezi1BjrfNHItvidHKIBPebPRMmCw'
    accessKey = 'umg6kwhTo2le1RNYWridgkSmy7e2R7RN904HTBc4cex1XMULQnXWPdsGXVFf3PVe'
    client = Client(secretKey, accessKey)

    def __init__(self, client):
        self.client = client
    
    def get_BTCUSDT_price(self):
        try:
            binancePrice = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT')
        except Exception as err:
            print(f"An error occurred when calling price from Binance: {err}")
            return None
        binancePrice = binancePrice.json()
        bistring = str(binancePrice)
        bistring = bistring[32:]
        biFilString = ''.join(char for char in bistring if char.isdigit() or char == '.')
        biFloat = float(biFilString)
        return biFloat

    def buy_order(self):
      try:
          self.order = self.client.create_order(
              symbol='BTCUSDT',
              side=self.client.SIDE_BUY,
              type=self.client.ORDER_TYPE_MARKET,
              quoteOrderQty=1000
          )
      except BinanceAPIException as e:
        print(f"Binance API returned an error. Error code: {e.status_code}, Error message: {e.message}")
      except BinanceOrderException as e:
        print(f"Order failed. Error message: {e.message}")
      except Exception as e:
        print(f"An unknown error occurred. Error message: {e}")

    def sell_order(self):
      try:
          self.order = self.client.create_order(
            symbol = 'BTCUSDT',
            side = self.client.SIDE_SELL,
            type = self.client.ORDER_TYPE_MARKET,
            quoteOrderQty = 1000
          )
      except BinanceAPIException as e:
        print(f"Binance API returned an error. Error code: {e.status_code}, Error message: {e.message}")
      except BinanceOrderException as e:
        print(f"Order failed. Error message: {e.message}")
      except Exception as e:
        print(f"An unknown error occurred. Error message: {e}")
    

class Calculations:
    coinSecretKey = "YhgPlByvWIGeNUP4lgkumniGao7usjha"
    coinAccessKey = "DFtojCm1QzzWWCXp"
    biSecretKey = 'EplcH4b00prUTAN4PRs2cAHO88kYGztwjZn7Ezi1BjrfNHItvidHKIBPebPRMmCw'
    biAccessKey = 'umg6kwhTo2le1RNYWridgkSmy7e2R7RN904HTBc4cex1XMULQnXWPdsGXVFf3PVe'
    client = Client(biSecretKey, biAccessKey)

    def __init__(self):
        self.coinbaseInstance = Coinbase(self.coinAccessKey, self.coinSecretKey)
        self.binanceInstance = Binance(self.client)
        

    def callCoinPrice(self):
        coinPrice = self.coinbaseInstance.get_btc_usd_price()
        return coinPrice
    
    def callBiPrice(self):
        biPrice = self.binanceInstance.get_BTCUSDT_price()
        return biPrice

    def checkProfitability1(self, biPrice, coinPrice):
        biPrice = self.callBiPrice()
        coinPrice = self.callCoinPrice()
        path1 = biPrice - coinPrice
        # Returns true if price is higher on Binance
        if path1 > 0:
            return True
        else: return False

    def checkProfitability2(self, biPrice, coinPrice):
        biPrice = self.callBiPrice()
        coinPrice = self.callCoinPrice()
        path2 = coinPrice - biPrice
        # Returns true if price is higher on Coinbase
        if path2 > 0:
            return True
        else: return False
    
    def run(self):
        # Get prices
        coinPrice = self.callCoinPrice()
        biPrice = self.callBiPrice()

        if self.checkProfitability1(biPrice, coinPrice):
            # If price is higher on Binance, buy on Coinbase and sell on Binance
            self.coinbaseInstance.buy_order()
            self.binanceInstance.sell_order()
        elif self.checkProfitability2(biPrice, coinPrice):
            # If price is higher on Coinbase, buy on Binance and sell on Coinbase
            self.binanceInstance.buy_order()
            self.coinbaseInstance.sell_order()

execution = Calculations()
schedule.every(30).seconds.do(execution.run)

while True:
    schedule.run_pending()
    time.sleep(1)
