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
import sys
import pyupbit
import json
import ta
import requests
import datetime
import traceback

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from pydantic import BaseModel, Field
from enum import Enum
from typing import Literal


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

UseCacheNews = False
UseCacheYoutube = False

# Enable TestMode
# UseCacheNews = True
# UseCacheYoutube = True


def get_fear_and_greed_index():
    url = "https://api.alternative.me/fng/"
    result = requests.get(url)
    if result.status_code == 200:
        data = result.json()
        return {
            "value": int(data["data"][0]["value"]),
            "classification": data["data"][0]["value_classification"],
        }
    else:
        return None


def get_news_headlines():

    data = None

    ###############################################################
    # 데이터 가져오기
    if not UseCacheNews:
        api_key = os.getenv("SERPAPI_API_KEY")
        params = {
            "engine": "google_news",
            "q": f"{target} {target_name} cryptocurrency",
            "api_key": api_key,
        }

        url = "https://serpapi.com/search"

        # try:
        result = requests.get(url, params=params)
        result.raise_for_status()
        data = result.json()

        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cache/news_{now}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        # except requests.RequestException as e:
        # 오류 발생시 멈춰야함
    else:
        data = json.load(
            open(
                "cache/"
                + max(
                    [
                        f
                        for f in os.listdir("cache")
                        if f.startswith("news_") and f.endswith(".json")
                    ],
                    key=lambda x: os.path.getctime(os.path.join("cache", x)),
                ),
                "r",
                encoding="utf-8",
            )
        )

    news_result = data.get("news_results", [])
    headlines = []
    tempHeadlines = []
    for news in news_result:
        headline = {
            "title": news.get("title", ""),
            "date": news.get("date", ""),
        }

        tempHeadlines.append(headline)
        if len(json.dumps(tempHeadlines)) > limit_news:
            break

        headlines.append(headline)

    return headlines


