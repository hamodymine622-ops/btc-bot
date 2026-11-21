import telebot
import requests
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

def get_btc():
    url = "https://api.bybit.com/v5/market/kline"
    p = {"category":"linear","symbol":"BTCUSDT","interval":"60","limit":100}
    r = requests.get(url, params=p).json()
    closes = [float(x[4]) for x in r['result']['list']]
    closes.reverse()
    return closes

def rsi_calc(closes):
    gains = 0
    losses = 0
    for i in range(1, 15):
        d = closes[-15+i] - closes[-15+i-1]
        if d > 0: gains += d
        else: losses += -d
    gains /= 14
    losses /= 14
    if losses == 0: return 100
    rs = gains / losses
    return round(100 - (100/(1+rs)), 2)

@bot.message_handler(commands=['start'])
def s(m):
    bot.reply_to(m, "اهلا بيك 🔥\nاكتب /signal حتى انطيك BTC صعود لو نزول")

@bot.message_handler(commands=['signal'])
def sig(m):
    try:
        c = get_btc()
        price = c[-1]
        rsi = rsi_calc(c)
        if rsi >= 70:
            txt = "🔴 نزول محتمل - لا تشتري هسه"
        elif rsi <= 30:
            txt = "🟢 صعود محتمل - منطقة شراء"
        elif rsi >= 50:
            txt = "🟡 صاعد - انتظر نزول بسيط واشتري"
        else:
            txt = "🟡 نازل - لا تشتري هسه"
        bot.reply_to(m, f"📊 BTC على Bybit\n💰 السعر: {price:,.0f} $\n📈 RSI: {rsi}\n\n🎯 {txt}")
    except:
        bot.reply_to(m, "صار خطأ حاول بعد شوية")

print("البوت شغال...")
bot.infinity_polling()
