# ----------------------------------------------------------------------------------------------------
# README.md:
"""
# 암호화폐 자동 매매 프로그램

이 프로그램은 주기적으로 암호화폐 데이터를 수집한 후, GPT 모델을 활용해 매매 결정을 내리고 Upbit API를 통해 자동으로 거래를 실행하는 시스템입니다. 감정에 영향을 받지 않는 객관적이고 데이터 기반의 거래 결정을 내리며, 실시간 시장 데이터를 반영하여 매매를 자동으로 수행합니다.

## 주요 기능

1. **암호화폐 데이터 수집**
   - Upbit API를 사용해 실시간 암호화폐 시장 데이터를 수집합니다.
   - OHLCV 데이터(시가, 고가, 저가, 종가, 거래량)와 오더북 정보를 수집하여 시장 동향을 파악합니다.

2. **기술적 지표 계산**
   - RSI, MACD, 볼린저 밴드 등 다양한 기술적 분석 지표를 계산해 시장 분석에 활용합니다.
   - 이 지표들은 현재 시장의 과매수 또는 과매도 상태를 판단하는 데 사용됩니다.

3. **공포/탐욕 지수 조회**
   - 외부 API를 이용해 시장의 공포와 탐욕 지수를 조회하여 전반적인 시장 심리를 파악합니다.
   - 공포와 탐욕 지수는 시장 참여자들의 심리적 상태를 반영하며, 시장의 전환점을 예측하는 데 도움을 줍니다.

4. **GPT 모델을 통한 매매 결정**
   - 수집된 데이터와 기술적 지표를 바탕으로 GPT 모델이 매매 결정을 내립니다.
   - AI는 매수, 매도 또는 보유(홀드)의 결정을 내리며, 그 이유와 매매 비율을 상세히 제공합니다.

5. **Upbit를 통한 실제 매매 실행**
   - GPT 모델의 결정에 따라 Upbit 거래소에서 실제 매매를 실행합니다.
   - 시장 상황에 맞춰 지정가 또는 시장가 주문을 사용하며, 성공적으로 거래가 완료되면 결과를 데이터베이스에 기록합니다.

6. **주기적 모니터링 및 거래 실행**
   - 프로그램은 주기적으로(기본값: 10분) 실행되어 실시간 시장 변화를 반영합니다.
   - 매번 최신 데이터를 수집하고 분석하여 새로운 거래 결정을 내립니다.

"""

# ----------------------------------------------------------------------------------------------------
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
import random

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
from openai.types.chat import ChatCompletion


# ----------------------------------------------------------------------------------------------------
# 프로그램 환경설정
load_dotenv()

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

os.makedirs('logs', exist_ok=True)
class DailyRotatingFileHandler(logging.FileHandler):
    def __init__(self, filename, mode='a', encoding=None, delay=False):
        self.base_filename = filename
        super().__init__(self.get_current_filename(), mode, encoding, delay)

    def get_current_filename(self):
        return self.base_filename.replace('{}', datetime.datetime.now().strftime("%Y%m%d"))

    def emit(self, record):
        current_filename = self.get_current_filename()
        if current_filename != self.baseFilename:
            self.baseFilename = current_filename
            if self.stream:
                self.stream.close()
                self.stream = self._open()
        super().emit(record)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        DailyRotatingFileHandler(os.path.join('logs', 'autotrade_{}.log'), mode='a'),
        logging.StreamHandler()
    ]
)
logging.getLogger().handlers[0].setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

