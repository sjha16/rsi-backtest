# RSI Trading Strategy Backtest Program

![License: MIT](https://img.shields.io/badge/License-MIT-green)

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Example](#example)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Introduction
This project is a Python program designed to backtest a trading strategy based on the Relative Strength Index (RSI) and divergences. The strategy involves buying stocks when there is a bullish divergence with RSI below 30 and selling when there is a bearish divergence with RSI above 70.

## Features
- Fetch historical stock data using the `yfinance` library.
- Calculate the RSI using the `ta` library.
- Identify bullish and bearish divergences.
- Simulate buy and sell trades based on the strategy.
- Output trade logs and performance metrics.
- Plot price and RSI charts with buy/sell signals.

## Installation
To run this project locally, follow these steps:

1. **Clone the repository**:
   ```sh
   git clone https://github.com/yourusername/rsi-trading-strategy.git
   cd rsi-trading-strategy
