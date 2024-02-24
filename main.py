import pandas as pd
from get_stonks import get_stonks_info, get_candles
import os

df = pd.read_csv('data.csv')
TOKEN = os.getenv('TOKEN')
df['Stock Data'] = None

# Пройдемся по каждой строке в DataFrame и загрузим исторические данные для каждой акции
for index, row in df.iterrows():
    stock = row['Stock']
    publication_date = row['Date']
    figi = get_stonks_info(stock, TOKEN)

    # Загружаем исторические данные для текущей акции и времени
    stock_data = get_candles(TOKEN, figi, publication_date)

    # Добавляем загруженные данные в соответствующую строку столбца 'Stock Data'
    df.at[index, 'Stock Data'] = stock_data
