
  
Google News API
==================

[

API uptime

100.000%



](https://serpapi.com/status/google_news)

Our Google News API allows you to scrape results from the Google News search page. The API is accessed through the following endpoint: `/search?engine=google_news`.  
  
A user may query the following: `https://serpapi.com/search?engine=google_news` utilizing a `GET` request. Head to the [playground](https://serpapi.com/playground?engine=google_news) for a live and interactive demo.

[](https://serpapi.com/google-news-api#api-parameters)API Parameters
--------------------------------------------------------------------

### [](https://serpapi.com/google-news-api#api-parameters-search-query)Search Query

[](https://serpapi.com/google-news-api#api-parameters-search-query-q)

q

Optional

Parameter defines the query you want to search. You can use anything that you would use in a regular Google News search. e.g. `site:`, `when:`.  
  
Parameter can't be used together with publication\_token, story\_token, and topic\_token parameters.

### [](https://serpapi.com/google-news-api#api-parameters-localization)Localization

[](https://serpapi.com/google-news-api#api-parameters-localization-gl)

gl

Optional

Parameter defines the country to use for the Google News search. It's a two-letter country code. (e.g., `us` for the United States (default), `uk` for United Kingdom, or `fr` for France). Head to the [Google countries page](https://serpapi.com/google-countries) for a full list of supported Google News countries.

[](https://serpapi.com/google-news-api#api-parameters-localization-hl)

hl

Optional

Parameter defines the language to use for the Google News search. It's a two-letter language code. (e.g., `en` for English, `es` for Spanish, or `fr` for French). Head to the [Google languages page](https://serpapi.com/google-languages) for a full list of supported Google languages.

### [](https://serpapi.com/google-news-api#api-parameters-advanced-google-news-parameters)Advanced Google News Parameters

[](https://serpapi.com/google-news-api#api-parameters-advanced-google-news-parameters-topic-token)

topic\_token

Optional

Parameter defines the Google News topic token. It is used for accessing the news results for a specific topic (e.g., "World", "Business", "Technology").  
  
The token can be found in our JSON response or the URL of the Google News page (in the URL, it is a string of characters preceded by `/topics/`).  
  
Parameter can't be used together with q, story\_token, and publication\_token parameters.

[](https://serpapi.com/google-news-api#api-parameters-advanced-google-news-parameters-publication-token)

publication\_token

Optional

Parameter defines the Google News publication token. It is used for accessing the news results from a specific publisher (e.g., "CNN", "BBC", "The Guardian").  
  
The token can be found in our JSON response or the URL of the Google News page (in the URL, it is a string of characters preceded by `/publications/`).  
  
Parameter can't be used together with q, story\_token, and topic\_token parameters.

[](https://serpapi.com/google-news-api#api-parameters-advanced-google-news-parameters-section-token)

section\_token

Optional

Parameter defines the Google News section token. It is used for accessing the sub-section of a specific topic. (e.g., "Business -> Economy").  
  
The token can be found in our JSON response or the URL of the Google News page (in the URL, it is a string of characters preceded by `/sections/`)  
  
Parameter can only be used in combination with topic\_token or publication\_token parameters.

[](https://serpapi.com/google-news-api#api-parameters-advanced-google-news-parameters-story-token)

story\_token

Optional

Parameter defines the Google News story token. It is used for accessing the news results with full coverage of a specific story.  
  
The token can be found in our JSON response or the URL of the Google News page (in the URL, it is a string of characters preceded by `/stories/`)  
  
Parameter can't be used together with q, topic\_token, and publication\_token parameters.

[](https://serpapi.com/google-news-api#api-parameters-advanced-google-news-parameters-so)

so

Optional

Parameter defines the sorting method. Results can be sorted by relevance or by date. By default, the results are sorted by relevance.  
List of supported values are:  
  
`0` \- Relevance  
`1` \- Date  
  
Parameter can only be used in combination with story\_token parameter.

### [](https://serpapi.com/google-news-api#api-parameters-serpapi-parameters)![](https://serpapi.com/img/square-logo-v3.png)Serpapi Parameters

[](https://serpapi.com/google-news-api#api-parameters-serpapi-parameters-engine)

engine

Required

Set parameter to `google_news` to use the Google News API engine.

[](https://serpapi.com/google-news-api#api-parameters-serpapi-parameters-no-cache)

no\_cache

Optional

Parameter will force SerpApi to fetch the Google News results even if a cached version is already present. A cache is served only if the query and all parameters are exactly the same. Cache expires after 1h. Cached searches are free, and are not counted towards your searches per month. It can be set to `false` (default) to allow results from the cache, or `true` to disallow results from the cache. no\_cache and async parameters should not be used together.

[](https://serpapi.com/google-news-api#api-parameters-serpapi-parameters-async)

async

Optional

Parameter defines the way you want to submit your search to SerpApi. It can be set to `false` (default) to open an HTTP connection and keep it open until you got your search results, or `true` to just submit your search to SerpApi and retrieve them later. In this case, you'll need to use our [Searches Archive API](https://serpapi.com/search-archive-api) to retrieve your results. async and no\_cache parameters should not be used together. async should not be used on accounts with [Ludicrous Speed](https://serpapi.com/plan) enabled.

[](https://serpapi.com/google-news-api#api-parameters-serpapi-parameters-api-key)

api\_key

Required

Parameter defines the SerpApi private key to use.

[](https://serpapi.com/google-news-api#api-parameters-serpapi-parameters-output)

output

Optional

Parameter defines the final output you want. It can be set to json (default) to get a structured `JSON` of the results, or `html` to get the raw html retrieved.

[](https://serpapi.com/google-news-api#api-results)API Results
--------------------------------------------------------------

### [](https://serpapi.com/google-news-api#api-results-json-results)JSON Results

JSON output includes structured data for News Results.  
  
A search status is accessible through `search_metadata.status`. It flows this way: `Processing` \-> `Success` || `Error`. If a search has failed, `error` will contain an error message. `search_metadata.id` is the search ID inside SerpApi.

### [](https://serpapi.com/google-news-api#api-results-html-results)HTML Results

This API does not have the HTML response, just a text. `search_metadata.prettify_html_file` contains prettified version of the result. It is displayed in the playground.

[](https://serpapi.com/google-news-api#api-examples)API Examples
----------------------------------------------------------------

### [](https://serpapi.com/google-news-api#api-examples-json-structure-overview)JSON structure overview

    {
      "top_stories_link": {
        "topic_token": "String - Token used for retrieving news results from a specific topic",
        "serpapi_link": "String - URL to the SerpApi search"
      },
      "title": "String - Page title",
      "news_results": [
        {
          "position": "Integer - News result position",
          "title": "String - News result title",
          "snippet": "String - News result snippet",
          "source": {
            "title": "String - Title of the source",
            "name": "String - Name of the source",
            "icon": "String - Link to the source icon",
            "authors": [
              "String - Name of the author"
            ]
          },
          "author": {
            "thumbnail": "String - Link to the author's thumbnail",
            "name": "String - Name of the author",
            "handle": "String - X (Twitter) username"
          },
          "link": "String - News result link",
          "thumbnail": "String - News result thumbnail link",
          "type": "String - News result type (e.g., 'Opinion', 'Local coverage')",
          "video": "Boolean - Returns 'true' if the result is a video",
          "topic_token": "String - Token used for retrieving news results from a specific topic",
          "story_token": "String - Token used for retrieving news results from a specific story",
          "serpapi_link": "String - URL to the SerpApi search",
          "date": "String - Date when the news result was posted",
          "related_topics": [
            {
              "position": "Integer - Related topic position",
              "name": "String - Name of the related topic",
              "topic_token": "String - Token used for retrieving news results from a specific topic",
              "serpapi_link": "String - URL to the SerpApi search"
            },
            ...
          ]
          "highlight": {
            // Can contain the same data as 'news_results' except 'related_topics', `stories` and 'highlight'
          },
          "stories": [
            {
              // Can contain the same data as 'news_results' except 'related_topics', `highlight` and 'stories'
            },
            ...
          ],
        },
        ...
      ],
      "menu_links": [
        {
          "title": "String - Text of the menu item",
          "topic_token": "String - Token used for retrieving news results from a specific topic",
          "serpapi_link": "String - URL to the SerpApi search"
        },
        ...
      ],
      "sub_menu_links": [
        {
          "title": "String - Text of the sub-menu item",
          "section_token": "String - Token used for retrieving news results from a specific section",
          "topic_token": "String - Token used for retrieving news results from a specific topic",
          "serpapi_link": "String - URL to the SerpApi search"
        },
        ...
      ]
    }
    

### [](https://serpapi.com/google-news-api#api-examples-example-with-search-query-q-pizza)Example with search query q:`Pizza`

![Example with search query q: Pizza](https://serpapi.com/assets/google_news/pizza-418ebb453e29ef904bf07d1e837383d039898949e5478ee103ee7a004e372a02.jpg)

GET

*       https://serpapi.com/search.json?engine=google_news&q=pizza&gl=us&hl=en
    

  

Code to integrate

cURLRubyPythonJavaScriptPHP.NETJavaGoRustGoogle Sheets

*   [](https://github.com/serpapi/google-search-results-ruby)[](https://rubygems.org/gems/google_search_results)
    
        require 'google_search_results' 
        
        params = {
          engine: "google_news",
          q: "pizza",
          gl: "us",
          hl: "en",
          api_key: "2219e06e0ecbde4eaba834faacc1d84519c512676e20b128e7ba65792f115a33"
        }
        
        search = GoogleSearch.new(params)
        news_results = search.get_hash[:news_results]
        
    

  

JSON Example

[](https://serpapi.com/playground?engine=google_news&q=pizza&gl=us&hl=en&highlight=news_results)

    {
      "search_metadata": {
        "id": "65538af1de9834b33185eb36",
        "status": "Success",
        "json_endpoint": "https://serpapi.com/searches/b3f3198aacffbe34/65538af1de9834b33185eb36.json",
        "created_at": "2023-11-14 14:57:53 UTC",
        "processed_at": "2023-11-14 14:57:53 UTC",
        "google_news_url": "https://news.google.com/search?q=pizza&hl=en&gl=US",
        "raw_html_file": "https://serpapi.com/searches/b3f3198aacffbe34/65538af1de9834b33185eb36.html",
        "total_time_taken": 2.44
      },
      "search_parameters": {
        "engine": "google_news",
        "gl": "us",
        "hl": "en",
        "q": "pizza"
      },
      "news_results": [
        {
          "position": 1,
          "title": "Parachute Pizza Opens With Sicilian-Style Squares and Oysters in Union Market",
          "snippet": "Sicilian-style pizzas, dressed-up oysters, and wines on tap arrive at Union Market on Wednesday, November 15. The team behind Brookland...",
          "source": {
            "name": "Washingtonian",
            "icon": "https://encrypted-tbn3.gstatic.com/faviconV2?url=https://www.washingtonian.com&client=NEWS_360&size=96&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
            "authors": [
              "Jessica Sidman"
            ]
          },
          "link": "https://www.washingtonian.com/2023/11/13/cacio-e-pepe-pizza-and-fancy-oyster-spot-opens-in-union-market/",
          "thumbnail": "https://lh4.googleusercontent.com/proxy/DlPqLNcTwjvQOL0j2cue8RAOy8RsJWlKj50A2TINpupfea3kABv7HmZHBwGeDpon7SXoU_rHFOPrZsipM6wNQ-XeKrRiica3dphkKzeJB6EC_K24h34J4rvV1akrA8DahdFqNTiNrrrvLNRevjPrfsM",
          "date": "11/13/2023, 05:43 PM, +0100 CET"
        },
        {
          "position": 2,
          "title": "Brewer's Pizza, home of Pinglehead Brewing Company, closing",
          "snippet": "A popular Jacksonville-area brewpub plans to close this week after 14 years serving up hand-crafted pizzas and artisan beers on tap.",
          "source": {
            "name": "The Florida Times-Union",
            "icon": "https://encrypted-tbn1.gstatic.com/faviconV2?url=https://www.jacksonville.com&client=NEWS_360&size=96&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
            "authors": [
              "Teresa Stepzinski"
            ]
          },
          "link": "https://www.jacksonville.com/story/entertainment/dining/2023/11/13/brewers-pizza-home-of-pinglehead-brewing-company-closing/71565634007/",
          "thumbnail": "https://lh6.googleusercontent.com/proxy/BWnbA4ykM42q3U5FGmljZHkhAsDAbFbOY9__RADuZTGxtUYvVWNWyc8vYTul8LXkmVl7V2qW8fSRadmqKmVpnL-jUiaDT04zWtSShHI18J04zPIwvLy1vYaeKRRx79eUHqtI6qTXnk8HvD3dYuStlqpoHVvcvS38syoNIytbSTQvQuloW4GaF5gozLp7d3PEILlUvzQdrHS-21iKGeV-cXSBu0NLA_3Ydu_B18Ub_TvEB223ufjf_BntTsfhSrPIhhvOnzssIKwdSyAlkaVdaSW7OjZdxgNjvnop",
          "date": "11/13/2023, 04:51 PM, +0100 CET"
        },
        {
          "position": 3,
          "title": "California Pizza Kitchen Invites Guests to Embrace the Holiday Spirit with Decadent New Dishes and a Signature Cocktail",
          "snippet": "COSTA MESA, Calif., November 14, 2023--With the holiday season around the corner, California Pizza Kitchen (CPK) is rolling out three new...",
          "source": {
            "name": "Yahoo Finance",
            "icon": "https://lh3.googleusercontent.com/L57n4HUzUS8lNXBPYNGQScsyxaqqx42Nym3-tUk8NzkTvMsa95NhzEqC8KMqVPFpAFpCuPFdlA"
          },
          "link": "https://finance.yahoo.com/news/california-pizza-kitchen-invites-guests-140000087.html",
          "thumbnail": "https://lh4.googleusercontent.com/proxy/juEVTbFNL_AJu48IxqJ_uumsmvqiXqmgaipRAf1ges1D82jgGp5y-JCKYxQcAKJQntSPm7Ayg7t4MXQpfcJqjJBUz19rrHOROQC5DE_XXZ6Un6twAzzm-VE9WcQk2_W2YwA_zqxdN5yR6bWXogTwFJYackIdbgGOGMfNsk38hAJs6yQiA-6EoOoRKkUVcWXKxV71Uk9EAHV7fq0sC2M0BxDqJ5yE5apgsX-uhA6AnR-G3WHY68nFDknjDWMIAjkbfg4RwJdla7d6X0tXuA",
          "date": "11/14/2023, 03:00 PM, +0100 CET"
        },
        ...
      ],
      "menu_links": [
        {
          "title": "U.S.",
          "topic_token": "CAAqIggKIhxDQkFTRHdvSkwyMHZNRGxqTjNjd0VnSmxiaWdBUAE",
          "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&topic_token=CAAqIggKIhxDQkFTRHdvSkwyMHZNRGxqTjNjd0VnSmxiaWdBUAE"
        },
        ...
      ]
    }
    

### [](https://serpapi.com/google-news-api#api-examples-example-with-technology-as-a-topic)Example with`Technology`as a topic

![Example with Technology as a topic](https://serpapi.com/assets/google_news/technology-b3635c90986b24006957dc82079c93d5a6198a523a423df1b9f34a2ee7290032.jpg)

GET

*       https://serpapi.com/search.json?engine=google_news&gl=us&hl=en&topic_token=CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB
    

  

Code to integrate

cURLRubyPythonJavaScriptPHP.NETJavaGoRustGoogle Sheets

*   [](https://github.com/serpapi/google-search-results-ruby)[](https://rubygems.org/gems/google_search_results)
    
        require 'google_search_results' 
        
        params = {
          engine: "google_news",
          gl: "us",
          hl: "en",
          topic_token: "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB",
          api_key: "2219e06e0ecbde4eaba834faacc1d84519c512676e20b128e7ba65792f115a33"
        }
        
        search = GoogleSearch.new(params)
        news_results = search.get_hash[:news_results]
        
    

  

JSON Example

[](https://serpapi.com/playground?engine=google_news&gl=us&hl=en&topic_token=CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB&highlight=news_results)

    {
      "search_metadata": {
        "id": "65538d4fde9834b32f4f4cc1",
        "status": "Success",
        "json_endpoint": "https://serpapi.com/searches/3111cbeb3042511f/65538d4fde9834b32f4f4cc1.json",
        "created_at": "2023-11-14 15:07:59 UTC",
        "processed_at": "2023-11-14 15:07:59 UTC",
        "google_news_url": "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB?hl=en&gl=US",
        "raw_html_file": "https://serpapi.com/searches/3111cbeb3042511f/65538d4fde9834b32f4f4cc1.html",
        "total_time_taken": 2.58
      },
      "search_parameters": {
        "engine": "google_news",
        "gl": "us",
        "hl": "en",
        "topic_token": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB"
      },
      "title": "Technology",
      "news_results": [
        {
          "position": 1,
          "title": "Why Apple Is Content With the Blue Bubble Divide in iMessage",
          "source": {
            "name": "CNET",
            "icon": "https://lh3.googleusercontent.com/pnQtIpgtVqvRT94UjYLY1CmOffa5B0j04FK18Kr6MhRx05UsTs913O_c4FDbQy0Vw0l1BjyrBdA",
            "authors": [
              "Imad Khan"
            ]
          },
          "link": "https://www.cnet.com/tech/mobile/why-apple-is-content-with-the-blue-bubble-divide-in-imessage/",
          "thumbnail": "https://lh3.googleusercontent.com/proxy/rccVi8unWxTnY1tQDENFj_e8ysw40zH0EIZUgx3c0MugWi0CrxTTzA8JLDND12-UMOU0N6bWb0kfFeMwqvQmNFRtxdnmFevIl-4WnYqu_-78zWR0nYlBbiWCTgkfG-Yy7jUpJG8i1Kd4PxyIxxKAd2TIqVL6_PotrWrCQbKgt2IFrPEoZZy1BmcWzieQV7agNPF9onuOa-eSq6LAIjoahQMpF8nWaZKa_MU7ADqr8MwsfuYwAM1YbnYbnrFWrYNknAR4O4mUnVyKe84plD75z8FDC7nRriRlG_BrVqiO6VMABY8xK961lmH668WktFgcxpJlYZFYrf2fOcc",
          "story_token": "CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2l6ME5uY0NSRjh2VkR0NnJ0NDhTZ0FQAQ",
          "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&story_token=CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2l6ME5uY0NSRjh2VkR0NnJ0NDhTZ0FQAQ",
          "date": "11/14/2023, 02:00 PM, +0100 CET"
        },
        {
          "position": 2,
          "highlight": {
            "title": "Google sues scammers that allegedly released a malware-filled Bard knockoff",
            "source": {
              "name": "Engadget",
              "icon": "https://lh3.googleusercontent.com/w1hw-XN8YegN8sGKZCmPe7kI0pLiUti33nZ-iKgN0SIOp0KGL_lwI6vgitklgkgrI1yBw28R8A",
              "authors": [
                "Lawrence Bonk"
              ]
            },
            "link": "https://www.engadget.com/google-sues-scammers-that-allegedly-released-a-malware-filled-bard-knockoff-162222150.html",
            "thumbnail": "https://lh6.googleusercontent.com/proxy/UlNVuMFST-WX_7EpBZKvaeQvUz5nafglEVOK_-8VBVklGiNG_0T4kgDx-5w-3qO7S6Z8rd0wFuQ2pSbyZWtI0gypTzY2Y7R6XgVlxmefeqq8dVAOedZi1Ui_40DyWBCX0vfns-XXVgJFeB3z7VrhJnJh09w_82fmYxumR4gLNLf5eGsMdc-dP58ggRWMQ7ah7s9565-u9ozKcRBrMoXJHLkZyi1_rDa1umReTuFPXNQXGNUVZUQZ_HjmDi1DhzdDSO3Iv9bvFZqBWndhcP2aa80I4TZQUEeGxg",
            "date": "11/13/2023, 05:22 PM, +0100 CET"
          },
          "stories": [
            {
              "position": 1,
              "title": "Google fights scammers using Bard hype to spread malware",
              "source": {
                "name": "The Verge",
                "icon": "https://lh3.googleusercontent.com/vkRH5gyHtLcKAoRSFHK1ATEgKtHDXoi9iRKKOdVhOng8g7qF2_QCVT1f11q_y_4y95_PY5VzWQ",
                "authors": [
                  "Jon Porter"
                ]
              },
              "link": "https://www.theverge.com/2023/11/13/23958629/google-scammers-bard-ai-malware-spread-lawsuit",
              "thumbnail": "https://lh4.googleusercontent.com/proxy/pXwoVgdzG8s69TRzRM8vQbwwOZSqWGiHq51qFDoojCGAKIGuHNyU830O834K-bY-YtrGTQBI3oCswkOqbMudzDKJSgGcv5H7jJEFxHemV7v9f6O4RdnkDqD5I2uqFmtT8BYUnoUp8XHW9l8AWHe42THV-M0Dqo5Q8yGVpt3rZ8PBGhEWN-ZOtxOdI_OJcJ7_hK8qSH8k1lSCGkvq6D5H6l92bPGVG8Pyi7N-3AU_rsn1a4_4NWUnosGfMVLD-Js52cr3kD3VzXXMwvkIzbM53M2ovN82MIFNkA",
              "story_token": "CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2pUNWJ2Y0NSR3VzOUx4LWVXcHRpZ0FQAQ",
              "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&story_token=CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2pUNWJ2Y0NSR3VzOUx4LWVXcHRpZ0FQAQ",
              "date": "11/13/2023, 12:00 PM, +0100 CET"
            },
            ...
          ],
          "story_token": "CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2pUNWJ2Y0NSR3VzOUx4LWVXcHRpZ0FQAQ",
          "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&story_token=CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2pUNWJ2Y0NSR3VzOUx4LWVXcHRpZ0FQAQ"
        },
        ...
      ],
      "menu_links": [
        {
          "title": "U.S.",
          "topic_token": "CAAqIggKIhxDQkFTRHdvSkwyMHZNRGxqTjNjd0VnSmxiaWdBUAE",
          "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&topic_token=CAAqIggKIhxDQkFTRHdvSkwyMHZNRGxqTjNjd0VnSmxiaWdBUAE"
        },
        ...
      ],
      "sub_menu_links": [
        {
          "title": "Latest",
          "section_token": "CAQqKggAKiYICiIgQ0JBU0Vnb0lMMjB2TURkak1YWVNBbVZ1R2dKVlV5Z0FQAQ",
          "topic_token": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB",
          "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&section_token=CAQqKggAKiYICiIgQ0JBU0Vnb0lMMjB2TURkak1YWVNBbVZ1R2dKVlV5Z0FQAQ&topic_token=CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB"
        },
        ...
      ]
    }
    

### [](https://serpapi.com/google-news-api#api-examples-example-for-a-full-coverage-page)Example for a full coverage page

![Example for a full coverage page](https://serpapi.com/assets/google_news/stories-56d26fe61c01aaf658d358582da26628eb60649464030c01d47dc4dd5b09b07a.jpg)

GET

*       https://serpapi.com/search.json?engine=google_news&gl=us&hl=en&story_token=CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2pqdU9UWENSRXNnR1puWWJtdzZ5Z0FQAQ
    

  

Code to integrate

cURLRubyPythonJavaScriptPHP.NETJavaGoRustGoogle Sheets

*   [](https://github.com/serpapi/google-search-results-ruby)[](https://rubygems.org/gems/google_search_results)
    
        require 'google_search_results' 
        
        params = {
          engine: "google_news",
          gl: "us",
          hl: "en",
          story_token: "CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2pqdU9UWENSRXNnR1puWWJtdzZ5Z0FQAQ",
          api_key: "2219e06e0ecbde4eaba834faacc1d84519c512676e20b128e7ba65792f115a33"
        }
        
        search = GoogleSearch.new(params)
        news_results = search.get_hash[:news_results]
        
    

  

JSON Example

[](https://serpapi.com/playground?engine=google_news&gl=us&hl=en&story_token=CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2pqdU9UWENSRXNnR1puWWJtdzZ5Z0FQAQ&highlight=news_results)

    {
      "search_metadata": {
        "id": "65538efade9834b33185eb37",
        "status": "Success",
        "json_endpoint": "https://serpapi.com/searches/34eaf87949612adb/65538efade9834b33185eb37.json",
        "created_at": "2023-11-14 15:15:06 UTC",
        "processed_at": "2023-11-14 15:15:06 UTC",
        "google_news_url": "https://news.google.com/stories/CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2pqdU9UWENSRXNnR1puWWJtdzZ5Z0FQAQ?hl=en&gl=US",
        "raw_html_file": "https://serpapi.com/searches/34eaf87949612adb/65538efade9834b33185eb37.html",
        "total_time_taken": 2.3
      },
      "search_parameters": {
        "engine": "google_news",
        "gl": "us",
        "hl": "en",
        "story_token": "CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2pqdU9UWENSRXNnR1puWWJtdzZ5Z0FQAQ"
      },
      "title": "News about CPI, October, and inflation",
      "news_results": [
        {
          "position": 1,
          "title": "Top news",
          "stories": [
            {
              "position": 1,
              "title": "Inflation was flat in October from the prior month, core CPI hits two-year low",
              "snippet": "The CPI, which measures a broad basket of commonly used goods and services, increased 3.2% from a year ago despite being unchanged for the...",
              "source": {
                "name": "CNBC",
                "icon": "https://lh3.googleusercontent.com/UEQEAUAyUNeb8PjnoA90xCxg3IIQc2RWP_EJNe4ljoowvxl8nR62HAdD_NTXlOFzSv1HEHfC",
                "authors": [
                  "Jeff Cox"
                ]
              },
              "link": "https://www.cnbc.com/2023/11/14/cpi-inflation-report-october-2023.html",
              "thumbnail": "https://lh5.googleusercontent.com/proxy/-uOaIuMdW6-O6ZV0YyAeycX9kvORXkRdAA2Phg7fbZ5sUX99VMKdI8bO9aesM7R4wEElgdmby03hXaCoEO5bdeCTPzMo-wREYynj6GfGrm14F8MuQnMrHL9oB3B7flC9Eo0MCPfUWekTbizWvpH_t8f5BnDAnNzHI3-_x1Ad-YVsQH8k0gn-9gOFWF9bVuFVpV8sho6RNJiLr3TSkEACEWU",
              "date": "11/14/2023, 02:31 PM, +0100 CET"
            },
            ...
          ]
        },
        {
          "position": 2,
          "title": "By the numbers",
          "stories": [
            {
              "position": 1,
              "title": "US stocks and bonds jump after inflation falls to 3.2%",
              "snippet": "US inflation fell more than expected to 3.2 per cent in October, the first decline in four months, prompting Treasury yields to fall sharply...",
              "source": {
                "name": "Financial Times",
                "icon": "https://lh3.googleusercontent.com/281oPpXmEcGU9cV4N2LudyLEG2aBqbqG2iDoMoXUXKl-SWD4AUdO5652KVTGNmcduSWZB_7j",
                "authors": [
                  "Colby Smith",
                  "Nicholas Megaw"
                ]
              },
              "link": "https://www.ft.com/content/7928101a-262f-475c-ac32-ac962f8925fb",
              "thumbnail": "https://lh4.googleusercontent.com/proxy/Omfiu_jfi1XtEe29yZuBBV6jxIevajO1-YkYQKfdQ3jH1xCnrTWAVQRqMgoh5DqA91751aqbypzZwFlRR8840DLRjOtqKw3Oncj2w_RPBxauxNb7E9qAB8oCuFPOafdtqBKLjjmhqovCqsWlcu1tw3tqYw_5d6H65HVZ_J6efU-o1BUvVJRaPaLgyYtvCNjTPI5aNiM4dm0GrtUKSljFu48T3TXoV71rVwK9yapEYVVA9D5TGu3TYoedxZeuwPb9dNpEmZ7pBfOH7JbMLtXRBtR5UKvutRoZAoozlCKljNL29mPlO6L8BzhhyHtKEYuNY8-1tx23SNMklmY",
              "date": "11/14/2023, 03:38 PM, +0100 CET"
            },
            ...
          ]
        },
        {
          "position": 3,
          "title": "Posts on X",
          "stories": [
            {
              "position": 1,
              "snippet": "Dollar was steady as traders awaited another batch of inflation data from the United States that is expected to offer further clues this week on whether the Federal Reserve has more work to do to tame price pressures.\n\n#Dollar #UnitedStates #Inflation \n\nwww.zeebiz.com/markets/currency/news-dollar-firm-ahead-of-us-inflation-data-yen-near-one-year-low-264081",
              "author": {
                "thumbnail": "https://pbs.twimg.com/profile_images/1072023698985705473/YftYvcTj_normal.jpg",
                "name": "Zee Business",
                "handle": "ZeeBusiness"
              },
              "link": "https://twitter.com/ZeeBusiness/status/1723900983573614825",
              "date": "11/13/2023, 04:09 AM, +0100 CET"
            },
            ...
          ],
          "link": "https://twitter.com/RepDarrenSoto/status/1724441285828731029"
        },
        {
          "position": 4,
          "title": "Frequently asked questions",
          "stories": [
            {
              "position": 1,
              "title": "When is the October CPI report?",
              "snippet": "The consumer price index reading for October will be reported on Nov. 14 by \nthe Bureau of Labor Statistics.",
              "source": {
                "title": "October CPI Data: The Key Points From Today's Inflation Report - Barrons",
                "name": "Barron's",
                "icon": "https://encrypted-tbn1.gstatic.com/faviconV2?url=https://www.barrons.com&client=NEWS_360&size=96&type=FAVICON&fallback_opts=TYPE,SIZE,URL"
              },
              "link": "https://www.barrons.com/articles/october-cpi-inflation-report-data-today-155d53f1",
              "date": "11/14/2023, 03:32 PM, +0100 CET"
            },
            ...
          ]
        },
        {
          "position": 5,
          "title": "10-year Treasury yield tumbles below 4.5% on cool October inflation report",
          "snippet": "U.S. Treasury yields fell on Tuesday as key inflation figures showed a surprisingly soft change in prices last month. The 10-year Treasury...",
          "source": {
            "name": "CNBC",
            "icon": "https://lh3.googleusercontent.com/UEQEAUAyUNeb8PjnoA90xCxg3IIQc2RWP_EJNe4ljoowvxl8nR62HAdD_NTXlOFzSv1HEHfC",
            "authors": [
              "Lisa Kailai Han",
              "Jesse Pound",
              "Sophie Kiderlin"
            ]
          },
          "link": "https://www.cnbc.com/2023/11/14/us-treasury-yields-investors-look-to-key-inflation-data.html",
          "thumbnail": "https://lh3.googleusercontent.com/proxy/2KnYfWGU2HTaJh4m2kGlH9g5KzFwV_CR3Yh8CA4QYf9OKsG7d06U6J--6GvfUEwCTb4-87zQncqczVKE-U4WG_YRoAmHjl3B9D7r2gnGWIS0qu1zMuG_4I5JMWv1rjxxPe6xS1eKxzPkW2GwDOG5s1kzVTwm12bY_C2pUi0U9SvR4aA-pS4limEduZcq1CyjLhcRln_nA9P_-apYbTqFRVZ3-wCnBrgZe-Xv8dwMfJg",
          "date": "11/14/2023, 10:14 AM, +0100 CET"
        },
        ...
      ],
      "menu_links": [
        {
          "title": "U.S.",
          "topic_token": "CAAqIggKIhxDQkFTRHdvSkwyMHZNRGxqTjNjd0VnSmxiaWdBUAE",
          "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&topic_token=CAAqIggKIhxDQkFTRHdvSkwyMHZNRGxqTjNjd0VnSmxiaWdBUAE"
        },
        ...
      ]
    }
    

### [](https://serpapi.com/google-news-api#api-examples-example-for-a-publications-page)Example for a publications page

![Example for a publications page](https://serpapi.com/assets/google_news/publications-4b25b0df9d114b51c9f5d66856dc0e967dfc2f632555255e79220f6dfda9f748.jpg)

GET

*       https://serpapi.com/search.json?engine=google_news&gl=us&hl=en&publication_token=CAAqBwgKMKHL9QowkqbaAg
    

  

Code to integrate

cURLRubyPythonJavaScriptPHP.NETJavaGoRustGoogle Sheets

*   [](https://github.com/serpapi/google-search-results-ruby)[](https://rubygems.org/gems/google_search_results)
    
        require 'google_search_results' 
        
        params = {
          engine: "google_news",
          gl: "us",
          hl: "en",
          publication_token: "CAAqBwgKMKHL9QowkqbaAg",
          api_key: "2219e06e0ecbde4eaba834faacc1d84519c512676e20b128e7ba65792f115a33"
        }
        
        search = GoogleSearch.new(params)
        news_results = search.get_hash[:news_results]
        
    

  

JSON Example

[](https://serpapi.com/playground?engine=google_news&gl=us&hl=en&publication_token=CAAqBwgKMKHL9QowkqbaAg&highlight=news_results)

    {
      "search_metadata": {
        "id": "65539292de9834b32f4f4cc4",
        "status": "Success",
        "json_endpoint": "https://serpapi.com/searches/cc14a4956b8d7f79/65539292de9834b32f4f4cc4.json",
        "created_at": "2023-11-14 15:30:26 UTC",
        "processed_at": "2023-11-14 15:30:26 UTC",
        "google_news_url": "https://news.google.com/publications/CAAqBwgKMKHL9QowkqbaAg?hl=en&gl=US",
        "raw_html_file": "https://serpapi.com/searches/cc14a4956b8d7f79/65539292de9834b32f4f4cc4.html",
        "total_time_taken": 2.99
      },
      "search_parameters": {
        "engine": "google_news",
        "gl": "us",
        "hl": "en",
        "publication_token": "CAAqBwgKMKHL9QowkqbaAg"
      },
      "title": "CNN",
      "news_results": [
        {
          "position": 1,
          "title": "Would you pay to go on vacation without your smartphone?",
          "snippet": "Could you survive a vacation without your mobile phone, resisting the compulsion to check emails, make a call, post a tweet or rely on the power of the ...",
          "source": {
            "name": "CNN",
            "icon": "https://lh3.googleusercontent.com/8zdvTbISHUn-4iHkauW-_yQSGPD9BMrx9EWfqTIhiVm2YMYqhHC1HJWNDQoSOkMk0MRPYKxjIg",
            "authors": [
              "Silvia Marchetti"
            ]
          },
          "link": "https://www.cnn.com/travel/phone-free-vacations-wellness/index.html",
          "thumbnail": "https://lh6.googleusercontent.com/proxy/MQLv-JTFVfF20eo3e9dJVcsjzcAmAs5iKdIwdQPgUwbdzYMiUaLhOTEhvwQfcN2mz_Vw7R4ghRIgpuewTM5ep7LbiAphZ2hbznfQaBuAEzoHj2u9znL2wUgIPfguWZtIHLnDbWP4OrWvyYF3sZA8D1Ms6eKUUqOA201tDBDG9oHSj9A",
          "date": "11/13/2023, 08:21 PM, +0100 CET"
        },
        {
          "position": 2,
          "title": "Footprints in the snow lead rescuers to Rocky Mountains hiker wearing a cotton hoodie with no way to warm themselves",
          "snippet": "A hiker who was unprepared for conditions at over 13000 feet in the Colorado Rockies was rescued when searchers followed footprints in freshly fallen snow ...",
          "source": {
            "name": "CNN",
            "icon": "https://lh3.googleusercontent.com/8zdvTbISHUn-4iHkauW-_yQSGPD9BMrx9EWfqTIhiVm2YMYqhHC1HJWNDQoSOkMk0MRPYKxjIg",
            "authors": [
              "Chris Boyette"
            ]
          },
          "link": "https://www.cnn.com/2023/11/13/us/rocky-mountains-colorado-hiker-rescue/index.html",
          "thumbnail": "https://lh4.googleusercontent.com/proxy/Gjb0c-RP3ruUuqXVllxY9JVAD8zGvBTr7qb0Yqt3YdjuwKmiOiSO4zMDHnOTa1VJZ-lCXKyXeGJYPDcwwl3hYBlOovGU2bcoOln4P6eujNcAuiwu_v-WRASYImKFSnyd0A9D25FGKRSUiz6irg_ZsNcyUF6V1M6ROoW2VvLcxlO8QhI4Tf2jpc-XlU_7m26IT0VlEQ",
          "date": "11/13/2023, 07:28 PM, +0100 CET"
        },
        {
          "position": 3,
          "title": "The need for 'a new moral imagination': Two experts on the difficult conversations on Israel and Gaza",
          "snippet": "Christiane Amanpour speaks with Guardian columnist Jonathan Freedland and Professor of Islamic and Interreligious Studies at the University of Edinburgh ...",
          "source": {
            "name": "CNN",
            "icon": "https://lh3.googleusercontent.com/8zdvTbISHUn-4iHkauW-_yQSGPD9BMrx9EWfqTIhiVm2YMYqhHC1HJWNDQoSOkMk0MRPYKxjIg"
          },
          "link": "https://www.cnn.com/videos/tv/2023/11/14/amanpour-freedland-siddiqui.cnn",
          "thumbnail": "https://lh4.googleusercontent.com/proxy/x8FBL7izx-wbfL59-dPFArz_U09IEgnk0HJLL41fOGOx-QN28LCc8U_CS27S839cSk9gvqeI_1fN3i8z-jMISf6u3G62F2RdqvGOajt7NyCdljuWYjV3g_3GiOsLfCmY9T7OFWZH04pvB1b0bhnzOz8NIJqFd0_GLuM",
          "date": "11/14/2023, 04:25 PM, +0100 CET"
        },
        ...
      ],
      "menu_links": [
        {
          "title": "U.S.",
          "topic_token": "CAAqIggKIhxDQkFTRHdvSkwyMHZNRGxqTjNjd0VnSmxiaWdBUAE",
          "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&topic_token=CAAqIggKIhxDQkFTRHdvSkwyMHZNRGxqTjNjd0VnSmxiaWdBUAE"
        },
        ...
      ],
      "sub_menu_links": [
        {
          "title": "Latest",
          "section_token": "CAQqEAgAKgcICjChy_UKMJKm2gIw-tOmBQ",
          "publication_token": "CAAqBwgKMKHL9QowkqbaAg",
          "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&publication_token=CAAqBwgKMKHL9QowkqbaAg&section_token=CAQqEAgAKgcICjChy_UKMJKm2gIw-tOmBQ"
        },
        ...
      ]
    }
    

### [](https://serpapi.com/google-news-api#api-examples-example-for-a-publications-page-with-business-subsection)Example for a publications page with Business subsection

![Example for a publications page with Business subsection](https://serpapi.com/assets/google_news/publications-section-1a7faaabb2e17a5df8000a24ae27a73b6d23be99604ac248de531608cda037c0.jpg)

GET

*       https://serpapi.com/search.json?engine=google_news&gl=us&hl=en&publication_token=CAAqBwgKMKHL9QowkqbaAg&section_token=CAQqEAgAKgcICjChy_UKMJKm2gIwxJScBg
    

  

Code to integrate

cURLRubyPythonJavaScriptPHP.NETJavaGoRustGoogle Sheets

*   [](https://github.com/serpapi/google-search-results-ruby)[](https://rubygems.org/gems/google_search_results)
    
        require 'google_search_results' 
        
        params = {
          engine: "google_news",
          gl: "us",
          hl: "en",
          publication_token: "CAAqBwgKMKHL9QowkqbaAg",
          section_token: "CAQqEAgAKgcICjChy_UKMJKm2gIwxJScBg",
          api_key: "2219e06e0ecbde4eaba834faacc1d84519c512676e20b128e7ba65792f115a33"
        }
        
        search = GoogleSearch.new(params)
        news_results = search.get_hash[:news_results]
        
    

  

JSON Example

[](https://serpapi.com/playground?engine=google_news&gl=us&hl=en&publication_token=CAAqBwgKMKHL9QowkqbaAg&section_token=CAQqEAgAKgcICjChy_UKMJKm2gIwxJScBg&highlight=news_results)

    {
      "search_metadata": {
        "id": "655e11f2de98340c9a4424e6",
        "status": "Success",
        "json_endpoint": "https://serpapi.com/searches/ef6f520b4e9e39a4/655e11f2de98340c9a4424e6.json",
        "created_at": "2023-11-22 14:36:34 UTC",
        "processed_at": "2023-11-22 14:36:34 UTC",
        "google_news_url": "https://news.google.com/publications/CAAqBwgKMKHL9QowkqbaAg/sections/CAQqEAgAKgcICjChy_UKMJKm2gIwxJScBg?hl=en&gl=US",
        "raw_html_file": "https://serpapi.com/searches/ef6f520b4e9e39a4/655e11f2de98340c9a4424e6.html",
        "total_time_taken": 2.44
      },
      "search_parameters": {
        "engine": "google_news",
        "gl": "us",
        "hl": "en",
        "publication_token": "CAAqBwgKMKHL9QowkqbaAg"
      },
      "title": "CNN",
      "news_results": [
        {
          "position": 1,
          "title": "Former CEO Sam Altman to return to OpenAI",
          "snippet": "OpenAI co-founder Sam Altman is returning to the company as C.E.O., less than a week after being fired by the board of directors. CNN's Anna Stewart joins ...",
          "source": {
            "name": "CNN",
            "icon": "https://lh3.googleusercontent.com/8zdvTbISHUn-4iHkauW-_yQSGPD9BMrx9EWfqTIhiVm2YMYqhHC1HJWNDQoSOkMk0MRPYKxjIg"
          },
          "link": "https://www.cnn.com/videos/business/2023/11/22/exp-openai-sam-altman-stewart-112204aseg1-cnni-business.cnn",
          "thumbnail": "https://lh3.googleusercontent.com/proxy/EB3c_N9IeG0g6nXESIDEUMbcel_E9P29jebrE014H7gDQ-f_d_CsJZAgetJ0QEwH91MOhOeQcV3uK9qqqWhcKIcvs1MqGafFHzAJ3Rky20BGh-bcS4ST_l8_qQAMdoGvKbJScIoaRMn29OTayBF40xcPrWcazRT_rGAfogdc9DG7Ir55gg56fqyC2loX0aduWNq1izL1uRZb95X-i7ogFVvT9nGyyf86cV86WobhhEhXyPXp",
          "date": "11/22/2023, 02:37 PM, +0100 CET"
        },
        {
          "position": 2,
          "title": "This Moroccan startup is growing crops in the desert",
          "snippet": "Sand to Green is working to transform patches of desert into sustainable and profitable plantations.",
          "source": {
            "name": "CNN",
            "icon": "https://lh3.googleusercontent.com/8zdvTbISHUn-4iHkauW-_yQSGPD9BMrx9EWfqTIhiVm2YMYqhHC1HJWNDQoSOkMk0MRPYKxjIg",
            "authors": [
              "Jacopo Prisco"
            ]
          },
          "link": "https://www.cnn.com/2023/10/24/business-food/sand-to-green-desert-morocco-spc-intl/index.html",
          "thumbnail": "https://lh4.googleusercontent.com/proxy/f_7xiCV1duhE7_TfsMhjkuf0m6ZspVfOEgi6pb0meehIw1YmB4LRQgUKG6uw6FzFR0Lr-99EDai0o78c7MlCEZC84i8Hu1O4Ka-bAVRGKKVIy4zwLSs3H8LhpEq45hAOYFePNhF5SvbQzeF0K5NacBFGvU0Smrr6SZ3S9DEk3b_AFmPdp8H_2FxYd9o1H1FVOtzuAQM7rpqtkA",
          "date": "10/24/2023, 09:00 AM, +0200 CEST"
        },
        {
          "position": 3,
          "title": "Warren Buffett donates $870 million to charities ahead of Thanksgiving",
          "snippet": "Warren Buffett is donating about $870 million to four family-run foundations ahead of the Thanksgiving holiday, continuing a tradition of giving away his ...",
          "source": {
            "name": "CNN",
            "icon": "https://lh3.googleusercontent.com/8zdvTbISHUn-4iHkauW-_yQSGPD9BMrx9EWfqTIhiVm2YMYqhHC1HJWNDQoSOkMk0MRPYKxjIg",
            "authors": [
              "Jordan Valinsky"
            ]
          },
          "link": "https://www.cnn.com/2023/11/22/business/warren-buffett-thanksgiving-donation/index.html",
          "thumbnail": "https://lh4.googleusercontent.com/proxy/BPSBdR36UxhPZbKjIjNxC_C32BGzTAePIix9O-vKDAPE0loAtkMMGNiwsUZS6GkBj2pbVq8MvGkSEYSotHbxD2xPBdYvhy2YLCqI_W8cYV3-Mysa252gB6YfTgfLOWsrhDUoxlTSw-1AUQmPSBcVvFIjy4CdR312yi1VKXFIgxTbWAJPim2-M2Ba1A0RMLwimH2d43Q",
          "date": "11/22/2023, 02:02 PM, +0100 CET"
        },
        ...
      ],
      "menu_links": [
        {
          "title": "U.S.",
          "topic_token": "CAAqIggKIhxDQkFTRHdvSkwyMHZNRGxqTjNjd0VnSmxiaWdBUAE",
          "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&topic_token=CAAqIggKIhxDQkFTRHdvSkwyMHZNRGxqTjNjd0VnSmxiaWdBUAE"
        },
        ...
      ],
      "sub_menu_links": [
        {
          "title": "Latest",
          "section_token": "CAQqEAgAKgcICjChy_UKMJKm2gIw-tOmBQ",
          "publication_token": "CAAqBwgKMKHL9QowkqbaAg",
          "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&publication_token=CAAqBwgKMKHL9QowkqbaAg&section_token=CAQqEAgAKgcICjChy_UKMJKm2gIw-tOmBQ"
        },
        ...
      ]
    }
    

### [](https://serpapi.com/google-news-api#api-examples-example-for-a-front-page)Example for a front page

![Example for a front page](https://serpapi.com/assets/google_news/frontpage-48c733bd5bccb68ca59378a44c5f078f88b426d0d156a1dbaa5822f073251d44.jpg)

GET

*       https://serpapi.com/search.json?engine=google_news&gl=us&hl=en
    

  

Code to integrate

cURLRubyPythonJavaScriptPHP.NETJavaGoRustGoogle Sheets

*   [](https://github.com/serpapi/google-search-results-ruby)[](https://rubygems.org/gems/google_search_results)
    
        require 'google_search_results' 
        
        params = {
          engine: "google_news",
          gl: "us",
          hl: "en",
          api_key: "2219e06e0ecbde4eaba834faacc1d84519c512676e20b128e7ba65792f115a33"
        }
        
        search = GoogleSearch.new(params)
        news_results = search.get_hash[:news_results]
        
    

  

JSON Example

[](https://serpapi.com/playground?engine=google_news&gl=us&hl=en&highlight=news_results)

    {
      "search_metadata": {
        "id": "65538a3dde9834b32f4f4cbf",
        "status": "Success",
        "json_endpoint": "https://serpapi.com/searches/ec7c288d93a3d064/65538a3dde9834b32f4f4cbf.json",
        "created_at": "2023-11-14 14:54:53 UTC",
        "processed_at": "2023-11-14 14:54:54 UTC",
        "google_news_url": "https://news.google.com/home?hl=en&gl=US",
        "raw_html_file": "https://serpapi.com/searches/ec7c288d93a3d064/65538a3dde9834b32f4f4cbf.html",
        "total_time_taken": 2.92
      },
      "search_parameters": {
        "engine": "google_news",
        "gl": "us",
        "hl": "en"
      },
      "top_stories_link": {
        "topic_token": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZxYUdjU0FtVnVHZ0pWVXlnQVAB",
        "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&topic_token=CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZxYUdjU0FtVnVHZ0pWVXlnQVAB"
      },
      "news_results": [
        {
          "position": 1,
          "highlight": {
            "title": "Inflation was flat in October from the prior month, core CPI hits two-year low",
            "source": {
              "name": "CNBC",
              "icon": "https://lh3.googleusercontent.com/UEQEAUAyUNeb8PjnoA90xCxg3IIQc2RWP_EJNe4ljoowvxl8nR62HAdD_NTXlOFzSv1HEHfC",
              "authors": [
                "Jeff Cox"
              ]
            },
            "link": "https://www.cnbc.com/2023/11/14/cpi-inflation-report-october-2023.html",
            "thumbnail": "https://lh5.googleusercontent.com/proxy/-uOaIuMdW6-O6ZV0YyAeycX9kvORXkRdAA2Phg7fbZ5sUX99VMKdI8bO9aesM7R4wEElgdmby03hXaCoEO5bdeCTPzMo-wREYynj6GfGrm14F8MuQnMrHL9oB3B7flC9Eo0MCPfUWekTbizWvpH_t8f5BnDAnNzHI3-_x1Ad-YVsQH8k0gn-9gOFWF9bVuFVpV8sho6RNJiLr3TSkEACEWU",
            "date": "11/14/2023, 02:31 PM, +0100 CET"
          },
          "stories": [
            {
              "position": 1,
              "title": "CPI Report Live Updates: Inflation Eases to 3.2% in October",
              "source": {
                "name": "The New York Times",
                "icon": "https://lh3.googleusercontent.com/tDFSwtr61ZReDD_jw6kEPWegHMSqGEHx-ZS_t-e10We-GfWEPVYkn0uLk_Vn8XQHg8wcnhMWmug",
                "authors": [
                  "Jeanna Smialek"
                ]
              },
              "link": "https://www.nytimes.com/live/2023/11/14/business/cpi-inflation-fed",
              "thumbnail": "https://lh4.googleusercontent.com/proxy/UMzdGaTaMJlERX1fzLCqOm9_a80o276WLHzlHENO1N8tSBPD4-Exl-DCnnKXEkgHejuWe-5Sscev_6avEBKYZnaz3jJOebM27MabMpISNwMSJvFRWY585NzSombsfcUBMV_JD_pC49wbS0f7_mMFG5xANvLYn-Bz2OZrHVLx20i53x3BAweuXRWGJpVnTsGBELBOsF5odZAmyiz80w",
              "story_token": "CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2pqdU9UWENSRXNnR1puWWJtdzZ5Z0FQAQ",
              "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&story_token=CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2pqdU9UWENSRXNnR1puWWJtdzZ5Z0FQAQ",
              "date": "11/14/2023, 03:05 PM, +0100 CET"
            },
            ...
          ],
          "story_token": "CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2pqdU9UWENSRXNnR1puWWJtdzZ5Z0FQAQ",
          "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&story_token=CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2pqdU9UWENSRXNnR1puWWJtdzZ5Z0FQAQ"
        },
        {
          "position": 2,
          "highlight": {
            "title": "Live updates: House to vote on GOP plan to avert government shutdown",
            "source": {
              "name": "The Washington Post",
              "icon": "https://lh3.googleusercontent.com/xkxhhmIcX17VMwusXl2s4VSgJXtQpnU43BCW3Xfi-Jrd-A05vsq0sfcc3cttfxac5dVc8Z2_CXc",
              "authors": [
                "Paul Kane",
                "Derek Hawkins",
                "Kevin Uhrmacher"
              ]
            },
            "link": "https://www.washingtonpost.com/politics/2023/11/14/government-shutdown-updates/",
            "thumbnail": "https://lh6.googleusercontent.com/proxy/xOw7lhjWCbhNkf65ge9NhBLgeqnuY0Q3pXBNUGhjr4s3pSJiY-ZMR_IS7o1lqG4TXGkNANW6uZCzSK6cDxnWYA2PUtWw5jsiiSYuU7_uENXgGKksRnr7KLeQVcEF5Xb1BV0DZr8hIJNvALbEp-CK2XhdpvxoD3FGR4BBqwAcO-ZipLI92-2lhXAH166R8JhHwxupKhqcicwZelr1JoVmAfyfh0IbxFravxNWsXhdm9QgZHU-5-WRudiYcTq-Ja2uyr3Hoqgh6w2nmNMN8XaaZz5n5GFcfvJFp5anRu1Flq11Nw",
            "date": "11/14/2023, 03:15 PM, +0100 CET"
          },
          "stories": [
            {
              "position": 1,
              "title": "Congress to vote on funding the government",
              "source": {
                "name": "FOX 5 New York",
                "icon": "https://yt3.ggpht.com/TfTa8HWjTh-Bc8vuyPrwj0hdrqAxvTnJ6Lkgy1SEN_kyptxPNhKPPd0CIKzaRC-rUmQwXEwJ"
              },
              "link": "https://www.youtube.com/watch?v=L8AOZaLS130",
              "thumbnail": "https://lh5.googleusercontent.com/proxy/alw9iCcaNykwfv638QTgK-qfA1CzDQcR0z7t7uzMMwNzFLg-9nF3QB5uaRW-RBgsb-EtRiKV7QPLgVxVXsyqoqWM5R19cQ_me-sq",
              "video": true,
              "story_token": "CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2lGdXJ2SENSR2diWVhMcFhMUzlDZ0FQAQ",
              "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&story_token=CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2lGdXJ2SENSR2diWVhMcFhMUzlDZ0FQAQ",
              "date": "11/14/2023, 01:14 PM, +0100 CET"
            },
            {
              "position": 2,
              "title": "House GOP pursuing two-step plan to avert government shutdown",
              "source": {
                "name": "Hawaii News Now",
                "icon": "https://yt3.ggpht.com/ytc/APkrFKYy8EgPXYM-SY8DbBWYNw_lNasN5ulCXVFdDnVmFlc"
              },
              "link": "https://www.youtube.com/watch?v=zD_Y8jrfYuw",
              "thumbnail": "https://lh6.googleusercontent.com/proxy/aJzJA7OL2hNbKHxfhfE2DiEj3KUJq4_6Dy1eaAnt9xFDy_D8x5xoMSuiLeKhVckDlzO3DXIenF9C1kTY2Dm6cN6WHbsbq8_WLIz79MNHxg",
              "video": true,
              "story_token": "CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2lGdXJ2SENSR2diWVhMcFhMUzlDZ0FQAQ",
              "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&story_token=CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2lGdXJ2SENSR2diWVhMcFhMUzlDZ0FQAQ",
              "date": "11/14/2023, 04:42 AM, +0100 CET"
            },
            {
              "position": 3,
              "title": "The spotlight is on Speaker Johnson — we need a budget now",
              "source": {
                "name": "The Hill",
                "icon": "https://lh3.googleusercontent.com/4GIV6VDGgeRBBo20kfZHEFjDrgPr1lxJmvxB32KUmZWsAU54y7SD2dfT385jXBnmdBoBMaM29A",
                "authors": [
                  "Elaine McCusker"
                ]
              },
              "link": "https://thehill.com/opinion/national-security/4308050-the-spotlight-is-on-speaker-johnson-we-need-a-budget-now/",
              "thumbnail": "https://lh3.googleusercontent.com/proxy/jo3vTjFFk3bpA4n-J_cWI-wD3JFWfkgAph6BUacJleYD_ohrjmLNnWCBgmmUacRY1cpVUzdQcWbOO6r2B25L9WNYb74h2McmcZXvdQE8DXNcz10Yia8vICcTf7VF6vN6FO99tEl9EbM_A1fh-FZZRLgM5hg_I_KwdF4KiiHGra2cR7EhnQ",
              "type": "Opinion",
              "story_token": "CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2lGdXJ2SENSR2diWVhMcFhMUzlDZ0FQAQ",
              "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&story_token=CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2lGdXJ2SENSR2diWVhMcFhMUzlDZ0FQAQ",
              "date": "11/14/2023, 02:30 PM, +0100 CET"
            }
            ...
          ],
          "story_token": "CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2lGdXJ2SENSR2diWVhMcFhMUzlDZ0FQAQ",
          "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&story_token=CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2lGdXJ2SENSR2diWVhMcFhMUzlDZ0FQAQ"
        },
        ...
      ],
      "menu_links": [
        {
          "title": "U.S.",
          "topic_token": "CAAqIggKIhxDQkFTRHdvSkwyMHZNRGxqTjNjd0VnSmxiaWdBUAE",
          "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&topic_token=CAAqIggKIhxDQkFTRHdvSkwyMHZNRGxqTjNjd0VnSmxiaWdBUAE"
        },
        ...
      ]
    }
    

### [](https://serpapi.com/google-news-api#api-examples-example-with-hip-hop-as-a-topic)Example with`Hip-hop`as a topic

![Example with Hip-hop as a topic](https://serpapi.com/assets/google_news/hip-hop-4f68007c90833b1f5336739264c70ea3a97ca85b5fc55b0c2c7071da147526c0.jpg)

GET

*       https://serpapi.com/search.json?engine=google_news&gl=us&hl=en&topic_token=CAAqJAgKIh5DQkFTRUFvS0wyMHZNR2RzZERZM01CSUNaVzRvQUFQAQ
    

  

Code to integrate

cURLRubyPythonJavaScriptPHP.NETJavaGoRustGoogle Sheets

*   [](https://github.com/serpapi/google-search-results-ruby)[](https://rubygems.org/gems/google_search_results)
    
        require 'google_search_results' 
        
        params = {
          engine: "google_news",
          gl: "us",
          hl: "en",
          topic_token: "CAAqJAgKIh5DQkFTRUFvS0wyMHZNR2RzZERZM01CSUNaVzRvQUFQAQ",
          api_key: "2219e06e0ecbde4eaba834faacc1d84519c512676e20b128e7ba65792f115a33"
        }
        
        search = GoogleSearch.new(params)
        news_results = search.get_hash[:news_results]
        
    

  

JSON Example

[](https://serpapi.com/playground?engine=google_news&gl=us&hl=en&topic_token=CAAqJAgKIh5DQkFTRUFvS0wyMHZNR2RzZERZM01CSUNaVzRvQUFQAQ&highlight=news_results)

    {
      "search_metadata": {
        "id": "6554e7acde98346cb79a227c",
        "status": "Success",
        "json_endpoint": "https://serpapi.com/searches/26aaac6032e1b163/6554e7acde98346cb79a227c.json",
        "created_at": "2023-11-15 15:45:48 UTC",
        "processed_at": "2023-11-15 15:45:48 UTC",
        "google_news_url": "https://news.google.com/topics/CAAqJAgKIh5DQkFTRUFvS0wyMHZNR2RzZERZM01CSUNaVzRvQUFQAQ?hl=en&gl=US",
        "raw_html_file": "https://serpapi.com/searches/26aaac6032e1b163/6554e7acde98346cb79a227c.html",
        "total_time_taken": 2.96
      },
      "search_parameters": {
        "engine": "google_news",
        "gl": "us",
        "hl": "en",
        "topic_token": "CAAqJAgKIh5DQkFTRUFvS0wyMHZNR2RzZERZM01CSUNaVzRvQUFQAQ"
      },
      "title": "Hip-hop",
      "news_results": [
        {
          "position": 1,
          "title": "Latest news 🎤 ",
          "stories": [
            {
              "position": 1,
              "title": "The secret to Aidan Hutchinson’s impressive spin moves? Dancing hip-hop and ballet as a kid",
              "source": {
                "name": "The Athletic",
                "icon": "https://lh3.googleusercontent.com/JtT8TIKMBXa1ii26ns4UDfsQe0HmS5NoY5JYbEr18itxEMYs4haETZW6vOwYnXnQlFy6jzUWdg",
                "authors": [
                  "Dan Pompei"
                ]
              },
              "link": "https://theathletic.com/5041445/2023/11/15/aidan-hutchinson-detroit-lions-dance/",
              "thumbnail": "https://lh5.googleusercontent.com/proxy/kXLFqb5xgsUBH_swnLuv_27yzGPKsupC4B8JvSNtdpElOpJg5injpbNxGALRlpJo77S91PpBE2IAn9-6kmOfh-xPkNIpNp_oQcbc0uIfc-lvk7ipVi0H4o6x4BGlWgqIffc0ri3oWNr3aeR60w3YmKiTuO9VVPdNRhXFiqRp9DIo8W3V9Z1hmxnhzBlG-TrTBrMNYAos91Oj9mlFwmpDOpx9",
              "date": "11/15/2023, 11:01 AM, +0100 CET"
            },
            ...
          ]
        },
        {
          "position": 2,
          "title": "Subgenres",
          "related_topics": [
            {
              "position": 1,
              "name": "Crunk",
              "topic_token": "CAAqIggKIhxDQkFTRHdvSkwyMHZNREY1TW0xeEVnSmxiaWdBUAE",
              "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&topic_token=CAAqIggKIhxDQkFTRHdvSkwyMHZNREY1TW0xeEVnSmxiaWdBUAE"
            },
            {
              "position": 2,
              "name": "Jazz rap",
              "topic_token": "CAAqIggKIhxDQkFTRHdvSkwyMHZNREZtT1hsZkVnSmxiaWdBUAE",
              "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&topic_token=CAAqIggKIhxDQkFTRHdvSkwyMHZNREZtT1hsZkVnSmxiaWdBUAE"
            },
            {
              "position": 3,
              "name": "Gangsta rap",
              "topic_token": "CAAqIQgKIhtDQkFTRGdvSUwyMHZNRE0yYW5ZU0FtVnVLQUFQAQ",
              "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&topic_token=CAAqIQgKIhtDQkFTRGdvSUwyMHZNRE0yYW5ZU0FtVnVLQUFQAQ"
            },
            ...
          ]
        },
        {
          "position": 3,
          "title": "Concerts & festivals",
          "stories": [
            {
              "position": 1,
              "title": "Organizers: 'Uneasy' T-Pain to skip Tallahassee hip-hop concert",
              "source": {
                "name": "Tallahassee Democrat",
                "icon": "https://encrypted-tbn2.gstatic.com/faviconV2?url=https://www.tallahassee.com&client=NEWS_360&size=96&type=FAVICON&fallback_opts=TYPE,SIZE,URL",
                "authors": [
                  "Alaijah Brown"
                ]
              },
              "link": "https://www.tallahassee.com/story/news/local/2023/11/10/t-pain-to-skip-tallahassee-hip-hop-concert-organizers-blame-leon-county-commissioner-comments/71530310007/",
              "thumbnail": "https://lh6.googleusercontent.com/proxy/plnvEa-ekW0bIzTGW57YdNYyz_eBZyx0_9Jb97dRRcW-ZfvvWwHVWNZo2Vl_6cTzmDlC-c5JVdhPUB6RgcEQCld-z9EOtxv0uiW4WEl5V7jhGeH9tDhnjUiM2Ho8OZXU9R1vRKGgyYbC_4RivUhx3ISMUD1H1Z2qa5j2BjgfKUWesDnoa3_EiOwV-kGfHESykDTx9mCzdvQc0oOSsWsQHOU_7GjLERf5eV6GLIb0zaOQ3CRMnBw4e-KjAXaWvFNStBRZiQ",
              "story_token": "CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2laOS1fV0NSR3U2WHltWGpTODdpZ0FQAQ",
              "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&story_token=CAAqNggKIjBDQklTSGpvSmMzUnZjbmt0TXpZd1NoRUtEd2laOS1fV0NSR3U2WHltWGpTODdpZ0FQAQ",
              "date": "11/10/2023, 09:18 PM, +0100 CET"
            },
            ...
          ],
          "topic_token": "CAAqBwgKMK-mjQswtIyfAw",
          "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&topic_token=CAAqBwgKMK-mjQswtIyfAw"
        },
        ...
      ],
      "menu_links": [
        {
          "title": "U.S.",
          "topic_token": "CAAqIggKIhxDQkFTRHdvSkwyMHZNRGxqTjNjd0VnSmxiaWdBUAE",
          "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&topic_token=CAAqIggKIhxDQkFTRHdvSkwyMHZNRGxqTjNjd0VnSmxiaWdBUAE"
        },
        ...
      ],
      "sub_menu_links": [
        {
          "title": "Hip-hop",
          "section_token": "CAQqEAgAKgcICjChovMKMOGr2gIwtbfUAw",
          "topic_token": "CAAqJAgKIh5DQkFTRUFvS0wyMHZNR2RzZERZM01CSUNaVzRvQUFQAQ",
          "serpapi_link": "https://serpapi.com/search.json?engine=google_news&gl=us&section_token=CAQqEAgAKgcICjChovMKMOGr2gIwtbfUAw&topic_token=CAAqJAgKIh5DQkFTRUFvS0wyMHZNR2RzZERZM01CSUNaVzRvQUFQAQ"
        }
      ]
    }
    

*   [Api Status](https://serpapi.com/status) ‧
*   [GitHub](https://github.com/serpapi) ‧
*   [Legal](https://serpapi.com/legal) ‧
*   [Security](https://serpapi.com/security) ‧
*   [Libraries](https://serpapi.com/libraries) ‧
*   [Release Notes](https://serpapi.com/release-notes) ‧
*   [Public Roadmap](https://github.com/serpapi/public-roadmap) ‧
*   [Support](mailto:support@serpapi.com)

© 2016-2024 SerpApi, LLC.