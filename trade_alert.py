from functions import i, symbol, timeframe, direction

# Create a csv template
log_df = pd.DataFrame(data=None)
log_df.columns = ['dt', 'symbol', 'timeframe', 'trade_type',
                  'direction', 'entry_price', 'momentum', 'in_htf_zone']

def log_notification((time=df.loc[i, 'dt'],
                      symbol=symbol,
                      timeframe=timeframe
                      name='Auction Volume',
                      direction=direction,
                      price=df.loc[i, 'open'],
                      momentum=df.loc[i, 'momentum'],
                      htf_zone=df.loc[i, 'in_htf_sr_zone']
    # For now just log
    f = open('/data/logs/{}_{}.csv').format(symbol, timeframe)
    f.write(time)
    f.write(symbol)
    f.write(name)
    f.write(direction)
    f.write(price)
    
                    trade_alert.log_notification
    