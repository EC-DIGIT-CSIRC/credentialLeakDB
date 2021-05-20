"""Pydantic models definitions

Author: Aaron Kaplan
License: see LICENSE.
"""

import datetime
from enum import Enum
from typing import Optional, Dict, List  # Union

from pydantic import BaseModel, EmailStr


class Leak(BaseModel):
    id: Optional[int]
    ticket_id: Optional[str]
    summary: str
    reporter_name: Optional[str]
    source_name: Optional[str]
    breach_ts: Optional[datetime.datetime]
    source_publish_ts: Optional[datetime.datetime]


class CredentialType(Enum):
    is_external = "External"
    is_proxy_login = "Proxy"
    is_EU_login = "EU Login"
    is_domain_login = "Domain"
    is_secem_login = "SECEM"


class LeakData(BaseModel):
    id: Optional[int]
    leak_id: int
    email: EmailStr
    password: str
    password_plain: Optional[str]
    password_hashed: Optional[str]
    hash_algo: Optional[str]
    ticket_id: Optional[str]
    email_verified: Optional[bool]
    password_verified_ok: Optional[bool]
    ip: Optional[str]
    domain: Optional[str]
    target_domain: Optional[str]  # new
    browser: Optional[str]
    malware_name: Optional[str]
    infected_machine: Optional[str]
    dg: Optional[str]
    is_vip: Optional[bool]
    credential_type: Optional[List[CredentialType]]
    report_to: Optional[List[str]]  # the security contact to report this to, in case it's not the the user directly.
    #
    # meta stuff and things for error reporting
    count_seen: Optional[int] = 1
    original_line: Optional[str]        # the original CSV file in case of errors
    error_msg: Optional[str]
    notify: bool
    needs_human_intervention: bool


class AnswerMeta(BaseModel):
    version: str
    duration: float
    count: int


class Answer(BaseModel):
    meta: Optional[AnswerMeta]
    data: List[Dict]  # Union[Dict,List]
    success: bool
    errormsg: Optional[str] = ""


""" Example:
Multiple answers:
{ "meta": { "version": "rel-1.0", "duration": 0.78, "count": 3 }, "data": [ <dict>, <dict>, <dict> ], "success": true,
  "errormsg": "all OK" }

No data:
{ "meta": { "version": "rel-1.0", "duration": 0.78 , "count": 0 }, "data": [], "success": true, "errormsg": "all OK" }

Single result:
{ "meta": { "version": "rel-1.0", "duration": 0.78 , "count": 1 }, "data": [ { "foo": "bar", "baz": 77 } ],
  "success": true, "errormsg": "all OK" }
"""
