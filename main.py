# buy and sell strategy rough copy
import math


alpha_g = 0.01
alpha_b = 0.02
r = 0.01  # annual continuous compounded interest rate, we assume same for all year
r_i = 0.02  # annual inflation rate, we currently assume same for all year
LONG_TERM = 180
MID_TERM = 30
SHORT_TERM = 7
LONG_INV_INDEX = 0.1


def price_vs_longInv(p: float, CI_long: list, p_0: float, n:int, gold: bool) -> float:
    """
    n: how many days from our first day of long term investment
    :param p: price of the product (gold/bitcoin) at t=n (today)
    :param CI_long: long term investment confidence interval
    :param p_0: price of the product (gold/bitcoin) at t=0 (first day of 180 investment)
    :return: percentage that tells you how much should you redeem, negative if not redeem, redeem all
    if greater than 1
    """
    k = 180  # we now assume long term investment = 180 days investment.
    #  we use 1 once to calculate the real money, and compare
    future_upper = p_0*CI_long[1]
    future_lower = p_0*CI_long[0]
    if gold:
        future_p = p*(1-alpha_g)*math.exp((r-r_i)*(k-n)/365)
    else:
        future_p = p * (1 - alpha_b) * math.exp((r - r_i) * (k - n) / 365)
    return (future_p-future_lower)/(future_upper-future_lower)


def long_term_inv(date_from_last_investment: int, upper:float, lower:float, gold:bool) -> float:
    """
    if already invested, do not invest until this investment ends
    :return: float, percentage to invest this product
    """
    # if we already invested in the last 180 days, we do not invest again.
    if date_from_last_investment < LONG_TERM:
        return 0
    if gold:
        alpha = alpha_g
    else:
        alpha = alpha_b
    if lower*(1-alpha) > 1:
        return LONG_INV_INDEX


def mid_term_inv(date_from_last_investment: int, upper: float, lower: float, gold: bool) -> float:
    """
    if already invested, do not invest until this investment ends
    :param upper:
    :param lower:
    :return: pct to invest this product
    """
    if date_from_last_investment < MID_TERM:
        return 0
    if gold:
        alpha = alpha_g
    else:
        alpha = alpha_b

    if upper*(1-alpha) <= 1:
        return 0
    elif lower*(1-alpha) >= 1:
        return 1
    else:
        return (upper*(1-alpha)-1)/(upper*(1-alpha)-lower*(1-alpha))


def short_term_inv(upper_mid: float, lower_mid: float,
                   r: float, p_0: float, p: float, date_from_last_invest: int, gold: bool) -> float:
    """
    :param upper_mid:
    :param lower_mid:
    :param upper_short:
    :param lower_short:
    :return:
    """
    # consider redeem to money
    if gold:
        future_p = p * (1 - alpha_g) * math.exp(r * (MID_TERM - date_from_last_invest) / 365)
    else:
        future_p = p * (1 - alpha_b) * math.exp(r * (MID_TERM - date_from_last_invest) / 365)
    if future_p > upper_mid*p_0:
        return 1  # sell all
    elif future_p < lower_mid*p_0:
        return -1  # buy all half
    return 0


def product_exchange(upper_g, lower_g, upper_b, lower_b, p_g, p_b) -> float:
    # first, consider sell gold to buy bitcoin
    future_lower_b = p_g*(1-alpha_g)*(1-alpha_b)*lower_b
    future_upper_g = p_g*upper_g
    if future_lower_b>future_upper_g:
        return 0.5
    # consider sell bitcoin to buy gold
    future_upper_b = p_b*upper_b
    future_lower_g = p_b*(1-alpha_b)*(1-alpha_g)*lower_g
    if future_lower_g > future_upper_b:
        return -0.5


