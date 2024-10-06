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


# youtube 검색 시스템의 한계때문에 하루에 50번 이상 실행할 수 없다.
# gpt-4o-mini의 경우 하루에 $0.15 를 사용한다.


# 라이브러리 가져오기
import glob
import os
import re
import sqlite3
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
import tiktoken
import logging
from contextlib import contextmanager


# Pandas 출력 옵션 설정
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# API 키 관리 개선
load_dotenv()
upbit_akey = os.getenv("UPBIT_ACCESS_KEY")
upbit_skey = os.getenv("UPBIT_SECRET_KEY")
openai_key = os.getenv("OPENAI_API_KEY")
youtube_api_key = os.getenv("YOUTUBE_API_KEY")
currency_code = os.getenv("CURRENCY_CODE")  # KRW
currency_name = os.getenv("CURRENCY_NAME")  # won
target_code = os.getenv("TARGET_CODE")  # ETH
target_name = os.getenv("TARGET_NAME")  # Ethereum
trade_code = os.getenv("TRADE_CODE")
limit_daily_count = int(os.getenv("LIMIT_DAILY_COUNT", 60))
limit_hourly_count = int(os.getenv("LIMIT_HOURLY_COUNT", 60))
limit_weekly_count = int(os.getenv("LIMIT_WEEKLY_COUNT", 60))
db_path = "trading_decisions.sqlite"

MODEL_NAME = "gpt-4o-mini"
MODEL_TOKENIZER_NAME = "gpt-4o-mini"

# 초기화하기
client = OpenAI()
upbit = pyupbit.Upbit(upbit_akey, upbit_skey)

db_decisions_id = "id"
db_decisions_decision = "decision"
db_decisions_percentage = "percentage"
db_decisions_reason = "reason"
db_decisions_currency_code_balance = f"{currency_code.lower()}_balance"
db_decisions_target_code_balance = f"{target_code.lower()}_balance"
db_decisions_target_code_avg_buy_price = f"{target_code.lower()}_avg_buy_price"
db_decisions_trade_code_price = f"{trade_code.lower()}_price"
db_decisions_timestamp = "timestamp"

db_decisions_NAME = "decisions"
db_decisions_COLUMNS = [
    db_decisions_decision,
    db_decisions_percentage,
    db_decisions_reason,
    db_decisions_currency_code_balance,
    db_decisions_target_code_balance,
    db_decisions_target_code_avg_buy_price,
    db_decisions_trade_code_price,
    db_decisions_timestamp,
]

# region db


# 데이터베이스 연결 최적화
@contextmanager
def get_db_connection():
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()


def initialize_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""

CREATE TABLE IF NOT EXISTS {db_decisions_NAME} (
    {db_decisions_id} INTEGER PRIMARY KEY AUTOINCREMENT,
    {db_decisions_decision} TEXT,
    {db_decisions_percentage} REAL,
    {db_decisions_reason} TEXT,
    {db_decisions_currency_code_balance} REAL,
    {db_decisions_target_code_balance} REAL,
    {db_decisions_target_code_avg_buy_price} REAL,
    {db_decisions_trade_code_price} REAL,
    {db_decisions_timestamp} TEXT
);

CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    ticker TEXT,
    trade_type TEXT,
    amount REAL,
    price REAL,
    total_price REAL
)
            """
        )
        conn.commit()


def record_trade(ticker, trade_type, amount, price):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_price = amount * price
        cursor.execute(
            """
        INSERT INTO trades (timestamp, ticker, trade_type, amount, price, total_price)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
            (timestamp, ticker, trade_type, amount, price, total_price),
        )
        conn.commit()


def get_decisions(num_decisions=10):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trading_decisions ORDER BY id DESC LIMIT ?", (num_decisions,))
        decisions = cursor.fetchall()
    return decisions


def record_decision(data):
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Preparing data for insertion
        data_to_insert = (
            data["response"]["decision"],
            data["response"]["percentage"],
            data["response"]["reason"],
            data["wallet"][db_decisions_currency_code_balance],
            data["wallet"][db_decisions_target_code_balance],
            data["wallet"][db_decisions_target_code_avg_buy_price],
            data["trade"][db_decisions_trade_code_price],
            data["trade"]["timestamp"],
        )

        data_to_names = ",".join(db_decisions_COLUMNS)
        data_to_column = ", ".join(["?" for _ in db_decisions_COLUMNS])

        # Inserting data into the database
        cursor.execute(
            f"INSERT INTO {db_decisions_NAME} ({data_to_names}) VALUES ({data_to_column})",
            data_to_insert,
        )

        conn.commit()


