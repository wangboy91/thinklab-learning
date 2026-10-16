function maxProfit(prices: number[]): number {
    if (prices.length === 0) return 0;
    let minimum = prices[0], best = 0;
    for (let day = 1; day < prices.length; day++) {
        const profit = prices[day] - minimum;
        if (profit > best) best = profit;
        if (prices[day] < minimum) minimum = prices[day];
    }
    return best;
}
