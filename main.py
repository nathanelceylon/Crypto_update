import pandas as pd
import yfinance as yf
import ta

# Télécharger les données pour chaque ticker
ticker_list = ['SEI-USD', 'OP-USD','STX4847-USD', 'TRX-USD', 'DOGE-USD',
               'TON-USD', 'WIF-USD', 'W-USD', 'BEAM28298-USD', 'LEO-USD','ENA-USD', 'RAY-USD']

Dataset_hour = {}
Dataset_hour_h = {}
for t in ticker_list:
    Dataset_hour[t] = yf.download(tickers=t, start='2024-01-01', end=None, interval='1d') #DAILY
    #Dataset_hour[t] = yf.download(tickers=t, start='2024-01-01', end=None, interval='1wk') #WEEKLY
    Dataset_hour_h[t] = yf.download(tickers=t, start='2024-08-23', end=None, interval='1h') #HOURLY

for t in ticker_list:
    Dataset_hour[t].columns = Dataset_hour[t].columns.get_level_values(0)  # Garder seulement le premier niveau
    Dataset_hour[t].reset_index(inplace=True)  # Réinitialiser l'index pour le rendre plus standard
    Dataset_hour_h[t].columns = Dataset_hour_h[t].columns.get_level_values(0)  # Garder seulement le premier niveau
    Dataset_hour_h[t].reset_index(inplace=True)  # Réinitialiser l'index pour le rendre plus standard

ticker_to_buy = []
ticker_to_sell = []
ticker_to_look_for_sell = []

