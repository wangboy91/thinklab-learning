def max_profit(prices: list[int]) -> int:
    if not prices:
        return 0
    minimum, best = prices[0], 0
    for day in range(1, len(prices)):
        profit = prices[day] - minimum
        if profit > best:
            best = profit
        if prices[day] < minimum:
            minimum = prices[day]
    return best
