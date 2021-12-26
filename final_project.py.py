# all imports
import json
import requests
import os
import pandas as pd
import numpy as np
import time

#get the stock data from the AlphaVintage Web API
def get_stock_data(ticker):
    url=f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&interval=5min&outputsize=full&apikey=NG9C9EPVYBMQT0C8'
    response = requests.get(url)
    data = response.json()

    #next, we will only keep 1000 data starting from the most recent

    #Get list of dates and prices
    dates = []
    prices = []
    for key, value in data['Time Series (Daily)'].items():
        dates.append(key)
        prices.append(float(value['4. close']))

    # We will only keep the most recent 1000 data points and drop everything else 
    dates = (dates[:1000])
    prices = (prices[:1000])

    #return the dates and prices
    return dates, prices


#function to save the result as csv file
def save_data_as_csv(results):

    #create filename from the last data date

    last_day = results.loc[0][0]
    filename = f'data/datafrom_{last_day}.csv'
    df.to_csv(filename, index=False)

def save_result_json(results, filename): 
    with open(filename, 'w') as f:
        json.dump(results, f)
    f.close()   #close the file


#method to mean reversion strategy trading
def meanRevisionStrategy(prices):
    bought = False  #boolean to check if we have bought or not
    shortsold = False  #boolean to check if we have sold or not (To check short selling)
    buyprice = 0
    sellprice = 0
    total_profit = 0
    initInvestment = 0 #to save the initial investment
    for i in range(5, len(prices)):
        average = (prices[i-5] + prices[i-4] + prices[i-3] + prices[i-2] + prices[i-1])/5 #calculate the average of the last 5 prices
        
        if (prices[i] < average * 0.95 and bought == False): #if the price is less than the average * 0.95 and we havent bought yet, we buy
            if initInvestment == 0:   #if we havent bought yet, we save the initial investment
                initInvestment = prices[i]

            print("Buy at price: \t", prices[i]) #print the buy price
            buyprice = prices[i]
            bought = True  #we have bought, set flag to true

            #check if it is already sold (shortselling), an dif so, update the profit
            if sellprice != 0:
                profit = sellprice - buyprice
                print(f"Trade Profit: \t{profit:.2f}" )
                total_profit += profit #add the profit to the total profit
                sellprice = 0
                shortsold = False

            #check if it is the last day, and if so, print the buy signal
            if i == len(prices)-1:
                print("BUY this stock Today at: \t", prices[i])

        elif(prices[i] > average * 1.05  and shortsold == False): #if the price is greater than the average * 1.05 and we have NOT sold before, we sell
            
            if buyprice != 0:
                print("Sell at price: \t", prices[i])
                profit = prices[i] - buyprice   #calculate the profit
                print(f"Trade Profit: \t{profit:.2f}" )
                total_profit += profit #add the profit to the total profit
                buyprice = 0
            else:
                sellprice = prices[i]
                print(f"Short Selling at : \t{sellprice:.2f}" )
                shortsold = True #we have sold, set flag to true

            #check if it is the last day, and if so, print the Sell signal
            if i == len(prices)-1:
                print("Sell this stock Today at: \t", prices[i])

    if initInvestment == 0:  #To avoid diving by zero problem
        returnrate = 0
    else:
        returnrate = total_profit/initInvestment * 100 #calculate the return rate
    print(f"Mean Revision Strategy Total profit: \t {total_profit:.3f}")
    print(f"Mean Revision Strategy Return rate: \t {returnrate:.3f} %")
    return total_profit, returnrate #return the total profit and the return rate

