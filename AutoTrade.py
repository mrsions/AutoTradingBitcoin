# 프로그램 정의:
# 이 코드는 주기적으로 여러가지의 코인(예:이더리움) 정보를 수집해서 GPT에게 매매의사를 판단하게하고
# 실제로 upbit의 api를 사용하여 매매를 진행해 수익을 만드는 프로그램이다.

# 주요 기능 및 의도:
# 1. Upbit API를 사용하여 암호화폐 시장 데이터 수집
#    - 실시간 시장 동향 파악을 위해 OHLCV 데이터와 오더북 정보를 가져옵니다.
# 2. 기술적 지표 계산 및 공포/탐욕 지수 조회
#    - RSI, MACD, 볼린저 밴드 등의 지표를 계산하여 시장 분석에 활용합니다.
#    - 공포/탐욕 지수를 통해 전반적인 시장 심리를 파악합니다.
# 3. GPT 모델을 활용한 매매 결정 분석
#    - 수집된 데이터와 계산된 지표를 AI에 제공하여 매매 결정을 요청합니다.
#    - AI의 분석을 통해 객관적이고 데이터 기반의 거래 결정을 내립니다.
# 4. Upbit를 통한 실제 매매 실행
#    - AI의 결정에 따라 실제 거래소에서 매수/매도 주문을 실행합니다.
#    - 시장 상황에 따라 지정가 또는 시장가 주문을 사용합니다.
# 5. 주기적인 모니터링 및 거래 실행 (10분 간격)
#    - 지속적인 시장 모니터링을 통해 변화하는 시장에 대응합니다.
#    - 10분 간격으로 전체 프로세스를 반복하여 최신 정보로 거래 결정을 업데이트합니다.

# 이 자동화된 거래 시스템은 24시간 운영되며, 감정을 배제한 객관적인 거래 결정을
# 내리는 것을 목표로 합니다. 다만, 암호화폐 시장의 높은 변동성과 예측 불가능성으로 인해
# 항상 주의가 필요하며, 지속적인 모니터링과 시스템 개선이 요구됩니다.


# 라이브러리 가져오기
import os
import re
import time
from dotenv import load_dotenv
from openai import OpenAI
import pyupbit
import json
import ta
import pandas as pd
import requests
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from datetime import datetime, timedelta

# Pandas 출력 옵션 설정
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

load_dotenv()
upbit_akey = os.getenv("UPBIT_ACCESS_KEY")
upbit_skey = os.getenv("UPBIT_SECRET_KEY")
openai_key = os.getenv("OPENAI_API_KEY")
currency = os.getenv("CURRENCY")  # KRW
currency_name = os.getenv("CURRENCY_NAME")  # won
target = os.getenv("TARGET")  # ETH
target_name = os.getenv("TARGET_NAME")  # Ethereum
trade_code = os.getenv("TRADE_CODE")
limit_news = int(os.getenv("LIMIT_NEWS", 3000))
limit_daily_count = int(os.getenv("LIMIT_DAILY_COUNT", 60))
limit_hourly_count = int(os.getenv("LIMIT_HOURLY_COUNT", 60))
limit_weekly_count = int(os.getenv("LIMIT_WEEKLY_COUNT", 60))


def get_fear_and_greed_index():
    url = "https://api.alternative.me/fng/"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "value": int(data["data"][0]["value"]),
            "classification": data["data"][0]["value_classification"],
        }
    else:
        return None


def get_news_headlines():
    api_key = os.getenv("SERPAPI_API_KEY")
    params = {
        "engine": "google_news",
        "q": f"{target} {target_name} cryptocurrency",
        "api_key": api_key,
    }

    url = "https://serpapi.com/search"

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        news_result = data.get("news_results", [])
        headlines = []
        tempHeadlines = []
        for news in news_result:
            headline = {"title": news.get("title", ""), "date": news.get("date", "")}

            tempHeadlines.append(headline)
            if len(json.dumps(tempHeadlines)) > limit_news:
                break

            headlines.append(headline)

        return headlines
    except requests.RequestException as e:
        print(f"뉴스 헤드라인을 가져오는 중 오류 발생: {e}")
        return []


