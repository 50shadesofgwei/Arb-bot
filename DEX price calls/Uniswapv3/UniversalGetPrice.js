const express = require('express');
const app = express();
const port = 3002;

const { ethers } = require("ethers");
const { abi: IUniswapV3PoolABI } = require("@uniswap/v3-core/artifacts/contracts/interfaces/IUniswapV3Pool.sol/IUniswapV3Pool.json");
const { abi: QuoterABI } = require("@uniswap/v3-periphery/artifacts/contracts/lens/Quoter.sol/Quoter.json");

const { getAbi, getPoolImmutables } = require('./helpers')

require('dotenv').config()
const ALCHEMY_URL = process.env.ALCHEMY_URL
const ETHERSCAN_API_KEY = process.env.ETHERSCAN_API_KEY

const provider = new ethers.providers.JsonRpcProvider(ALCHEMY_URL)

const quoterAddress = "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6"

const knownTokenData = {
    // Token address: {symbol, decimals}
    '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48': {symbol: 'USDC', decimals: 6},
    '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': {symbol: 'WETH', decimals: 18}
    // Add any tokens that use a proxy w/out the relevant details here
};

const getTokenData = async (tokenAddress, provider) => {
    // First check if we have data for this token in our knownTokenData
    if (knownTokenData[tokenAddress]) {
        console.log(`Token data found in knownTokenData for ${tokenAddress}`);
        return knownTokenData[tokenAddress];
    }

    console.log(`Token data not found in knownTokenData for ${tokenAddress}. Fetching from contract...`);

    // If not, query the token contract (assuming getAbi returns the ABI for the token)
    const tokenAbi = await getAbi(tokenAddress);
    const tokenContract = new ethers.Contract(
        tokenAddress,
        tokenAbi,
        provider
    );

    // Get the token symbol and decimal count
    const symbol = tokenContract.interface.functions.symbol
        ? await tokenContract.symbol()
        : 'unknown';

    const decimals = tokenContract.interface.functions.decimals
        ? await tokenContract.decimals()
        : 18;

    console.log(`Fetched data for ${tokenAddress}: symbol=${symbol}, decimals=${decimals}`);

    return {symbol, decimals};
};


const getPrice = async (inputAmount, poolAddress) => {
  const poolContract = new ethers.Contract(
    poolAddress,
    IUniswapV3PoolABI,
    provider
  )

  const tokenAddress0 = await poolContract.token0();
  const tokenAddress1 = await poolContract.token1();

  const {symbol: tokenSymbol0, decimals: tokenDecimals0} = await getTokenData(ethers.utils.getAddress(tokenAddress0), provider);
  const {symbol: tokenSymbol1, decimals: tokenDecimals1} = await getTokenData(ethers.utils.getAddress(tokenAddress1), provider);
  

  const quoterContract = new ethers.Contract(
    quoterAddress,
    QuoterABI,
    provider
  )

  const immutables = await getPoolImmutables(poolContract)

  const amountIn = ethers.utils.parseUnits(
    inputAmount.toString(),
    tokenDecimals0
  )

  const quotedAmountOut = await quoterContract.callStatic.quoteExactInputSingle(
    immutables.token0,
    immutables.token1,
    immutables.fee,
    amountIn,
    0
  )

  const amountOut = ethers.utils.formatUnits(quotedAmountOut, tokenDecimals1)

  console.log(`${inputAmount} ${tokenSymbol0} can be swapped for ${amountOut} ${tokenSymbol1}`)

  return amountOut
}

app.get('/getPrice', async (req, res) => {
  // Get parameters from the request
  const amount = req.query.amount;
  const poolAddress = req.query.poolAddress;
  
  // call getPrice() function
  const price = await getPrice(amount, poolAddress);
  res.send({ price });
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});

getPrice(1, '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640')