# endregion


# region Utils


def get_expect_token_count(text):
    try:
        encoding = tiktoken.encoding_for_model(MODEL_TOKENIZER_NAME)
        return len(encoding.encode(text))
    except ValueError:
        logging.warning(f"Model {MODEL_TOKENIZER_NAME} not found. Using {MODEL_TOKENIZER_NAME} instead.")
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        return len(encoding.encode(text))


def caching(ignore, applyDate, filename, lambda_func):

    # 폴더 생성
    dir = os.path.dirname(filename)
    split = os.path.splitext(filename)
    os.makedirs(dir, exist_ok=True)

    # ignore가 True이면 캐싱을 무시하고 새로운 데이터를 가져옴
    if not ignore:
        if applyDate:
            # 가장 최신 파일 찾기
            files = glob.glob(f"{split[0]}-*{split[1]}")
            latest_file = max(files, key=os.path.getctime) if files else None

            if latest_file:
                with open(latest_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        else:
            # 정확한 파일명으로 찾기
            if os.path.exists(filename) and not ignore:
                with open(filename, "r", encoding="utf-8") as f:
                    return json.load(f)

    data = lambda_func()

    # 파일명에 시간 추가
    if applyDate:
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f")[:-3]
        actual_filename = f"{split[0]}-{timestamp}{split[1]}"
    else:
        actual_filename = filename

    jsonData = json.dumps(force_dumps(data), ensure_ascii=False, indent=4)

    # 새로운 데이터를 항상 파일로 저장
    with open(actual_filename, "w", encoding="utf-8") as f:
        f.write(jsonData)

    return data


def replace_instruction_format(text):

    def apply(text, key, value):
        text = text.replace("{{{" + key.lower() + "}}}", value.lower())
        text = text.replace("{{{" + key.upper() + "}}}", value.upper())
        text = text.replace("{{{" + key.capitalize() + "}}}", value.capitalize())
        return text

    text = apply(text, "target_code", target_code)
    text = apply(text, "currency_code", currency_code)
    text = apply(text, "target_name", target_name)
    text = apply(text, "currency_name", currency_name)
    text = apply(text, "trade_code", trade_code)
    text = apply(text, "limit_daily_count", str(limit_daily_count))
    text = apply(text, "limit_hourly_count", str(limit_hourly_count))
    text = apply(text, "limit_weekly_count", str(limit_weekly_count))
    return text


# endregion


# region Collect Data Utils


def get_fear_and_greed_index():
    url = "https://api.alternative.me/fng/"
    result = requests.get(url)
    if result.status_code == 200:
        data = result.json()
        return {
            "value": int(data["data"][0]["value"]),
            "classification": data["data"][0]["value_classification"],
            "timestamp": data["data"][0]["timestamp"],
        }
    else:
        return None


def get_latest_news():
    from GoogleNews import GoogleNews

    NEWS_REACH_DAYS = os.getenv("NEWS_REACH_DAYS", "14")

    googlenews = GoogleNews(lang="en", region="US")
    googlenews.set_period(f"{NEWS_REACH_DAYS}d")
    googlenews.set_encode("utf-8")

    search_query = f"{target_code} {target_name} cryptocurrency"
    googlenews.search(search_query)

    NEWS_LIMIT_LENGTH = int(os.getenv("NEWS_LIMIT_LENGTH", 3000))

    headlines = []
    tempHeadlines = []
    page = 1
    max_pages = int(os.getenv("NEWS_REACH_PAGES", "5"))

    while page <= max_pages:
        news_results = googlenews.page_at(page)
        for news in news_results:
            headline = {
                "title": news["title"],
                "date": news["date"],
            }

            tempHeadlines.append(headline)
            if len(json.dumps(tempHeadlines)) > NEWS_LIMIT_LENGTH:
                page = max_pages
                break

            headlines.append(headline)

        page += 1
        time.sleep(1)

    googlenews.clear()  # 결과를 지웁니다

    return headlines


def get_latest_youtube():
    """
    유튜브에서 최신 관련 영상을 찾아온다.
    찾아온 영상은 제목, 설명, 조회수, 좋아요, 구독자수, 캡션을 갖고있다.
    """
    ###############################################################

    youtube = build("youtube", "v3", developerKey=youtube_api_key)

    # 현재 시간부터 1일 전의 날짜-시간을 구합니다
    one_day_ago = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat() + "Z"

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
        video_result = youtube.videos().list(part="statistics", id=video_id).execute()

        # 채널 통계 가져오기
        channel_result = youtube.channels().list(part="statistics", id=channel_id).execute()

        # 통계 정보 추가
        item["statistics"] = {
            "viewCount": video_result["items"][0]["statistics"]["viewCount"],
            "likeCount": video_result["items"][0]["statistics"]["likeCount"],
            "subscriberCount": channel_result["items"][0]["statistics"]["subscriberCount"],
        }

    # 비디오가 1개라도 없는 상황 확인
    if not search_result.get("items") or len(search_result["items"]) == 0:
        return None

    ###############################################################
    # 필터링

    # TARGET_KEYWORDS를 환경 변수에서 가져오기
    target_keywords = os.getenv("TARGET_KEYWORDS", "").strip()
    keywords_list = [keyword.strip() for keyword in target_keywords.split(",") if keyword.strip()]

    # TARGET_KEYWORDS에 해당하는 영상만 필터링
    filtered_items = []
    for item in search_result["items"]:
        title = item["snippet"]["title"]
        description = item["snippet"]["description"]

        if any(re.search(keyword, title, re.IGNORECASE) or re.search(keyword, description, re.IGNORECASE) for keyword in keywords_list):
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

    search_result["items"] = sorted(search_result["items"], key=calculate_score, reverse=True)

    ###############################################################
    # 캡션 가져오기

    captions = []
    for index, item in enumerate(search_result["items"]):
        video_id = item["id"]["videoId"]

        caption_text = caching(False, False, f"cache/video_{video_id}.json", lambda: get_video_caption(video_id))

        if caption_text == None:
            continue

        caption = {
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"],
            "view_count": item["statistics"]["viewCount"],
            "like_count": item["statistics"]["likeCount"],
            "subscriber_count": item["statistics"]["subscriberCount"],
            "caption": caption_text,
        }

        if caption and "caption" in caption and len(caption["caption"]) > 0:
            captions.append(caption)

    ###############################################################
    # 3000자를 넘는 캡션만 필터링
    minimum_caption_length = int(os.getenv("MINIMUM_CAPTION_LENGTH", 1000))
    filtered_captions = [caption for caption in captions if len(caption["caption"]) > minimum_caption_length]

    if not filtered_captions:
        return captions[0]
    else:
        return filtered_captions[0]


def get_video_caption(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        caption_text = " ".join([entry["text"] for entry in transcript])
        return caption_text
    except Exception as e:
        log(f"[Youtube] GetCaption Error(videoid={video_id}, exception={str(e)})")
        return None


def get_chart_data():

    # 시간봉
    df_5min = pyupbit.get_ohlcv(trade_code, interval="minute5", count=limit_hourly_count)
    df_hourly = pyupbit.get_ohlcv(trade_code, interval="minute60", count=limit_hourly_count)
    df_daily = pyupbit.get_ohlcv(trade_code, interval="day", count=limit_daily_count)
    df_weekly = pyupbit.get_ohlcv(trade_code, interval="week", count=limit_weekly_count)

    # 지표 추가
    def AddIndicators(df):
        # RSI
        df["RSI_14"] = ta.momentum.RSIIndicator(df["close"], window=14).rsi()

        # MACD
        macd = ta.trend.MACD(df["close"], window_slow=26, window_fast=12, window_sign=9)
        df["MACD_12_26"] = macd.macd()
        df["MACD_signal_9"] = macd.macd_signal()
        df["MACD_diff_12_26_9"] = macd.macd_diff()

        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(df["close"], window=20, window_dev=2)
        df["BB_high_20_2"] = bollinger.bollinger_hband()
        df["BB_low_20_2"] = bollinger.bollinger_lband()
        df["BB_mid_20"] = bollinger.bollinger_mavg()

        # Stochastic Oscillator
        stoch = ta.momentum.StochasticOscillator(df["high"], df["low"], df["close"], window=14, smooth_window=3)
        df["Stoch_k_14_3"] = stoch.stoch()
        df["Stoch_d_14_3"] = stoch.stoch_signal()

        # 이동평균선 추가
        # for period in [5, 10, 20, 60, 120]:
        for period in [5, 10, 20]:
            df[f"SMA_{period}"] = ta.trend.SMAIndicator(df["close"], window=period).sma_indicator()
            df[f"EMA_{period}"] = ta.trend.EMAIndicator(df["close"], window=period).ema_indicator()

        # ATR
        df["ATR_14"] = ta.volatility.AverageTrueRange(df["high"], df["low"], df["close"], window=14).average_true_range()

        # OBV
        df["OBV"] = ta.volume.OnBalanceVolumeIndicator(df["close"], df["volume"]).on_balance_volume()

        return df

    df_5min = AddIndicators(df_5min)
    df_hourly = AddIndicators(df_hourly)
    df_daily = AddIndicators(df_daily)
    df_weekly = AddIndicators(df_weekly)

    combined_df = pd.concat(
        [df_5min, df_hourly, df_daily, df_weekly],
        keys=["5min", "hourly", "daily", "weekly"],
    )
    combined_data = combined_df.to_json(orient="split")

    return combined_data


def get_current_wallet():
    balances = upbit.get_balances()
    rst = {}

    for b in balances:
        if b["currency"].upper() == target_code.upper():
            rst[db_decisions_target_code_balance] = b["balance"]
            rst[db_decisions_target_code_avg_buy_price] = b["avg_buy_price"]
        if b["currency"].upper() == currency_code.upper():
            rst[db_decisions_currency_code_balance] = b["balance"]

    caching(True, True, "cache/wallet.json", lambda: {"source": balances, "result": rst})

    return rst


def get_instruction(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            instructions = file.read()
        return instructions
    except FileNotFoundError:
        print(f"File not found: '{file_path}'")
    except Exception as e:
        print("An error occurred while reading the file: '{file_path}'", e)


def get_orderbook():
    orderbook = pyupbit.get_orderbook(trade_code)
    return orderbook


# endregion

# region Logging Utils


def log(name, data=None):
    if data and not isinstance(data, (str, dict, list)):
        try:
            data = json.loads(json.dumps(force_dumps(data)))
        except:
            data = str(data)

    logging.info(f"{name}: {data}")

    LogData.append(
        {
            "time": datetime.datetime.now().isoformat(),
            "name": name,
            "data": data,
        }
    )


def force_dumps(data) -> dict:
    """객체까지 강제로 dictionary로 변경한다."""

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
            rst[key] = force_dumps(value)
    elif isinstance(data, list):
        rst = []
        for item in data:
            rst.append(force_dumps(item))
    elif isinstance(data, Enum):
        rst = data.value
    elif hasattr(data, "__dict__"):
        rst = force_dumps(data.__dict__)
    else:
        rst = data

    return rst


LogFileName = ""
LogData = []


def begin_log():
    global LogFileName, LogData

    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    LogFileName = f"history/{now}.log"
    LogData = []


def end_log():
    global LogFileName, LogData

    # 디렉토리가 없으면 생성
    os.makedirs(os.path.dirname(LogFileName), exist_ok=True)

    # 파일 열기 모드를 'a'로 변경하여 append 모드로 열기
    with open(LogFileName, "w", encoding="utf-8") as f:
        f.write(json.dumps(LogData, indent=4, ensure_ascii=False))  # 줄바꿈 추가


# endregion


class TradingDecisionEnum(str, Enum):
    buy = "buy"
    sell = "sell"
    hold = "hold"


class TradingDecision(BaseModel):
    decision: TradingDecisionEnum = Field(..., description="The trading decision: 'buy', 'sell', or 'hold'")
    reason: str = Field(..., description="Detailed reason for the trading decision")
    percentage: float = Field(
        ...,
        description="Percentage of KRW to use for buying or ETH to sell. Must be between 0 and 100.",
    )


def get_trading_decision_model_format():
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "TradingDecision",
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


def execute_buy(ticker, amount):
    try:
        order = upbit.buy_market_order(ticker, amount)
        if "error" in order:
            log(f"[Upbit] Buy failed: {order['error']['message']}")
            return False

        time.sleep(1)  # API 요청 제한 고려
        order_info = upbit.get_order(order["uuid"])

        if order_info["state"] == "done":
            executed_volume = float(order_info["executed_volume"])
            trades = order_info["trades"]
            if trades:
                avg_price = sum(float(trade["price"]) * float(trade["volume"]) for trade in trades) / executed_volume
                record_trade(ticker, "buy", executed_volume, avg_price)
                log(f"[Upbit] Buy success: {ticker} {executed_volume} @ {avg_price}")
                return True
    except Exception as e:
        log(f"[Upbit] Buy error: {str(e)}")
    return False


def execute_sell(ticker, amount):
    try:
        order = upbit.sell_market_order(ticker, amount)
        if "error" in order:
            log(f"[Upbit] Sell failed: {order['error']['message']}")
            return False

        time.sleep(1)  # API 요청 제한 고려
        order_info = upbit.get_order(order["uuid"])

        if order_info["state"] == "done":
            executed_volume = float(order_info["executed_volume"])
            trades = order_info["trades"]
            if trades:
                avg_price = sum(float(trade["price"]) * float(trade["volume"]) for trade in trades) / executed_volume
                record_trade(ticker, "sell", executed_volume, avg_price)
                log(f"[Upbit] Sell success: {ticker} {executed_volume} @ {avg_price}")
                return True
    except Exception as e:
        log(f"[Upbit] Sell error: {str(e)}")
    return False


def execute_trading():
    # Db 초기화
    initialize_db()

    # 데이터 가져오기
    newsData = caching(True, True, "cache/news.json", lambda: get_latest_news())
    log("[Collect] GetLatestNews()", newsData)
    youtubeData = caching(True, True, "cache/youtube.json", lambda: get_latest_youtube())
    log("[Collect] GetLatestYoutube()", youtubeData)
    lastDecisions = get_decisions()
    log("[Collect] GetLastDecisions()", lastDecisions)
    fngData = get_fear_and_greed_index()
    log("[Collect] GetFearAndGreedIndex()", fngData)
    chartData = get_chart_data()
    log("[Collect] GetChartData()", chartData)
    orderbook = get_orderbook()
    log("[Collect] GetOrderbook()", orderbook)
    wallet = get_current_wallet()
    wallet["timestamp"] = orderbook["timestamp"]
    log("[Collect] GetCurrentWallet()", wallet)

    # 명령어 입력
    messages = [
        {"role": "system", "content": replace_instruction_format(get_instruction("Instruction.txt"))},
        {"role": "user", "content": "Latest News: " + json.dumps(force_dumps(newsData), ensure_ascii=False)},
        {"role": "user", "content": "Latest Youtube: " + json.dumps(force_dumps(youtubeData), ensure_ascii=False)},
        {"role": "user", "content": "Current Charts: " + json.dumps(force_dumps(chartData), ensure_ascii=False)},
        {"role": "user", "content": "Last Decisions: " + json.dumps(force_dumps(lastDecisions), ensure_ascii=False)},
        {"role": "user", "content": "Fear and Greed Index: " + json.dumps(force_dumps(fngData), ensure_ascii=False)},
        {"role": "user", "content": "Upbit Orderbook: " + json.dumps(force_dumps(orderbook), ensure_ascii=False)},
        {"role": "user", "content": "My Wallet: " + json.dumps(force_dumps(wallet), ensure_ascii=False)},
    ]
    log("[GPT] Make request messages.", messages)

    log(f"[GPT] Request GPT({MODEL_NAME}, ExpectTokens: {get_expect_token_count(json.dumps(messages)):,})")
    response = caching(
        True,
        True,
        "cache/gpt.json",
        lambda: client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            store=False,
            response_format=get_trading_decision_model_format(),
            temperature=0.5,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0.1,
            presence_penalty=0.1,
            n=10,
        ),
    )
    if isinstance(response, dict):
        from openai.types.chat import ChatCompletion

        response = ChatCompletion.model_validate(response)

    log(f"[GPT] Response GPT", response)
    log(f"[GPT] Completion_tokens: {response.usage.completion_tokens:,}")
    log(f"[GPT] Prompt_tokens: {response.usage.prompt_tokens:,}")
    log(f"[GPT] Total_tokens: {response.usage.total_tokens:,}")

    trading_decision = TradingDecision(**json.loads(response.choices[0].message.content))
    log("[GPT] Result", trading_decision)

    decision = trading_decision.decision
    reason = trading_decision.reason
    percentage = trading_decision.percentage
    target_balance = wallet[f"{target_code.lower()}_balance"]
    currency_balance = wallet[f"{currency_code.lower()}_balance"]

    # 3. AI의 판단에 따라 실제 매수매도하기
    if decision == "buy":
        # 매수
        buy_amount = float(currency_balance) * (percentage / 100)
        if execute_buy(trade_code, buy_amount):
            log(f"[Upbit] Buy completed: {trade_code}, {buy_amount}")
    elif decision == "sell":
        # 매도
        sell_amount = float(target_balance) * (percentage / 100)
        if execute_sell(trade_code, sell_amount):
            log(f"[Upbit] Sell completed: {trade_code}, {sell_amount}")
    elif decision == "hold":
        # 지나감
        log(f"[Upbit] Hold")


while True:

    try:
        begin_log()

        execute_trading()

        end_log()

        time.sleep(3600)

    except Exception as e:
        print(e, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        time.sleep(60)
