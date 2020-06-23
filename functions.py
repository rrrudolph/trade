from symbols import symbols, timeframes
import cockpit
import pandas as pd
import numpy as np
from datetime import datetime


# Only run the resampling of timeframes
# once they have a new closed candle
# now = datetime.now()
# if now.second == 0:
#     timeframe = '1m'
#     update_df()
# if now.minute == 0 or now.minute % 5 == 0:
#     timeframe = '5m'
#     update_df()
# if now.minute == 0 or now.minute % 15 == 0: 
#     timeframe = '15m'
#     update_df()
# if now.minute == 0: 
    # timeframe = '1h'
    # update_df()


# ... Functions for creating the df ... #
def resample_new_data():
    raw = pd.read_csv('data/{}_1m_raw.csv'.format(symbol))
    print(symbol, timeframe)
    raw['dt'] = pd.to_datetime(raw['dt'])
    raw.set_index('dt', inplace=True, drop=False)
    resampled = pd.DataFrame(
                {"open":raw.open.resample(timeframe).first(),
                "high": raw.high.resample(timeframe).max(),
                "low": raw.low.resample(timeframe).min(),
                "close":raw.close.resample(timeframe).last(),
                "volume": raw.volume.resample(timeframe).sum()})
    print('resampled: ', resampled.head(3))

    # By using open, files will be created if they don't exist
    f = open('C:/Users/R/Desktop/code/2nd-tda-api/data/{}_{}.csv'.format(symbol, timeframe), 'w+')
    original = pd.DataFrame(f)
    df = original.append(resampled)
    df.drop_duplicates(inplace=True)
    df.reset_index(inplace=True)
    # df.to_csv('C:/Users/R/Desktop/code/2nd-tda-api/data/{}_{}.csv'.format(symbol, timeframe))
def update_df():
    # original = pd.read_csv('C:/Users/R/Desktop/code/2nd-tda-api/data/{}_{}.csv'.format(symbol, timeframe))
    # Limit the amount of data that's being processed
    # df = original.tail(300)
    find_adr()
    print('adr''d')
    find_fractals()
    print('find frac')
    find_swings()
    print('swings')
    find_trade_zones()
    print('tz')
    find_sr_zones()
    print('sr')
    df = original.append(df)
    df.drop_duplicates(inplace=True)
    df.to_csv('C:/Users/R/Desktop/code/2nd-tda-api/data/{}_{}.csv'.format(symbol, timeframe))
    print(df.head())
    # f.close()

def find_adr(days=5):
    ''' Get the average daily price range
        from high to low '''
    daily = pd.read_csv('data/{}_1d.csv'.format(symbol))
    window = cockpit.adr_window['length']
    # skip first n rows
    temp = df.iloc[window:]
    # only iterate over new rows
    for i in temp[temp['adr'] == np.nan].index:
        group = daily.tail(window)
        adr = (group['high'] - group['low']).mean
        # Divide the price range by symbol's min tick to get adr as tick count
        min_tick = symbols['{}'.format(symbol)]
        adr = adr / min_tick
        # Set new value
        df.loc[i, 'adr'] = adr

        # Not really related, but set bar type
        df['bar'][df['close'] < df['open']] = 'down'
        df['bar'][df['close'] > df['open']] = 'up'