def get_news_headlines():

    testApi = True

    api_key = os.getenv("SERPAPI_API_KEY")
    params = {
        "engine": "google_news",
        "q": f"{target} {target_name} cryptocurrency",
        "api_key": api_key,
    }

    url = "https://serpapi.com/search"

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        news_result = data.get("news_results", [])
        headlines = []
        tempHeadlines = []
        for news in news_result:
            headline = {"title": news.get("title", ""), "date": news.get("date", "")}

            tempHeadlines.append(headline)
            if len(json.dumps(tempHeadlines)) > limit_news:
                break

            headlines.append(headline)

        return headlines
    except requests.RequestException as e:
        print(f"뉴스 헤드라인을 가져오는 중 오류 발생: {e}")
        return []


# 유튜브에서 최신 관련 영상을 찾아온다.
# 찾아온 영상은 제목, 설명, 조회수, 좋아요, 구독자수, 캡션을 갖고있다.
def get_youtube_captions():

    testApi = True

    ###############################################################
    # 데이터 가져오기
    if not testApi:
        api_key = os.getenv("YOUTUBE_API_KEY")
        youtube = build("youtube", "v3", developerKey=api_key)

        # 현재 시간부터 1일 전의 날짜-시간을 구합니다
        one_day_ago = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"

        search_response = (
            youtube.search()
            .list(
                q=f"{target_name} price prediction",
                type="video",
                publishedAfter=one_day_ago,
                maxResults=10,
                order="relevance",
                videoCaption="closedCaption",
                videoDuration="medium",
                relevanceLanguage="en",
                part="id,snippet",
            )
            .execute()
        )

        # 조회수, 좋아요, 채널구독수 추가
        for item in search_response["items"]:
            video_id = item["id"]["videoId"]
            channel_id = item["snippet"]["channelId"]

            # 비디오 통계 가져오기
            video_response = (
                youtube.videos().list(part="statistics", id=video_id).execute()
            )

            # 채널 통계 가져오기
            channel_response = (
                youtube.channels().list(part="statistics", id=channel_id).execute()
            )

            # 통계 정보 추가
            item["statistics"] = {
                "viewCount": video_response["items"][0]["statistics"]["viewCount"],
                "likeCount": video_response["items"][0]["statistics"]["likeCount"],
                "subscriberCount": channel_response["items"][0]["statistics"][
                    "subscriberCount"
                ],
            }

        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"response/youtubelist_{now}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(search_response, f, ensure_ascii=False, indent=4)
    else:
        search_response = json.load(
            open(
                "response/"
                + max(
                    [
                        f
                        for f in os.listdir("response")
                        if f.startswith("youtubelist_") and f.endswith(".json")
                    ],
                    key=lambda x: os.path.getctime(os.path.join("response", x)),
                ),
                "r",
                encoding="utf-8",
            )
        )

    # 비디오가 1개라도 없는 상황 확인
    if not search_response.get("items") or len(search_response["items"]) == 0:
        return None

    ###############################################################
    # 필터링

    # TARGET_KEYWORDS를 환경 변수에서 가져오기
    target_keywords = os.getenv("TARGET_KEYWORDS", "").strip()
    keywords_list = [
        keyword.strip() for keyword in target_keywords.split(",") if keyword.strip()
    ]

    # TARGET_KEYWORDS에 해당하는 영상만 필터링
    filtered_items = []
    for item in search_response["items"]:
        title = item["snippet"]["title"]
        description = item["snippet"]["description"]

        if any(
            re.search(keyword, title, re.IGNORECASE)
            or re.search(keyword, description, re.IGNORECASE)
            for keyword in keywords_list
        ):
            filtered_items.append(item)

    # 필터링된 영상이 1개 이상 있으면 search_response 업데이트
    if filtered_items:
        search_response["items"] = filtered_items
        search_response["pageInfo"]["totalResults"] = len(filtered_items)

    ###############################################################
    # 정렬

    # search_response를 점수 기반으로 내림차순 정렬
    def calculate_score(item):
        view_count = int(item["statistics"]["viewCount"])
        like_count = int(item["statistics"]["likeCount"])
        subscriber_count = int(item["statistics"]["subscriberCount"])
        return view_count + (like_count * 5) + (subscriber_count * 10)

    search_response["items"] = sorted(
        search_response["items"], key=calculate_score, reverse=True
    )

    ###############################################################
    # 캡션 가져오기

    captions = []
    for index, item in enumerate(search_response["items"]):
        video_id = item["id"]["videoId"]

        jsonData = ""
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            caption_text = " ".join([entry["text"] for entry in transcript])
            caption = {
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "view_count": item["statistics"]["viewCount"],
                "like_count": item["statistics"]["likeCount"],
                "subscriber_count": item["statistics"]["subscriberCount"],
                "caption": caption_text,
            }
            captions.append(caption)
            jsonData = json.dumps(caption, ensure_ascii=False, indent=4)
        except Exception as e:
            jsonData = f"{jsonData}\n{e}"

        filename = f"response/video_{index}_{video_id}.json"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(jsonData)

    ###############################################################
    # 3000자를 넘는 캡션만 필터링
    filtered_captions = [
        caption
        for caption in captions
        if len(caption["caption"]) > int(os.getenv("MINIMUM_CAPTION_LENGTH", 1000))
    ]

    if not filtered_captions:
        return captions[0]
    else:
        return filtered_captions[0]


