# Arb-bot
Basic python script


Script detects if a difference exists between the prices of various tokens on both centralised and decentralised exchanges, then executes the respective trades in the event that a profitable route is found. To check for the most profitable path across a multilegged opportunity (anything with more than two trades) an instantiation of the bellman ford algorithm will be used.

IMPROVEMENTS:

- Proxy Contracts
  
When calling a price from Uniswap, if either of the pooled assets uses a proxy contract then calling 'await tokenContract0.symbol()' or other related functions (.decimals, etc) will throw an 'is not a function' error. As a temporary workaround we can hardcode the relevant data as is done in the GetPriceUSDCBase/Quote scripts, but this process will be harder to scale. For now while dealing with only a handful of tokens this is fine but in future a fix will be needed.

- Speed 

The bot is slow - transcribing to a different language (C, Mojo, etc) could improve the time taken to execute the floating point math
and such. There also may be a way to parse the price from the API return faster than what is implemented here and save a couple milliseconds.

- Fees

For the sake of simplicity the current model does not factor in the respective exchange trading fees. For the sake of practicing coding
this is fine although if one wanted to optimise for profit it'd be essential to factor in the cost of a given trade and weight that
against the expected profit. Some function to simulate a trade (with fees) and see if the end result is a net positive should fix this.

- USDT != USD

The Binance BTC price call goes to the BTC/USDT endpoint, which creates a reliance upon the peg of USDT to stay accurate. If the peg were to 
break, the bot would submit incorrect trades until told to stop.
To get around this a couple of options are possible, either by factoring in the USDT/USD exchange rate into the trade class or by 
checking if the peg is within a bounded threshold X and requiring peg<X before a trade can be submitted.

- Logging

The bot currently takes no record of whether it is functioning correctly or not. In an updated model, various checks could be 
included to detect what errors are occuring with what frequency, and also a function that calculates how much profit the bot
thinks it should have given its trade history, and then raising an error if the numbers vary by more than some amount.
