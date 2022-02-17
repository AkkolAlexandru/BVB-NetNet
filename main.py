from selenium import webdriver
from financials import get_financials

def compute_NNR(price, shares, cur_assets, st_liab, lt_liab):
    # TODO remove this
    print(st_liab, type(st_liab))
    if price == None or shares == None or cur_assets == None or st_liab == None or lt_liab == None:
        return "N/A"
    else:
        return round((((cur_assets - (st_liab + lt_liab)) / shares) / price) * 100, 2)

# get symbols list
with open("symbols.txt", "r") as file:
    symbols = file.read().splitlines()

#TODO
symbol="mecp"
############
url = f"https://bvb.ro/FinancialInstruments/Details/FinancialInstrumentsDetails.aspx?s={symbol}"
driver = webdriver.Chrome()
driver.get(url)


if get_status(driver) != 'Tradeable':
    print(get_status(driver))
    return {symbol:"delisted"}

fin = get_financials(driver)
print()





