import threading
import time
import pandas as pd
import ta
import logging
import traceback
from pybit.unified_trading import HTTP
from config import API_KEY, API_SECRET

class Config:
    API_KEY = API_KEY
    API_SECRET = API_SECRET
    SYMBOL = "BTCUSDT"
    TRADE_AMOUNT = 0.001
    ATR_PERIOD = 7
    RSI_PERIOD = 7
    TRAILING_SL_MULTIPLIER = 1.5
    VOLUME_MA_PERIOD = 20
    ATR_BUY_MULTIPLIER = 0.025
    ATR_SELL_MULTIPLIER = 0.025
    PAPER_TRADING = False
    RSI_OVERSOLD = 35
    RSI_OVERBOUGHT = 70
    COOLDOWN = 300
    BASE_ATR_MULTIPLIER = 0.02
    TREND_MA_PERIOD = 50
    TREND_BUFFER = 0.992
    VOLUME_BUFFER = 0.5
    MOMENTUM_PERIOD = 3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("trading_bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AdaptiveConfig:
    def __init__(self):
        self.atr_multiplier = Config.BASE_ATR_MULTIPLIER
        
    def update(self, atr):
        if atr is None:
            logger.warning("Попытка обновления с ATR=None")
            return
        if atr > 200:
            self.atr_multiplier = Config.BASE_ATR_MULTIPLIER * 0.6
        elif atr > 150:
            self.atr_multiplier = Config.BASE_ATR_MULTIPLIER * 0.8
        else:
            self.atr_multiplier = Config.BASE_ATR_MULTIPLIER

class TradingBot:
    def __init__(self):
        self.session = HTTP(api_key=Config.API_KEY, api_secret=Config.API_SECRET)
        self.running = True
        self.last_max_price = None
        self.last_min_price = None
        self.entry_price = None
        self.stop_loss = None
        self.last_trade_time = 0
        self.in_position = False
        self.adaptive_config = AdaptiveConfig()
        self.current_atr = None
        self.ma50 = None
        self.prev_prices = []

    def get_price(self):
        try:
            data = self.session.get_tickers(symbol=Config.SYMBOL, category="spot")
            return float(data["result"]["list"][0]["lastPrice"])
        except Exception as e:
            logger.error(f"Ошибка получения цены: {e}")
            return None

    def get_ohlc(self, interval="1", limit=100):
        try:
            data = self.session.get_kline(
                category="spot",
                symbol=Config.SYMBOL,
                interval=interval,
                limit=limit
            )
            if not data["result"]["list"]:
                logger.error("Пустой ответ от API")
                return None
                
            df = pd.DataFrame(
                data["result"]["list"],
                columns=["timestamp", "open", "high", "low", "close", "volume", "turnover"]
            ).astype({
                "timestamp": str,
                "open": float,
                "high": float,
                "low": float,
                "close": float,
                "volume": float,
                "turnover": float
            })
            
            df["timestamp"] = pd.to_numeric(df["timestamp"])
            df["time"] = pd.to_datetime(df["timestamp"], unit="ms")
            return df
        except Exception as e:
            logger.error(f"Ошибка получения свечей: {e}")
            return None

    def calculate_indicators(self, df):
        try:
            min_periods = max(
                Config.ATR_PERIOD, Config.RSI_PERIOD, Config.TREND_MA_PERIOD
            )
            if df.empty or len(df) < min_periods:
                logger.warning("Недостаточно данных для расчета индикаторов")
                return (None,) * 6

            self.prev_prices = df["close"].tail(
                Config.MOMENTUM_PERIOD + 1
            ).tolist()
            
            df["ATR"] = ta.volatility.AverageTrueRange(
                high=df["high"],
                low=df["low"],
                close=df["close"],
                window=Config.ATR_PERIOD
            ).average_true_range()
            
            df["RSI"] = ta.momentum.RSIIndicator(
                close=df["close"], window=Config.RSI_PERIOD
            ).rsi()
            df["Volume_MA"] = df["volume"].rolling(
                Config.VOLUME_MA_PERIOD
            ).mean()
            df["MA50"] = df["close"].rolling(Config.TREND_MA_PERIOD).mean()
            
            return (
                df["ATR"].iloc[-1],
                df["RSI"].iloc[-1],
                df["volume"].iloc[-1],
                df["Volume_MA"].iloc[-1],
                df["MA50"].iloc[-1],
                df["close"].iloc[-1]
            )
        except Exception as e:
            logger.error(f"Ошибка расчета индикаторов: {e}")
            return (None,) * 6

    def check_conditions(self, price, atr, rsi, volume, volume_ma, ma50, close_price):
        current_time = time.time()
        if current_time - self.last_trade_time < Config.COOLDOWN:
            return False, False

        try:
            self.adaptive_config.update(atr)
            self.current_atr = atr

            self.last_max_price = max(self.last_max_price or price, price)
            self.last_min_price = min(self.last_min_price or price, price)

            drop_threshold = self.last_max_price - (atr * Config.ATR_BUY_MULTIPLIER)
            rise_threshold = self.last_min_price + (atr * Config.ATR_SELL_MULTIPLIER)

            volume_condition = volume > volume_ma * (
                0.5 if rsi < 25 else Config.VOLUME_BUFFER
            )
            trend_condition = price > ma50 * Config.TREND_BUFFER

            # Momentum condition
            has_sufficient_data = (
                len(self.prev_prices) >= Config.MOMENTUM_PERIOD + 1
            )
            if has_sufficient_data:
                prices_are_increasing = all(
                    self.prev_prices[-i] > self.prev_prices[-i - 1]
                    for i in range(1, Config.MOMENTUM_PERIOD + 1)
                )
                momentum_condition = prices_are_increasing
            else:
                momentum_condition = False

            buy_condition = (
                price <= drop_threshold and
                rsi < Config.RSI_OVERSOLD and
                volume_condition and
                trend_condition and
                momentum_condition
            )
            
            sell_condition = (
                price >= rise_threshold and
                rsi > Config.RSI_OVERBOUGHT and
                (price > self.entry_price * 1.001 if self.entry_price else False)
            )

            log_line1 = (
                f"Индикаторы: ATR={atr:.2f} RSI={rsi:.2f} "
                f"Volume={volume:.2f}/{volume_ma:.2f} MA50={ma50:.2f}"
            )
            log_line2 = (
                f"Пороги: Покупка <= {drop_threshold:.2f} | "
                f"Продажа >= {rise_threshold:.2f}"
            )
            log_line3 = (
                f"Тренд: {trend_condition} | Импульс: {momentum_condition} | "
                f"Объем: {volume_condition}"
            )
            logger.info(f"{log_line1}\n{log_line2}\n{log_line3}")
            return buy_condition and not self.in_position, \
                   sell_condition and self.in_position
        except Exception as e:
            logger.error(f"Ошибка проверки условий: {e}")
            return False, False

    def calculate_stop_loss(self, price):
        if self.current_atr is None or self.adaptive_config.atr_multiplier is None:
            logger.warning("Невозможно рассчитать стоп-лосс: отсутствуют данные ATR")
            return price * 0.95  # Значение по умолчанию
        
        volatility_adjustment = 1 + (self.adaptive_config.atr_multiplier / Config.BASE_ATR_MULTIPLIER)
        return price - (self.current_atr * Config.TRAILING_SL_MULTIPLIER * volatility_adjustment)

    def execute_buy(self, price):
        try:
            self.stop_loss = self.calculate_stop_loss(price)
            if Config.PAPER_TRADING:
                logger.info(f"[ТЕСТ] Покупка {Config.TRADE_AMOUNT} {Config.SYMBOL} по {price}")
            else:
                order = self.session.place_order(
                    category="spot",
                    symbol=Config.SYMBOL,
                    side="Buy",
                    orderType="Market",
                    qty=Config.TRADE_AMOUNT
                )
                if order["retCode"] != 0:
                    raise Exception(order["retMsg"])

            self.entry_price = price
            self.last_trade_time = time.time()
            self.in_position = True
            logger.info(f"Начальный стоп-лосс: {self.stop_loss:.2f}")
        except Exception as e:
            logger.error(f"Сбой покупки: {e}")
            self.in_position = False

    def execute_sell(self, price):
        try:
            profit = (price - self.entry_price)/self.entry_price*100 if self.entry_price else 0
            if Config.PAPER_TRADING:
                logger.info(f"[ТЕСТ] Продажа {Config.TRADE_AMOUNT} {Config.SYMBOL} по {price} (+{profit:.2f}%)")
            else:
                order = self.session.place_order(
                    category="spot",
                    symbol=Config.SYMBOL,
                    side="Sell",
                    orderType="Market",
                    qty=Config.TRADE_AMOUNT
                )
                if order["retCode"] != 0:
                    raise Exception(order["retMsg"])

            self.entry_price = None
            self.stop_loss = None
            self.last_trade_time = time.time()
            self.in_position = False
        except Exception as e:
            logger.error(f"Сбой продажи: {e}")
            self.in_position = True

    def check_risk_management(self, current_price):
        if self.in_position and self.current_atr is not None:
            try:
                new_stop = self.calculate_stop_loss(current_price)
                self.stop_loss = max(self.stop_loss, new_stop)
                
                if current_price <= self.stop_loss:
                    logger.warning(f"🔥 Сработал стоп-лосс: {self.stop_loss:.2f}")
                    self.execute_sell(current_price)
                else:
                    logger.info(f"Текущий стоп-лосс: {self.stop_loss:.2f}")
            except Exception as e:
                logger.error(f"Ошибка риск-менеджмента: {e}")

    def run(self):
        logger.info("🚀 Запуск торгового бота...")
        while self.running:
            try:
                price = self.get_price()
                if not price:
                    time.sleep(5)
                    continue
                
                df = self.get_ohlc()
                if df is None:
                    continue
                
                indicators = self.calculate_indicators(df)
                if None in indicators:
                    logger.warning("Пропуск итерации из-за ошибки в индикаторах")
                    time.sleep(5)
                    continue

                atr, rsi, volume, volume_ma, ma50, close_price = indicators
                buy_cond, sell_cond = self.check_conditions(price, atr, rsi, volume, volume_ma, ma50, close_price)
                
                self.check_risk_management(price)
                
                if buy_cond:
                    self.execute_buy(price)
                elif sell_cond:
                    self.execute_sell(price)
                
                time.sleep(5)
                
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                logger.error(f"Критическая ошибка: {str(e)}\n{traceback.format_exc()}")
                self.running = False

        logger.info("🛑 Бот остановлен")

if __name__ == "__main__":
    bot = TradingBot()
    threading.Thread(target=lambda: input("⏹ Нажмите Enter для остановки...")).start()
    bot.run()
