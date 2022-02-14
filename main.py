from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import concurrent.futures

symbol = "SATU"
url = f"https://bvb.ro/FinancialInstruments/Details/FinancialInstrumentsDetails.aspx?s={symbol}"
driver = webdriver.Chrome()
driver.get(url)
delay = 2

def get_price(driver):
    global delay
    data = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,"/html/body/form/div[3]/div/div[1]/div[1]/div[2]/div[1]/div[2]/div[3]/div[1]/div/strong")))
    return float(data.text)

def get_cur_assets(driver):
    current_assets = None
    global delay
    try:
        # if type1

        if WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, """/html/body/form/div[3]/div/div[1]/div[3]/div/div[1]/div[1]/div/div/table/tbody/tr[4]/td[1]"""))).text == "Total Current Assets":
            current_assets = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,"""/html/body/form/div[3]/div/div[1]/div[3]/div/div[1]/div[1]/div/div/table/tbody/tr[4]/td[2]"""))).text
            #print(f"Current assets: {current_assets}.")
        # if type2

        if WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, """/html/body/form/div[3]/div/div[1]/div[3]/div/div[1]/div/div/div/table/tbody/tr[2]/td[1]"""))).text == "Current assets - Total":
            current_assets = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,"""/html/body/form/div[3]/div/div[1]/div[3]/div/div[1]/div/div/div/table/tbody/tr[2]/td[2]"""))).text
            #print(f"Current assets: {current_assets}.")
    except TimeoutException:
        print(f"Loading took too much time!")

    return int(current_assets.replace(",", ""))

def get_shares_outs(driver):
    global delay
    shares_outstanding = str()
    data = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, """/ html / body / form / div[3] / div / div[1] / div[3] / div / div[2] / div / div[5] / div / table / tbody / tr[1] /td[2]""")))
#convert txt to number and remove commas
    for item in data.text:
        if item.isdigit():
            shares_outstanding += item

    return int(shares_outstanding)

def get_st_liab(driver):
    total_st_liab = None
    rev_advance = None
    global delay
    try:

        # if type1
        if WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,
                                                                              """/html/body/form/div[3]/div/div[1]/div[3]/div/div[1]/div[1]/div/div/table/tbody/tr[10]/td[1]"""))).text == "Total Current Liabilities":
            total_st_liab = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,
                                                                                               """/html/body/form/div[3]/div/div[1]/div[3]/div/div[1]/div[1]/div/div/table/tbody/tr[10]/td[2]"""))).text
            # print(f"Shortterm liabilities: {total_st_liab}.")

        # if type2
        if WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,
                                                                              """/html/body/form/div[3]/div/div[1]/div[3]/div/div[1]/div/div/div/table/tbody/tr[3]/td[1]"""))).text == "Debtors - due within one year":
            total_st_liab = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,
                                                                                               """/html/body/form/div[3]/div/div[1]/div[3]/div/div[1]/div/div/div/table/tbody/tr[3]/td[2]"""))).text
            # print(f"Shortterm debt: {total_st_liab}.")

        # if revenue advance
        if WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,
                                                                              """/html/body/form/div[3]/div/div[1]/div[3]/div/div[1]/div/div/div/table/tbody/tr[7]/td[1]"""))).text == "Revenues in advance":
            rev_advance = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,
                                                                                             """/html/body/form/div[3]/div/div[1]/div[3]/div/div[1]/div/div/div/table/tbody/tr[7]/td[2]"""))).text
            # print(f"Revenue in advance: {rev_advance}.")

    except TimeoutException:
        print(f"Loading took too much time!")

    if rev_advance:
        try:
            return int(rev_advance.replace(",", "")) + int(total_st_liab.replace(",", ""))
        except ValueError:
            return int(total_st_liab.replace(",", ""))


def get_lt_liab(driver):

    total_lt_liab = None
    try:
        # if type1
        if WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,"""/html/body/form/div[3]/div/div[1]/div[3]/div/div[1]/div[1]/div/div/table/tbody/tr[15]/td[1]"""))).text == "Total Longterm Liabilities":
            total_lt_liab = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,"""/html/body/form/div[3]/div/div[1]/div[3]/div/div[1]/div[1]/div/div/table/tbody/tr[15]/td[2]"""))).text
            #print(f"Longterm liabilities: {total_lt_liab}.")

        # if type2
        if WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,"""/html/body/form/div[3]/div/div[1]/div[3]/div/div[1]/div/div/div/table/tbody/tr[6]/td[1]"""))).text == "Debtors - due after more than one year":
            total_lt_liab = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,"""/html/body/form/div[3]/div/div[1]/div[3]/div/div[1]/div/div/div/table/tbody/tr[6]/td[2]"""))).text
            #print(f"Longterm debt: {total_lt_liab}.")

    except TimeoutException:
        print(f"Loading took too much time!")
    if total_lt_liab.isnumeric() == False:
        return 0
    return int(total_lt_liab.replace(",", ""))


def get_financials(driver):
    price = get_price(driver)
    shares = get_shares_outs(driver)
    try:
        financial_tab = WebDriverWait(driver, delay).until(EC.presence_of_element_located(
            (By.XPATH, """/html/body/form/div[3]/div/div[1]/div[2]/div/div[1]/div/div/input[5]""")))
        financial_tab.click()
    except TimeoutException:
        print(f"Loading took too much time!")

    cur_assets = get_cur_assets(driver)
    st_liab = get_st_liab(driver)
    lt_liab = get_lt_liab(driver)

    return [price, shares, cur_assets, st_liab, lt_liab]

def compute_NNR(price, shares, cur_assets, st_liab, lt_liab):
    return round((((cur_assets - (st_liab + lt_liab)) / shares) / price) * 100 , 2)

# get symbols list
with open("symbols.txt", "r") as file:
    symbols = file.read().splitlines()


fin = get_financials(driver)
print(compute_NNR(fin[0],fin[1],fin[2],fin[3],fin[4]))

driver.quit()

