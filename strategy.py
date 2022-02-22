# trading strategy
import math
import datetime

# --------------------------------------------------------------------------------------------------------------------
# constant
import pandas

alpha_g = 0.0
alpha_b = 0.0
r_i = [0.0126, 0.0213, 0.0249, 0.0167, 0.0123, 0.047]  # annual inflation rate, we currently assume same for all year
r = [0.0001, 0.0001, 0.0001, 0.0001, 0.0001,
     0.0001]  # annual continuous compounded interest rate, we assume same for all year
PERIOD = 30
START_DATE = datetime.date(2016, 9, 10)
N = 1826
INV_RATE = 0.5
# --------------------------------------------------------------------------------------------------------------------


def investment(fv, p, gold: bool, r) -> float:
    if gold:
        alpha = alpha_g
    else:
        alpha = alpha_b
    fv_product = fv * (1 - alpha)
    fv_money = p * math.exp(r * PERIOD / 365)
    # if fv_product * (1 - alpha) > fv_money:
    if fv_product > fv_money:
        return INV_RATE
    else:
        return 0  # do not invest


def redeem(maturity_value, p, days_from_inv: int, gold: bool, r) -> float:
    if gold:
        alpha = alpha_g
    else:
        alpha = alpha_b
    # forward
    fv_money = p * (1 - alpha) * math.exp(r * (PERIOD - days_from_inv) / 365)
    # reversed re-investment
    fv_money_ = p * math.exp(r * (PERIOD - days_from_inv) / 365)
    fv_inv = maturity_value * (1 - alpha)

    if fv_money > maturity_value:
        return INV_RATE
    elif fv_money_ < fv_inv:
        return -INV_RATE
    else:
        return 0


def transactions(portfolio, redeem_rate, investment_rate, p, days_from_inv, gold: bool) -> list:
    if gold and math.isnan(p):
        return portfolio  # if gold market is closed then no transactions
    if days_from_inv == PERIOD:  # mature date
        if redeem_rate > 0:
            print("error!!!!!!!!!!!")
        if investment_rate > 0:
            if gold:
                # k = (portfolio[1]+portfolio[0]/p)*investment_rate - portfolio[1]  # todo: double check formula
                k = (portfolio[0] + portfolio[1] * p * (1 - alpha_g)) * investment_rate * (1 - alpha_g) / p - portfolio[
                    1]
                # k positive means we invest such gold, negative means we redeem money
                portfolio[1] = portfolio[1] + k
                portfolio[0] = portfolio[0] - k * p / (1 - alpha_g)
            else:
                # k = (portfolio[2] + portfolio[0] / p) * investment_rate - portfolio[2]  # todo: double check formula
                k = (portfolio[0] + portfolio[2] * p * (1 - alpha_b)) * investment_rate * (1 - alpha_b) / p - portfolio[
                    2]
                # k positive means we invest such gold, negative means we redeem money
                portfolio[2] = portfolio[2] + k
                portfolio[0] = portfolio[0] - k * p / (1 - alpha_b)

        elif investment_rate <= 0:
            # deplit everything
            if gold:
                portfolio[0] = portfolio[0] + portfolio[1] * p * (1 - alpha_g)
                portfolio[1] = 0
            else:
                portfolio[0] = portfolio[0] + portfolio[2] * p * (1 - alpha_b)
                portfolio[2] = 0
        return portfolio

    # no deplete
    if gold:
        if investment_rate > 0:
            portfolio[1] = portfolio[1] + portfolio[0] * investment_rate * (
                        1 - alpha_g) / p  # exchange money to buy gold
            portfolio[0] = portfolio[0] - portfolio[0] * investment_rate
        elif redeem_rate > 0:
            portfolio[0] = portfolio[0] + portfolio[1] * redeem_rate * (1 - alpha_g) * p  # exchange gold to get money
            portfolio[1] = portfolio[1] - portfolio[1] * redeem_rate
        elif redeem_rate < 0:
            portfolio[0] = portfolio[0] + redeem_rate * portfolio[0]
            portfolio[1] = portfolio[1] - redeem_rate * portfolio[0] * (1 - alpha_g) / p
    else:
        if investment_rate > 0:
            portfolio[2] = portfolio[2] + portfolio[0] * investment_rate * (
                    1 - alpha_b) / p  # exchange bitcoin to buy gold
            portfolio[0] = portfolio[0] - portfolio[0] * investment_rate
        elif redeem_rate > 0:
            portfolio[0] = portfolio[0] + portfolio[2] * redeem_rate * (
                        1 - alpha_b) * p  # exchange bitcoin to get money
            portfolio[2] = portfolio[2] - portfolio[2] * redeem_rate
        elif redeem_rate < 0:
            portfolio[0] = portfolio[0] + redeem_rate * portfolio[0]
            portfolio[2] = portfolio[2] - redeem_rate * portfolio[0] * (1 - alpha_b) / p
    return portfolio


