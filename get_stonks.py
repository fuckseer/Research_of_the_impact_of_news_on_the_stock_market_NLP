import os

import pytz
from tinkoff.invest import Client, SecurityTradingStatus
from tinkoff.invest.async_services import InstrumentsService
from tinkoff.invest.utils import quotation_to_decimal

from datetime import timedelta, datetime
from tinkoff.invest import CandleInterval
from tinkoff.invest.utils import now


def get_stonks_info(ticker, TOKEN):
    with Client(TOKEN) as client:
        instruments: InstrumentsService = client.instruments
        ticker_info = None
        for method in ["shares", "bonds", "etfs", "currencies", "futures"]:
            for item in getattr(instruments, method)().instruments:
                if item.ticker == ticker:
                    ticker_info = {
                        "Название": item.name,
                        "ticker": item.ticker,
                        "class_code": item.class_code,
                        "figi": item.figi,
                        "uid": item.uid,
                        "type": method,
                        "min_price_increment": quotation_to_decimal(
                            item.min_price_increment
                        ),
                        "scale": 9 - len(str(item.min_price_increment.nano)) + 1,
                        "lot": item.lot,
                        "trading_status": str(
                            SecurityTradingStatus(item.trading_status).name
                        ),
                        "api_trade_available_flag": item.api_trade_available_flag,
                        "currency": item.currency,
                        "exchange": item.exchange,
                        "buy_available_flag": item.buy_available_flag,
                        "sell_available_flag": item.sell_available_flag,
                        "short_enabled_flag": item.short_enabled_flag,
                        "klong": quotation_to_decimal(item.klong),
                        "kshort": quotation_to_decimal(item.kshort),
                    }
                    break
            if ticker_info:
                break

        if ticker_info:
            return ticker_info["figi"]
        else:
            print(f"ticker not found")

def convert_to_units_nano(quotation):
    return float(str(quotation.units) + '.' + str(quotation.nano))
def get_candles(TOKEN, figi, time):
    time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
    difference = datetime.now() - time
    days_difference = difference.days
    candles_data = []
    with Client(TOKEN) as client:
        for candle in client.get_all_candles(
                figi=figi,
                from_=now() - timedelta(days=days_difference),
                interval=CandleInterval.CANDLE_INTERVAL_10_MIN,
        ):
            candle_dict = {
                'open': convert_to_units_nano(candle.open),
                'high': convert_to_units_nano(candle.high),
                'low': convert_to_units_nano(candle.low),
                'close': convert_to_units_nano(candle.close),
                'volume': candle.volume,
                'time': candle.time
            }
            candles_data.append(candle_dict)
            print(candles_data)

            return candles_data
    return 0

