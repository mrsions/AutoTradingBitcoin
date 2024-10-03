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

limit_news = int(os.getenv("LIMIT_NEWS", 1000))
limit_daily_count = int(os.getenv("LIMIT_DAILY_COUNT", 30))
limit_hourly_count = int(os.getenv("LIMIT_HOURLY_COUNT", 30))
limit_monthly_count = int(os.getenv("LIMIT_MONTHLY_COUNT", 30))


# print(get_news_headlines())
youtube_captions = get_youtube_captions()
print(youtube_captions)