# ----------------------------------------------------------------------------------------------------
# API키 읽기
UPBIT_ACCESS_KEY = os.getenv("UPBIT_ACCESS_KEY")
UPBIT_SECRET_KEY = os.getenv("UPBIT_SECRET_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# 대상 코인 설정 읽기
CURRENCY_CODE = os.getenv("CURRENCY_CODE", "KRW")
CURRENCY_NAME = os.getenv("CURRENCY_NAME", "Korean Won")
COIN_CODE = os.getenv("TARGET_CODE", "BTC")
COIN_NAME = os.getenv("TARGET_NAME", "Bitcoin")
TRADE_CODE = os.getenv("TRADE_CODE", "KRW-BTC")

# 마켓 데이터 설정 읽기
LIMIT_MINUTE5_COUNT = int(os.getenv("LIMIT_MINUTE5_COUNT", 60))
LIMIT_HOURLY_COUNT = int(os.getenv("LIMIT_HOURLY_COUNT", 60))
LIMIT_DAILY_COUNT = int(os.getenv("LIMIT_DAILY_COUNT", 60))
LIMIT_WEEKLY_COUNT = int(os.getenv("LIMIT_WEEKLY_COUNT", 60))

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini-2024-07-18")
MODEL_TOKENIZER_NAME = os.getenv("MODEL_TOKENIZER_NAME", "gpt-4o-mini")
MODEL_PRICE_BASE = float(os.getenv("MODEL_PRICE_BASE", "1000000")) # 100만 토큰당 달러
MODEL_PRICE_INPUT = float(os.getenv("MODEL_PRICE_INPUT", "0.150")) # MODEL_PRICE_BASE 토큰 기분가격
MODEL_PRICE_CACHE = float(os.getenv("MODEL_PRICE_CACHE", "0.075")) # MODEL_PRICE_BASE 토큰 기분가격
MODEL_PRICE_OUTPUT = float(os.getenv("MODEL_PRICE_OUTPUT", "0.600")) # MODEL_PRICE_BASE 토큰 기분가격
MODEL_RESULT_CASE = int(os.getenv("MODEL_RESULT_CASE", "1"))  # ai에게 답변을 받아서 최종 반영할 갯수

NEWS_REACH_DAYS = os.getenv("NEWS_REACH_DAYS", "14")
NEWS_LIMIT_LENGTH = int(os.getenv("NEWS_LIMIT_LENGTH", 3000))
NEWS_REACH_PAGES = os.getenv("NEWS_REACH_PAGES", "5")

# 데이터베이스 설정 읽기
DB_PATH = os.getenv("DB_PATH", "AutoTrade.sqlite3")

BUY_MAX_ATTEMPTS = int(os.getenv("BUY_MAX_ATTEMPTS", "5"))
BUY_RETRY_DELAY = int(os.getenv("BUY_RETRY_DELAY", "2"))
BUY_API_DELAY = int(os.getenv("BUY_API_DELAY", "1"))

SELL_MAX_ATTEMPTS = int(os.getenv("SELL_MAX_ATTEMPTS", "5"))
SELL_RETRY_DELAY = int(os.getenv("SELL_RETRY_DELAY", "2"))
SELL_API_DELAY = int(os.getenv("SELL_API_DELAY", "1"))

VIRTUAL_TRADE = os.getenv("VIRTUAL_TRADE", "True").lower() == "true"
VIRTUAL_TRADE_BALANCE = float(os.getenv("VIRTUAL_TRADE_BALANCE", "100000000"))
print("VIRTUAL_TRADE", VIRTUAL_TRADE)

# ----------------------------------------------------------------------------------------------------
# 초기화하기
client = OpenAI()
upbit = pyupbit.Upbit(UPBIT_ACCESS_KEY, UPBIT_SECRET_KEY)

# ----------------------------------------------------------------------------------------------------
# region 앞으로 사용될 유틸리티 함수 영역


def log(name, data=None):
    if data and not isinstance(data, (str, dict, list)):
        try:
            data = json.loads(json.dumps(force_dumps(data), ensure_ascii=False))
        except:
            data = str(data)

    logging.info(f"{name}")

    LogData.append(
        {"time": datetime.datetime.now().isoformat(), "name": name, "data": data}
    )


def force_dumps(data) -> dict:
    """객체까지 강제로 dictionary로 변경한다."""

    if isinstance(data, (int, float, str, bool, type(None))):
        return data

    try:
        json.dumps(data, ensure_ascii=False)
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


def get_expect_token_count(text):
    try:
        encoding = tiktoken.encoding_for_model(MODEL_TOKENIZER_NAME)
        return len(encoding.encode(text))
    except ValueError:
        logging.warning(
            f"Model {MODEL_TOKENIZER_NAME} not found. Using {MODEL_TOKENIZER_NAME} instead."
        )
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        return len(encoding.encode(text))


def safe_save_or_load(ignore, applyDate, filename, data_or_func, lambda_load_cache=None):

    # 폴더 생성
    dir = os.path.dirname(filename)
    split = os.path.splitext(filename)
    os.makedirs(dir, exist_ok=True)

    # ignore가 True이면 캐싱을 무시하고 새로운 데이터를 가져옴
    if not ignore:
        if applyDate.lower() == "all":
            # 가장 최신 파일 찾기
            files = glob.glob(f"{split[0]}-*{split[1]}")
            latest_file = max(files, key=os.path.getctime) if files else None

            if latest_file:
                with open(latest_file, "r", encoding="utf-8") as f:
                    jsonData = json.load(f)
                    if lambda_load_cache:
                        return lambda_load_cache(jsonData)
                    else:
                        return jsonData
        else:
            if applyDate.lower() == "day":
                filename = f"{split[0]}-{datetime.datetime.now().strftime('%Y%m%d')}{split[1]}"
            elif applyDate.lower() == "hour":
                filename = f"{split[0]}-{datetime.datetime.now().strftime('%Y%m%d-%H')}{split[1]}"

            # 정확한 파일명으로 찾기
            if os.path.exists(filename) and not ignore:
                with open(filename, "r", encoding="utf-8") as f:
                    jsonData = json.load(f)
                    if lambda_load_cache:
                        return lambda_load_cache(jsonData)
                    else:
                        return jsonData

    if callable(data_or_func):
        data = data_or_func()
    else:
        data = data_or_func

    if data:

        # 파일명에 시간 추가
        if applyDate.lower() == "all":
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f")[:-3]
            actual_filename = f"{split[0]}-{timestamp}{split[1]}"
        elif applyDate.lower() == "day":
            actual_filename = f"{split[0]}-{datetime.datetime.now().strftime('%Y%m%d')}{split[1]}"
        elif applyDate.lower() == "hour":
            actual_filename = f"{split[0]}-{datetime.datetime.now().strftime('%Y%m%d-%H')}{split[1]}"
        else:
            actual_filename = filename

        jsonData = json.dumps(force_dumps(data), ensure_ascii=False, indent=4)

        # 새로운 데이터를 항상 파일로 저장
        with open(actual_filename, "w", encoding="utf-8") as f:
            f.write(jsonData)

    return data


# endregion 앞으로 사용될 유틸리티 함수 영역


# ----------------------------------------------------------------------------------------------------
# region DB와 관련된 초기화, 읽기, 쓰기 함수 영역
DB_TABLES = {
    "decisions": {
        "columns": [
            ["id", "INTEGER", "PRIMARY KEY", "AUTOINCREMENT"],  # 고유 식별자
            ["coin", "TEXT"],  # 코인 종류
            ["decision", "TEXT"],  # 거래 결정 (buy/sell/hold)
            ["percentag", "REAL"],  # 거래 비율
            ["reason", "TEXT"],  # 거래 결정 이유
            ["timestamp", "TEXT"],  # 거래 시간
        ]
    },
    "decisions_meta": {
        "columns": [
            ["id", "INTEGER"],  # 고유 식별자
            ["type", "TEXT"],  # 메타데이터 이름
            ["value", "TEXT"],  # 값
        ],
        "PRIMARY KEY": [
            "id", "type"
        ]
    },
    "trades": {
        "columns": [
            ["id", "INTEGER", "PRIMARY KEY", "AUTOINCREMENT"],  # 고유 식별자
            ["ticker", "TEXT"],  # 거래 코인 티커
            ["type", "TEXT"],  # 거래 유형 (buy/sell)
            ["price", "REAL"],  # 거래 단가
            ["amount", "REAL"],  # 코인 거래량
            ["funds", "REAL"],  # 거래금 (KRW)
            ["fee", "REAL"],  # 수수료 (KRW)
            ["before_currency_balance", "REAL"],  # 거래 전 화폐 잔액
            ["before_coin_balance", "REAL"],  # 거래 전 코인 잔액
            ["before_coin_avg_buy_price", "REAL"],  # 거래 전 코인 평균 매수가
            ["after_currency_balance", "REAL"],  # 거래 후 화폐 잔액
            ["after_coin_balance", "REAL"],  # 거래 후 코인 잔액
            ["after_coin_avg_buy_price", "REAL"],  # 거래 후 코인 평균 매수가
            ["attempts", "INTEGER"],  # 거래 시도 횟수
            ["timestamp", "TEXT"],  # 거래 시간
        ]
    },
    "wallets": {
        "columns": [
            ["id", "TEXT", "PRIMARY KEY"],  # 지갑 ID (코인 코드)
            ["balance", "REAL"],  # 지갑 잔액
            ["avg_price", "REAL"],  # 평균 매수가
        ]
    },
}

# 'decisions' 테이블의 컬럼 이름을 전역 변수로 정의
DB_DECISIONS_COIN = DB_TABLES["decisions"]["columns"][1][0]  # "coin"
DB_DECISIONS_DECISION = DB_TABLES["decisions"]["columns"][2][0]  # "decision"
DB_DECISIONS_PERCENTAGE = DB_TABLES["decisions"]["columns"][3][0]  # "percentag"
DB_DECISIONS_REASON = DB_TABLES["decisions"]["columns"][4][0]  # "reason"
DB_DECISIONS_TIMESTAMP = DB_TABLES["decisions"]["columns"][5][0]  # "timestamp"

# 'decisions_meta' 테이블의 컬럼 이름을 전역 변수로 정의
DB_DECISIONS_META_ID = DB_TABLES["decisions_meta"]["columns"][0][0]  # "id"
DB_DECISIONS_META_TYPE = DB_TABLES["decisions_meta"]["columns"][1][0]  # "type"
DB_DECISIONS_META_VALUE = DB_TABLES["decisions_meta"]["columns"][2][0]  # "value"

# 'trades' 테이블의 컬럼 이름을 전역 변수로 정의
DB_TRADES_TICKER = DB_TABLES["trades"]["columns"][1][0]  # "ticker"
DB_TRADES_TYPE = DB_TABLES["trades"]["columns"][2][0]  # "type"
DB_TRADES_PRICE = DB_TABLES["trades"]["columns"][3][0]  # "price"
DB_TRADES_AMOUNT = DB_TABLES["trades"]["columns"][4][0]  # "amount"
DB_TRADES_FUNDS = DB_TABLES["trades"]["columns"][5][0]  # "funds"
DB_TRADES_FEE = DB_TABLES["trades"]["columns"][6][0]  # "fee"
DB_TRADES_BEFORE_CURRENCY_BALANCE = DB_TABLES["trades"]["columns"][7][0]  # "before_currency_balance"
DB_TRADES_BEFORE_COIN_BALANCE = DB_TABLES["trades"]["columns"][8][0]  # "before_coin_balance"
DB_TRADES_BEFORE_COIN_AVG_BUY_PRICE = DB_TABLES["trades"]["columns"][9][0]  # "before_coin_avg_buy_price"
DB_TRADES_AFTER_CURRENCY_BALANCE = DB_TABLES["trades"]["columns"][10][0]  # "after_currency_balance"
DB_TRADES_AFTER_COIN_BALANCE = DB_TABLES["trades"]["columns"][11][0]  # "after_coin_balance"
DB_TRADES_AFTER_COIN_AVG_BUY_PRICE = DB_TABLES["trades"]["columns"][12][0]  # "after_coin_avg_buy_price"
DB_TRADES_ATTEMPTS = DB_TABLES["trades"]["columns"][13][0]  # "attempts"
DB_TRADES_TIMESTAMP = DB_TABLES["trades"]["columns"][14][0]  # "timestamp"

# 'wallets' 테이블의 컬럼 이름을 전역 변수로 정의
DB_WALLETS_ID = DB_TABLES["wallets"]["columns"][0][0]  # "id"
DB_WALLETS_BALANCE = DB_TABLES["wallets"]["columns"][1][0]  # "balance"
DB_WALLETS_AVG_PRICE = DB_TABLES["wallets"]["columns"][2][0]  # "avg_price"

# 데이터베이스 연결 최적화
@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def initialize_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        for table_name, table_info in DB_TABLES.items():
            # 기존 테이블 정보 가져오기
            cursor.execute(f"PRAGMA table_info({table_name})")
            existing_columns = {row[1]: row[2] for row in cursor.fetchall()}

            columns = table_info["columns"]

            if not existing_columns:
                if 'options' in table_info:
                    columns.append(table_info["options"])

                # 테이블이 없으면 새로 생성
                column_definitions = ", ".join([" ".join(col) for col in columns])

                if 'PRIMARY_KEY' in table_info:
                    primary_key_str = ",".join(table_info['PRIMARY_KEY'])
                    column_definitions += f", PRIMARY KEY ({primary_key_str})"

                create_table_query = f"""
                CREATE TABLE {table_name} (
                    {column_definitions}
                )
                """
                cursor.execute(create_table_query)
            else:
                # 테이블이 있으면 컬럼 비교 후 필요한 경우 수정
                for col in columns:
                    col_name = col[0]
                    col_type = col[1]
                    if col_name not in existing_columns:
                        # 새 컬럼 추가
                        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
                    elif existing_columns[col_name] != col_type:
                        # 컬럼 타입 변경 (SQLite는 직접적인 컬럼 타입 변경을 지원하지 않으므로 복잡한 과정이 필요)
                        # 여기서는 간단히 로그만 남깁니다.
                        print(f"Warning: Column type mismatch for {table_name}.{col_name}. Expected {col_type}, found {existing_columns[col_name]}")
                
                # PRIMARY KEY 확인 및 수정
                if 'PRIMARY_KEY' in table_info:
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    existing_primary_keys = [row[1] for row in cursor.fetchall() if row[5] == 1]
                    required_primary_keys = table_info['PRIMARY_KEY']
                    
                    if set(existing_primary_keys) != set(required_primary_keys):
                        # PRIMARY KEY가 다르면 테이블을 재생성
                        temp_table_name = f"{table_name}_temp"
                        column_definitions = ", ".join([" ".join(col) for col in columns])
                        primary_key_str = ",".join(table_info['PRIMARY_KEY'])
                        column_definitions += f", PRIMARY KEY ({primary_key_str})"
                        
                        cursor.execute(f"CREATE TABLE {temp_table_name} AS SELECT * FROM {table_name}")
                        cursor.execute(f"DROP TABLE {table_name}")
                        cursor.execute(f"""
                        CREATE TABLE {table_name} (
                            {column_definitions}
                        )
                        """)
                        cursor.execute(f"INSERT INTO {table_name} SELECT * FROM {temp_table_name}")
                        cursor.execute(f"DROP TABLE {temp_table_name}")
                        print(f"Table {table_name} recreated with new PRIMARY KEY")

        conn.commit()

    # 기본 값 입력
    if get_db_row_count('wallets') == 0:
        set_db_wallet(CURRENCY_CODE, VIRTUAL_TRADE_BALANCE, 0)

def record_trade(ticker, trade_type, amount, price, funds, fee, before_wallet, attempts):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # before 정보 가져오기
        before_currency_balance = before_wallet[f"currency_balance"]
        before_coin_balance = before_wallet[f"coin_balance"]
        before_coin_avg_buy_price = before_wallet[f"coin_avg_buy_price"]
        
        # after 정보 가져오기
        after_wallet = get_current_wallet()
        after_currency_balance = after_wallet[f"currency_balance"]
        after_coin_balance = after_wallet[f"coin_balance"]
        after_coin_avg_buy_price = after_wallet[f"coin_avg_buy_price"]
        
        cursor.execute(
            f"""
INSERT INTO trades (
    {DB_TRADES_TIMESTAMP}, {DB_TRADES_TICKER}, {DB_TRADES_TYPE}, {DB_TRADES_PRICE}, 
    {DB_TRADES_AMOUNT}, {DB_TRADES_FUNDS}, {DB_TRADES_FEE}, 
    {DB_TRADES_BEFORE_CURRENCY_BALANCE}, {DB_TRADES_BEFORE_COIN_BALANCE}, {DB_TRADES_BEFORE_COIN_AVG_BUY_PRICE},
    {DB_TRADES_AFTER_CURRENCY_BALANCE}, {DB_TRADES_AFTER_COIN_BALANCE}, {DB_TRADES_AFTER_COIN_AVG_BUY_PRICE},
    {DB_TRADES_ATTEMPTS}
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                timestamp, ticker, trade_type, price,
                amount, funds, fee,
                before_currency_balance, before_coin_balance, before_coin_avg_buy_price,
                after_currency_balance, after_coin_balance, after_coin_avg_buy_price,
                attempts
            ),
        )
        conn.commit()
        
        # 생성된 거래 ID 가져오기
        trade_id = cursor.lastrowid
        
        # 생성한 거래 정보 다시 읽어서 반환
        return get_trade(trade_id)


def get_trade(trade_id):
    if trade_id > 0:
        db_name = "trades"
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {db_name} WHERE id = ?", (trade_id,))
            trade = cursor.fetchone()
            
        if trade:
            result = {}
            for index, column in enumerate(DB_TABLES[db_name]["columns"]):
                result[column[0]] = trade[index]
            return result
    else:
        return { "id":0 }
    
def get_decisions(include_trade=True, num_decisions=10):
    db_name = "decisions"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {db_name} ORDER BY id DESC LIMIT ?", (num_decisions,))
        decisions = cursor.fetchall()
        
    result = []
    for decision in decisions:
        
        decision_dict = {}
        result.append(decision_dict)

        for index, column in enumerate(DB_TABLES[db_name]["columns"]):
            decision_dict[column[0]] = decision[index]
    
    return result

def record_decision(ticker, decision, percentage, reason, meta):
    db_name = "decisions"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            f"""
        INSERT INTO {db_name} (
            {DB_DECISIONS_COIN}, {DB_DECISIONS_DECISION}, {DB_DECISIONS_PERCENTAGE}, {DB_DECISIONS_REASON}, {DB_DECISIONS_TIMESTAMP}
        ) VALUES (?, ?, ?, ?, ?)
        """,
            (
                ticker,
                decision,
                percentage,
                reason,
                timestamp,
            ),
        )
        
        # 생성된 결정 ID 가져오기
        decision_id = cursor.lastrowid
        
        # meta 데이터를 decisions_meta 테이블에 기록
        for key, value in meta.items():

            if not isinstance(value, str):
                value = json.dumps(force_dumps(value), ensure_ascii=False, indent=4)

            cursor.execute(
                f"""
                INSERT INTO decisions_meta (
                    {DB_DECISIONS_META_ID}, {DB_DECISIONS_META_TYPE}, {DB_DECISIONS_META_VALUE}
                ) VALUES (?, ?, ?)
                """,
                (decision_id, key, str(value))
            )
        
        conn.commit()

def get_decision_meta(id, type):
    db_name = "decisions_meta"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT {DB_DECISIONS_META_VALUE} FROM {db_name} WHERE {DB_DECISIONS_META_ID} = ? AND {DB_DECISIONS_META_TYPE} = ?", (id, type))
        return cursor.fetchone()[0]

def get_db_wallet(ticker):
    db_name = "wallets"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {db_name} WHERE {DB_WALLETS_ID} = ?", (ticker,))
        wallet = cursor.fetchone()
        
    if wallet:
        result = {}
        for index, column in enumerate(DB_TABLES[db_name]["columns"]):
            result[column[0]] = wallet[index]
        return result
    else:
        return {DB_WALLETS_ID: ticker, DB_WALLETS_BALANCE: 0, DB_WALLETS_AVG_PRICE: 0}


def get_db_row_count(table_name):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        return cursor.fetchone()[0]


def set_db_wallet(ticker, balance, avg_price):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            INSERT OR REPLACE INTO wallets ({DB_WALLETS_ID}, {DB_WALLETS_BALANCE}, {DB_WALLETS_AVG_PRICE})
            VALUES (?, ?, ?)
            """,
            (ticker, balance, avg_price),
        )
        conn.commit()


# endregion DB와 관련된 초기화, 읽기, 쓰기 함수 영역


# ----------------------------------------------------------------------------------------------------
# region 외부의 시장 및 글로벌 데이터를 읽는 함수 영역


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

    googlenews = GoogleNews(lang="en", region="US")
    googlenews.set_period(f"{NEWS_REACH_DAYS}d")
    googlenews.set_encode("utf-8")

    search_query = f"{COIN_CODE} {COIN_NAME} cryptocurrency"
    googlenews.search(search_query)

    headlines = []
    tempHeadlines = []
    page = 1
    max_pages = int(NEWS_REACH_PAGES)

    while page <= max_pages:
        news_results = googlenews.page_at(page)
        for news in news_results:
            headline = {"title": news["title"], "date": news["date"]}

            tempHeadlines.append(headline)
            if len(json.dumps(tempHeadlines)) > NEWS_LIMIT_LENGTH:
                page = max_pages
                break

            headlines.append(headline)

        page += 1
        time.sleep(1)

    googlenews.clear()  # 결과를 지웁니다

    return headlines


# def get_latest_youtube():
#     """
#     유튜브에서 최신 관련 영상을 찾아온다.
#     찾아온 영상은 제목, 설명, 조회수, 좋아요, 구독자수, 캡션을 갖고있다.
#     """
#     ###############################################################

#     youtube = build("youtube", "v3", developerKey=youtube_api_key)

#     # 현재 시간부터 1일 전의 날짜-시간을 구합니다
#     one_day_ago = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat() + "Z"

#     search_result = (
#         youtube.search()
#         .list(
#             q=f"{coin_name} price prediction",
#             type="video",
#             publishedAfter=one_day_ago,
#             maxResults=10,
#             order="relevance",
#             videoCaption="closedCaption",
#             videoDuration="medium",
#             relevanceLanguage="en",
#             part="id,snippet",
#         )
#         .execute()
#     )

#     # 조회수, 좋아요, 채널구독수 추가
#     for item in search_result["items"]:
#         video_id = item["id"]["videoId"]
#         channel_id = item["snippet"]["channelId"]

#         # 비디오 통계 가져오기
#         video_result = youtube.videos().list(part="statistics", id=video_id).execute()

#         # 채널 통계 가져오기
#         channel_result = youtube.channels().list(part="statistics", id=channel_id).execute()

#         # 통계 정보 추가
#         item["statistics"] = {
#             "viewCount": video_result["items"][0]["statistics"]["viewCount"],
#             "likeCount": video_result["items"][0]["statistics"]["likeCount"],
#             "subscriberCount": channel_result["items"][0]["statistics"]["subscriberCount"],
#         }

#     # 비디오가 1개라도 없는 상황 확인
#     if not search_result.get("items") or len(search_result["items"]) == 0:
#         return None

#     ###############################################################
#     # 필터링

#     # TARGET_KEYWORDS를 환경 변수에서 가져오기
#     target_keywords = os.getenv("TARGET_KEYWORDS", "").strip()
#     keywords_list = [keyword.strip() for keyword in target_keywords.split(",") if keyword.strip()]

#     # TARGET_KEYWORDS에 해당하는 영상만 필터링
#     filtered_items = []
#     for item in search_result["items"]:
#         title = item["snippet"]["title"]
#         description = item["snippet"]["description"]

#         if any(re.search(keyword, title, re.IGNORECASE) or re.search(keyword, description, re.IGNORECASE) for keyword in keywords_list):
#             filtered_items.append(item)

#     # 필터링된 영상이 1개 이상 있으면 search_response 업데이트
#     if filtered_items:
#         search_result["items"] = filtered_items
#         search_result["pageInfo"]["totalResults"] = len(filtered_items)

#     ###############################################################
#     # 정렬

#     # search_response를 점수 기반으로 내림차순 정렬
#     def calculate_score(item):
#         view_count = int(item["statistics"]["viewCount"])
#         like_count = int(item["statistics"]["likeCount"])
#         subscriber_count = int(item["statistics"]["subscriberCount"])
#         return view_count + (like_count * 5) + (subscriber_count * 10)

#     search_result["items"] = sorted(search_result["items"], key=calculate_score, reverse=True)

#     ###############################################################
#     # 캡션 가져오기

#     captions = []
#     for index, item in enumerate(search_result["items"]):
#         video_id = item["id"]["videoId"]

#         caption_text = caching(False, False, f"cache/video_{video_id}.json", lambda: get_video_caption(video_id))

#         if caption_text == None:
#             continue

#         caption = {
#             "title": item["snippet"]["title"],
#             "description": item["snippet"]["description"],
#             "view_count": item["statistics"]["viewCount"],
#             "like_count": item["statistics"]["likeCount"],
#             "subscriber_count": item["statistics"]["subscriberCount"],
#             "caption": caption_text,
#         }

#         if caption and "caption" in caption and len(caption["caption"]) > 0:
#             captions.append(caption)

#     ###############################################################
#     # 3000자를 넘는 캡션만 필터링
#     minimum_caption_length = int(os.getenv("MINIMUM_CAPTION_LENGTH", 1000))
#     filtered_captions = [caption for caption in captions if len(caption["caption"]) > minimum_caption_length]

#     if not filtered_captions:
#         return captions[0]
#     else:
#         return filtered_captions[0]


# def get_video_caption(video_id):
#     try:
#         transcript = YouTubeTranscriptApi.get_transcript(video_id)
#         caption_text = " ".join([entry["text"] for entry in transcript])
#         return caption_text
#     except Exception as e:
#         log(f"[Youtube] GetCaption Error(videoid={video_id}, exception={str(e)})")
#         return None


def get_chart_data():

    # 시간봉
    df_5min = pyupbit.get_ohlcv(
        TRADE_CODE, interval="minute5", count=int(LIMIT_MINUTE5_COUNT)
    )
    df_hourly = pyupbit.get_ohlcv(
        TRADE_CODE, interval="minute60", count=int(LIMIT_HOURLY_COUNT)
    )
    df_daily = pyupbit.get_ohlcv(
        TRADE_CODE, interval="day", count=int(LIMIT_DAILY_COUNT)
    )
    df_weekly = pyupbit.get_ohlcv(
        TRADE_CODE, interval="week", count=int(LIMIT_WEEKLY_COUNT)
    )

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
        stoch = ta.momentum.StochasticOscillator(
            df["high"], df["low"], df["close"], window=14, smooth_window=3
        )
        df["Stoch_k_14_3"] = stoch.stoch()
        df["Stoch_d_14_3"] = stoch.stoch_signal()

        # 이동평균선 추가
        # for period in [5, 10, 20, 60, 120]:
        for period in [5, 10, 20]:
            df[f"SMA_{period}"] = ta.trend.SMAIndicator(
                df["close"], window=period
            ).sma_indicator()
            df[f"EMA_{period}"] = ta.trend.EMAIndicator(
                df["close"], window=period
            ).ema_indicator()

        # ATR
        df["ATR_14"] = ta.volatility.AverageTrueRange(
            df["high"], df["low"], df["close"], window=14
        ).average_true_range()

        # OBV
        df["OBV"] = ta.volume.OnBalanceVolumeIndicator(
            df["close"], df["volume"]
        ).on_balance_volume()

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


def get_current_wallet(includeChances = False):
    chance = upbit.get_chance(TRADE_CODE)

    if VIRTUAL_TRADE:
        krw_wallet = get_db_wallet(CURRENCY_CODE)
        coin_wallet = get_db_wallet(COIN_CODE)
        chance["bid_account"]["balance"] = krw_wallet["balance"]
        chance["bid_account"]["locked"] = "0"
        chance["bid_account"]["avg_buy_price"] = "0"
        chance["ask_account"]["balance"] = coin_wallet["balance"]
        chance["ask_account"]["locked"] = "0"
        chance["ask_account"]["avg_buy_price"] = coin_wallet["avg_price"]

    if chance["market"]["state"] != "active":
        raise Exception("마켓이 활성 상태가 아닙니다.")

    rst = {}
    # 기존 설정
    rst["currency_balance"] = float(chance["bid_account"]["balance"]) - float(chance["bid_account"]["locked"])
    rst["coin_code"] = chance["ask_account"]["currency"]
    rst["coin_balance"] = float(chance["ask_account"]["balance"]) - float(chance["ask_account"]["locked"])
    rst["coin_avg_buy_price"] = float(chance["ask_account"]["avg_buy_price"])
    # 이름별 설정
    rst[f"{CURRENCY_CODE}_balance"] = rst["currency_balance"]
    rst[f"{COIN_CODE}_balance"] = rst["coin_balance"]
    rst[f"{COIN_CODE}_avg_buy_price"] =  rst["coin_avg_buy_price"]
    # 매수 설정
    rst["bid"] = chance["bid_account"]["currency"]
    rst["bid_balance"] = rst["currency_balance"]
    rst["bid_fee"] = float(chance["bid_fee"])
    # 매도 설정
    rst["ask"] = chance["ask_account"]["currency"]
    rst["ask_balance"] = rst["coin_balance"]
    rst["ask_fee"] = float(chance["ask_fee"])
    rst["ask_avg_buy_price"] = rst["coin_avg_buy_price"]

    safe_save_or_load(True, "all", "cache/wallets/wallet.json", lambda: {"chances": chance, "result": rst})

    if(includeChances):
        return rst, chance
    else:
        return rst


# def get_instruction(file_path):
#     try:
#         with open(file_path, "r", encoding="utf-8") as file:
#             text = file.read()
#     except FileNotFoundError:
#         print(f"File not found: '{file_path}'")
#     except Exception as e:
#         print("An error occurred while reading the file: '{file_path}'", e)
#     else:

#         def apply(text, key, value):
#             text = text.replace("{{{" + key.lower() + "}}}", value.lower())
#             text = text.replace("{{{" + key.upper() + "}}}", value.upper())
#             text = text.replace("{{{" + key.capitalize() + "}}}", value.capitalize())
#             return text

#         text = apply(text, "target_code", target_code)
#         text = apply(text, "currency_code", currency_code)
#         text = apply(text, "target_name", target_name)
#         text = apply(text, "currency_name", currency_name)
#         text = apply(text, "trade_code", trade_code)
#         text = apply(text, "limit_daily_count", str(limit_daily_count))
#         text = apply(text, "limit_hourly_count", str(limit_hourly_count))
#         text = apply(text, "limit_weekly_count", str(limit_weekly_count))
#         return text


def get_orderbook():
    orderbook = pyupbit.get_orderbook(TRADE_CODE)
    return orderbook


# endregion 외부의 시장 및 글로벌 데이터를 읽는 함수 영역

# ----------------------------------------------------------------------------------------------------
# region 모델 정의 영역


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


# endregion 모델 정의 영역


# ----------------------------------------------------------------------------------------------------
# region 거래 실행 함수 영역
def execute_buy(percentage):
    result = {
        "success": False,
        "action": "buy",
        "error": "",
        "ticker": TRADE_CODE,
        "fee": 0,
        "attempts": 0,
        "executed_volume": 0,
        "avg_price": 0,
        "currency_funds": 0,
        "currency_fee": 0,
        "currency_total": 0,
        "trade": {"id":0}
    }

    for attempt in range(1, SELL_MAX_ATTEMPTS + 1):
        result["attempts"] = attempt
        log(f"[Upbit] execute_buy({TRADE_CODE}, {percentage}%) [{attempt}/{BUY_MAX_ATTEMPTS}]")
        try:
            # 잔고 조회
            wallet, chance = get_current_wallet(True)
            balance = wallet["currency_balance"] # KRW 주문 가능 잔액 조회
            fee = float(chance["bid_fee"])  # 매수 수수료
            min_total = float(chance["market"]["bid"]["min_total"])
            result["fee"] = fee

            # 구매 가능한 금액 계산 (수수료 고려)
            upscale_fee = (
                fee * 1.01
            )  # 100%구매할때 fee에 1%를 곱하여 floating 오류로인한 거래실패를 방지함.
            available_amount_krw = balance * (percentage / 100) / (1 + upscale_fee)
            available_amount = available_amount_krw

            if available_amount_krw < min_total:
                result["success"] = False
                result["error"] = "매수 가능한 수량이 최소 주문 금액보다 작습니다."
                break

            if VIRTUAL_TRADE:

                def SimmulateBuy(amount, fee):

                    if random.random() < 0.01:
                        raise Exception(f"매수 실패: 랜덤 오류")

                    krw_wallet = get_db_wallet(CURRENCY_CODE)
                    krw = krw_wallet["balance"]
                    coin_wallet = get_db_wallet(COIN_CODE)
                    coin = coin_wallet["balance"]
                    coin_avg = coin_wallet["avg_price"]
                    coin_price = pyupbit.get_current_price(TRADE_CODE)

                    fund = amount * (random.random() * 0.0002 + 0.9999)
                    fund_fee = fund * fee
                    add_coin = fund / coin_price

                    if krw < available_amount_krw:
                        raise Exception(f"Not enough balance.")

                    krw -= fund + fund_fee
                    set_db_wallet(CURRENCY_CODE, krw, 0)

                    coin_total = coin + add_coin
                    coin_avg = ((coin / coin_total) * coin_avg) + (
                        (add_coin / coin_total) * coin_price
                    )
                    set_db_wallet(COIN_CODE, coin_total, coin_avg)

                    return {
                        "uuid": "00000000-0000-0000-0000-000000000000",
                        "side": "bid",
                        "ord_type": "price",
                        "price": str(amount),
                        "state": "done",
                        "market": TRADE_CODE,
                        "created_at": datetime.datetime.now().strftime(
                            "%Y-%m-%dT%H:%M:%S%z"
                        ),
                        "reserved_fee": str(fund_fee),
                        "remaining_fee": str(fund_fee),
                        "paid_fee": str(fund_fee),
                        "locked": "0",
                        "executed_volume": str(add_coin),
                        "trades_count": 1,
                        "trades": [
                            {
                                "market": TRADE_CODE,
                                "uuid": "00000000-0000-0000-0000-000000000000",
                                "price": str(coin_price),
                                "volume": str(add_coin),
                                "funds": str(krw),
                                "trend": "up",
                                "created_at": datetime.datetime.now().strftime(
                                    "%Y-%m-%dT%H:%M:%S%z"
                                ),
                                "side": "bid",
                            }
                        ],
                    }

                order = order_info = SimmulateBuy(available_amount, fee)
            else:
                # 시장가 매수 주문
                order = upbit.buy_market_order(TRADE_CODE, available_amount)
                safe_save_or_load(True, "all", "cache/upbits/buy.json", order)
                log(f"[Upbit] execute_buy({TRADE_CODE}, {percentage}%) [{attempt}/{BUY_MAX_ATTEMPTS}] Ordered", order)
                if "error" in order:
                    raise Exception(f"매수 실패: {order['error']['message']}")

                while True:
                    time.sleep(BUY_API_DELAY)  # API 요청 제한 고려
                    order_info = upbit.get_order(order["uuid"])
                    safe_save_or_load(True, "all", "cache/upbits/buy_info.json", order_info)
                    log(f"[Upbit] execute_buy({TRADE_CODE}, {percentage}%) Validate", order_info)
                    if order_info["state"] != "wait":
                        break

            # HACK:오류로 인해 주문성공에서 cancel로 될 수 있음. 아래 코드 임시 제외함.
            # if order_info["state"] != "done":
            #     continue

            trades = order_info["trades"]
            if order_info["trades_count"] == 0 or not trades:
                raise Exception(f"매수 실패: {json.dumps(order_info, ensure_ascii=False)}")

            executed_volume = float(order_info["executed_volume"])  # 체결된 코인 수량
            avg_price = (sum(float(trade["price"]) * float(trade["volume"]) for trade in trades) / executed_volume )  # 체결 평단가
            paid_funds = sum( float(trade["funds"]) for trade in trades )  # 체결에 지불한 KRW
            paid_fee = float(order_info["paid_fee"])  # 지불한 수수료
            paid_total = paid_funds + paid_fee  # 최종 지불량
            
            record_data =record_trade(
                TRADE_CODE,
                "buy",
                executed_volume,
                avg_price,
                paid_funds,
                paid_fee,
                wallet,
                attempt
            )

            result["success"] = True
            result["executed_volume"] = executed_volume
            result["avg_price"] = avg_price
            result["currency_funds"] = paid_funds
            result["currency_fee"] = paid_fee
            result["currency_total"] = paid_total
            result["trade"] = record_data

            log(f"[Upbit] execute_buy({TRADE_CODE}, {percentage}%): price={avg_price}, executed_volume:{executed_volume}, paid:{paid_total}", result)
            return result

        except Exception as e:
            log(f"[Upbit] execute_sell({TRADE_CODE}, {percentage}%): failed({attempt}/{SELL_MAX_ATTEMPTS}): {str(e)}")
            logging.exception(e)
            if attempt == SELL_MAX_ATTEMPTS:
                result["success"] = False
                result["error"] = str(e)
            time.sleep(SELL_RETRY_DELAY)  # 재시도 전 잠시 대기

    result["success"] = False
    return result


def execute_sell_krw(krw):
    cur_price = pyupbit.get_current_price(TRADE_CODE)
    cur_balance = upbit.get_balance(COIN_CODE)
    sell_percent = (krw / cur_price) / cur_balance
    execute_sell(sell_percent * 100)


def execute_sell(percentage):
    result = {
        "success": False,
        "action": "sell",
        "error": "",
        "ticker": TRADE_CODE,
        "fee": 0,
        "attempts": 0,
        "executed_volume": 0,
        "avg_price": 0,
        "currency_funds": 0,
        "currency_fee": 0,
        "currency_total": 0,
        "received_funds": 0,
        "received_fee" : 0,
        "received_total" : 0,
        "trade": {"id":0}
    }

    for attempt in range(1, SELL_MAX_ATTEMPTS + 1):
        result["attempts"] = attempt
        log(f"[Upbit] execute_sell({TRADE_CODE}, {percentage}%) [{attempt}/{BUY_MAX_ATTEMPTS}]")
        try:
            wallet, chance = get_current_wallet(True)
            balance = wallet["coin_balance"]  # 코인 주문 가능 잔액 조회
            fee = wallet["ask_fee"]  # 매도 수수료
            min_total = float(chance["market"]["ask"]["min_total"])
            result["fee"] = fee

            # 판매 가능한 수량 계산 (수수료 고려)
            upscale_fee = (
                fee * 1.01
            )  # 100%구매할때 fee에 1%를 곱하여 floating 오류로인한 거래실패를 방지함.
            available_amount = balance * (percentage / 100) / (1 + upscale_fee)
            available_amount_krw = (
                pyupbit.get_current_price(TRADE_CODE) * available_amount
            )

            if available_amount_krw < min_total:
                result["success"] = False
                result["error"] = "매수 가능한 수량이 최소 주문 금액보다 작습니다."
                break

            # 시장가 매도 주문
            if VIRTUAL_TRADE:

                def SimmulateSell(amount, fee):

                    if random.random() < 0.01:
                        raise Exception(f"매도 실패: 랜덤 오류")

                    krw_wallet = get_db_wallet(CURRENCY_CODE)
                    krw = krw_wallet["balance"]
                    coin_wallet = get_db_wallet(COIN_CODE)
                    coin = coin_wallet["balance"]
                    coin_avg = coin_wallet["avg_price"]
                    coin_price = pyupbit.get_current_price(TRADE_CODE)

                    fund = amount * coin_price
                    fund_fee = fund * fee

                    if fund < available_amount_krw:
                        raise Exception(f"Not enough balance.")

                    krw += fund - fund_fee
                    set_db_wallet(CURRENCY_CODE, krw, 0)
                    set_db_wallet(COIN_CODE, coin - amount, coin_avg)

                    return {
                        "uuid": "00000000-0000-0000-0000-000000000000",
                        "side": "ask",
                        "ord_type": "market",
                        "volume": str(amount),
                        "state": "done",
                        "market": TRADE_CODE,
                        "created_at": datetime.datetime.now().strftime(
                            "%Y-%m-%dT%H:%M:%S%z"
                        ),
                        "reserved_fee": "0",
                        "remaining_fee": "0",
                        "paid_fee": str(fund_fee),
                        "locked": "0",
                        "executed_volume": str(amount),
                        "trades_count": 1,
                        "trades": [
                            {
                                "market": TRADE_CODE,
                                "uuid": "00000000-0000-0000-0000-000000000000",
                                "price": str(coin_price),
                                "volume": str(amount),
                                "funds": str(fund),
                                "trend": "down",
                                "created_at": datetime.datetime.now().strftime(
                                    "%Y-%m-%dT%H:%M:%S%z"
                                ),
                                "side": "ask",
                            }
                        ],
                    }

                order = order_info = SimmulateSell(available_amount, fee)
            else:
                order = upbit.sell_market_order(TRADE_CODE, available_amount)
                safe_save_or_load(True, "all", "cache/upbits/sell.json", order)
                log(f"[Upbit] execute_sell({TRADE_CODE}, {percentage}%) [{attempt}/{BUY_MAX_ATTEMPTS}] Ordered", order)
                if "error" in order:
                    raise Exception(f"매도 실패: {order['error']['message']}")

                while True:
                    time.sleep(BUY_API_DELAY)  # API 요청 제한 고려
                    order_info = upbit.get_order(order["uuid"])
                    safe_save_or_load(True, "all", "cache/upbits/sell_info.json", order_info)
                    log(f"[Upbit] execute_sell({TRADE_CODE}, {percentage}%) [{attempt}/{BUY_MAX_ATTEMPTS}] Validate", order_info)
                    if order_info["state"] != "wait":
                        break

            # HACK:오류로 인해 주문성공에서 cancel로 될 수 있음. 아래 코드 임시 제외함.
            # if order_info["state"] != "done":
            #     continue

            trades = order_info["trades"]
            if order_info["trades_count"] == 0 or not trades:
                raise Exception(
                    f"매도 실패: {json.dumps(order_info, ensure_ascii=False)}"
                )

            executed_volume = float(order_info["executed_volume"])  # 체결된 코인 수량
            avg_price = (sum(float(trade["price"]) * float(trade["volume"]) for trade in trades) / executed_volume )  # 체결 평단가
            received_funds = sum(float(trade["funds"]) for trade in trades)  # 체결로 받은 KRW
            received_fee = float(order_info["paid_fee"])  # 지불한 수수료
            received_total = received_funds - received_fee  # 최종 받은 금액

            record_data = record_trade(
                TRADE_CODE,
                "sell",
                executed_volume,
                avg_price,
                received_funds,
                received_fee,
                wallet,
                attempt,
            )

            result["success"] = True
            result["executed_volume"] = executed_volume
            result["avg_price"] = avg_price
            result["received_funds"] = received_funds
            result["received_fee"] = received_fee
            result["received_total"] = received_total
            result["trade"] = record_data

            log(f"[Upbit] execute_sell({TRADE_CODE}, {percentage}%), price:{avg_price}, executed_volume:{executed_volume}, received:{received_total}", result)
            return result

        except Exception as e:
            log(f"[Upbit] execute_sell({TRADE_CODE}, {percentage}%): failed({attempt}/{SELL_MAX_ATTEMPTS}): {str(e)}")
            logging.exception(e)
            if attempt == SELL_MAX_ATTEMPTS:
                result["success"] = False
                result["error"] = str(e)
            time.sleep(SELL_RETRY_DELAY)  # 재시도 전 잠시 대기

    result["success"] = False
    return result


def execute_trading():
    # Db 초기화
    initialize_db()

    # 데이터 가져오기
    news_data = safe_save_or_load(False, "hour", "cache/news/news.json", lambda: get_latest_news())
    log("[Collect] get_latest_news()", news_data)

    # youtube_data = caching(True, True, "cache/youtube.json", lambda: get_latest_youtube())
    # log("[Collect] get_latest_youtube()", youtube_data)

    last_decisions = get_decisions()
    for decision in last_decisions:
        
        trade_id = get_decision_meta(decision["id"], "trade_id")
        decision.pop("id")
        decision.pop(DB_DECISIONS_COIN)

        if not trade_id: continue
        trade = get_trade(int(trade_id))
        if not trade: continue
        decision["trade"] = trade
    log("[Collect] get_decisions()", last_decisions)

    fnq_data = get_fear_and_greed_index()
    log("[Collect] get_fear_and_greed_index()", fnq_data)

    market_data = get_chart_data()
    log("[Collect] get_chart_data()", market_data)

    orderbook_data = get_orderbook()
    log("[Collect] get_orderbook()", orderbook_data)

    wallet_data = get_current_wallet()
    wallet_data["timestamp"] = orderbook_data["timestamp"]
    log("[Collect] get_current_wallet()", wallet_data)

    # 명령어 입력
    system_instruction = """
# Bitcoin Investment Automation Instruction

## Role

Your role is to serve as an advanced virtual assistant for Bitcoin trading, specifically for the KRW-BTC pair. Your objectives are to optimize profit margins, minimize risks, and use a data-driven approach to guide trading decisions. Utilize market analytics, real-time data, and crypto news insights to form trading strategies. For each trade recommendation, clearly articulate the action, its rationale, and the proposed investment proportion, ensuring alignment with risk management protocols. **Your response must be in JSON format, adhering to the specified schema.**

## Data Overview

### Data 1: Crypto News

- **Purpose**: To leverage recent news trends for identifying market sentiment and influencing factors. Prioritize credible sources and use a systematic approach to evaluate news relevance and credibility, ensuring an informed weighting in decision-making.

- **Contents**:
  - A list of news articles relevant to Bitcoin trading. Each article includes:
    - `title`: The news headline summarizing the article's content.
    - `date`: The publication date of the article.

- **Example**:
  ```json
  [
    {"title": "Bitcoin Surges Above $60,000 as Demand Increases", "date": "2023-10-06"},
    {"title": "Regulatory Uncertainty Causes Market Fluctuations", "date": "2023-10-05"}
  ]
  ```

### Data 2: Market Analysis

- **Purpose**: Provides comprehensive analytics on the KRW-BTC trading pair to facilitate market trend analysis and guide investment decisions.

- **Contents**:
  - A JSON representation of combined OHLCV (Open, High, Low, Close, Volume) data from multiple time intervals (5-minute, hourly, daily, weekly), including calculated technical indicators.
  - Includes:
    - `columns`: Essential data points like "open", "high", "low", "close", "volume", and technical indicators such as "RSI_14", "MACD_12_26", "BB_high_20_2", etc.
    - `index`: Multi-level index indicating the time interval (e.g., "5min", "hourly") and the timestamp.
    - `data`: Numeric values for each column at specified timestamps.

- **Example Structure**:
  ```json
  {
    "columns": ["open", "high", "low", "close", "volume", "RSI_14", "MACD_12_26", "..."],
    "index": [
      ["5min", "2023-10-07T10:00:00"],
      ["5min", "2023-10-07T10:05:00"],
      ["hourly", "2023-10-07T10:00:00"],
      ["daily", "2023-10-07"]
    ],
    "data": [
      [95000000, 95500000, 94500000, 95200000, 120.5, 55.3, -0.5, "..."],
      [95200000, 96000000, 95000000, 95800000, 130.2, 57.8, 0.3, "..."],
      [96000000, 97000000, 95000000, 96500000, 500.0, 60.1, 1.2, "..."],
      [90000000, 97000000, 89000000, 96000000, 2000.0, 65.0, 2.0, "..."]
    ]
  }
  ```

### Data 3: Previous Decisions

- **Purpose**: Provides a historical record of the most recent trading decisions to refine future strategies by evaluating past decisions against market data.

- **Contents**:
  - A list where each item includes:
    - `id`: Unique identifier of the decision.
    - `timestamp`: The exact moment the decision was recorded.
    - `coin`: The trading pair or coin involved (e.g., "KRW-BTC").
    - `decision`: The action taken—`buy`, `sell`, or `hold`.
    - `percentage`: The proportion of the portfolio allocated for the decision.
    - `reason`: Detailed reasoning behind the decision.
    - `trade`: Details of the executed trade, if any, including balance changes and trade outcomes.

- **Example**:
  ```json
  [
    {
      "id": 1,
      "timestamp": "2023-10-07T10:00:00",
      "coin": "KRW-BTC",
      "decision": "buy",
      "percentage": 30,
      "reason": "Bullish market indicators and positive news.",
      "trade": {
        "id": 1001,
        "timestamp": "2023-10-07T10:01:00",
        "ticker": "KRW-BTC",
        "type": "buy",
        "price": 95000000,
        "amount": 0.0315,
        "funds": 3000000,
        "fee": 1500,
        "before_currency_balance": 10000000,
        "after_currency_balance": 7000000,
        "before_coin_balance": 0.0,
        "after_coin_balance": 0.0315
      }
    }
  ]
  ```

### Data 4: Fear and Greed Index

- **Purpose**: Gauges overall crypto market sentiment, ranging from "Extreme Fear" to "Extreme Greed," to inform trading decisions.

- **Contents**:
  - An object containing:
    - `value`: Index value from 0 (Extreme Fear) to 100 (Extreme Greed).
    - `classification`: Textual representation like "Fear", "Greed", etc.
    - `timestamp`: When the index was recorded.

- **Example**:
  ```json
  {
    "value": 72,
    "classification": "Greed",
    "timestamp": "2023-10-07T09:00:00"
  }
  ```

### Data 5: Upbit Orderbook

- **Purpose**: Provides real-time market depth details to understand current buy and sell pressures.

- **Contents**:
  - An object containing:
    - `market`: The trading pair (e.g., "KRW-BTC").
    - `timestamp`: Time when the orderbook was retrieved.
    - `total_ask_size`: Total size of sell orders.
    - `total_bid_size`: Total size of buy orders.
    - `orderbook_units`: A list of price levels with:
      - `ask_price`: Sellers' prices.
      - `bid_price`: Buyers' prices.
      - `ask_size`: Quantity available at ask price.
      - `bid_size`: Quantity available at bid price.

- **Example**:
  ```json
  {
    "market": "KRW-BTC",
    "timestamp": "2023-10-07T10:00:00",
    "total_ask_size": 50.0,
    "total_bid_size": 45.0,
    "orderbook_units": [
      {"ask_price": 95500000, "bid_price": 95400000, "ask_size": 10.0, "bid_size": 8.0},
      {"ask_price": 95600000, "bid_price": 95300000, "ask_size": 12.0, "bid_size": 10.0}
    ]
  }
  ```

### Data 6: My Wallet

- **Purpose**: Offers a real-time overview of the investment status, including current holdings and balances.

- **Contents**:
  - An object containing:
    - `currency_balance`: Amount of KRW available for trading.
    - `coin_code`: The coin code (e.g., "BTC").
    - `coin_balance`: Amount of Bitcoin currently held.
    - `coin_avg_buy_price`: The average purchase price of the held Bitcoin.
    - Additional keys for convenience:
      - `KRW_balance`: Same as `currency_balance`.
      - `BTC_balance`: Same as `coin_balance`.
      - `BTC_avg_buy_price`: Same as `coin_avg_buy_price`.
    - `timestamp`: When the wallet data was retrieved.

- **Example**:
  ```json
  {
    "currency_balance": 7000000,
    "coin_code": "BTC",
    "coin_balance": 0.0315,
    "coin_avg_buy_price": 95000000,
    "KRW_balance": 7000000,
    "BTC_balance": 0.0315,
    "BTC_avg_buy_price": 95000000,
    "timestamp": "2023-10-07T10:00:00"
  }
  ```

## Technical Indicator Glossary

- **RSI_14**: Relative Strength Index over 14 periods. Values below 30 indicate oversold conditions; above 70 indicate overbought conditions.
- **MACD_12_26**, **MACD_signal_9**, **MACD_diff_12_26_9**: Indicators showing the relationship between two moving averages of prices. Positive values suggest upward momentum.
- **Bollinger Bands (BB_high_20_2, BB_low_20_2, BB_mid_20)**: Indicators that define high and low on a relative basis, indicating overbought and oversold conditions.
- **Stochastic Oscillator (Stoch_k_14_3, Stoch_d_14_3)**: Momentum indicators comparing a closing price to its price range over a specific period.
- **SMA (Simple Moving Average)** and **EMA (Exponential Moving Average)**: Averages that smooth out price data to identify trends.
- **ATR_14**: Average True Range over 14 periods, measuring market volatility.
- **OBV**: On-Balance Volume, indicating buying and selling pressure.

### Clarification on Ask and Bid Prices

- **Ask Price**: The lowest price a seller is willing to accept. Relevant for buying decisions.
- **Bid Price**: The highest price a buyer is willing to pay. Relevant for selling decisions.

## Instruction Workflow

### Pre-Decision Analysis:

1. **Review Current Investment State and Previous Decisions**: Understand your current portfolio and evaluate past decisions for effectiveness.
2. **Analyze Market Data**: Use technical indicators to assess market trends.
3. **Incorporate Crypto News Insights**: Identify news that could impact market sentiment.
4. **Analyze Fear and Greed Index**: Gauge overall market sentiment.
5. **Assess Orderbook Dynamics**: Understand current buy and sell pressures.

### Decision Making:

6. **Synthesize Analysis**: Combine all data to form a market view.
7. **Apply Risk Management Principles**: Align actions with your investment strategy.
8. **Determine Action and Percentage**: Decide to `buy`, `sell`, or `hold` and specify the portfolio percentage.

## Considerations

- **Factor in Transaction Fees**: Account for fees in your calculations.
- **Account for Market Slippage**: Be aware of the impact of large orders.
- **Maximize Returns**: Focus on strategies that offer the best risk-adjusted returns.
- **Mitigate Risks**: Use risk management techniques to protect your portfolio.
- **Stay Informed and Agile**: Be ready to adjust strategies as market conditions change.
- **Holistic Strategy**: Consider all available data for informed decisions.
- **Response Format**: Your response must be in JSON format, adhering to the specified schema.

## Response Schema

Your response must follow this JSON schema:

```json
{
  "decision": "buy" | "sell" | "hold",
  "percentage": <number between 0 and 100>,
  "reason": "<detailed reasoning>"
}
```

- **decision**: Must be one of `"buy"`, `"sell"`, or `"hold"`.
- **percentage**: Percentage of KRW to use for buying or BTC to sell.
- **reason**: Detailed explanation based on your analysis.

## Examples

### Example: Recommendation to Buy

```json
{
  "decision": "buy",
  "percentage": 40,
  "reason": "After analyzing the market data, the RSI_14 is at 45, indicating that Bitcoin is not overbought. The MACD line has crossed above the signal line, suggesting bullish momentum. Bollinger Bands show that the price is near the lower band, indicating a potential upward reversal. Recent news articles report increased institutional adoption of Bitcoin. The Fear and Greed Index is at 40 ('Fear'), suggesting that now might be a good time to buy before the market sentiment shifts. Therefore, it is recommended to buy, allocating 40% of the available KRW balance."
}
```

### Example: Recommendation to Sell

```json
{
  "decision": "sell",
  "percentage": 50,
  "reason": "The RSI_14 is at 75, indicating overbought conditions. The MACD histogram shows decreasing momentum. The price has touched the upper Bollinger Band, suggesting a potential downward correction. The Fear and Greed Index is at 80 ('Extreme Greed'), which often precedes a market pullback. Recent news mentions potential regulatory crackdowns. The orderbook shows higher ask sizes than bid sizes. Therefore, it is prudent to sell 50% of the BTC holdings to secure profits."
}
```

### Example: Recommendation to Hold

```json
{
  "decision": "hold",
  "percentage": 0,
  "reason": "Market indicators are mixed. The RSI_14 is around 50, indicating neutrality. The MACD line is flat, and there is no clear trend in the SMA and EMA. The Bollinger Bands are narrowing, suggesting low volatility. The Fear and Greed Index is at 50 ('Neutral'). Recent news is also mixed. The orderbook does not show significant imbalances. Therefore, it is advisable to hold the current position and wait for clearer market signals."
}
```

---

**Note**: Ensure all your analyses are based on the provided data. Be objective, and avoid any speculative language. Remember to adhere strictly to the JSON response format specified.
    """

    messages = [
        {"role": "system", "content": system_instruction},
        {
            "role": "user",
            "content": "Crypto News: "
            + json.dumps(force_dumps(news_data), ensure_ascii=False),
        },
        {
            "role": "user",
            "content": "Current Charts: "
            + json.dumps(force_dumps(market_data), ensure_ascii=False),
        },
        {
            "role": "user",
            "content": "Last Decisions: "
            + json.dumps(force_dumps(last_decisions), ensure_ascii=False),
        },
        {
            "role": "user",
            "content": "Fear and Greed Index: "
            + json.dumps(force_dumps(fnq_data), ensure_ascii=False),
        },
        {
            "role": "user",
            "content": "Upbit Orderbook: "
            + json.dumps(force_dumps(orderbook_data), ensure_ascii=False),
        },
        {
            "role": "user",
            "content": "My Wallet: "
            + json.dumps(force_dumps(wallet_data), ensure_ascii=False),
        },
    ]
    log("[GPT] Make request messages.", messages)
    log(f"[GPT] Request GPT({MODEL_NAME }, ExpectTokens: {get_expect_token_count(json.dumps(messages, ensure_ascii=False)):,})")

    response = safe_save_or_load(True, "all", "cache/gpts/gpt.json",
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
            n=MODEL_RESULT_CASE,
        ),
        lambda jsonData: ChatCompletion.model_validate(jsonData),
    )

    log(f"[GPT] Response GPT", response)
    output_tokens = response.usage.completion_tokens
    input_tokens = response.usage.prompt_tokens
    cached_tokens = response.usage.prompt_tokens_details.cached_tokens
    model_pricing = ((input_tokens - cached_tokens) / MODEL_PRICE_BASE * MODEL_PRICE_INPUT) 
    model_pricing += (output_tokens / MODEL_PRICE_BASE * MODEL_PRICE_OUTPUT)
    model_pricing += (cached_tokens / MODEL_PRICE_BASE *MODEL_PRICE_CACHE)

    log(f"[GPT] Completion_tokens: {output_tokens:,}")
    log(f"[GPT] Prompt_tokens: {input_tokens:,}")
    log(f"[GPT] Caching_tokens: {cached_tokens:,}")
    log(f"[GPT] Total_tokens: {response.usage.total_tokens:,}")
    log(f"[GPT] Model_pricing: ${model_pricing:,}")

    response_data = TradingDecision(**json.loads(response.choices[0].message.content))
    log("[GPT] Result", response_data)

    decision = response_data.decision
    reason = response_data.reason
    percentage = response_data.percentage

    # 3. AI의 판단에 따라 실제 매수매도하기

    if decision == "buy":
        trade = execute_buy(percentage)
        try:
            executed_volume = trade["executed_volume"]
            currency_total = trade["currency_total"]
            if trade["success"]:
                log(f"[Trade] Buy success (+{executed_volume:,} {COIN_CODE}, -{currency_total:,} {CURRENCY_CODE})", trade)
            else:
                log(f"[Trade] Buy failed", trade)
        except Exception as ex:
            logging.exception(ex)

    elif decision == "sell":
        trade = execute_sell(percentage)
        try:
            executed_volume = trade["executed_volume"]
            currency_total = trade["received_total"]
            if trade["success"]:
                log(f"[Trade] Sell success (-{executed_volume:,} {COIN_CODE}, +{currency_total:,} {CURRENCY_CODE})", trade)
            else:
                log(f"[Trade] Sell failed", trade)
        except Exception as ex:
            logging.exception(ex)

    elif decision == "hold":
        trade = {
            "success": True,
            "action": "hold",
            "error": "",
            "ticker": TRADE_CODE,
            "fee": 0,
            "attempts": 0,
            "executed_volume": 0,
            "avg_price": 0,
            "currency_funds": 0,
            "currency_fee": 0,
            "currency_total": 0,
            "trade": {"id":0}
        }
        log(f"[Trade] Hold")
    
    record_decision(TRADE_CODE, 
                    decision, 
                    percentage,
                    reason,
                    {
                        "trade_id": trade["trade"]["id"],
                        "news": news_data,
                        "market": market_data,
                        "decisions":last_decisions,
                        "fnq": fnq_data,
                        "orderbook": orderbook_data,
                        "wallet": wallet_data,
                        "response": response,
                        "trade": trade,
                        "model_pricing": model_pricing
                    })
    
    log(f"[Trade] Done")


# endregion 거래 실행 함수 영역

import signal

def signal_handler(signum, frame):
    log("[AutoTrade] 프로그램이 종료 신호를 받았습니다.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

while True:

    try:
        begin_log()

        execute_trading()

        end_log()

        log(f"[AutoTrade] Wait for 10 minutes.")

        time.sleep(600)

    except KeyboardInterrupt:
        logging.info("[AutoTrade] 키보드 인터럽트로 프로그램을 종료합니다.")
        break
    except SystemExit:
        logging.info("[AutoTrade] 시스템 종료 신호로 프로그램을 종료합니다.")
        break
    except Exception as e:
        logging.exception(str(e))
        log(f"[AutoTrade] Wait for 1 minutes.")
        time.sleep(60)

logging.info("[AutoTrade] 프로그램이 정상적으로 종료되었습니다.")