def simpleMovingAvgXover(prices): #method to calculate profit from the simple moving average crossover strategy
    bought = False  #boolean to check if we have bought or not
    shortsold = False  #boolean to check if we have sold or not (To check short selling)
    buyprice = 0
    sellprice = 0
    total_profit = 0
    initInvestment = 0  #to save the initial investment
    for i in range(5, len(prices)):
        average = (prices[i-5] + prices[i-4] + prices[i-3] + prices[i-2] + prices[i-1])/5   #calculate the average of the last 5 prices
        
        if (prices[i] > average and bought == False): #if the price is greater than the average and we havent bought yet, we buy
            if initInvestment == 0:  #if we havent bought yet, we save the initial investment
                initInvestment = prices[i]

            print("Buy at price: \t", prices[i]) #print the buy price
            buyprice = prices[i]
            bought = True  #we have bought, set flag to true

            #check if it is already sold (shortselling), an dif so, update the profit
            if sellprice != 0:
                profit = sellprice - buyprice
                print(f"Trade Profit: \t{profit:.2f}" )
                total_profit += profit #add the profit to the total profit
                sellprice = 0
                shortsold = False

            #check if it is the last day, and if so, print the buy signal
            if i == len(prices)-1:
                print("BUY this stock Today at: \t", prices[i])
        elif (prices[i] < average  and shortsold == False):  #if the price is less than the average and we have bought, we sell
            
            if buyprice != 0:
                print("Sell at price: \t", prices[i])
                profit = prices[i] - buyprice   #calculate the profit
                print(f"Trade Profit: \t{profit:.2f}" )
                total_profit += profit #add the profit to the total profit
                buyprice = 0
            else:
                sellprice = prices[i]
                print(f"Short Selling at : \t{sellprice:.2f}" )
                shortsold = True #we have sold, set flag to true

            #check if it is the last day, and if so, print the Sell signal
            if i == len(prices)-1:
                print("Sell this stock Today at: \t", prices[i])

    if initInvestment == 0:  #To avoid diving by zero problem
        returnrate = 0
    else:
        returnrate = total_profit/initInvestment * 100 #calculate the return rate
    print("Simple Moving Average Crossover Total profit: \t", total_profit)
    print("Simple Moving Average CrossoverReturn rate: \t", returnrate, '%')
    return total_profit, returnrate #return the total profit and the return rate

#method to calculate profit from the bolinger band strategy
'''
Please note that I am using the  standard deviation of the prices as the upper and lower band.
This gives a dynamic range of the prices that the strategy can work with, which helps with avoiding the frequent 
trading of the stocks which are too volatile or too stable for the fixed band
'''
def bolingerBandStrategy(prices):
    bought = False  #boolean to check if we have bought or not
    shortsold = False  #boolean to check if we have sold or not (To check short selling)
    buyprice = 0
    sellprice = 0
    total_profit = 0
    initInvestment = 0  #to save the initial investment
    for i in range(5, len(prices)):
        average = (prices[i-5] + prices[i-4] + prices[i-3] + prices[i-2] + prices[i-1])/5   #calculate the average of the last 5 prices
        std = np.std([prices[i-5], prices[i-4], prices[i-3], prices[i-2], prices[i-1]]) #calculate the standard deviation of the last 5 prices
        upper = average + (std ) #calculate the upper band
        lower = average - (std ) #calculate the lower band

        if (prices[i] > upper and bought == False): #if the price is greater than the upper band and we havent bought yet, we buy

            if initInvestment == 0:   #if we havent bought yet, we save the initial investment
                initInvestment = prices[i]

            print("Buy at price: \t", prices[i]) #print the buy price
            buyprice = prices[i]
            bought = True  #we have bought, set flag to true

            #check if it is already sold (shortselling), an dif so, update the profit
            if sellprice != 0:
                profit = sellprice - buyprice
                print(f"Trade Profit: \t{profit:.2f}" )
                total_profit += profit #add the profit to the total profit
                sellprice = 0
                shortsold = False

            #check if it is the last day, and if so, print the buy signal
            if i == len(prices)-1:
                print("BUY this stock Today at: \t", prices[i])

        elif (prices[i] < lower and shortsold == False):  #if the price is less than the lower band and we have bought, we sell
            
            if buyprice != 0:
                print("Sell at price: \t", prices[i])
                profit = prices[i] - buyprice   #calculate the profit
                print(f"Trade Profit: \t{profit:.2f}" )
                total_profit += profit #add the profit to the total profit
                buyprice = 0
            else:
                sellprice = prices[i]
                print(f"Short Selling at : \t{sellprice:.2f}" )
                shortsold = True #we have sold, set flag to true

            #check if it is the last day, and if so, print the Sell signal
            if i == len(prices)-1:
                print("Sell this stock Today at: \t", prices[i])


    if initInvestment == 0:  #To avoid diving by zero problem
        returnrate = 0
    else:
        returnrate = total_profit/initInvestment * 100 #calculate the return rate
    print("Bolinger Band Strategy Total profit: \t", total_profit)
    print("Bolinger Band Strategy Total Return rate: \t", returnrate, '%')
    return total_profit, returnrate #return the total profit and the return rate


