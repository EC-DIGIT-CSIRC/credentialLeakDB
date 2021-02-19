"""Pydantic models definitions

Author: Aaron Kaplan
License: see LICENSE.
"""

from pydantic import BaseModel, EmailStr
import datetime

class leak(BaseModel):
    id: int
    summary: str
    reporter_name: str
    source_name: str
    breach_ts: datetime.datetime
    source_publish_ts: datetime.datetime
    ingestion_ts: datetime.datetime


class leak_data(BaseModel):
    id: int