def ai_trading():

    # 초기화하기
    client = OpenAI()
    upbit = pyupbit.Upbit(upbit_akey, upbit_skey)

    # 1. 업비트 차트데이터 가져오기
    all_balances = upbit.get_balances()
    filtered_balances = [
        balance for balance in all_balances if balance["currency"] in [currency, target]
    ]

    # region Response Json
    # {
    #    "currency": "KRW",
    #    "balance": "5452609.30591501",
    #    "locked": "0",
    #    "avg_buy_price": "0",
    #    "avg_buy_price_modified": true,
    #    "unit_currency": "KRW"
    # }
    # endregion
    currency_balance = next(
        (balance for balance in all_balances if balance["currency"] == currency), None
    )

    # region Response Json
    # {
    #    "currency": "ETH",
    #    "balance": "0.00144258",
    #    "locked": "0",
    #    "avg_buy_price": "3466000",
    #    "avg_buy_price_modified": false,
    #    "unit_currency": "KRW"
    # }
    # endregion
    target_balance = next(
        (balance for balance in all_balances if balance["currency"] == target), None
    )

    PrintsPretty("BALANCES", {currency: currency_balance, target: target_balance})

    # 2. 오더북(호가 데이터) 조회

    # 호가 데이터
    # region Response Json
    # {
    #     "market": "KRW-ETC",
    #     "timestamp": 1727950005328,
    #     "total_ask_size": 3248.53544706,
    #     "total_bid_size": 3690.19583091,
    #     "orderbook_units": [
    #         {
    #             "ask_price": 24800,
    #             "bid_price": 24790,
    #             "ask_size": 20.140293209999999,
    #             "bid_size": 1
    #         },
    #         {
    #             "ask_price": 24820,
    #             "bid_price": 24780,
    #             "ask_size": 58.572072499999997,
    #             "bid_size": 0.79342568999999996
    #         },
    #         {
    #             "ask_price": 24830,
    #             "bid_price": 24770,
    #             "ask_size": 605.22653410999999,
    #             "bid_size": 625.40363657
    #         },
    #         {
    #             "ask_price": 24840,
    #             "bid_price": 24760,
    #             "ask_size": 106.2,
    #             "bid_size": 4.5032310100000004
    #         },
    #         {
    #             "ask_price": 24850,
    #             "bid_price": 24750,
    #             "ask_size": 400.80823442000002,
    #             "bid_size": 874.87162388000002
    #         },
    #         {
    #             "ask_price": 24860,
    #             "bid_price": 24740,
    #             "ask_size": 864.70000000000005,
    #             "bid_size": 244.78062376
    #         },
    #         {
    #             "ask_price": 24870,
    #             "bid_price": 24730,
    #             "ask_size": 27.787189779999999,
    #             "bid_size": 1142.33004448
    #         },
    #         {
    #             "ask_price": 24880,
    #             "bid_price": 24720,
    #             "ask_size": 0.40192927000000001,
    #             "bid_size": 1.1901207
    #         },
    #         {
    #             "ask_price": 24890,
    #             "bid_price": 24710,
    #             "ask_size": 12.20008133,
    #             "bid_size": 187.16249094
    #         },
    #         {
    #             "ask_price": 24910,
    #             "bid_price": 24700,
    #             "ask_size": 162,
    #             "bid_size": 90.125958650000001
    #         },
    #         {
    #             "ask_price": 24920,
    #             "bid_price": 24690,
    #             "ask_size": 0.80547723999999998,
    #             "bid_size": 26.39334122
    #         },
    #         {
    #             "ask_price": 24930,
    #             "bid_price": 24680,
    #             "ask_size": 251.79753977999999,
    #             "bid_size": 171.703
    #         },
    #         {
    #             "ask_price": 24950,
    #             "bid_price": 24670,
    #             "ask_size": 478.20033776000002,
    #             "bid_size": 242.12445805999999
    #         },
    #         {
    #             "ask_price": 24960,
    #             "bid_price": 24660,
    #             "ask_size": 147.87115413999999,
    #             "bid_size": 10.543309000000001
    #         },
    #         {
    #             "ask_price": 24970,
    #             "bid_price": 24650,
    #             "ask_size": 111.82460352,
    #             "bid_size": 67.270566950000003
    #         }
    #     ],
    #     "level": 0
    # }
    # endregion
    orderbook = pyupbit.get_orderbook(trade_code)

    # 시간봉
    df_hourly = pyupbit.get_ohlcv(
        trade_code, interval="minute60", count=limit_hourly_count
    )
    df_hourly = df_hourly.dropna()
    df_hourly = add_indicators(df_hourly)

    # 일봉
    df_daily = pyupbit.get_ohlcv(trade_code, interval="day", count=limit_daily_count)
    df_daily = df_daily.dropna()
    df_daily = add_indicators(df_daily)

    # 주봉 추가
    df_weekly = pyupbit.get_ohlcv(trade_code, interval="week", count=limit_weekly_count)
    df_weekly = df_weekly.dropna()
    df_weekly = add_indicators(df_weekly)

    PrintsPretty("OrderBook", orderbook)
    Prints("COIN CHART hourly with indicators", df_hourly)
    Prints("COIN CHART daily with indicators", df_daily)
    Prints("COIN CHART weekly with indicators", df_weekly)  # 주봉 데이터 출력

    # 공포탐욕지수 가져오기
    fng_index = get_fear_and_greed_index()
    PrintsPretty("Fear and Greed Index", fng_index)

    # 뉴스 헤드라인 가져오기
    news_headlines = get_news_headlines()
    PrintsPretty("Latest News Headlines", news_headlines)

    # YouTube 캡션 가져오기
    youtube_caption = get_youtube_captions()
    PrintsPretty("YouTube Caption", youtube_caption)

    # 2. AI에게 데이터 제공하고 판단 받기

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"""You are an expert in {target_name} investing. 
Based on the provided chart data, news headlines, YouTube video information, and market indicators, please decide whether to buy, sell, or hold at the current moment.

Please consider the following factors in your analysis:
1. Technical indicators: 
   - RSI (Relative Strength Index)
   - MACD (Moving Average Convergence Divergence)
   - Bollinger Bands
   - Stochastic Oscillator
   - Moving Averages (5-day, 10-day, 20-day)

2. Fear and Greed Index: This index represents the current market sentiment.

3. Latest news headlines: Consider the potential impact of recent news on the market.

4. YouTube video information: Analyze the content of the most relevant recent video about {target_name} price prediction.

5. Chart data:
   - Hourly data: For short-term trend analysis
   - Daily data: For medium-term trend analysis
   - Weekly data: For long-term trend analysis

6. Orderbook data: Use this to assess the current supply and demand situation in the market.

7. Current balance: Consider the amount of {currency} and {target} currently held when making your decision.

8. When making your decision, please consider short-term, medium-term, and long-term perspectives for a comprehensive judgment. Also, please provide a detailed explanation of the current market situation and future outlook.

response in json format.

Response examples:
{{"decision":"buy", "reason":"Detailed reason for buying based on technical indicators, news impact, and YouTube video analysis"}}
{{"decision":"sell", "reason":"Detailed reason for selling based on technical indicators, news impact, and YouTube video analysis"}}
{{"decision":"hold", "reason":"Detailed reason for holding based on technical indicators, news impact, and YouTube video analysis"}}""",
                    }
                ],
            },
            {
                "role": "user",
                "content": f"""Current investment status: {json.dumps(filtered_balances)}
Oderbook: {json.dumps(orderbook)}
Hourly OHLCV with indicators: {df_hourly.to_json()}
Daily OHLCV with indicators: {df_daily.to_json()}
Weekly OHLCV with indicators: {df_weekly.to_json()}
Fear and Greed Index: {json.dumps(fng_index)}
Latest News Headlines: {json.dumps(news_headlines)}
YouTube Video Information: {json.dumps(youtube_caption)}""",
            },
        ],
        temperature=1,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "json_object"},
    )

    print("------------------------------------------------")
    print("-- GPT RESPONSE")
    print("------------------------------------------------")
    print(response)
    print("")

    # json 형식으로 변환
    result = json.loads(response.choices[0].message.content)
    # {
    #   "decision":"hold",
    #   "reason":"The short-term trend shows a sideways movement with recent closing prices reflecting minimal fluctuations. Entering a position now may not provide significant benefits, suggesting a wait-and-see approach until a clearer trend emerges."
    # }

    print("------------------------------------------------")
    print("-- GPT RESULT")
    print("------------------------------------------------")
    print(result)
    print("")
    decision = result["decision"]
    reason = result["reason"]

    # 3. AI의 판단에 따라 실제 매수매도하기

    print("------------------------------------------------")
    print("-- UPBIT Balance")
    print("------------------------------------------------")
    upbit_target_balance = upbit.get_balance(target)
    upbit_currency_balance = upbit.get_balance(currency)

    print(currency + " : ", upbit.get_balance(currency))
    print(target + " : ", upbit.get_balance(target))

    if decision == "buy":
        # 매수
        print("매수")
    elif decision == "sell":
        # 매도
        print("매도")
    elif decision == "hold":
        # 지나감
        print("HOLD")

    upbit.get_balance("KRW")


