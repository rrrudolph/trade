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
        period_type = 'day'
        period = 2 
        frequency_type = 'minute'
        frequency = 1

        # Make request
        backfill = td_client.get_price_history(symbol=symbol, period_type=period_type,
                                            period=period, frequency_type=frequency_type,
                                            frequency=frequency)

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
            
            print(new_data.iloc[:5])
            # If the files don't exist, create them. Comment out after first run.
            f = open('C:/Users/R/Desktop/code/2nd-tda-api/data/{}_1m_raw.csv'.format(symbol), 'w+')
            # f.close()
            print('file opened/closed')
            # append to existing raw data and delete duplicates
            old_data = pd.DataFrame(f)
            print('done reading csv')
            df = old_data.append(new_data)
            print('concatd')
            df.drop_duplicates(inplace=True)
            print('duplicates dropped')
            df.to_csv('C:/Users/R/Desktop/code/2nd-tda-api/data/{}_1m_raw.csv'.format(symbol), index=False)
            print('backfill saved!!!!!!!!!!!!!!!!!!!')
        except:
            print('FAILED')
            pass
    # Everytime a new 1min candle has been created, 
    # request the new data for all symbols 
    now = datetime.now()
    while True:
        # Create a flag to notify the next module when to run
        data_request_complete = False
        if now.second == 0:
            for symbol in symbols:
                period_type = 'minute'
                period = 1 # buffer in case of timeout
                frequency_type = 'minute'
                frequency = 1

                # Make request
                # (returns a dictionary with 3 items: a list of candles, 'empty', and symbol)
                # found a typo:  http://prntscr.com/sw8dtq
                minute = td_client.get_price_history(symbol=symbol, period_type=period_type,
                                                    period=period, frequency_type=frequency_type,
                                                    frequency=frequency)

                # In case I get bad data that causes an error 
                try:
                    # Save the OHLC data
                    s = backfill['candles']
                    new_data = pd.DataFrame(s)
                    print(new_data.iloc[:3])
                    # If the files don't exist, create them. Comment out after first run.
                    f = open('C:/Users/R/Desktop/code/2nd-tda-api/data/{}_1m_raw.csv'.format(symbol), 'w+')
                    # f.close()
                    print('file opened/closed')
                    # append to existing raw data and delete duplicates
                    old_data = pd.DataFrame(f)
                    print('done reading csv')
                    df = old_data.append(new_data)
                    print('concatd')
                    df.drop_duplicates(inplace=True)
                    print('duplicates dropped')
                    df.to_csv('C:/Users/R/Desktop/code/2nd-tda-api/data/{}_1m_raw.csv'.format(symbol), index=False)
                    print('backfill saved!!!!!!!!!!!!!!!!!!!')
                except:
                    pass

                # Change the completion flag status after getting to the end of the list
                if symbol == symbols[-1]:
                    data_request_complete = True
                    time.sleep(10)

request_data()