---
title: "Coding Trend Factor"
subtitle: "From Paper to Python: Implementing a High-Performing Factor from Academic Research"
date: 2025-02-07
author: Quantitativo
source_url: https://www.quantitativo.com/p/coding-trend-factor
tags:
  - code
  - trend-following
  - trading strategy
audience: everyone
wordcount: 2164
fetched_at: 2026-05-18
---

# Coding Trend Factor

[![](https://substackcdn.com/image/fetch/$s_!qYDk!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Febac90b6-c47f-4d96-a7af-3757d86306c4_1400x934.png)](https://substackcdn.com/image/fetch/$s_!qYDk!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Febac90b6-c47f-4d96-a7af-3757d86306c4_1400x934.png)

# The idea

> **"Every great developer you know got there by solving problems they were unqualified to solve until they actually did it."** — Patrick McKenzie.

Patrick McKenzie is a well-known software developer, entrepreneur, and writer, widely recognized for his work in the software industry, particularly in bootstrapped startups and software-as-a-service (SaaS) businesses.

He built his entire career around **sharing everything he learned**, and his blog posts and tweets are often cited as **must-reads for software entrepreneurs**.

His quote about developers solving problems for which they were initially unqualified reflects a fundamental truth in programming—many great developers learn by doing rather than waiting until they are "ready.”

This week, I will share the implementation of the paper "[A Trend Factor: Any Economic Gains from Using Information Over Investment Horizons?](https://www.sciencedirect.com/science/article/abs/pii/S0304405X16301271)" from Yufeng Han, Guofu Zhou, and Yingzi Zhu. This paper was published in the Journal of Financial Economics (2016).

Before we dive into the paper's code, let me share a bit about the why and the how. The why is basically two reasons. First, I love implementing papers. I think by coding classic ideas, new ideas can emerge. Second, I believe these implementations might help other people who like studying. After all, sharing code implementations is the #1 ask I have received from the +3,500 readers in these past 8 months.

Now, to the how. I will share paper implementations and suggestions I find interesting. Every week, I receive many suggestions. And I read a lot of papers. The code I share here will be written in Python. I also like to code in C++, but I believe Python is more suitable for what I intend to write. I plan to share some implementations for free (like this one); I intend to put others on a larger course I want to launch. More on that later.

Finally, I love how the Gitbook platform works: it's great for creating and sharing code documentation and looks beautiful. In particular, I believe they do a much better job as a code-sharing platform than Substack. Therefore, I will share the implementations on both platforms: here and [Gitbook](https://tutorials.quantitativo.com/momentum-and-trend-following/a-trend-factor). If you are like me, you'll prefer [Gitbook](https://tutorials.quantitativo.com/momentum-and-trend-following/a-trend-factor).

# **Why implement this paper?**

The idea to write about this paper first appeared when I read another paper: “[Design Choices, Machine Learning, and the Cross-section of Stock Returns](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5031755)” by Minghui Chen, Matthias X. Hanauer, and Tobias Kalsbach. The suggestion to read this came from one of  's great [weekly recaps](https://www.quantseeker.com/p/weekly-recap-de9?utm_source=publication-search).

There, I found this table on page 33:

[![](https://substackcdn.com/image/fetch/$s_!dPVa!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F89eb518d-bdb1-4d9b-b85f-07db729575fb_2048x1685.png)](https://substackcdn.com/image/fetch/$s_!dPVa!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F89eb518d-bdb1-4d9b-b85f-07db729575fb_2048x1685.png)

The most important features, according to the paper

Figure 6 also illustrates the same point:

[![](https://substackcdn.com/image/fetch/$s_!2FwC!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fcdbcaf13-e662-42c5-88d9-1e866089bf7d_1630x1950.png)](https://substackcdn.com/image/fetch/$s_!2FwC!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fcdbcaf13-e662-42c5-88d9-1e866089bf7d_1630x1950.png)

The most important features, according to the paper

The table and the chart showed this TrendFactor feature as one of the most important predictors in the model. Looking at the references, I discovered that this feature was introduced in the paper "[A Trend Factor: Any Economic Gains from Using Information Over Investment Horizons?](https://www.sciencedirect.com/science/article/abs/pii/S0304405X16301271)" by Yufeng Han, Guofu Zhou, and Yingzi Zhu, published in the Journal of Financial Economics (2016).

Unlike previous studies that examine short-term reversals (daily/monthly), momentum (6-12 months), and long-term reversals (3-5 years) separately, the authors construct a **single factor** that incorporates **all three price trends** using moving averages over different time horizons.

In the paper, the authors report that the **trend factor** earns an **average return of 1.63% per month**, significantly higher than short-term reversal (0.79%), momentum (0.79%), and long-term reversal (0.34%). It **more than doubles the Sharpe ratios** of existing factors.

During the **2007-2009 financial crisis**, the trend factor earned **+0.75% per month**, while:

- The **market lost -2.03% per month**.
- The **momentum factor lost -3.88% per month**.
- The **short-term reversal factor lost -0.82% per month**.
- The **long-term reversal factor barely gained 0.03%**.

Let's dive into the implementation. You can continue reading here or [head to Gitbook](https://tutorials.quantitativo.com/momentum-and-trend-following) for a better reading experience.

## **Data**

The study **uses daily stock prices from January 2, 1926, to December 31, 2014**, obtained from the **Center for Research in Security Prices (CRSP)**.

Our replication will use daily stock prices from January 1, 1990, to January 1, 2025, obtained from Norgate data. Norgate provides high-quality survivorship bias-free daily data for the US stock market that is very affordable. For more information on how to acquire a Norgate data subscription, please check the [Norgate website](https://norgatedata.com/).

The paper explains that to compute the trend factor, monthly moving average signals are calculated at the **end of each month**. So, first, let's create a `fullcalendar` variable, which is a [Pandas DatetimeIndex](https://pandas.pydata.org/docs/reference/api/pandas.DatetimeIndex.html) that holds the last trading day of each month:

[![](https://substackcdn.com/image/fetch/$s_!APPP!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fac69a37d-38c2-4b50-a015-52e4c25595f7_1562x338.png)](https://substackcdn.com/image/fetch/$s_!APPP!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fac69a37d-38c2-4b50-a015-52e4c25595f7_1562x338.png)

Now, let's see what the paper says about the stock universe:

- The dataset includes **all domestic common stocks** listed on NYSE, AMEX and NASDAQ;
- The dataset excludes Close-end funds, REITs, unit trusts, ADRs and foreign stocks;
- **Price Filter**: Stocks with prices **below $5** at the end of each month are excluded;
- **Size Filter**: Stocks in the **smallest decile** (based on NYSE breakpoints) are excluded.

These filters are applied to **reduce noise and ensure liquidity**, following the methodology used in **Jegadeesh & Titman (1993)** for constructing momentum strategies.

We will implement something close: we will only consider Russell 3000 current & past constituents. That should address the first, second, and last bullets above. Considering stocks only when they were part of the index also ensures we are not adding survivorship bias. Finally, we will exclude stocks whenever their unadjusted closing price is below $5. Here's how that translates into code for a given `symbol`:

[![](https://substackcdn.com/image/fetch/$s_!xm7x!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F122780ab-f92c-435a-8fe2-bf6d32ead538_1560x1172.png)](https://substackcdn.com/image/fetch/$s_!xm7x!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F122780ab-f92c-435a-8fe2-bf6d32ead538_1560x1172.png)

Now, let's compute the moving averages (trend signals). Moving averages are computed at the **end of each month** using stock prices over different lag lengths. The moving average (MA) for stock *j* with lag *L* at month *t* is defined as:

where $P\_{j,d}$ (I know, this is not good… but Substack does not support inline LaTex… but Gitbook does, [check it out](https://tutorials.quantitativo.com/momentum-and-trend-following)) is the closing price for stock *j* on the last trading day *d* of month *t*, and *L* is the lag length. Then, we normalize the moving average prices by the closing price on the last trading day of the month:

This ensures stationarity and prevents biases from high-priced stocks.

The paper considers MAs of lag lengths 3-, 5-, 10-, 20-, 50-, 100-, 200-, 400-, 600-, 800- and 1,000-days. Let's see how this translates into code:

[![](https://substackcdn.com/image/fetch/$s_!ARnV!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F444a71a7-1975-48cd-a7dd-b0f3bda71a06_1560x176.png)](https://substackcdn.com/image/fetch/$s_!ARnV!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F444a71a7-1975-48cd-a7dd-b0f3bda71a06_1560x176.png)

We are getting to the final steps of the data-gathering stage. Now, we must add the target variable that will be used to predict the monthly expected stock returns cross-sectionally.

In other words, we must compute the next month return for every date:

1. First, we gather the prices from a given symbol;
2. Next, we compute the normalized MAs for all lags;
3. Then, we select only the last day of every month and compute the next month's return;
4. Finally, we apply the size/price filters.

We already did (1), (2) and (4). Now, let's see how to do (3):

[![](https://substackcdn.com/image/fetch/$s_!sHv_!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F7c02675b-e2e2-4506-8fde-4544fd2b9546_1560x254.png)](https://substackcdn.com/image/fetch/$s_!sHv_!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F7c02675b-e2e2-4506-8fde-4544fd2b9546_1560x254.png)

It's important to observe the correct use of the `.shift(x)` operator.

> `.shift(1)` gets the previous value, while `.shift(-1)` gets the next value. Messing with these operators is a common source of error in many quant codebases found online.

So, when we run `(df['Close'] / df['Close'].shift(1) - 1)` , we are computing the current month's return. After that, when we apply `.shift(-1)` , this results in the next month's return, which is exactly what we need.

Now, let's put everything together into a method that retrieves data for a given symbol:

[![](https://substackcdn.com/image/fetch/$s_!9swj!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F101bd8ea-87bd-4638-9ae4-2570bd3325e5_1562x1772.png)](https://substackcdn.com/image/fetch/$s_!9swj!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F101bd8ea-87bd-4638-9ae4-2570bd3325e5_1562x1772.png)

The last few lines organize the columns and the index. The index, in particular, is organized in a Multi-level indexing, which is a great Pandas feature to work with higher dimensional data. To more information about MultiIndex / advanced indexing, please check [Pandas documentation](https://pandas.pydata.org/docs/user_guide/advanced.html).

Let's see the data from the past 12 months of AAPL by running `get_data('AAPL').tail(12)` :

[![](https://substackcdn.com/image/fetch/$s_!rcLS!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fb6d2dc78-01ca-4e35-b6a0-c4e030278f8e_1960x678.png)](https://substackcdn.com/image/fetch/$s_!rcLS!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fb6d2dc78-01ca-4e35-b6a0-c4e030278f8e_1960x678.png)

Data from the past 12 months of AAPL

We can now gather data for all stocks in the **Russell 3000 universe**:

[![](https://substackcdn.com/image/fetch/$s_!pVGb!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F5ae35ba3-a906-4502-871d-777dd1120bf4_1560x374.png)](https://substackcdn.com/image/fetch/$s_!pVGb!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F5ae35ba3-a906-4502-871d-777dd1120bf4_1560x374.png)

The data DataFrame is a table with approximately 800k rows and 12 columns that looks like this:

[![](https://substackcdn.com/image/fetch/$s_!m4XH!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Ffa6261f3-94f3-40e9-94f2-20151535a3fa_1976x742.png)](https://substackcdn.com/image/fetch/$s_!m4XH!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Ffa6261f3-94f3-40e9-94f2-20151535a3fa_1976x742.png)

DataFrame ready to compute the trend factors

Great! We are ready to move to the next step: compute the trend factors. It's important to highlight how the data is organized:

- In the first level of our index, we have the last day of each month;
- In the second level of our index, we have all stocks in our universe for that particular date;
- In the columns, we have the MAs computed with the prices up until that specific date for that specific stock, and the next month return for that particular stock.

## **Step 1: Cross-sectional regressions**

To predict the monthly expected stock returns cross-sectionally, we use a two-step procedure. In the first step, we run in each month t*t* a cross-section regression of stock returns on observed normalized MA signals to obtain the time-series of the coefficients on the signals:

where:

- $r\_{j,t}=$ return on stock *j* in month *t*
- $\tilde{A}\_{j,t-1,L\_i}=$ trend signal at the end of month *t−1* on stock *j* with lag $L\_i$
- $\beta\_{i,t}=$ coefficient of the trend signal with lag $L\_i$ in month *t*
- $\beta\_{0,t}=$ intercept in month *t*

To do the regressions, we will use Python's [Statsmodels package](https://www.statsmodels.org/stable/index.html). We loop through all dates, doing the cross-sectional regressions:

[![](https://substackcdn.com/image/fetch/$s_!8CaF!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F65fc24b9-4e93-447d-a631-3ee6a0995c65_1558x574.png)](https://substackcdn.com/image/fetch/$s_!8CaF!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F65fc24b9-4e93-447d-a631-3ee6a0995c65_1558x574.png)

The code above is straightforward. It produces the coefs DataFrame, a table with close to 400 rows and 12 columns with all \beta\_{i,t} coefficients:

[![](https://substackcdn.com/image/fetch/$s_!gbA3!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Ff80442df-a9cc-463d-b80b-29a28b12eea5_1878x634.png)](https://substackcdn.com/image/fetch/$s_!gbA3!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Ff80442df-a9cc-463d-b80b-29a28b12eea5_1878x634.png)

Coefficients of the trend signals

> The paper has the following important sentence: "It should be noted that only information in month ttt or prior is used above to regress returns in month *t*." This is what the `.shift(1)` operator in the last line of the last code block is for. Omitting that code would result in lookahead bias and results too good to be true.

## Step 2: Expected returns

We estimate the expected return for month *t+1* from

where $E\_t[r\_{j,t+1}]$ is our forecasted expected return on stock *j* for month *t+1* and $E\_t[\beta\_{i,t+1}]$ is the estimated expected coefficient of the trend signal with lag $L\_i$ and is given by

which is the average of the estimated loadings on the trend signals over the past 12 months.

First, let's compute the matrix $E\_t[\beta\_{i,t+1}]$:

[![](https://substackcdn.com/image/fetch/$s_!7hE-!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F326ba0ec-858d-49d2-9aa6-82961064a996_1554x140.png)](https://substackcdn.com/image/fetch/$s_!7hE-!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F326ba0ec-858d-49d2-9aa6-82961064a996_1554x140.png)

[![](https://substackcdn.com/image/fetch/$s_!CoSn!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F16074d28-2e2d-46fe-8f52-004544d4c5da_1700x634.png)](https://substackcdn.com/image/fetch/$s_!CoSn!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F16074d28-2e2d-46fe-8f52-004544d4c5da_1700x634.png)

Estimated expected coefficients of the trend signals

Note that we do not include an intercept above because it is the same for all stocks in the same cross-section regression, and thus it plays no role in ranking the stocks.

## **Trend factor**

Now, we are ready to construct the trend factor. We loop through all dates, performing the dot product between the estimated expected coefficients of the trend signals and the trend signals matrices:

[![](https://substackcdn.com/image/fetch/$s_!znrD!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F6db6ab78-3143-4fbb-a528-8f7a4b90ed8f_1562x620.png)](https://substackcdn.com/image/fetch/$s_!znrD!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F6db6ab78-3143-4fbb-a528-8f7a4b90ed8f_1562x620.png)

And that's all there is to it. We get the following table, with approximately 800k rows and 4 columns:

[![](https://substackcdn.com/image/fetch/$s_!ZLlQ!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F8fb83bbc-68ad-4ac8-bc75-8103c0538b1e_914x632.png)](https://substackcdn.com/image/fetch/$s_!ZLlQ!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F8fb83bbc-68ad-4ac8-bc75-8103c0538b1e_914x632.png)

Trend factors for every symbol-date pair

In our last step, we sort all stocks into five portfolios by their expected returns. The portfolios are equal-weighted and rebalanced every month. The return difference between the quintile portfolio of the highest expected returns and the quintile portfolio of the lowest is defined as the return on the trend factor. Intuitively, the trend factor buys stocks that are forecasted to yield the highest expected returns (Buy High) and shorts stocks that are forecasted to yield the lowest expected returns (Sell Low).

Adding the quantiles is straightforward:

[![](https://substackcdn.com/image/fetch/$s_!yCFD!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F9706b7ee-1f6c-47f9-a376-450db6b2a53e_1558x336.png)](https://substackcdn.com/image/fetch/$s_!yCFD!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F9706b7ee-1f6c-47f9-a376-450db6b2a53e_1558x336.png)

The code above produces the following table:

[![](https://substackcdn.com/image/fetch/$s_!k1il!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fff3e9a0e-da26-4bbb-a643-d01142c3d9c1_1170x632.png)](https://substackcdn.com/image/fetch/$s_!k1il!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fff3e9a0e-da26-4bbb-a643-d01142c3d9c1_1170x632.png)

Trend factor quantiles

Now, we group by date:

[![](https://substackcdn.com/image/fetch/$s_!nvOZ!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fdad3d98f-2632-4e35-9f35-4eec4790147c_1556x338.png)](https://substackcdn.com/image/fetch/$s_!nvOZ!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fdad3d98f-2632-4e35-9f35-4eec4790147c_1556x338.png)

The rets DataFrame has the monthly returns and the number of stocks from each quantile, as we can see below:

[![](https://substackcdn.com/image/fetch/$s_!4cna!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F13586477-527d-4b47-8924-a5f82542b06b_1218x734.png)](https://substackcdn.com/image/fetch/$s_!4cna!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F13586477-527d-4b47-8924-a5f82542b06b_1218x734.png)

Final results

# Visualizing the results

Finally, we can plot the return of the trend factor:

[![](https://substackcdn.com/image/fetch/$s_!RbGX!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F813f3f45-f4ad-4916-aa0f-1cde9cd82286_1562x182.png)](https://substackcdn.com/image/fetch/$s_!RbGX!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F813f3f45-f4ad-4916-aa0f-1cde9cd82286_1562x182.png)

Looking at this equity curve, we see that the factor performs until 2016. After that, it's basically flat. If we reduce the exposure on the shorts to 0.5 instead of 1, we can get a better equity curve.

Adding a bit of formatting, we get the following:

[![](https://substackcdn.com/image/fetch/$s_!-6kJ!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fe0093bd2-f0a9-4ebc-a9d0-c31f1da0d423_1536x1472.png)](https://substackcdn.com/image/fetch/$s_!-6kJ!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fe0093bd2-f0a9-4ebc-a9d0-c31f1da0d423_1536x1472.png)

TrendFactor equity curve

[![](https://substackcdn.com/image/fetch/$s_!bKn4!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa2a7ef91-cacb-4921-bd19-bf8c1ab87662_1074x940.png)](https://substackcdn.com/image/fetch/$s_!bKn4!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa2a7ef91-cacb-4921-bd19-bf8c1ab87662_1074x940.png)

Summary of backtest statistics

We can also see the average return per quantile:

[![](https://substackcdn.com/image/fetch/$s_!v35g!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F3050480b-bd7f-4059-897a-4286102b2b61_1978x1250.png)](https://substackcdn.com/image/fetch/$s_!v35g!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F3050480b-bd7f-4059-897a-4286102b2b61_1978x1250.png)

Returns for each quantile

And finally, we can see the monthly and annual returns:

[![](https://substackcdn.com/image/fetch/$s_!iN9I!,w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F46b6f4e6-c493-40a7-a165-5032ff5c941c_1412x1628.png)](https://substackcdn.com/image/fetch/$s_!iN9I!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F46b6f4e6-c493-40a7-a165-5032ff5c941c_1412x1628.png)

Monthly and annual returns

## **Conclusion**

This paper introduces a **trend factor** that synthesizes short-, intermediate-, and long-term price trends using moving averages, significantly outperforming traditional factors like **momentum, short-term reversal, and long-term reversal**. The trend factor provides **higher returns, better risk-adjusted performance, and reduced crash risk**, making it a valuable addition to both asset pricing models and portfolio construction strategies.

Implementing this approach in **Python** is a **good exercise** in **quantitative finance and systematic trading**. It allows practitioners to explore **data handling, time-series analysis, and cross-sectional regressions** using libraries such as **Pandas, NumPy, and Statsmodels**. Coding this methodology in Python is a practical way to deepen one’s understanding of **factor-based investing and trend-following strategies**.

I'd love to hear your thoughts about this. If you have any questions or comments, **just reach out via [Twitter](https://x.com/quantitativo1) or [email](mailto:cs@quantitativo.com)**. Also, I would love if you could answer a few questions about the content I am sharing: this is useful in determining what to share in the next articles, and how:

Cheers!