def find_fractals():
    ''' Iterate over rows to find fractal counts '''

    highs = df['high'].values
    lows = df['low'].values

    # Ignore rows where the swings are locked
    temp = df[df['locked'] != 1]

    # Omit first and last row
    for i in temp.index:
        low = lows[i]
        high = highs[i]
        locked_hi = False
        locked_low = False

        ####  Highs  ####
        # Iterate forwards
        count_prior = 0   
        count_next = 0
        next_ = i + 1
        prior_ = i - 1
        try:
            while high > df.loc[next_, 'high'] and count_next < 70: # iter limit
                next_ +=1
                count_next +=1
                # Break if counter is at last row of df (to avoid error)
                if next_ >= df.index[-1]:
                    break
            # Lock the row if high is breached or iter limit reached
            else:
                locked_hi = True
        except: pass
        # Iterate backwards
        try:
            while high >= highs[prior_] and count_prior < 70: 
                prior_ -=1
                count_prior +=1
                # Break if counter is at first row of df (to avoid error)
                if prior_ <= df.index[0]:
                    break
            # Lock the row if high is breached or iter limit reached
            else:
                locked_hi = True
            frac_h = min([count_prior, count_next])
        except: pass

        ####  lows  ####
        # Iter forwards 
        count_prior = 0
        count_next = 0
        next_ = i + 1
        prior_ = i - 1
        try:
            while low < lows[next_] and count_next < 70: 
                next_ +=1
                count_next +=1
                # Break if counter is at last row of df (to avoid error)
                if next_ >= df.index[-1]:
                    break
            # Lock the row if high is breached or iter limit reached
            else:
                locked_low = True
        except: pass
        try: 
            # iter backwards
            while low <= lows[prior_] and count_prior < 70: 
                prior_ -=1
                count_prior +=1
                # Break if counter is at first row of df (to avoid error)
                if prior_ <= df.index[0]:
                    break
            # Lock the row if high is breached or iter limit reached
            else:
                locked_low = True
            frac_low = min([count_prior, count_next])
        except: pass

        # Choose correct swing and save data to df
        try:  
            if frac_low > frac_h:
                df.loc[i, 'fractal'] = frac_low
                df.loc[i, 'locked'] = locked_low
                # Find the max price movement that occured (in ticks)
                # from the swing to n bars forward (n = fractal)
                df.loc[i,'sw_size'] = (max(highs[i:i+frac_low]) - low) / min_tick
                # Index of lowest low within fractal count (couldn't think of a good name)
                df.loc[i, 'sw_zz'] =  max(highs[i:i+frac_low]).index
            if frac_h > frac_low:
                df.loc[i, 'fractal'] = frac_h
                df.loc[i, 'locked'] = locked_hi
                df.loc[i,'sw_size'] = (min(lows[i:i+frac_h]) - high) / min_tick
                peak = min(lows[i:i+frac_h])
                df.loc[i, 'sw_zz'] = peak.index
        except: pass
def find_swings():

    ''' Calculate swing size as a percentage of 
        ADR, set the swing rating, and record 
        the actual price of each swing '''

    # Swing size as % of ADR
    df['sw_pct_adr'] = df['sw_size'] / df['adr']
    # The swing rating is a combination of the fractal rating and the amount
    # of ticks that price moved within the fractal rating
    df['sw_rating'] = (abs(df['sw_size']) / min_tick + df['fractal']) / 2

    # Record the swing prices
    temp = df[df['sw_rating'] > 0]
    for i in temp.index:
        a = df.loc[i,'high'][ df.loc[i,'sw_size'] < 0]
        b = df.loc[i,'low'][ df.loc[i,'sw_size'] > 0]
        if len(a) > 0:
            df.loc[i,'sw_price'] = a
        elif len(b) > 0: 
            df.loc[i,'sw_price'] = b
def tz_sell_viz():
    '''Captures all sell trade setups'''
    f = open('data/logs/{}_{}_tz_sell_zones_viz.csv', 'a').format(symbol, timeframe)
    f.write(start)
    f.write(end)
    f.write(end)
    f.write(start)
    f.write(start)
    f.write(None)
    f.write(lower)
    f.write(lower)
    f.write(upper)
    f.write(upper)
    f.write(lower)
    f.write(None)
    f.write('/n')
    f.close()
    f = open('data/logs/{}_{}_tz_sell_names_viz.csv', 'a').format(symbol, timeframe)
    f.write(zone_type)
    f.close()
    f = open('data/logs/{}_{}_tz_sell_dates_viz.csv', 'a').format(symbol, timeframe)
    f.write(df.loc[i, 'dt'])
    f.close()