def update_portfolio(portfolio: list, gold_dir: list, bit_dir: list, exchange: float, price_g, price_b) -> list:
    """
    defualt buy long term first, default buy gold first
    :param portfolio:
    :param gold_dir:
    :param bid_dir:
    :param exchange:
    :return:
    """
    # long term
    # transaction of gold, portfolio[1] saves n onces of gold
    if gold_dir[2] < 0:
        portfolio[1] = portfolio[0]*gold_dir[0]*(1-alpha_g)/price_g
        portfolio[1] = portfolio[0] * gold_dir[1] * (1 - alpha_g) / price_g

    if bit_dir[2] < 0:
        portfolio[2] = portfolio[0]*bit_dir[0]*(1-alpha_b)/price_b
        portfolio[2] = portfolio[0]*bit_dir[1]*(1-alpha_b)/price_b

    if gold_dir[2] < 0:
        portfolio[1] = portfolio[0]*(-1*gold_dir[2])*(1-alpha_g)/price_g
    else:
        portfolio[0] = portfolio[1]*gold_dir[2]*(1-alpha_g)*price_g

    # bitcoin short term
    if bit_dir[2] < 0:
        portfolio[1] = portfolio[0]*(-1*gold_dir[2])*(1-alpha_g)/price_g
    else:
        portfolio[0] = portfolio[1]*gold_dir[2]*(1-alpha_g)*price_g
    # short term




if __name__ == '__main__':
    upper_long = [0,0,0,1,2,3,4,6,7,9]
    lower_long = [0,0,0,0.1,2,3,4,5,6]
    upper_mid = [0, 0, 0, 1, 2, 3, 4, 6, 7, 9]
    lower_mid = [0, 0, 0, 0.1, 2, 3, 4, 5, 6]
    upper_short = [0, 0, 0, 1, 2, 3, 4, 6, 7, 9]
    lower_short = [0, 0, 0, 0.1, 2, 3, 4, 5, 6]
    gold_price = [1,2,3,4]
    bitcoin_price = [1,2,3,4]
    n = 1826
    k = 0
    y = 1 # which year are we in
    portfolio = [1000, 0, 0]
    days_from_last_long_gold = 180
    days_from_last_long_bit = 180
    days_from_last_mid_gold = 30
    days_from_last_mid_bit = 30

    for day in range(0, n-1):
        # consider long term investment
        long_pct_g = long_term_inv(days_from_last_long_gold, upper_long[day], lower_long[day], gold=True)
        if long_pct_g > 0:
            days_from_last_long_gold = 0
        else:
            days_from_last_long_gold += 1

        long_pct_b = long_term_inv(days_from_last_long_bit, upper_long[day], lower_long[day], gold=False)
        # todo: set upper and lower for bitcoin
        if long_pct_b > 0:
            days_from_last_long_bit = 0
        else:
            days_from_last_long_bit += 1

        # mid term investment
        mid_pct_g = mid_term_inv(days_from_last_mid_gold, upper_mid[day], lower_mid[day], gold=True)
        if mid_pct_g > 0:
            days_from_last_mid_gold = 0
        else:
            days_from_last_mid_gold += 1
        mid_pct_b = mid_term_inv(days_from_last_mid_bit, upper_mid[day], lower_mid[day], gold=False)
        if mid_pct_b > 0:
            days_from_last_mid_bit = 0
        else:
            days_from_last_mid_bit += 1

        # short term investment
        if days_from_last_mid_gold < 30:
            short_pct_g = short_term_inv(upper_mid[day-days_from_last_mid_gold], lower_mid[day-days_from_last_mid_gold],
                                       r[y] - r_i[y], p_0=gold_price[day-days_from_last_mid_gold],
                                       p = gold_price[day], date_from_last_invest = days_from_last_mid_gold,
                                       gold=True)
            short_pct_b = short_term_inv(upper_mid[day - days_from_last_mid_bit],
                                         lower_mid[day - days_from_last_mid_bit],
                                         r[y] - r_i[y], p_0=bitcoin_price[day - days_from_last_mid_bit],
                                         p=bitcoin_price[day], date_from_last_invest=days_from_last_mid_bit,
                                         gold=False)

            if short_pct_g == 0 or short_pct_b == 0:
                pct_exchange = product_exchange(upper_long[day], upper_short[day], upper_long[day], upper_short[day],
                                                gold_price[day], bitcoin_price[day])
        gold_dir = [long_pct_g, mid_pct_g, short_pct_g]
        bit_dir = [long_pct_b, mid_pct_b, short_pct_b]
        portfolio = update_portfolio(gold_dir, bit_dir, pct_exchange)
        value = worth()

