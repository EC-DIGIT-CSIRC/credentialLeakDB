from typing import List, Optional, Union
from pydantic import BaseModel, IPvAnyAddress


class InternalDataFormat(BaseModel):
    """The Internal Data Format (IDF)."""
    email: str
    password: str
    password_plain: Optional[str]
    password_hashed: Optional[str]
    hash_algo: Optional[str]
    ticket_id: Optional[str]
    email_verified: Optional[bool] = False
    password_verified_ok: Optional[bool] = False
    ip: Optional[IPvAnyAddress]
    domain: Optional[str]
    target_domain: Optional[str]
    browser: Optional[str]
    malware_name: Optional[str]
    infected_machine: Optional[str]
    dg: Optional[str]
    # meta stuff and things for error reporting
    count_seen: Optional[int] = 1
    original_line: Optional[str]
    error_msg: Optional[str]
    notify: bool
    needs_human_intervention: bool

