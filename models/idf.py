from typing import List, Optional, Union
from pydantic import BaseModel, IPvAnyAddress


class InternalDataFormat(BaseModel):
    """The Internal Data Format (IDF)."""
    leak_id: Optional[str]      # the leak(id) reference
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
    #
    # flags set by the enrichers
    dg: Optional[str]
    external_user: Optional[bool]
    is_vip: Optional[bool]
    is_active_account: Optional[bool]
    credential_type: Optional[List[str]]    # External, EU Login, etc.
    report_to: Optional[List[str]]          # whom to report this to?
    #
    # meta stuff and things for error reporting
    count_seen: Optional[int] = 1
    original_line: Optional[str]
    error_msg: Optional[str]
    notify: Optional[bool]
    needs_human_intervention: Optional[bool]