def tz_buy_viz():
    '''Captures all sell trade setups'''
    f = open('{}_{}_tz_buy_viz.csv', 'a').format(symbol, timeframe)
    f.write(start)
    f.write(end)
    f.write(end)
    f.write(start)
    f.write(start)
    f.write(None)
    f.write(lower)
    f.write(lower)
    f.write(upper)
    f.write(upper)
    f.write(lower)
    f.write(None)
    f.write('/n')
    f.close()
    f = open('data/logs/{}_{}_tz_buy_names_viz.csv', 'a').format(symbol, timeframe)
    f.write(zone_type)
    f.close()
    f = open('data/logs/{}_{}_tz_buy_dates_viz.csv', 'a').format(symbol, timeframe)
    f.write(df.loc[i, 'dt'])
    f.close()

def find_trade_zones():
    def set_tz_params():
        df.loc[i, 'tz_type'] = zone_type
        df.loc[i, 'tz_end'] = end
        df.loc[i, 'tz_upper'] = upper
        df.loc[i, 'tz_lower'] = lower 
    temp =  df[(df['tz_active'] != False) & (df['sw_rating'] > 1)]
    for i in temp.index: 
        swing = df.loc[i, 'sw_rating']
        zone_height = swing * cockpit.trade_zones['height_multiplier']

        # Set a limit on zone height
        a = df.loc[2, 'dt'] - df.loc[1, 'dt']  
        b = pd.Timedelta(days = 1)
        cpd = b / a         # candles per day
        max_size = df.loc[i, 'adr'] / cpd * cockpit.trade_zones['height_multiplier']  
        # (wont work for D1 TF. and might not work at all, or be needed?)

        if zone_height > max_size:
            zone_height = max_size
        # print("zone height: ", zone_height, "\n max: ", max_size)

        if df.loc[i, 'sw_size'] < 0:       # swing high
            zone_type = 'sell'
            upper = df.loc[i,'sw_price'] + zone_height    
            lower = df.loc[i,'sw_price']         
        if df.loc[i, 'sw_size'] > 0:      # swing low
            zone_type = 'buy'
            upper = df.loc[i,'sw_price']   
            lower = df.loc[i,'sw_price'] - zone_height  
        
        # Set zone 'end' and find length
        try:
            end = round(i + df.loc[i, 'sw_rating'] * cockpit.trade_zones['height_multiplier'])
        except:
            if end >  len(df) - 1:
                end = len(df) - 1

        # Set buffers  (used for switching zone type)
        buffer_upper = upper + (zone_height * cockpit.trade_zones['buffer_multiplier'])
        buffer_lower = lower - (zone_height * cockpit.trade_zones['buffer_multiplier'])

    # Filter df to only show candles between i and end,
    # then from that only show candles between upper and lower 
        zone_df = df.loc[i:end]
        zone_df = zone_df[(zone_df['high'].between(lower, upper)) |
                        (zone_df['low'].between(lower, upper))]
        set_tz_params() # Saved so other time frames can access

        
        # Check for candles within zone
        if not zone_df.empty():

            ###### SELL ZONES ######
            if zone_type == 'sell':
                set_tz_params() # Saved so other time frames can access

                # Check if zone gets crossed to the upside
                # If not, look for an entry signal
                new_high = zone_df[zone_df['high'] > buffer_upper]
                if new_high.empty():  
                    if auction_volume():
                        # log_notification(name='auction_volume', direction=zone_type)
                        tz_sell_viz()

                        ### Sell flips to buy ###
                else: 
                    # Change zone type, set a new end extended
                    # to the right by 50% and shift zone down by 50% 
                    zone_type = 'buy'
                    start2 = min(new_high.index) 
                    end = round((end - start) * 0.5 + end)    
                    if end > len(df) - 1:
                        end = len(df) - 1
                    upper = upper - zone_height / 2 
                    lower = lower - zone_height / 2 
                    set_tz_params()

                    # Refilter the zone_df to reflect new zone dimensions
                    flipped_zone = df.loc[start2:end]
                    flipped_zone = flipped_zone[(flipped_zone['high'].between(lower, upper)) |
                                    (flipped_zone['low'].between(lower, upper))]
                    if not flipped_zone.empty():     
                        # If zone gets crossed again it becomes inactive,
                        # otherwise look for trades 
                        new_low = flipped_zone['low'][flipped_zone['low'] < lower]   
                        if not new_low.empty():    
                            df.loc[i,'tz_active'] = False  
                        else: 
                            if auction_volume():
                                # log_notification(name='auction_volume', direction=zone_type)
                                tz_buy_viz()
                                
            ###### BUY ZONES ######
            if zone_type == 'buy':
                set_tz_params() # Saved so other time frames can access

                # Check if zone gets crossed to the downside
                # If not, look for an entry signal
                new_low = zone_df[zone_df['low'] < buffer_lower]
                if new_low.empty():  
                    if auction_volume():
                        # log_notification(name='auction_volume', direction=zone_type)
                        tz_buy_viz()

                        ### Sell flips to buy ###
                else: 
                    # Change zone type, set a new end extended
                    # to the right by 50% and shift zone down by 50% 
                    zone_type = 'sell'
                    start2 = min(new_low.index) 
                    end = round((end - start) * 0.5 + end)    
                    if end > len(df) - 1:
                        end = len(df) - 1
                    upper = upper - zone_height / 2 
                    lower = lower - zone_height / 2 
                    set_tz_params() # Saved so other time frames can access

                    # Refilter the zone_df to reflect new zone dimensions
                    flipped_zone = df.loc[start2:end]
                    flipped_zone = flipped_zone[(flipped_zone['high'].between(lower, upper)) |
                                    (flipped_zone['low'].between(lower, upper))]

                    if not flipped_zone.empty():     
                        # If zone gets crossed again it becomes inactive,
                        # otherwise look for trades 
                        new_high = flipped_zone[flipped_zone['high'] < upper]   
                        if not new_high.empty():    
                            df.loc[i,'tz_active'] = False  
                        else: 
                            if auction_volume():
                                tz_buy_viz() 
