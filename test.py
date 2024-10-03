from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field
import json


class TradingDecisionEnum(str, Enum):
    buy = "buy"
    sell = "sell"
    hold = "hold"


class TradingDecision(BaseModel):
    decision: TradingDecisionEnum = Field(
        ..., description="The trading decision: 'buy', 'sell', or 'hold'"
    )
    reason: str = Field(..., description="Detailed reason for the trading decision")


responseFormat2 = TradingDecision.schema_json()
print(json.dumps(json.loads(responseFormat2), indent=4))

schema1 = TradingDecision.model_json_schema()
schemaEnum = TradingDecisionEnum.model_json_schema()

responseFormat = {
    "type": "json_schema",
    "json_schema": {
        "name": TradingDecision.__name__,
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "": {
                    "type": "string",
                    "description": "The trading decision: 'buy', 'sell', or 'hold'",
                    "enum": ["buy", "sell", "hold"],
                },
                TradingDecision.reason.__name__: {
                    "type": "string",
                    "description": "Detailed reason for the trading decision",
                },
            },
            "required": ["decision", "reason"],
            "additionalProperties": False,
        },
    },
}