# Fonction pour calculer les indicateurs techniques, y compris l'ADX et les DI
def calculate_technical_indicators(df):
    df = df.copy()
    
    # Calculer les indicateurs de base
    df['SMA_10'] = df['Close'].rolling(window=10).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['EMA_10'] = df['Close'].ewm(span=10, adjust=False).mean()    
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()

    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()

    # Calculer les bandes de Bollinger
    bollinger = ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2)
    df['BB_Upper'] = bollinger.bollinger_hband()
    df['BB_Middle'] = bollinger.bollinger_mavg()
    df['BB_Lower'] = bollinger.bollinger_lband()

    # Calculer le MACD
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_Signal'] = macd.macd_signal()

    # Calculer l'ATR
    df['ATR'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close'], window=14).average_true_range()

    # Calculer l'ADX, +DI et -DI
    adx = ta.trend.ADXIndicator(df['High'], df['Low'], df['Close'], window=14)
    df['ADX'] = adx.adx()
    df['+DI'] = adx.adx_pos()  # Positive Directional Indicator
    df['-DI'] = adx.adx_neg()  # Negative Directional Indicator

    return df


#######################################################################################################
print("############################################ Analyse DAILY ############################################")
#######################################################################################################
last_values = {}
for t in ticker_list:
    Dataset_hour[t] = calculate_technical_indicators(Dataset_hour[t])
    last_row = Dataset_hour[t].iloc[-1]
    last_values[t] = {
        'BB_Middle': last_row['BB_Middle'],
        'ADX': last_row['ADX'],
        '+DI': last_row['+DI'],
        '-DI': last_row['-DI'],
        'Close': last_row['Close'],
        'RSI': last_row['RSI'],
        'Close_BB_Middle_Diff': last_row['Close'] - last_row['BB_Middle'],
        'Evolution': -(last_row['Close'] - last_row['BB_Middle']) / last_row['Close'] * 100,
        'MACD': last_row['MACD'],
        'MACD_Signal': last_row['MACD_Signal'],
        'SMA_50' : last_row['SMA_50'],
        'SMA_10' : last_row['SMA_10'],
        'EMA_50' : last_row['EMA_50'],
        'EMA_10' : last_row['EMA_10']
    }

# Afficher les dernières valeurs des indicateurs et la différence
for t in ticker_list:
    print(f"{t} - Last BB_Middle: {last_values[t]['BB_Middle']}, Last RSI: {last_values[t]['RSI']}, Last ADX: {last_values[t]['ADX']}, Last +DI: {last_values[t]['+DI']}, Last -DI: {last_values[t]['-DI']}, Close: {last_values[t]['Close']}, MACD: {last_values[t]['MACD']}, MACD Signal: {last_values[t]['MACD_Signal']}, SMA_50 : {last_values[t]['SMA_50']}, EMA_50 : {last_values[t]['EMA_50']}, Close - BB_Middle: {last_values[t]['Close_BB_Middle_Diff']}")
    #print(f"{t} - Evolution probable: {last_values[t]['Evolution']}%")
    if (last_values[t]['RSI'] < 80 and last_values[t]['+DI'] - 5 > last_values[t]['-DI'] and last_values[t]['MACD'] > last_values[t]['MACD_Signal']) :
      ticker_to_buy.append(t)
      print(f"{t} - <<<<<<<<< BUY URGENT >>>>>>>>>")
    if (last_values[t]['RSI'] > 90 or (last_values[t]['+DI'] + 5 < last_values[t]['-DI'] and last_values[t]['ADX'] > 25 )) :
      print(f"{t} - <<<<<<<< SELL URGENT >>>>>>>>")

#######################################################################################################
print("############################################ Analyse HOURLY ###########################################")
#######################################################################################################

last_values_hour = {}
for t in ticker_list:
    Dataset_hour_h[t] = calculate_technical_indicators(Dataset_hour_h[t])
    last_row_hour = Dataset_hour_h[t].iloc[-1]
    last_values_hour[t] = {
        'BB_Middle': last_row_hour['BB_Middle'],
        'ADX': last_row_hour['ADX'],
        '+DI': last_row_hour['+DI'],
        '-DI': last_row_hour['-DI'],
        'Close': last_row_hour['Close'],
        'RSI': last_row_hour['RSI'],
        'Close_BB_Middle_Diff': last_row_hour['Close'] - last_row_hour['BB_Middle'],
        'Evolution': -(last_row_hour['Close'] - last_row_hour['BB_Middle']) / last_row_hour['Close'] * 100,
        'MACD': last_row_hour['MACD'],
        'MACD_Signal': last_row_hour['MACD_Signal'],
        'SMA_50' : last_row_hour['SMA_50'],
        'SMA_10' : last_row_hour['SMA_10'],
        'EMA_50' : last_row_hour['EMA_50'],
        'EMA_10' : last_row_hour['EMA_10']
    }

# Afficher les dernières valeurs des indicateurs et la différence
for t in ticker_list:
    print(f"{t} - Last BB_Middle: {last_values_hour[t]['BB_Middle']}, Last RSI: {last_values_hour[t]['RSI']}, Last ADX: {last_values_hour[t]['ADX']}, Last +DI: {last_values_hour[t]['+DI']}, Last -DI: {last_values_hour[t]['-DI']}, Close: {last_values_hour[t]['Close']}, MACD: {last_values_hour[t]['MACD']}, MACD Signal: {last_values_hour[t]['MACD_Signal']}, Close - BB_Middle: {last_values_hour[t]['Close_BB_Middle_Diff']}")
    if (last_values_hour[t]['RSI'] < 80 and last_values_hour[t]['+DI'] - 5 > last_values_hour[t]['-DI'] and last_values_hour[t]['MACD'] > last_values_hour[t]['MACD_Signal']) :
      print(f"{t} - <<<<<<<<< BUY URGENT >>>>>>>>>")
    if (last_values_hour[t]['RSI'] > 90 or (last_values_hour[t]['+DI'] + 5 < last_values_hour[t]['-DI'] and last_values_hour[t]['ADX'] > 25 )) :
      ticker_to_sell.append(t)

import requests
import yfinance as yf

def get_top_20_cryptos():
    # Récupérer une large liste de cryptomonnaies par capitalisation boursière
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 100,
        'page': 1
    }
    response = requests.get(url, params=params)
    data = response.json()
    large_ticker_list = [coin['symbol'].upper() for coin in data]

    # Télécharger les données horaires pour ces cryptomonnaies
    evolutions = {}
    for t in large_ticker_list:
        symbol = f"{t}-USD"
        try:
            # Télécharger les données
            data = yf.download(tickers=symbol, interval='1h')  # Récupérer 2 heures de données
            if not data.empty and len(data) > 1:
                # Calculer l'évolution horaire
                last_close = data['Close'].iloc[-1]
                prev_close = data['Close'].iloc[-2]
                hourly_change = (last_close - prev_close) / prev_close
                # Stocker le changement horaire comme une valeur numérique
                evolutions[symbol] = hourly_change.item()  # Convertir en valeur numérique simple
        except Exception as e:
            pass

    # Vérifiez l'état des évolutions avant de trier
    print(f"Evolutions dictionary: {evolutions}")

    # Trier les évolutions par ordre décroissant
    sorted_evolutions = sorted(evolutions.items(), key=lambda x: x[1], reverse=True)

    # Obtenir les 20 cryptos avec les évolutions positives
    top_20_positive_evolutions = [symbol for symbol, change in sorted_evolutions if change > 0][:10]
    
    return top_20_positive_evolutions


# Appel de la fonction
top_20_cryptos = get_top_20_cryptos()



Dataset_hour = {}
valid_tickers = []

for t in top_20_cryptos:
    symbol = f"{t}-USD"
    try:
        data = yf.download(tickers=t, start='2024-04-01', end=None, interval='1d')
        if not data.empty:
            Dataset_hour[t] = data
            valid_tickers.append(t)
    except Exception:
        pass
