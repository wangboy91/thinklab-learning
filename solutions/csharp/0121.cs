public class Solution {
    public int MaxProfit(int[] prices) {
        if (prices.Length == 0) return 0;
        int minimum = prices[0], best = 0;
        for (int day = 1; day < prices.Length; day++) {
            int profit = prices[day] - minimum;
            if (profit > best) best = profit;
            if (prices[day] < minimum) minimum = prices[day];
        }
        return best;
    }
}
