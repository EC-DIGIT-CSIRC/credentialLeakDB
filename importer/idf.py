"""Internal Data Format for the parser.
Author: Aaron Kaplan
License: See LICENSE file.

"""

internal_format = {
    id:  int,
    leak_id: int,
    email: str,
    password: str,
    password_plain text,
    password_hashed text,
    hash_algo text,
    ticket_id text,
    email_verified boolean DEFAULT false,
    password_verified_ok boolean DEFAULT false,
    ip inet,
    domain text,
    url text,
    browser text,
    malware_name text,
    infected_machine text,
	DG text NOT NULL
}