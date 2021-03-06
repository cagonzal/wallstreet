from wallstreet import Stock, Call, Put
import datetime
import itertools
import pandas as pd

def expirationsOfInterest(tick,minDays,maxDays):
    
    putOption = Put(tick)
    
    allExpirations = putOption.expirations
    print('List of all expirations\n')
    print(allExpirations)
    print('\n')
    validExpirations = []
    minDaysTillExpiration = 15
    maxDaysTillExpiration = 45
    
    for expDate in allExpirations:
    
        expir = expDate.split('-')
        day = int(expir[0])
        month = int(expir[1])
        year = int(expir[2])
        
        daysOut = datetime.date(year,month,day) - datetime.date.today()
        daysOut = daysOut.days
        
        if daysOut > minDaysTillExpiration and daysOut < maxDaysTillExpiration:
            validExpirations.append(expDate)
            
    return validExpirations

def putCreditSpread(tick,minDays,maxDays,strikeSpread,minPoP):
    
    s = Stock(tick)
    stockPrice = s.price
    validExpirations = expirationsOfInterest(tick,minDays,maxDays)
    
    print('List of valid expirations:\n')
    print(validExpirations)
    print('\n')
    my_columns = ['Expiry','PoP','Premium','Long Strike','Short Strike']
    #spread_dataframe = pd.DataFrame(columns = my_columns)
    
    frames = []
    for expDate in validExpirations[:1]:
        
        print('Current expiration being analyzed\n')
        print(expDate)
        expir =  expDate.split('-')
        day = int(expir[0])
        month = int(expir[1])
        year = int(expir[2])
        
        if day == 3:
            blah = 5
        
        day = 5
        month = 3
        year = 2021
        temp = Put(tick, d=day, m=month, y=year)
        
        spread_dataframe = pd.DataFrame(columns = my_columns)
        strikes = []
        strike1 = []
        strike2 = []
        longStrike = []
        shortStrike = []
        longPremium = []
        shortPremium = []
        
        strikes = (temp.strikes)
        
        strikes = [strike for strike in strikes if (strike / stockPrice > 1-strikeSpread  and strike / stockPrice < 1+strikeSpread)]
        
        strike1 = [a for (a,b) in itertools.product(strikes,strikes)]
        strike2 = [b for (a,b) in itertools.product(strikes,strikes)]
        
        
        
        for i in range(0,len(strike1)):
            if strike1[i] < strike2[i]:
                longStrike.append(strike1[i])
                shortStrike.append(strike2[i])
                
                temp.set_strike(strike1[i])
                
                price = (temp.bid + temp.ask) / 2
                longPremium.append(price)
                
                temp.set_strike(strike2[i])
                price = (temp.bid + temp.ask) / 2
                shortPremium.append(price)
            
            elif strike1[i] > strike2[i]:
                longStrike.append(strike2[i])
                shortStrike.append(strike1[i])
                
                temp.set_strike(strike1[i])
                
                price = (temp.bid + temp.ask) / 2
                shortPremium.append(price)
                
                temp.set_strike(strike2[i])
                price = (temp.bid + temp.ask) / 2
                longPremium.append(price)
            else:
                continue
    
        
        for i in range(0,len(shortStrike)):
            credit = shortPremium[i] - longPremium[i]
            strikeWidth = shortStrike[i] - longStrike[i]
            spread_dataframe = spread_dataframe.append(
                pd.Series(
                    [
                    expir,
                    100 - credit / strikeWidth * 100,
                    credit,
                    longStrike[i],
                    shortStrike[i]
                    ],
                    index = my_columns),
                ignore_index = True
                )
            
        frames.append(spread_dataframe)
        
    result = pd.concat(frames)
            
    spread_dataframe.sort_values('PoP', ascending = False, inplace = True)
    spread_dataframe.reset_index(drop = True, inplace = True)
    spread_dataframe = spread_dataframe[spread_dataframe['PoP'] >= minPoP]
    
    result.sort_values('PoP', ascending = False, inplace = True)
    result.reset_index(drop = True, inplace = True)
    result = result[spread_dataframe['PoP'] >= minPoP]
    
    return result
    
#%%

tick = 'PLTR'
minDays= 15
maxDays = 45
strikeSpread = 0.2 # percentage to vary around underlying stock price 
minPoP = 60

#%%

spread_dataframe = putCreditSpread(tick, minDays, maxDays, strikeSpread, minPoP)

#%%
s = Stock(tick)
stockPrice = s.price

print(f'Credit Spread Table for {tick} at the current trading price of {stockPrice}')
print(spread_dataframe)