def sr_viz_inactive():
    '''Invalidated sr_zones'''
    f = open('{}_{}_sr_viz_inactive.csv', 'a').format(symbol, timeframe)
    f.write(start)
    f.write(end)
    f.write(end)
    f.write(start)
    f.write(start)
    f.write(None)
    f.write(lower)
    f.write(lower)
    f.write(upper)
    f.write(upper)
    f.write(lower)
    f.write(None)
    f.close()
def sr_viz_active():
    '''Active sr_zones'''
    f = open('{}_{}_sr_viz_active.csv', 'a').format(symbol, timeframe)
    f.write(start)
    f.write(end)
    f.write(end)
    f.write(start)
    f.write(start)
    f.write(None)
    f.write(lower)
    f.write(lower)
    f.write(upper)        
    f.write(upper)
    f.write(lower)
    f.write(None)
    f.close()
def set_sr_params():
        df.loc[i, 'sr_start'] = start
        df.loc[i, 'sr_end'] = end
        df.loc[i, 'sr_upper'] = upper
        df.loc[i, 'sr_lower'] = lower
        df.loc[i, 'sr_type'] = sr_type
def find_sr_zones():
    '''This is essentially the same as the trade
    zones function but with fewer parameters'''
    # These are used for recording data to df and for plotting     
    
    # Filter df for rows with swings and,
    # if an SR zone exists, is still active
    active_swings = temp[temp['sr_active'] != False]
    for i in active_swings.index:
        # Create a zone and set its 4 coordinates (start, end, upper, lower)
        sw_rating = df.loc[i, 'sw_rating']
        zone_height = round(sw_rating * cockpit.sr_zones['height_multiplier'], 4)
        upper = df.loc[i,'sw_price'] + (zone_height / 2)    
        lower = df.loc[i,'sw_price'] - (zone_height / 2)
        # Set the start of zone (if not before first row of df)
        try:
            start = i - (cockpit.sr_zones['lookback_multiplier'] * sw_rating)
        except:
            start = df.head(1).index
        # Set the length of zone (if not longer than df)
        try:
            end = i + sw_rating * cockpit.sr_zones['length_multiplier']
        except:
            end = df['dt'].tail(1)
        
        # Set buffers  (used for switching zone type)
        buffer_upper = upper + (zone_height * cockpit.sr_zones['buffer_multiplier'])
        buffer_lower = lower - (zone_height * cockpit.ar_zones['buffer_multiplier'])
        # Filter the df to only show candles that 
        # are between the zone's start and end. Then
        # find any swings that occur within the zone
        temp = df.loc[start:end, ['dt','sw_price','sw_size']]
        in_zone = temp[(temp['sw_price'] > lower) & (temp['sw_price'] < upper)]
        in_zone.reset_index(inplace=True, drop=False)

        # If no new swings are found within the zone, 
        # set as False to skip the row in future iterations
        if in_zone.empty():
            df.loc[i, 'sr_active'] = False
        
        else:
            # To see if the zone is currently valid, check
            # if candles have crossed through it
            above = temp[temp['high'] > upper]
            below = temp[temp['low'] < lower]
            if not above.empty() and not below.empty():
                # Zone has been intersected at least once
                # Find the first high or low to intersect (whichever came after) 
                if min(above.index) > min(below.index):
                    # Check if zone was crossed a second time
                    # (find a candle that exists 1. below the zone and 
                    #  2. after the first candle that existed above it)
                    new_low = below[below.index > min(above.index)]
                    if not new_low.empty():
                        df.loc[i, 'sr_active'] = False
                        # For plotting historical zones, change the end
                        # to match the final candle to pierce the zone
                        end = min(new_low.index)
                        set_sr_params()
                        sr_viz_inactive()
                else: 
                    # Same thing but for highs
                    new_high = above[above.index > min(below.index)] 
                    if not new_high.empty():
                        df.loc[i, 'sr_active'] = False
                        end = min(new_high.index)
                        set_sr_params()
                        sr_viz_inactive()
            else: 
                # Zone is active
                if df.loc[i, 'high'] > buffer_upper:
                    sr_type = 'buy'
                if df.loc[i, 'low'] < buffer_lower:
                    sr_type = 'sell'
                set_sr_params()
                sr_viz_active()

    # Finally, invalidate by expiry
    temp = df[(df['sr_end'] < i) & (df['sr_active'] != False)]
    for i in temp:
        df.loc[i, 'sr_active'] = False