#driver code
if __name__ == '__main__':

    print("final project")
    tickers = ["aapl",	"bbby",	"goog",	"adbe",	"car", "amc", "cvx","csco","bac","tsla"]

    #create a pandas dataframe to store the whoel data
    df = pd.DataFrame()
 
    #add date column to dataframe
    df['date'] = 0

    for ticker in tickers:
        print('Hold on, we are getting the data for ', ticker)
        d, p = get_stock_data(ticker)
        #save date only if its not already in the dataframe
        if ticker == 'aapl':
            df['date'] = d
        df[ticker] = p

        #THE FOLLOWING CODE IS WAIT ONE MINUTE TO AVOID THE API LIMITATION. This is not required for the assignment
        #This gives one minute timer so show the user that the program is not frozen
        if ticker ==  "car":
            print("\n\nBecause of wait limitation of the API, we need to wait another minute to get the data.. waiting..")
            for i in range(62):
                print(f"\rWaiting for {i} seconds", end = "")
                time.sleep(1)


    # call function to save the dataframe to a csv file
    save_data_as_csv(df)


    #For saving the results in json file, create a master dictionary to store the tickers
    masterDict = dict()
    #variable to store the most profitable ticker and stategy used
    mostProfitableTicker = ''
    mostProfitableStrategy = ''
    maxProfit = float('-inf')

    
    for t in tickers:
        print(f"\n\nNow Processing: {t} \n\n")
        localMaxprofit = float("-inf") #Negative infinity
        localBestStrategy = ''
        #create a dictionary to store the results for each ticker
        tickerDict = dict()
        #run the mean reversion strategy and save the results
        mean_revision_total_profit, mean_revision_returnrate = meanRevisionStrategy(df[t])
        if mean_revision_total_profit > localMaxprofit:
            localMaxprofit = mean_revision_total_profit
            localBestStrategy = 'Mean Reversion'

        #run the simple moving average crossover strategy and save the results
        simple_moving_avg_total_profit, simple_moving_avg_returnrate = simpleMovingAvgXover(df[t])
        if simple_moving_avg_total_profit > localMaxprofit:
            localMaxprofit = simple_moving_avg_total_profit
            localBestStrategy = 'Simple Moving Average Crossover'

        #run the bolinger band strategy and save the results
        bolinger_band_total_profit, bolinger_band_returnrate = bolingerBandStrategy(df[t])
        if bolinger_band_total_profit > localMaxprofit:
            localMaxprofit = bolinger_band_total_profit
            localBestStrategy = 'Bolinger Band'


        #find the most profitable strategy for this ticker
        print(f"Most Profitable Strategy for {t} is {localBestStrategy}")

        #find the most profitable ticker and strategy
        if localMaxprofit > maxProfit:
            maxProfit = localMaxprofit
            mostProfitableTicker = t
            mostProfitableStrategy = localBestStrategy


        #add the results to the dictionary
        tickerDict['mean_revision_total_profit'] = mean_revision_total_profit
        tickerDict['mean_revision_returnrate'] = mean_revision_returnrate
        tickerDict['simple_moving_avg_total_profit'] = simple_moving_avg_total_profit
        tickerDict['simple_moving_avg_returnrate'] = simple_moving_avg_returnrate
        tickerDict['bolinger_band_total_profit'] = bolinger_band_total_profit
        tickerDict['bolinger_band_returnrate'] = bolinger_band_returnrate


        #save the results in the master dictionary
        masterDict[t] = tickerDict

    #save the results in json file
    save_result_json(masterDict, 'results.json')

    #print the most profitable ticker and strategy
    print(f"\n\nMost Profitable Ticker is {mostProfitableTicker} with {mostProfitableStrategy} strategy. \n The total profit is {maxProfit} ")


