# 라이브러리 가져오기
import os
from dotenv import load_dotenv
from openai import OpenAI
import pyupbit
import json

load_dotenv()
upbit_akey = os.getenv("UPBIT_ACCESS_KEY")
upbit_skey = os.getenv("UPBIT_SECRET_KEY")
openai_key = os.getenv("OPENAI_API_KEY")
upbit_currency = "KRW"
upbit_target = "ETH"
upbit_target_name = "Ethereum"
upbit_code = upbit_currency + "-" + upbit_target


def ai_trading():
    # 초기화하기
    client = OpenAI()
    upbit = pyupbit.Upbit(upbit_akey, upbit_skey)

    # 1. 업비트 차트데이터 가져오기
    df = pyupbit.get_ohlcv(upbit_code, interval="day", count=30)

    print("------------------------------------------------")
    print("-- BITCOIN CHART")
    print("------------------------------------------------")
    print(df)
    print("")

    # 2. AI에게 데이터 제공하고 판단 받기

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are an expert in "
                        + upbit_target_name
                        + ' investing. Tell me whether to buy, sell, or hold at the moment based on the chart data provided. response in json format\n\nResponse Example:\n{"decision":"buy", "reason":"some technical reason"}\n{"decision":"sell", "reason":"some technical reason"}\n{"decision":"hold", "reason":"some technical reason"}',
                    }
                ],
            },
            {"role": "user", "content": [{"type": "text", "text": df.to_json()}]},
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
    upbit_target_balance = upbit.get_balance(upbit_target)
    upbit_currency_balance = upbit.get_balance(upbit_currency)

    print(upbit_currency + " : ", upbit.get_balance(upbit_currency))
    print(upbit_target + " : ", upbit.get_balance(upbit_target))

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