# 유튜브에서 최신 관련 영상을 찾아온다.
# 찾아온 영상은 제목, 설명, 조회수, 좋아요, 구독자수, 캡션을 갖고있다.
def get_youtube_captions():

    ###############################################################
    # 데이터 가져오기
    if not UseCacheYoutube:
        api_key = os.getenv("YOUTUBE_API_KEY")
        youtube = build("youtube", "v3", developerKey=api_key)

        # 현재 시간부터 1일 전의 날짜-시간을 구합니다
        one_day_ago = (
            datetime.datetime.now() - datetime.timedelta(days=1)
        ).isoformat() + "Z"

        search_result = (
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
        for item in search_result["items"]:
            video_id = item["id"]["videoId"]
            channel_id = item["snippet"]["channelId"]

            # 비디오 통계 가져오기
            video_result = (
                youtube.videos().list(part="statistics", id=video_id).execute()
            )

            # 채널 통계 가져오기
            channel_result = (
                youtube.channels().list(part="statistics", id=channel_id).execute()
            )

            # 통계 정보 추가
            item["statistics"] = {
                "viewCount": video_result["items"][0]["statistics"]["viewCount"],
                "likeCount": video_result["items"][0]["statistics"]["likeCount"],
                "subscriberCount": channel_result["items"][0]["statistics"][
                    "subscriberCount"
                ],
            }

        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cache/youtubelist_{now}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(search_result, f, ensure_ascii=False, indent=4)
    else:
        search_result = json.load(
            open(
                "cache/"
                + max(
                    [
                        f
                        for f in os.listdir("cache")
                        if f.startswith("youtubelist_") and f.endswith(".json")
                    ],
                    key=lambda x: os.path.getctime(os.path.join("cache", x)),
                ),
                "r",
                encoding="utf-8",
            )
        )

    # 비디오가 1개라도 없는 상황 확인
    if not search_result.get("items") or len(search_result["items"]) == 0:
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
    for item in search_result["items"]:
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
        search_result["items"] = filtered_items
        search_result["pageInfo"]["totalResults"] = len(filtered_items)

    ###############################################################
    # 정렬

    # search_response를 점수 기반으로 내림차순 정렬
    def calculate_score(item):
        view_count = int(item["statistics"]["viewCount"])
        like_count = int(item["statistics"]["likeCount"])
        subscriber_count = int(item["statistics"]["subscriberCount"])
        return view_count + (like_count * 5) + (subscriber_count * 10)

    search_result["items"] = sorted(
        search_result["items"], key=calculate_score, reverse=True
    )

    ###############################################################
    # 캡션 가져오기

    captions = []
    for index, item in enumerate(search_result["items"]):
        video_id = item["id"]["videoId"]
        filename = f"cache/video_{video_id}.json"

        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                caption = json.load(f)
        else:
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

                with open(filename, "w", encoding="utf-8") as f:
                    f.write(json.dumps(caption, ensure_ascii=False, indent=4))

            except Exception as e:
                caption = None
                Log(f"[Youtube] Get Caption Error: {str(e)}")

        if caption and "caption" in caption and len(caption["caption"]) > 0:
            captions.append(caption)

    ###############################################################
    # 3000자를 넘는 캡션만 필터링
    minimum_caption_length = int(os.getenv("MINIMUM_CAPTION_LENGTH", 1000))
    filtered_captions = [
        caption
        for caption in captions
        if len(caption["caption"]) > minimum_caption_length
    ]

    if not filtered_captions:
        return captions[0]
    else:
        return filtered_captions[0]


class TradingDecisionEnum(str, Enum):
    buy = "buy"
    sell = "sell"
    hold = "hold"


class TradingDecision(BaseModel):
    decision: TradingDecisionEnum = Field(
        ..., description="The trading decision: 'buy', 'sell', or 'hold'"
    )
    reason: str = Field(..., description="Detailed reason for the trading decision")
    percentage: float = Field(
        ...,
        description="Percentage of KRW to use for buying or ETH to sell. Must be between 0 and 100.",
    )


def ai_trading():

    # 초기화하기
    client = OpenAI()
    Log("Create OpenAI Client")

    upbit = pyupbit.Upbit(upbit_akey, upbit_skey)
    Log("Create Upbit Client")

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

    Log("[Upbit] GetBalances", {currency: currency_balance, target: target_balance})

    # 2. 오더북(호가 데이터) 조회
    orderbook = pyupbit.get_orderbook(trade_code)
    Log("[Upbit] Get Orderbook", orderbook)

    # 시간봉
    df_hourly = pyupbit.get_ohlcv(
        trade_code, interval="minute60", count=limit_hourly_count
    )
    df_hourly = df_hourly.dropna()
    df_hourly = add_indicators(df_hourly)
    df_hourly = df_hourly.to_json()
    Log("[Upbit] Get OHLCV Hourly", json.loads(df_hourly))

    # 일봉
    df_daily = pyupbit.get_ohlcv(trade_code, interval="day", count=limit_daily_count)
    df_daily = df_daily.dropna()
    df_daily = add_indicators(df_daily)
    df_daily = df_daily.to_json()
    Log("[Upbit] Get OHLCV Daily", json.loads(df_daily))

    # 주봉 추가
    df_weekly = pyupbit.get_ohlcv(trade_code, interval="week", count=limit_weekly_count)
    df_weekly = df_weekly.dropna()
    df_weekly = add_indicators(df_weekly)
    df_weekly = df_weekly.to_json()
    Log("[Upbit] Get OHLCV Weekly", json.loads(df_weekly))

    # 공포탐욕지수 가져오기
    fng_index = get_fear_and_greed_index()
    Log("[Upbit] Get Fear and Greed Index", fng_index)

    # 뉴스 헤드라인 가져오기
    news_headlines = get_news_headlines()
    Log("[Upbit] Get Google News", news_headlines)

    # YouTube 캡션 가져오기
    youtube_caption = get_youtube_captions()
    Log("[Upbit] Get Youtube captions", youtube_caption)

    # 2. AI에게 데이터 제공하고 판단 받기
    systemMessage = f"""You are an expert in {target_name} investing. 
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

9. If you decide to buy or sell, please specify the percentage of {currency} to use for buying or {target} to sell. This should be based on your confidence in the decision and market conditions.

Respond with:
1. A decision (buy, sell, or hold)
2. A detailed explanation of the current market situation and future outlook
3. The percentage of '{currency}' to use for buying or '{target}' to sell (between 0 and 100)

Important: Ensure that the percentage is a number between 0 and 100. Do not use percentages outside this range.
Important: The percentage must be a number between 0 and 100. Do not use percentages outside this range."""
    Log("[GPT] Create System Message", systemMessage)

    userMessage = f"""Current investment status: {json.dumps(filtered_balances)}
Oderbook: {json.dumps(orderbook)}
Hourly OHLCV with indicators: {df_hourly}
Daily OHLCV with indicators: {df_daily}
Weekly OHLCV with indicators: {df_weekly}
Fear and Greed Index: {json.dumps(fng_index)}
Latest News Headlines: {json.dumps(news_headlines)}
YouTube Video Information: {json.dumps(youtube_caption)}"""
    Log("[GPT] Create User Message", userMessage)

    responseFormat = {
        "type": "json_schema",
        "json_schema": {
            "name": TradingDecision.__name__,
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "decision": {
                        "type": "string",
                        "description": "The trading decision: 'buy', 'sell', or 'hold'",
                        "enum": ["buy", "sell", "hold"],
                    },
                    "reason": {
                        "type": "string",
                        "description": "Detailed reason for the trading decision",
                    },
                    "percentage": {
                        "type": "number",
                        "description": "Percentage of KRW to use for buying or ETH to sell. Must be between 0 and 100.",
                    },
                },
                "required": ["decision", "reason", "percentage"],
                "additionalProperties": False,
            },
        },
    }

    Log("[GPT] Request GPT")
    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {
                "role": "system",
                "content": systemMessage,
            },
            {
                "role": "user",
                "content": userMessage,
            },
        ],
        temperature=1,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format=responseFormat,
    )

    Log("[GPT] Response GPT", response)

    result = json.loads(response.choices[0].message.content)
    trading_decision = TradingDecision(**result)
    Log("[GPT] Result", trading_decision)

    decision = trading_decision.decision
    reason = trading_decision.reason
    percentage = trading_decision.percentage

    # 3. AI의 판단에 따라 실제 매수매도하기

    if decision == "buy":
        # 매수
        Log(f"[Upbit] Buy({percentage * currency_balance['balance']})")
    elif decision == "sell":
        # 매도
        Log(f"[Upbit] Sell({percentage * target_balance['balance']})")
    elif decision == "hold":
        # 지나감
        Log(f"[Upbit] Hold")


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


