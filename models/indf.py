from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, IPvAnyAddress


class SpyCloudInputEntry(BaseModel):
    """The SpyCloud intput format - one entry."""
    breach_title: str
    spycloud_publish_date: Optional[Union[str, datetime]]
    breach_date: Optional[Union[str, datetime]]
    email: str  # mandatory
    domain: str  # mandatory
    username: Optional[str]
    password: str
    salt: Optional[str]
    target_domain: Optional[str]
    target_url: Optional[str]
    password_plaintext: str = None
    sighting: Optional[int]
    severity: Optional[str]
    status: Optional[str]
    password_type: Optional[str]
    cc_number: Optional[str]
    infected_path: Optional[str]
    infected_machine_id: Optional[str]
    email_domain: str
    cc_expiration: Optional[str]
    cc_last_four: Optional[str]
    email_username: str
    user_browser: Optional[str]
    infected_time: Optional[Union[str, datetime]]
    ip_addresses: Optional[Union[str, IPvAnyAddress]]
