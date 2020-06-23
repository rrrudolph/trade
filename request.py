from config import CONSUMER_KEY, REDIRECT_URI, JSON_PATH, TD_ACCOUNT
from symbols import symbols, timeframes
from td.client import TDClient
import pandas as pd
from datetime import datetime
import time 
print('imported files')
def request_data():
    # Create a new session
    td_client = TDClient(                 
        client_id='AZ2BZPRDVDNFBHUB5ADYDAPMD2CLG9RG',
        redirect_uri='https://localhost/first',
        credentials_path='C:/Users/R/Desktop/code/2nd-tda-api/td_state.json'
    )

    # Login to a new session
    td_client.login()
    print('td client logged in')

    # ... Backfill data ...
    ''' This is for filling in data from overnight or
        whenever the program hasn't been running during
        market hours '''
    for symbol in symbols:
            print(symbol)
            ext_hours = True   # extended hours
            period_type = 'month'
            period = 3
            frequency_type = 'daily'
            frequency = 1

            # Make request
            backfill = td_client.get_price_history(symbol=symbol, period_type=period_type,
                                                period=period, frequency_type=frequency_type,
                                                frequency=frequency, extended_hours=ext_hours)

            # returns a dictionary with 3 items: candles (a list), empty, and symbol
            # found a typo:  http://prntscr.com/sw8dtq
            # Remove symbol prefix if present 
            if symbol[0] == '$' or symbol[0] == '/':
                symbol = symbol[1:]

            # in case I get bad data that causes an error 
            # (log something too)
            print('backfill requested')
            try:
                # Save the OHLC data
                s = backfill['candles']
                new_data = pd.DataFrame(s)
                new_data['datetime'] = pd.to_datetime(new_data['datetime'], unit='ms', origin='unix')
                new_data.rename(columns={"datetime": "dt"}, inplace=True)
                # new_data.set_index('dt', inplace=True)
                new_data = new_data[['dt', 'open', 'high', 'low', 'close', 'volume']]
                f = open('C:/Users/R/Desktop/code/2nd-tda-api/data/{}_1d.csv'.format(symbol), 'w+')
                # append to existing raw data and delete duplicates
                old_data = pd.DataFrame(f)
                df = old_data.append(new_data)
                df.drop_duplicates(inplace=True)
                df.fillna(method='ffill', inplace=True)
                df.to_csv('C:/Users/R/Desktop/code/2nd-tda-api/data/{}_1d.csv'.format(symbol), index=True)
                f.close()
                print('backfill saved!!!!')
            except Exception as e:
                print(e)
                #log someting maybe
                pass
    # Eeach time a new 1min candle has been created, 
    # request the new data for all symbols 
#     while True:
#         # Create a flag to notify the next module when to run
#         data_request_complete = False
#         # Wait for the close of a new candle
#         now = datetime.now()
#         if now.second == 0:
#             for symbol in symbols:
#                 period_type = 'day'  # lowest period is day
#                 period = 1 
#                 frequency_type = 'minute'
#                 frequency = 1

#                 # Make request
#                 # (returns a dictionary with 3 items: a list of candles, 'empty', and symbol)
#                 # found a typo:  http://prntscr.com/sw8dtq
#                 minute = td_client.get_price_history(symbol=symbol, period_type=period_type,
#                                                     period=period, frequency_type=frequency_type,
#                                                     frequency=frequency)

#                 # In case I get bad data that causes an error 
#                 try:
#                     # Save the OHLC data
#                     s = backfill['candles']
#                     new_data = pd.DataFrame(s)
#                     new_data['datetime'] = pd.to_datetime(new_data['datetime'], unit='ms', origin='unix')
#                     new_data.rename(columns={"datetime": "dt"}, inplace=True)
#                     # new_data.set_index('dt')
#                     new_data = new_data[['dt', 'open', 'high', 'low', 'close', 'volume']]
#                     f = open('C:/Users/R/Desktop/code/2nd-tda-api/data/{}_1m_raw.csv'.format(symbol), 'w+')
#                     # append to existing raw data and delete duplicates
#                     old_data = pd.DataFrame(f)
#                     df = old_data.append(new_data)
#                     df.drop_duplicates(inplace=True)
#                     df.to_csv('C:/Users/R/Desktop/code/2nd-tda-api/data/{}_1m_raw.csv'.format(symbol), index=True)
#                     f.close()
#                     print('new bar saved!!!!!')
#                 except Exception as e:
#                     print(e)
#                     pass

#                 # Change the completion flag status after getting to the end of the list
#                 keys = list(symbols.keys())
#                 if symbol == keys[-1]:
#                     data_request_complete = True
#                     time.sleep(10)

# # (temporarily here for testing)
# data_request_complete = True

request_data()