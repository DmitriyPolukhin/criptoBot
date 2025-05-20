# CriptoBot - Automated Trading Bot for Bybit

## Project Description
CriptoBot is an automated cryptocurrency trading bot that leverages technical analysis indicators to execute trades on the Bybit exchange. It is designed to identify potential entry and exit points based on various market conditions, manage risk with trailing stop-losses, and adapt to changing market volatility.

## Features
- **Automated Trading**: Executes buy and sell orders based on technical analysis
- **Technical Indicators**: Utilizes RSI, ATR, volume analysis, and moving averages
- **Risk Management**: Implements trailing stop-losses that adjust with market volatility
- **Adaptive Parameters**: Adjusts trading parameters based on market conditions
- **Trend Following**: Incorporates trend analysis to filter trades
- **Volume Confirmation**: Uses volume analysis to confirm trading signals
- **Paper Trading Mode**: Option to run in simulation mode without risking real funds
- **Logging**: Comprehensive logging of all activities and trades

## Installation

### Prerequisites
- Python 3.7 or higher
- Bybit account with API access

### Steps
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/criptoBot.git
   cd criptoBot
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration Setup

1. Create your configuration file:
   ```
   cp config.example.py config.py
   ```

2. Edit `config.py` with your Bybit API credentials:
   ```python
   API_KEY = "your_api_key_here"
   API_SECRET = "your_api_secret_here"
   ```

3. (Optional) Adjust trading parameters in the `Config` class in `bybit_bot.py`:
   ```python
   class Config:
       # Trading parameters
       SYMBOL = "BTCUSDT"  # Trading pair
       TRADE_AMOUNT = 0.001  # Trading amount
       PAPER_TRADING = True  # Set to False for real trading
       # ... other parameters
   ```

## Usage

Run the bot with:
```
python bybit_bot.py
```

The bot will:
1. Connect to Bybit using your API credentials
2. Analyze the market conditions
3. Execute trades based on the configured strategy
4. Log all activities to both console and `trading_bot.log`

To stop the bot, simply press Enter in the terminal window.

## Requirements and Dependencies

- **pybit**: Official Bybit API client
- **pandas**: Data analysis library
- **ta**: Technical analysis library for indicators
- **Other dependencies**: See `requirements.txt` for full list

## Important Security Notes

1. **API Key Security**: Never share your API keys or commit them to version control
2. **Permissions**: It's recommended to create API keys with trading permissions only (not withdrawal)
3. **Risk Management**: Start with small amounts or use paper trading mode
4. **Monitoring**: Regularly monitor the bot's performance and make adjustments as needed

## Trading Strategy Explanation

The bot employs a multi-factor strategy that combines several technical indicators:

1. **RSI (Relative Strength Index)**: Identifies overbought and oversold conditions
2. **ATR (Average True Range)**: Measures volatility and adapts stop-loss levels
3. **Moving Averages**: Determines overall trend direction
4. **Volume Analysis**: Confirms trade signals with volume data
5. **Price Action**: Identifies potential reversal points after significant moves

### Entry Conditions (Buy)
- RSI below oversold threshold
- Price dropped by a significant amount (based on ATR)
- Current price above long-term moving average (bullish trend)
- Sufficient trading volume
- Recent price momentum in favor of the trade

### Exit Conditions (Sell)
- RSI above overbought threshold
- Price rise surpasses threshold (based on ATR)
- Trailing stop-loss hit
- Minimum profit target achieved

## Risk Disclaimer

This bot is provided for educational and research purposes only. Cryptocurrency trading involves significant risk and can result in the loss of your invested capital. You should not trade with money you cannot afford to lose. The developers of this bot are not responsible for any financial losses incurred from using it.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

