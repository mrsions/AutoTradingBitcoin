# Why Measure Fear and Greed?
The crypto market behaviour is very emotional. People tend to get greedy when the market is rising which results in FOMO (Fear of missing out). Also, people often sell their coins in irrational reaction of seeing red numbers. With our Fear and Greed Index, we try to save you from your own emotional overreactions. There are two simple assumptions:

- Extreme fear can be a sign that investors are too worried. That could be a buying opportunity.
- When Investors are getting too greedy, that means the market is due for a correction.

Therefore, we analyze the current sentiment of the Bitcoin market and crunch the numbers into a simple meter from 0 to 100. Zero means "Extreme Fear", while 100 means "Extreme Greed". See below for further information on our data sources.

---
# Data Sources
We are gathering data from the five following sources. Each data point is valued the same as the day before in order to visualize a meaningful progress in sentiment change of the crypto market.

First of all, the current index is for bitcoin only (we offer separate indices for large alt coins soon), because a big part of it is the volatility of the coin price.

But let’s list all the different factors we’re including in the current index:

## Volatility (25 %)
We’re measuring the current volatility and max. drawdowns of bitcoin and compare it with the corresponding average values of the last 30 days and 90 days. We argue that an unusual rise in volatility is a sign of a fearful market.

## Market Momentum/Volume (25%)
Also, we’re measuring the current volume and market momentum (again in comparison with the last 30/90 day average values) and put those two values together. Generally, when we see high buying volumes in a positive market on a daily basis, we conclude that the market acts overly greedy / too bullish.

## Social Media (15%)
While our reddit sentiment analysis is still not in the live index (we’re still experimenting some market-related key words in the text processing algorithm), our twitter analysis is running. There, we gather and count posts on various hashtags for each coin (publicly, we show only those for Bitcoin) and check how fast and how many interactions they receive in certain time frames). A unusual high interaction rate results in a grown public interest in the coin and in our eyes, corresponds to a greedy market behaviour.

## Surveys (15%) currently paused
Together with strawpoll.com (disclaimer: we own this site, too), quite a large public polling platform, we’re conducting weekly crypto polls and ask people how they see the market. Usually, we’re seeing 2,000 - 3,000 votes on each poll, so we do get a picture of the sentiment of a group of crypto investors. We don’t give those results too much attention, but it was quite useful in the beginning of our studies. You can see some recent results here.

## ominance (10%)
The dominance of a coin resembles the market cap share of the whole crypto market. Especially for Bitcoin, we think that a rise in Bitcoin dominance is caused by a fear of (and thus a reduction of) too speculative alt-coin investments, since Bitcoin is becoming more and more the safe haven of crypto. On the other side, when Bitcoin dominance shrinks, people are getting more greedy by investing in more risky alt-coins, dreaming of their chance in next big bull run. Anyhow, analyzing the dominance for a coin other than Bitcoin, you could argue the other way round, since more interest in an alt-coin may conclude a bullish/greedy behaviour for that specific coin.

## Trends (10%)
We pull Google Trends data for various Bitcoin related search queries and crunch those numbers, especially the change of search volumes as well as recommended other currently popular searches. For example, if you check Google Trends for "Bitcoin", you can’t get much information from the search volume. But currently, you can see that there is currently a +1,550% rise of the query „bitcoin price manipulation“ in the box of related search queries (as of 05/29/2018). This is clearly a sign of fear in the market, and we use that for our index.

---
# Share & Embed

Feel free to share or embed our Bitcoin Fear & Greed Index image widget. There is a daily absolute path and an always refreshing permalink to an image of the latest index available. No JavaScript, no bullshit.

<img src="https://alternative.me/crypto/fear-and-greed-index.png" alt="Latest Crypto Fear & Greed Index" />

## Embed Self-Updating Image

```
<img src="https://alternative.me/crypto/fear-and-greed-index.png" alt="Latest Crypto Fear & Greed Index" />
```

## Embed Fixed Date Image

```
<img src="https://alternative.me/images/fng/crypto-fear-and-greed-index-2020-5-13.png" alt="Crypto Fear & Greed Index on May 13, 2020" />
```
(change the given date in the image path)

## Feel Free to Share This Page


---
# Fear and Greed Index API

Rules:
- You may not use our data to impersonate us or to create a service that could be confused with our offering.
- You must properly acknowledge the source of the data and prominently reference it accordingly.
- Commercial use is allowed as long as the attribution is given right next to the display of the data. Please contact us in case of questions.
- This applies to all of our fear and greed data, not just the API.

API: https://api.alternative.me/

Endpoint: /fng/

Method: GET

Description: Get the latest data of the Fear and Greed Index.

Optional Parameters:
- limit, [int]: Limit the number of returned results. The default value is '1', use '0' for all available data. Please note that the field "time_until_update" will only be returned for the latest value ( in other words: when the value '1' is used).
- format, [string]: Choose to either receive the data part formatted as regular JSON or formatted as CSV for easy pasting in spreadsheets, use either 'json' or 'csv' respectively. The default is 'json'.
- date_format, [string]: Choose to either receive the date part formatted for the United States (MM/DD/YYYY), for China and Korea (YYYY/MM/DD) or for the rest of the world (DD/MM/YYYY). Use 'us', 'cn', 'kr' or 'world' respectively. The default is an empty string which will return the date in unixtime, unless format is set to 'csv'. When "format" is set to 'csv' the default "date_format" is 'world'.

Example URL: https://api.alternative.me/fng/

Example URL: https://api.alternative.me/fng/?limit=10

Example URL: https://api.alternative.me/fng/?limit=10&format=csv

Example URL: https://api.alternative.me/fng/?limit=10&format=csv&date_format=us

```
GET https://api.alternative.me/fng/?limit=2

Response
{
	"name": "Fear and Greed Index",
	"data": [
		{
			"value": "40",
			"value_classification": "Fear",
			"timestamp": "1551157200",
			"time_until_update": "68499"
		},
		{
			"value": "47",
			"value_classification": "Neutral",
			"timestamp": "1551070800"
		}
	],
	"metadata": {
		"error": null
	}
}
```
	
For more endpoints of the API, visit our free crypto API documentation page.
Problems with the fear and greed API? Just drop us a mail at support@alternative.me


---
# More on Alternative.me

Beside this index we run here a website with valuable content about Discord bots, for which we offer help, commands and statistics. We also list various softwares and their alternatives, so that nobody has to buy too expensive licenses anymore, when there is also a reasonable open source alternative. Furthermore we try to give product recommendations for popular items. User input is always in the foreground for us. Feedback is also always welcome!


---
# Disclaimer

No Investment Advice
The information provided on this website does not constitute investment advice, financial advice, trading advice, or any other sort of advice and you should not treat any of the website's content as such. Alternative.me does not recommend that any cryptocurrency should be bought, sold, or held by you. Do conduct your own due diligence and consult your financial advisor before making any investment decisions.