for t in top_20_cryptos:
    Dataset_hour[t].columns = Dataset_hour[t].columns.get_level_values(0)  # Garder seulement le premier niveau
    Dataset_hour[t].reset_index(inplace=True)  # Réinitialiser l'index pour le rendre plus standard
# Calculer les indicateurs pour chaque ticker et obtenir les dernières valeurs
last_values = {}
for t in valid_tickers:
    Dataset_hour[t] = calculate_technical_indicators(Dataset_hour[t])
    last_row = Dataset_hour[t].iloc[-1]
    last_values[t] = {
        'BB_Middle': last_row['BB_Middle'],
        'RSI': last_row['RSI'],
        'ADX': last_row['ADX'],
        '+DI': last_row['+DI'],
        '-DI': last_row['-DI'],
        'Close': last_row['Close'],
        'Close_BB_Middle_Diff': last_row['Close'] - last_row['BB_Middle'],
        'Evolution': -(last_row['Close'] - last_row['BB_Middle']) / last_row['Close'] * 100,
        'MACD': last_row['MACD'],
        'MACD_Signal': last_row['MACD_Signal'],
        'SMA_50' : last_row['SMA_50'],
        'SMA_10' : last_row['SMA_10'],
        'EMA_50' : last_row['EMA_50'],
        'EMA_10' : last_row['EMA_10']
    }

buy_tickers = []

# Afficher les dernières valeurs des indicateurs et la différence
for t in top_20_cryptos:
    print(f"{t} - Last BB_Middle: {last_values[t]['BB_Middle']}, Last RSI: {last_values[t]['RSI']}, Last ADX: {last_values[t]['ADX']}, Last +DI: {last_values[t]['+DI']}, Last -DI: {last_values[t]['-DI']}, Close: {last_values[t]['Close']}, MACD: {last_values[t]['MACD']}, MACD Signal: {last_values[t]['MACD_Signal']}, SMA_50 : {last_values[t]['SMA_50']}, EMA_50 : {last_values[t]['EMA_50']}, Close - BB_Middle: {last_values[t]['Close_BB_Middle_Diff']}")
    #print(f"{t} - Evolution probable: {last_values[t]['Evolution']}%")
    if (last_values[t]['RSI'] < 80 and last_values[t]['+DI']- 5 > last_values[t]['-DI'] and last_values[t]['MACD'] > last_values[t]['MACD_Signal']) :
      print(f"{t} - BUY")
      buy_tickers.append(t)
      
print(buy_tickers)

stocks_to_sell = []
stocks_to_buy = []

for t in ticker_list:
  if t in ticker_to_buy and t in ticker_to_sell:
    ticker_to_look_for_sell.append(t)
  if t not in ticker_to_buy and t in ticker_to_sell:
    stocks_to_sell.append(t)
  if t in ticker_to_buy and t not in ticker_to_sell:
    stocks_to_buy.append(t)

for t in buy_tickers : 
  if t not in ticker_to_buy and t not in ticker_to_sell:
    ticker_to_buy.append(t)

unique_stocks_to_buy = list(set(stocks_to_buy + ticker_to_buy))
print("Ticker à regarder pour SELL : ", ticker_to_look_for_sell)
print("Ticker à SELL : ", stocks_to_sell)
print("Ticker à BUY : ", unique_stocks_to_buy)

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time

def send_email(subject, body, recipient_email):
    sender_email = "nathanelceylon@gmail.com"
    sender_password = "wnqy dyrm pqjd sxyh"
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"Email envoyé à {recipient_email}")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {e}")

# Fonction pour vérifier les alertes et envoyer des emails
def check_and_alert(stocks_to_sell, unique_stocks_to_buy, ticker_to_look_for_sell):

    body = "Alertes Crypto:\n\n"
    
    if unique_stocks_to_buy:
        body += "=== Crypto(s) à acheter rapidement ===\n"
        body += "\n".join(unique_stocks_to_buy) + "\n\n"
    
    if stocks_to_sell:
        body += "=== Crypto(s) à vendre rapidement ===\n"
        body += "\n".join(stocks_to_sell) + "\n\n"
    
    if ticker_to_look_for_sell:
        body += "=== Crypto(s) à surveiller pour une éventuelle vente ===\n"
        body += "\n".join(ticker_to_look_for_sell) + "\n"
    
    # Vérifie s'il y a du contenu dans le corps du message avant l'envoi
    if body.strip():
        send_email("Crypto Alerts", body, "nathanelceylon@gmail.com")
    else:
        print("Aucune alerte pour le moment.")
    
    for stock in stocks_to_sell[:]:  
      if stock in ticker_list:
        ticker_list.remove(stock)
      stocks_to_sell.remove(stock)


print(ticker_list)


check_and_alert(stocks_to_sell, unique_stocks_to_buy, ticker_to_look_for_sell)

