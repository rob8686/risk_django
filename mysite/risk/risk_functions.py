import yfinance as yf
import math

def get_yf_data(tickers):
    data = yf.download(  # or pdr.get_data_yahoo(...
        # tickers list or string as well
        tickers=tickers,

        # use "period" instead of start/end
        # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        # (optional, default is '1mo')
        period="ytd",

        # fetch data by interval (including intraday if period < 60 days)
        # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
        # (optional, default is '1d')
        interval="1d",

        # group by ticker (to access via data['SPY'])
        # (optional, default is 'column')
        group_by='column',

        # adjust all OHLC automatically
        # (optional, default is False)
        auto_adjust=True,

        # download pre/post regular market hours data
        # (optional, default is False)
        prepost=False,

        # use threads for mass downloading? (True/False/Integer)
        # (optional, default is True)
        threads=True,

        # proxy URL scheme use use when downloading?
        # (optional, default is None)
        proxy=None

    )
    return data

def calc_liquidity(quantity,adv):
    # calcualtes the number of days to liquidate position at 10% of ADV per day 
    max_liquid_per_day = adv * .1
    days_to_liquidate = math.ceil(quantity / max_liquid_per_day)
    amount_final_day = quantity % max_liquid_per_day 

    bucket_dict = {'1':0,'7':0,'30':0,'90':0,'180':0,'365':0,'365+':0}

    # create list of lists with day and amount elements
    liquidity_days_list = [[day,max_liquid_per_day] if day < days_to_liquidate 
               else [day,amount_final_day] 
               for day in range(1,days_to_liquidate +1)]

    for day in liquidity_days_list:
        if day[0] ==1:
            bucket_dict['1'] = bucket_dict['1'] + day[1] 
        elif day[0] <= 7:
            bucket_dict['7']= bucket_dict['7'] + day[1]
        elif day[0] <= 30:
            bucket_dict['30']= bucket_dict['30'] + day[1]
        elif day[0] <= 90:
            bucket_dict['90']= bucket_dict['90'] + day[1]
        elif day[0] <= 180:
            bucket_dict['180']= bucket_dict['180'] + day[1]
        elif day[0] <= 365:
            bucket_dict['365']= bucket_dict['365'] + day[1]
        else:
            bucket_dict['365+']= day[1]

    return bucket_dict

def calc_performance(yf_df,):
    #for tickier  
    return True