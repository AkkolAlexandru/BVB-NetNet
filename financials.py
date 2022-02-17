from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

DEBUG_MODE_FINANCIALS = True
delay = 2

def get_status(driver):
    status = None
    try:
        status = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, """//td[contains(.,'Status:')]/following::td/span"""))).text
        if DEBUG_MODE_FINANCIALS:
            print(f"status:{status}")
    except TimeoutException:
        print(f"Cannot find status")

    return status

def get_price(driver):
    global delay
    data = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,"/html/body/form/div[3]/div/div[1]/div[1]/div[2]/div[1]/div[2]/div[3]/div[1]/div/strong")))

   #Exceptions
    if data.text == None:
        print("price error")
        return None
    try:
        if data.text[0].isnumeric() == False:
            print("Price is not numeric")
            return None
    except IndexError:
        print("price error")
        return None

    return float(data.text)

def get_cur_assets(driver):
    find = None
    global delay
    try:
        find = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, """//td[contains(.,'Total Current Assets')]/following::td"""))).text
    except TimeoutException:
        try:
            find = WebDriverWait(driver, delay).until(EC.presence_of_element_located(
                (By.XPATH, """//td[contains(.,'Current assets - Total')]/following::td"""))).text
        except TimeoutException:
            try:
                find = WebDriverWait(driver, delay).until(EC.presence_of_element_located(
                    (By.XPATH, """//td[contains(.,'Cash')]/following::td"""))).text
            except TimeoutException:
                return None

    return int(find.replace(",", ""))

def get_shares_outs(driver):
    global delay
    shares_outstanding = str()
    data = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, """/ html / body / form / div[3] / div / div[1] / div[3] / div / div[2] / div / div[5] / div / table / tbody / tr[1] /td[2]""")))
    #convert txt to number and remove commas
    for item in data.text:
        if item.isdigit():
            shares_outstanding += item

    #Exceptions
    if shares_outstanding == None:
        print("shares outstanding error")
        return None
    return int(shares_outstanding)

def get_st_liab(driver):
    global delay
    t_st_liab = str()
    debtors = None
    rev_advance = None

    # scraping block
    try:
        t_st_liab = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.XPATH, """//td[contains(.,'Total Current Liabilities')]/following::td"""))).text
    except TimeoutException:
        try:
            debtors = WebDriverWait(driver, delay).until(
                EC.presence_of_element_located(
                    (By.XPATH, """//td[contains(.,'Debtors - due within one year')]/following::td"""))).text
        except TimeoutException:
            debtors = 0

    try:
        rev_advance = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located(
                (By.XPATH, """//td[contains(.,'Revenues in advance')]/following::td"""))).text
    except TimeoutException:
        rev_advance = 0

    if t_st_liab:
        t_st_liab = t_st_liab.replace(",", "")
    if debtors:
        debtors = debtors.replace(",", "")
    if rev_advance:
        rev_advance = rev_advance.replace(",", "")

    if DEBUG_MODE_FINANCIALS:
        print(f"t_st_liab: {t_st_liab}")
        print(f"debtors: {debtors}")
        print(f"rev_advance: {rev_advance}")

    if t_st_liab:
        if t_st_liab[0].isnumeric() is False:
            if debtors or rev_advance:
                return int(rev_advance) + int(debtors)
            else:
                return None
    else:
        if debtors or rev_advance:
            if rev_advance[0].isnumeric():
                return int(rev_advance) + int(debtors)
            else:
                return int(debtors)
        else:
            return None


    return int(t_st_liab)

def get_lt_liab(driver):

    total_lt_liab = None
    try:
        total_lt_liab = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located(
                (By.XPATH, """//td[contains(.,'Total Longterm Liabilities')]/following::td"""))).text
    except TimeoutException:
        try:
            total_lt_liab = WebDriverWait(driver, delay).until(
                EC.presence_of_element_located(
                    (By.XPATH, """//td[contains(.,'Debtors - due after more than one year')]/following::td"""))).text
        except TimeoutException:
            return None

    if total_lt_liab:
        total_lt_liab = total_lt_liab.replace(",", "")

    if DEBUG_MODE_FINANCIALS:
        print(f"total_lt_liab: {total_lt_liab}")

    return int(total_lt_liab)

#todo test
def alternative_Total_Liab(driver):
    alt_total_liab = None
    try:
        alt_total_liab = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located(
                (By.XPATH, """//td[contains(.,'Total liabilities')]/following::td"""))).text
    except TimeoutException:
        try:
            alt_total_liab = WebDriverWait(driver, delay).until(
                EC.presence_of_element_located(
                    (By.XPATH, """//td[contains(.,'Total Liabilities')]/following::td"""))).text
        except TimeoutException:
            return None

    if alt_total_liab:
        alt_total_liab = alt_total_liab.replace(",", "")

    if DEBUG_MODE_FINANCIALS:
        print(f"alt_total_liab: {alt_total_liab}")

    return int(alt_total_liab)

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
