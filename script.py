

import requests 
import json
import time
import hmac
import hashlib
import numpy as np
import http.client
from binance.client import Client


# NOTE: All keys are for testing wallets and have no access to any capital
# NOTE: All keys are for testing wallets and have no access to any capital
# NOTE: All keys are for testing wallets and have no access to any capital

# Binance keys
client = Client(
    'EplcH4b00prUTAN4PRs2cAHO88kYGztwjZn7Ezi1BjrfNHItvidHKIBPebPRMmCw',
    'umg6kwhTo2le1RNYWridgkSmy7e2R7RN904HTBc4cex1XMULQnXWPdsGXVFf3PVe'
    )

# Coinbase sig + keys
secretKey = "YhgPlByvWIGeNUP4lgkumniGao7usjha"
accessKey = "DFtojCm1QzzWWCXp"

timestamp = str(int(time.time()))
method = "GET"
url_path = "/api/v3/brokerage/accounts"
url = "https://api.coinbase.com/api/v3/brokerage/accounts"
body = ""
message = timestamp + method + url_path + body

signature = hmac.new(secretKey.encode(
    "utf-8"), message.encode("utf-8"), digestmod=hashlib.sha256).digest()

coinbaseHeaders = {
    "CB-ACCESS-KEY": accessKey,
    "CB-ACCESS-SIGN": signature.hex(),
    "CB-ACCESS-TIMESTAMP": timestamp,
}

# Store price request URLs for CEXes
binanceAPI = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT')
coinbaseAPI = requests.get('https://api.coinbase.com/v2/prices/BTC-USD/buy', headers=coinbaseHeaders)

# Get amount held in accounts
biHoldings = client.get_asset_balance(asset='BTC')
coinHoldingsRaw = requests.get("https://api.coinbase.com/api/v3/brokerage/accounts", headers = coinbaseHeaders)
coinHoldings = coinHoldingsRaw.json()

# Parse price data, store as float 
binanceAPI = binanceAPI.json()
bistring = str(binanceAPI)
bistring = bistring[32:]
biFilString = ''.join(char for char in bistring if char.isdigit() or char == '.')
biFloat = float(biFilString)


coinbaseAPI = coinbaseAPI.json()
coinstring = str(coinbaseAPI)
coinstring = coinstring[55:]
filtered_string = ''.join(char for char in coinstring if char.isdigit() or char == '.')
coinFloat = float(filtered_string)

# Parse account holdings, store as float
biHoldingsStr = str(biHoldings)
biHoldingsStr = biHoldingsStr[22:50]
biHoldingsStr = ''.join(char for char in biHoldingsStr if char.isdigit() or char == '.')
biAccFloat = float(biHoldingsStr)

coinHoldings = str(coinHoldings)
coinHoldings = coinHoldings[130:157]
coinHoldings = ''.join(char for char in coinHoldings if char.isdigit() or char == '.')
coinAccFloat = float(coinHoldings)

# Basic math to check if arb is profitable
# Define trade amount
TradeAmount = 1000

# Assume zero fees

def checkProfitability1(biFloat, coinFloat):

    path1 = coinFloat - biFloat

    # Returns true if price is higher on Coinbase
    if path1 > 0:
        return True
    
    else: return False
    

    
    

def checkProfitability2(biFloat, coinFloat):

    path2 = biFloat - coinFloat

    # Returns true if price is higher on Binance
    if path2 > 0:
        return True

    else: return False



path1bool = checkProfitability1(biFloat, coinFloat)
path2bool = checkProfitability2(biFloat, coinFloat)

# If path1bool == True then send a sell order to Coinbase and a buy order to Binance

if path1bool == True:

    # Coinbase sell order
    conn = http.client.HTTPSConnection("api.coinbase.com")
    method = "POST"
    url_path = "/api/v3/brokerage/orders"
    int_order_id = np.random.randint(2**63)
    timestamp = str(int(time.time()))
    url = "https://api.coinbase.com/api/v3/brokerage/orders"
    body = ""

    
    baseSize = 1/(coinFloat/1000)
    baseSize = str(baseSize)
    payload = json.dumps({
        "client_order_id": str(int_order_id),
        "product_id": "BTC-USD",
        "side": "SELL",
        "order_configuration": {
        "market_market_ioc": {
        "quote_size": "1000"
    }
  }
})
    message = timestamp + method + url_path + str(payload)
    signature = hmac.new(secretKey.encode("utf-8"), message.encode("utf-8"), digestmod=hashlib.sha256).digest()

    headers={
    'CB-ACCESS-KEY': accessKey,
    'CB-ACCESS-TIMESTAMP': timestamp,
    'CB-ACCESS-SIGN': signature.hex()
    }

    conn.request(method, url_path, payload, headers=headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))

    # Binance buy order
    order = client.create_order(
        symbol = 'BTCUSDT',
        side = Client.SIDE_BUY,
        type = Client.ORDER_TYPE_MARKET,
        quoteOrderQty = 1000
    )

# If path2bool == True, send a buy order to Coinbase and a sell order to Binance
if path2bool == True:

    conn = http.client.HTTPSConnection("api.coinbase.com")
    method = "POST"
    url_path = "/api/v3/brokerage/orders"
    int_order_id = np.random.randint(2**62)
    str_order_id = str(int_order_id)
    timestamp = str(int(time.time()))
    url = "https://api.coinbase.com/api/v3/brokerage/orders"
    body = ""
    message = timestamp + method + url_path + body

    signature = hmac.new(secretKey.encode(
    "utf-8"), message.encode("utf-8"), digestmod=hashlib.sha256).digest()
    baseSize = 1/(coinFloat/1000)
    baseSize = str(baseSize)
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
    message = timestamp + method + url_path.split('?')[0] + str(payload)

    headers={
    'CB-ACCESS-KEY': accessKey,
    'CB-ACCESS-TIMESTAMP': timestamp,
    'CB-ACCESS-SIGN': signature.hex(),
    'accept':'application/json'
    }

    
    conn.request(method, url_path, payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))

    # Binance sell order
    order = client.create_order(
        symbol = 'BTCUSDT',
        side = Client.SIDE_SELL,
        type = Client.ORDER_TYPE_MARKET,
        quoteOrderQty = 1000
    )
