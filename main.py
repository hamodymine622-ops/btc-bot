import telebot
import requests
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

def get_btc():
    try:
        url = "https://api.bybit.com/v5/market/kline"
        p = {"category": "linear", "symbol": "BTCUSDT", "interval": "15", "limit": "100"}
        r = requests.get(url, params=p, timeout=10).json()
        closes = [float(x[4]) for x in r["result"]["list"]]
        closes.reverse()
        if len(closes) >= 20:
            return closes
    except Exception as e:
        print("Bybit failed:", e)
    try:
        url = "https://api.binance.com/api/v3/klines"
        p = {"symbol": "BTCUSDT", "interval": "15m", "limit": "100"}
        r = requests.get(url, params=p, timeout=10).json()
        closes = [float(x[4]) for x in r]
        if len(closes) >= 20:
            return closes
    except Exception as e:
        print("Binance failed:", e)
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    p = {"vs_currency": "usd", "days": "1", "interval": "hourly"}
    r = requests.get(url, params=p, timeout=10).json()
    closes = [float(x[1]) for x in r["prices"]]
    return closes

def rsi_calc(closes):
    gains = 0
    losses = 0
    for i in range(1, 15):
        d = closes[-15+i] - closes[-15+i-1]
        if d > 0:
            gains += d
        else:
            losses += -d
    gains /= 14
    losses /= 14
    if losses == 0:
        return 100
    rs = gains / losses
    return round(100 - (100/(1+rs)), 2)

@bot.message_handler(commands=['start'])
def s(m):
    bot.reply_to(m, "اهلا بيك 🔥\nاكتب /signal حتى تشوف اشارة BTC")

@bot.message_handler(commands=['signal'])
def sig(m):
    try:
        c = get_btc()
        price = c[-1]
        rsi = rsi_calc(c)
        if rsi >= 70:
            txt = "🔴 لا تشتري هسه - متشبع شراء"
        elif rsi <= 30:
            txt = "🟢 منطقة شراء محتمل"
        elif rsi >= 50:
            txt = "🟡 نزول بسيط واشتري"
        else:
            txt = "🟡 لا تشتري هسه - نزل بعد"
        bot.reply_to(m, f"📊 اشارة BTC على فريم 15 دقيقة\n\nالسعر: {price:,.2f}$\nRSI: {rsi}\n\n{txt}")
    except Exception as e:
        print("Signal Error:", e)
        bot.reply_to(m, "صار خطأ حاول بعد شوية")

print("البوت شغال...")
bot.infinity_polling()