def worth(portfo, p_b, p_g) -> float:
    return portfo[0] + portfo[2] * p_b + portfo[1] * p_g


# --------------------------------------------------------------------------------------------------------------------
# read from csv
# prices = pandas.read_csv("files/bcgold.csv")


estimation = pandas.read_csv("files/ma_price.csv")
estimate_g = estimation['gold_ma' + str(PERIOD)].to_list()
estimate_b = estimation['bitcoin_ma' + str(PERIOD)].to_list()
price_g = estimation["gold_price"].to_list()
price_b = estimation["bitcoin_price"].to_list()
# main
# estimate_g = [1283.3, 1348.65,1254.5,1258.75,1326.1,1339.1]
# estimate_b = [615.65, 612, 609.62, 607.18, 612.08, 617.21]

inv_info_g = [PERIOD + 1, 0]  # [days from investment, maturity value]
inv_info_b = [PERIOD + 1, 0]
today = datetime.date(2016, 9, 11)
portfolio = [1000, 0, 0]  # $, G, B

risk_free_rate = []
for i in range(0, len(r)):
    risk_free_rate.append(r[i] - r_i[i])
redeem_gold = 0
redeem_bit = 0

for day in range(0, N):
    if today == datetime.date(2020,3,20):
        print("time")
    if today == datetime.date(2016,9,11):
        portfolio = transactions(portfolio, redeem_rate=0, investment_rate=0.3, p=price_b[day],
                                 days_from_inv=PERIOD+1, gold=False)
    if today == datetime.date(2016,9,12):
        portfolio = transactions(portfolio, redeem_rate=0, investment_rate=0.5, p=price_g[day],
                                 days_from_inv=PERIOD+1, gold=True)
    rate = risk_free_rate[today.year - 2016]
    if inv_info_g[0] >= PERIOD:
        invest_gold = investment(estimate_g[day], price_g[day], gold=True, r=rate)
    else:
        redeem_gold = redeem(inv_info_g[1], price_g[day], inv_info_g[0], gold=True, r=rate)
    if inv_info_b[0] >= PERIOD:
        invest_bit = investment(estimate_b[day], price_b[day], gold=False, r=rate)
    else:
        redeem_bit = redeem(inv_info_b[1], price_b[day], inv_info_b[0], gold=False, r=rate)
    if invest_gold > 0:
        inv_info_g[0] = 0
        inv_info_g[1] = estimate_g[day]
    if invest_bit > 0:
        inv_info_b[0] = 0
        inv_info_b[1] = estimate_b[day]
    # transactions, default gold first
    portfolio = transactions(portfolio, redeem_gold, invest_gold, p=price_g[day], days_from_inv=inv_info_g[0],
                             gold=True)
    portfolio = transactions(portfolio, redeem_bit, invest_bit, p=price_b[day], days_from_inv=inv_info_b[0], gold=False)
    a = worth(portfolio, price_g[day], price_b[day])
    print("today:", today, "    money on hand:", "{:.2f}".format(portfolio[0]), "dollars;    "
                                                                                "gold on hand:",
          "{:.2f}".format(portfolio[1]), "ounces;    ", "bitcoin on hand:",
          "{:.2f}".format(portfolio[2]), "bitcoins;", "     worth", "{:.2f}".format(a), "dollars", inv_info_b[0])

    today = today + datetime.timedelta(days=1)
    inv_info_g[0] = inv_info_g[0] + 1
    inv_info_b[0] = inv_info_b[0] + 1
    portfolio[0] = portfolio[0] * math.exp(rate / 365)