def add_indicators(df):
    # RSI
    df["RSI"] = ta.momentum.RSIIndicator(df["close"]).rsi()

    # MACD
    macd = ta.trend.MACD(df["close"])
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()
    df["MACD_diff"] = macd.macd_diff()

    # Bollinger Bands
    bollinger = ta.volatility.BollingerBands(df["close"])
    df["BB_high"] = bollinger.bollinger_hband()
    df["BB_low"] = bollinger.bollinger_lband()
    df["BB_mid"] = bollinger.bollinger_mavg()

    # Stochastic Oscillator
    stoch = ta.momentum.StochasticOscillator(df["high"], df["low"], df["close"])
    df["Stoch_k"] = stoch.stoch()
    df["Stoch_d"] = stoch.stoch_signal()

    # 이동평균선 추가
    # for period in [5, 10, 20, 60, 120]:
    for period in [5, 10, 20]:
        df[f"MA_{period}"] = ta.trend.SMAIndicator(
            df["close"], window=period
        ).sma_indicator()

    return df


def PrintsPretty(name, data):
    print("------------------------------------------------")
    print("-- ", name)
    print("------------------------------------------------")
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str):
                try:
                    json_data = json.loads(value)
                    print(
                        f"{key} : {json.dumps(json_data, indent=4, ensure_ascii=False)}"
                    )
                except json.JSONDecodeError:
                    print(f"{key} : {value}")
            else:
                print(f"{key} : {json.dumps(value, indent=4, ensure_ascii=False)}")
    elif isinstance(data, str):
        try:
            json_data = json.loads(data)
            print(json.dumps(json_data, indent=4, ensure_ascii=False))
        except json.JSONDecodeError:
            print(data)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                print(json.dumps(item, indent=4, ensure_ascii=False))
            elif isinstance(item, str):
                try:
                    json_data = json.loads(item)
                    print(json.dumps(json_data, indent=4, ensure_ascii=False))
                except json.JSONDecodeError:
                    print(item)
            else:
                print(item)
    else:
        print(json.dumps(data, indent=4, ensure_ascii=False))


def Prints(name, data):
    print("------------------------------------------------")
    print("-- ", name)
    print("------------------------------------------------")
    if isinstance(data, dict):
        for key, value in data.items():
            print(f"{key} : {value}")
    elif isinstance(data, list):
        for index, item in enumerate(data):
            print(f"{index}: {item}")
    else:
        print(data)


while True:
    try:
        ai_trading()
        time.sleep(600)
    except Exception as e:
        print(e)
        time.sleep(60)
