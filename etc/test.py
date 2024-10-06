from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field
import json
import os

print(os.path.splitext("cache/test.json"))
print(os.path.splitext("cache/test.json"))

print(os.path.splitext(os.path.splitext("cache/test.json")[0]))
print(os.path.splitext(os.path.splitext("cache/test.json")[0]))