LogFileName = ""
LogData = []


def Log(name, data=None):
    time = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=9))
    ).strftime("%Y-%m-%d %H:%M:%S.%f%z")[:-3]

    print(f"{time} {name}")

    # 디렉토리가 없으면 생성
    os.makedirs(os.path.dirname(LogFileName), exist_ok=True)

    # data를 JSON으로 저장 가능한 형태로 변환
    if data and not isinstance(data, (str, dict, list)):
        try:
            data = json.loads(json.dumps(Dump(data)))
        except:
            data = str(data)

    LogData.append(
        {
            "time": time,
            "name": name,
            "data": data,
        }
    )

    # 파일 열기 모드를 'a'로 변경하여 append 모드로 열기
    with open(LogFileName, "w", encoding="utf-8") as f:
        f.write(json.dumps(LogData, indent=4, ensure_ascii=False))  # 줄바꿈 추가


def Dump(data):
    if isinstance(data, (int, float, str, bool, type(None))):
        return data

    try:
        json.dumps(data)
        return data
    except:
        pass  # JSON으로 직렬화할 수 없는 경우 계속 진행

    if isinstance(data, dict):
        rst = {}
        for key, value in data.items():
            rst[key] = Dump(value)
    elif isinstance(data, list):
        rst = []
        for item in data:
            rst.append(Dump(item))
    elif isinstance(data, Enum):
        rst = data.value
    elif hasattr(data, "__dict__"):
        rst = Dump(data.__dict__)
    else:
        rst = data

    return rst


while True:
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    LogFileName = f"history/{now}.log"
    LogData = []

    try:
        ai_trading()
        time.sleep(3600)
    except Exception as e:
        print(e, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        Log(f"Error {e}", str(traceback.format_exc()))
        time.sleep(60)