for symbol in symbols:
    for timeframe in timeframes:
        raw = pd.read_csv('data/{}_1m_raw.csv'.format(symbol))
        print(symbol, timeframe)
        raw['dt'] = pd.to_datetime(raw['dt'])
        raw.set_index('dt', inplace=True, drop=False)
        resampled = pd.DataFrame({"dt": raw.dt.resample(timeframe).last(),
                                  "open": raw.open.resample(timeframe).first(),
                                  "high": raw.high.resample(timeframe).max(),
                                  "low": raw.low.resample(timeframe).min(),
                                  "close":raw.close.resample(timeframe).last(),
                                  "volume": raw.volume.resample(timeframe).sum()})
        print('resampled: ', resampled.head(3))

        # By using open, files will be created if they don't exist
        f = open('C:/Users/R/Desktop/code/2nd-tda-api/data/{}_{}.csv'.format(symbol, timeframe), 'w+')
        original = pd.DataFrame(f)
        df = original.append(resampled)
        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)
        print(df.head())
        # This is needed the first time to create columns
        df = df.reindex(columns=(['dt', 'open', 'high', 'low', 'close', 'volume', 'bar', 'adr', 'fractal', 'locked',
                                  'sw_zz', 'sw_price', 'sw_size', 'sw_pct_adr', 'sw_rating', 'tz_active', 'tz_type',
                                  'tz_end', 'tz_high', 'tz_low', 'sr_active', 'sr_type', 'sr_start', 
                                  'sr_end', 'sr_high', 'sr_low']))
        min_tick = symbols[symbol]
        update_df()


# def log_notification(time=df.loc[i, 'dt'],
#                     symbol=symbol,
#                     timeframe=timeframe,
#                     name=name,
#                     direction=direction,
#                     price=df.loc[i, 'open'],
#                     momentum=df.loc[i, 'momentum'],
#                     htf_zone=df.loc[i, 'in_htf_sr_zone']):

