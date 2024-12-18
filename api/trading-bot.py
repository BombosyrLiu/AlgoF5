import sqlite3
from binance.client import Client
import time

# Set up Binance client with your API credentials
api_key = 'your_api_key_here'
api_secret = 'your_api_secret_here'
client = Client(api_key, api_secret)

# Set up SQLite database and create a table if it doesn't exist
def setup_db():
    conn = sqlite3.connect('trading_bot.db')  # Create or connect to a database file
    c = conn.cursor()
    
    # Create a table for storing trades if it doesn't already exist
    c.execute('''CREATE TABLE IF NOT EXISTS trades (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 action TEXT,
                 symbol TEXT,
                 quantity REAL,
                 stop_loss REAL,
                 take_profit REAL,
                 executed INTEGER DEFAULT 0,
                 date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

# Function to store trade info in the SQLite database
def store_trade(action, symbol, quantity, stop_loss, take_profit):
    conn = sqlite3.connect('trading_bot.db')
    c = conn.cursor()
    
    # Insert trade data into the table
    c.execute('''INSERT INTO trades (action, symbol, quantity, stop_loss, take_profit) 
                 VALUES (?, ?, ?, ?, ?)''', 
              (action, symbol, quantity, stop_loss, take_profit))
    
    conn.commit()
    conn.close()
    print(f"Trade stored: {action} {quantity} of {symbol} with stop-loss {stop_loss} and take-profit {take_profit}")

# Function to place orders (buy/sell) and set stop-loss and take-profit
def place_order(action, symbol, quantity, stop_loss, take_profit):
    if action == 'BUY':
        # Place a market buy order
        order = client.order_market_buy(
            symbol=symbol,
            quantity=quantity
        )
        print(f"Market Buy Order placed: {order}")
        
        # Set Stop-Loss and Take-Profit orders (if applicable)
        if stop_loss:
            client.create_order(
                symbol=symbol,
                side='SELL',
                type='STOP_MARKET',
                stopPrice=stop_loss,
                quantity=quantity
            )
            print(f"Stop-Loss set at {stop_loss}")
        
        if take_profit:
            client.create_order(
                symbol=symbol,
                side='SELL',
                type='LIMIT',
                price=take_profit,
                quantity=quantity
            )
            print(f"Take-Profit set at {take_profit}")
    
    elif action == 'SELL':
        # Place a market sell order
        order = client.order_market_sell(
            symbol=symbol,
            quantity=quantity
        )
        print(f"Market Sell Order placed: {order}")

# Function to continuously check for new trades in the SQLite database and execute them
def check_for_new_trades():
    conn = sqlite3.connect('trading_bot.db')
    c = conn.cursor()

    # Select all trades that have not been executed yet
    c.execute("SELECT * FROM trades WHERE executed = 0")
    trades = c.fetchall()

    for trade in trades:
        # Extract the trade details
        trade_id, action, symbol, quantity, stop_loss, take_profit, _, _ = trade

        # Place the order based on the trade info
        place_order(action, symbol, quantity, stop_loss, take_profit)

        # Mark the trade as executed in the database
        c.execute("UPDATE trades SET executed = 1 WHERE id = ?", (trade_id,))
        conn.commit()

    conn.close()

# Main loop to check for new trades every minute
def main():
    setup_db()  # Set up the database and table
    while True:
        check_for_new_trades()  # Check for new trades to execute
        time.sleep(60)  # Sleep for 1 minute before checking again

# Run the bot
if __name__ == "__main__":
    main()
