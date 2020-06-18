from request import request_data, data_request_complete
from functions import update_df
from trade_alert import trade_alert

''' The main functions have been created so that data can
    be added intermittently. I plan on only running the
    program during the day, so each morning the overnight
    data will be requested and then for the rest of the day
    only one bar at a time will be requested (upon candle close).
    
    Each sub function within update_df() runs its own loop
    so that it can filter the df down to only calculate
    new missing values.
    
    Trade alerts are controlled via...  '''

while True:
    request_data()
    if data_request_complete == True:
        update_df()



# ... Function Parameters and Settings ...


# Confidence Functions: 

# Trend strength / weakness
# (threshold probably won't adapt to a large variety
#  of timeframe variation. 1min will need higher values
#  than 4h)
mommentum = {'active': True,
             'threshold': 2,  
             'weight_multiplier': 1
}


auction_volume = {'active': True,
                  'weight_multiplier': 1
}

# Lookback period for average daily price range
adr_window = {'length': 5}


# Update DataFrame Functions

# sw_pct_adr multiplier for setting swing ratings
# (might need to make this timeframe specific)
sw_pct_buffer = 100 


# do these need to be TF specific?
trade_zones = {'height_multiplier': 0.02,
               'length_multiplier': 8,
               'buffer_multiplier': .25
              }

sr_zones = {'height_multiplier': 0.02,
            'length_multiplier': 10,
            'lookback_multiplier': 0.2 
           }

