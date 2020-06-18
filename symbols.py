# Requested symbols and their minimum price movements
symbols = {
           'ES': 0.25,
           'TLT': 1, # dont actually know tick. 30 yr bond ETF
        #    'NQ': 0.25,
        #    'YM': 1, 
           'CL': 0.01,  
           'NG': 0.001, 
        #    'GC': 0.1,
        #    'ZB': 0.01,
        #    '6E': 0.0001,
        #    '6B': 0.0001,
        #    '6A': 0.0001,
        #    '6J': 0.0000005  
           }  
           
# Requested timeframes
# timeframes = [1, 5, 15, 60]
timeframes = ['1m', '5m', '15m', '1h']

# Mapping to higher timeframes
htf_dict = {'m1': 'm5',
            'm5': 'm15',
            'm15': 'h1',
            'h1': 'h4',
            'h4': 'd1'
            } 