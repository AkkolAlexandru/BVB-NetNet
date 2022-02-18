from selenium import webdriver
from financials import get_financials, get_status

DEBUG_MODE = True
results = []

def compute_NNR(price, shares, cur_assets, st_liab, lt_liab):

    if price == None or shares == None or cur_assets == None or st_liab == None or lt_liab == None:
        return "N/A"
    else:
        return round((((cur_assets - (st_liab + lt_liab)) / shares) / price) * 100, 2)

def run_scraper(symbol):
    # init webdriver
    url = f"https://bvb.ro/FinancialInstruments/Details/FinancialInstrumentsDetails.aspx?s={symbol}"
    driver = webdriver.Chrome()
    driver.get(url)
    status = get_status(driver)

    # check if stock is listed
    if status != 'Tradeable':
        if DEBUG_MODE:
            print(f"{symbol} is delisted.")
        return {symbol: "Delisted"}

    # get financials
    fin = get_financials(driver)
    driver.quit()
    if fin is None:
        return {symbol:"N/A"}

    nnr = compute_NNR(fin[0],fin[1],fin[2],fin[3],fin[4])
    if DEBUG_MODE:
        print(f"[{symbol}] Price = {fin[0]}")
        print(f"[{symbol}] Shares = {fin[1]}")
        print(f"[{symbol}] Current assets = {fin[2]}")
        print(f"[{symbol}] ST Liabilities = {fin[3]}")
        print(f"[{symbol}] LT Liabilities = {fin[4]}")
        print(f"[{symbol}] NNR Ratio = {nnr}")
    return {symbol:nnr}

#read file
with open("symbols.txt", "r") as file:
    symbols = file.read().splitlines()

#final script run
for symbol in symbols:
    results.append(run_scraper(symbol))
    print(results)





