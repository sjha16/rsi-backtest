import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ta.momentum import RSIIndicator

def fetch_data(ticker, period, interval):
    try:
        data = yf.download(ticker, period=period, interval=interval)
        if data.empty:
            raise ValueError("No data fetched. Please check the ticker symbol and try again.")
        data['Close'] = data['Adj Close']
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

def identify_divergences(data, window=10):
    data['Price_Low'] = data['Close'].rolling(window=window).min()
    data['Price_High'] = data['Close'].rolling(window=window).max()
    data['RSI_Low'] = data['RSI'].rolling(window=window).min()
    data['RSI_High'] = data['RSI'].rolling(window=window).max()
    
    data['Bullish_Div'] = (data['Close'] <= data['Price_Low']) & (data['RSI'] > data['RSI_Low'])
    data['Bearish_Div'] = (data['Close'] >= data['Price_High']) & (data['RSI'] < data['RSI_High'])
    
    return data

def backtest_strategy(data, initial_balance=100000):
    balance = initial_balance
    position = 0
    trades = []
    entry_price = 0

    for i in range(1, len(data)):
        if data['RSI'].iloc[i] < 35 and data['Bullish_Div'].iloc[i] and position == 0:
            # Buy signal
            entry_price = data['Close'].iloc[i]
            position = balance / entry_price
            balance = 0
            trades.append({
                'Date': data.index[i],
                'Action': 'Buy',
                'Price': entry_price,
                'Quantity': position,
                'Balance': balance
            })
        elif (data['RSI'].iloc[i] > 65 and data['Bearish_Div'].iloc[i] and position > 0) or \
             (data['Close'].iloc[i] < entry_price * 0.95 and position > 0):  # 5% stop loss
            # Sell signal
            exit_price = data['Close'].iloc[i]
            balance = position * exit_price
            trade_profit = (exit_price - entry_price) * position
            trades.append({
                'Date': data.index[i],
                'Action': 'Sell',
                'Price': exit_price,
                'Quantity': position,
                'Balance': balance,
                'Profit': trade_profit
            })
            position = 0

    # Final balance
    final_balance = balance if position == 0 else position * data['Close'].iloc[-1]
    total_profit = final_balance - initial_balance

    # Create DataFrame from trades
    trades_df = pd.DataFrame(trades)
    trades_df['Cumulative_Profit'] = trades_df['Profit'].cumsum().fillna(0)

    # Calculate additional metrics
    trades_df['Trade_Duration'] = trades_df['Date'].diff().shift(-1)
    trades_df['Trade_Duration'] = trades_df['Trade_Duration'].fillna(pd.Timedelta(seconds=0))

    # Save trades to CSV
    trades_df.to_csv(f'{ticker}_trades.csv', index=False)

    # Print summary
    print(f"Initial Balance: ${initial_balance:.2f}")
    print(f"Final Balance: ${final_balance:.2f}")
    print(f"Total Profit: ${total_profit:.2f}")
    print(f"Number of trades: {len(trades_df) // 2}")
    print(f"Trade log saved to {ticker}_trades.csv")

    return trades_df

def plot_results(data, trades_df):
    # Plotting
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # Price and signals plot
    ax1.plot(data['Close'], label='Close Price')
    buy_signals = trades_df[trades_df['Action'] == 'Buy']
    sell_signals = trades_df[trades_df['Action'] == 'Sell']
    ax1.scatter(buy_signals['Date'], buy_signals['Price'], color='g', marker='^', label='Buy')
    ax1.scatter(sell_signals['Date'], sell_signals['Price'], color='r', marker='v', label='Sell')
    ax1.set_title(f"{ticker} Buy/Sell Signals")
    ax1.set_ylabel('Price')
    ax1.legend()

    # RSI plot
    ax2.plot(data['RSI'], label='RSI')
    ax2.axhline(y=35, color='g', linestyle='--')
    ax2.axhline(y=65, color='r', linestyle='--')
    ax2.fill_between(data.index, 35, 65, alpha=0.1)
    ax2.set_ylabel('RSI')
    ax2.set_xlabel('Date')
    ax2.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    try:
        ticker = input('Please enter stock ticker: ').upper()
        ticker += ".NS"
        period = input("Please enter the period (in years) to backtest (e.g., '1', '2'): ")
        interval = input("Please enter the interval (e.g., '1d', '1wk', '1mo'): ")

        data = fetch_data(ticker, period + 'y', interval)
        if data.empty:
            raise ValueError("No data fetched. Please check the inputs and try again.")

        # Calculate RSI
        rsi_period = 14
        data['RSI'] = RSIIndicator(data['Close'], rsi_period).rsi()

        # Identify divergences
        data = identify_divergences(data)

        # Backtest strategy
        trades_df = backtest_strategy(data)

        # Plot results
        plot_results(data, trades_df)
    
    except Exception as e:
        print(f"An error occurred: {e}")