#     f = open('/data/logs/{}_{}.csv').format(symbol, timeframe)
#     f.write(time)
#     f.write(symbol)
#     f.write(name)
#     f.write(direction)
#     f.write(price)
#     f.write(momentum)
#     f.write(htf_zone)
#     f.write('/n')
#     f.close()
# ... Confidence and Trade Setups ... #
 # Confidence
def in_htf_sr_zone():
    '''Check if price is currently in an active HTF SR zone'''
    # Load df of higher timeframe
    htf = htf_dict[timeframe]
    htf_df = pd.read_csv('data/{}_{}.csv').format(symbol, htf)
    # Filter df for active zones with relevant coordinates (start, end, upper, lower)
    htf_df = htf_df[htf_df['sr_active'] != False]
    htf_df = htf_df[(htf_df['sr_start'] < df.loc[i, 'dt']) & (htf_df['sr_end'] > df.loc[i, 'dt'])]
    htf_df = htf_df[(htf_df['sr_lower'] < df.loc[i, 'close']) & (htf_df['sr_upper'] > df.loc[i, 'close'])]
    if not htf_df.empty():
        # Count each zone as a +2 or -2 for confidence
        total = 0
        for zone in htf_df:
            if htf_df.loc[zone, 'sr_type'] == 'buy':
                total += 2
            else:
                total -= 2
        return total

        df.loc[i, 'in_htf_sr_zone'] = True
        return True
def momentum():
    '''Watch for momentum changes to set trade directions'''
    if cockpit.momentum['active'] == True:

        # Recent group of swings
        rec_highs = df[df['sw_pct_adr'] < 0].tail(4)
        rec_lowows = df[df['sw_pct_adr'] > 0].tail(4)
        rec_avg_hi = rec_highs['sw_rating'].mean()
        rec_avg_lowo = rec_lowows['sw_rating'].mean()

        # Historical group
        hist_highs = df.iloc[-12:-3][df['sw_pct_adr'] < 0]
        hist_lowows = df.iloc[-12:-3][df['sw_pct_adr'] > 0]
        hist_avg_hi = hist_highs['sw_rating'].mean()
        hist_avg_lowo = hist_lowows['sw_rating'].mean()

        # Get diffs between recent and historical
        highs_diff = rec_avg_hi - hist_avg_hi
        lows_diff = rec_avg_lowo - hist_avg_lowo
        diff = highs_diff - lows_diff  # log this

        # Make adr a whole number if it's not
        # Divide adr by the minimum price movement of that symbol
        adr = df['adr'].tail(1) / symbols.symbols[symbol]
        # Minimum threshold value that when hit will change trade direction (up/down/both)
        # (ticks per day divied by candles per day)
        threshold = adr / cpd * cockpit.momentum['threshold'] 
        if diff > threshold:
            df.loc[i, 'momentum'] = 1
        if diff < threshold * -1:
            df.loc[i, 'momentum'] = -1
        else:
            df.loc[i, 'momentum'] = 0
        return df.loc[i, 'momentum']

# Trade Setups
def auction_volume(direction='both', minimum_threshold=2):
    ''' Sequentially decreasing volume with 
        candles of the same type'''
    if cockpit.auction_vol['active'] == True:
        vol = df['volume']
        bar = df['bar_type']
        gate_one = direction == 'sell' and bar.iloc[i-1] == 'buy'
        gate_two = direction == 'buy' and bar.iloc[i-1] == 'sell'

        # Verify logic gates and avoid index errors
        if gate_one or gate_two or direction == 'both' and i > 3:
            x = 0
            if bar.iloc[i] == bar.iloc[i-1] and vol.iloc[i] < vol.iloc[i-1]:
                x = 1
                if bar.iloc[i-1] == bar.iloc[i-2] and vol.iloc[i-1] < vol.iloc[i-2]:
                    x = 2
                    if bar.iloc[i-2] == bar.iloc[i-3] and vol.iloc[i-2] < vol.iloc[i-3]:
                        x = 3
            if x >= minimum_threshold:
                return True
                # Find out what direction got triggered
                if bar.iloc[-1] == 'down':
                    direction = 'buy'
                else:
                    direction = 'sell'
                    log_notification(name='auction volume', direction=direction)

# def wobble():
#     '''A pause after an impulse'''



