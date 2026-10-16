class Solution {
    public int maxProfit(int[] prices) {
        if (prices.length == 0) return 0;
        int minimum = prices[0], best = 0;
        for (int day = 1; day < prices.length; day++) {
            int profit = prices[day] - minimum;
            if (profit > best) best = profit;
            if (prices[day] < minimum) minimum = prices[day];
        }
        return best;
    }
}
