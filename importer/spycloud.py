#!/usr/bin/env python3
"""Spycloud parser"""
import sys
import collections
import logging
from pathlib import Path


import pandas as pd
# from parser import BaseParser
from .parser import BaseParser


class SpycloudParser(BaseParser):
    """Parse Spycloud CSVs"""
    def parse_file(self, fname: Path, csv_dialect='excel', leak_id=None) -> pd.DataFrame:
        """Parse the Spycloud CSV files, which are in the form:

            breach_title,spycloud_publish_date,breach_date,email,domain,username,password,salt,target_domain,target_url,password_plaintext,sighting,severity,status,password_type,cc_number,infected_path,infected_machine_id,email_domain,cc_expiration,cc_last_four,email_username,user_browser,infected_time,ip_addresses

        Returns:
            a DataFrame
            number of errors while parsing
        """
        logging.debug("Parsing SPYCLOUD file %s...", fname)
        try:
            # df = pd.read_csv(fname, dialect=csv_dialect, header=1, error_bad_lines=False, warn_bad_lines=True)
            df = pd.read_csv(fname, error_bad_lines=False, warn_bad_lines=True)
            print(df)
            return df

        except Exception as ex:
            logging.error("could not pandas.read_csv(%s). Reason: %s. Skipping file." %(fname, str(ex)))
            return None

    def normalize_data(self, df: pd.DataFrame, leak_id=None) -> pd.DataFrame:
        """Bring the pandas DataFrame into an internal data format."""

        """ Spycloud headers:
          breach_title, spycloud_publish_date, breach_date, email,     domain, username, password, salt, target_domain, target_url, password_plaintext, sighting, severity, status, password_type, cc_number, infected_path, infected_machine_id, email_domain, cc_expiration, cc_last_four, email_username, user_browser, infected_time, ip_addresses
        map to:
          _,            leak.source_publish_ts, leak.breach_ts, email, domain, _,        password, _,    target_domain, _,          password_plain, _,            _,          _,    hash_algo, _, _,                          infected_machine, _ , _, _, _, browser, _, ip
        """
        mapping_tbl = collections.OrderedDict({
            "breach_title": None,
            "spycloud_publish_date": None,
            "breach_date": None,
            "email": "email",
            "domain": "domain",
            "username": None,
            "password": "password",
            "salt": None,
            "target_domain": "target_domain",
            "target_url": None,
            "password_plaintext": "password_plain",
            "sighting": None,
            "severity": None,
            "status": None,
            "password_type": "hash_algo",
            "cc_number": None,
            "infected_path": None,
            "infected_machine_id": "infected_machine",
            "email_domain": None,
            "cc_expiration": None,
            "cc_last_four": None,
            "email_username": None,
            "user_browser": "browser",
            "infected_time": None,
            "ip_addresses": "ip"
        })

        # This complexity sucks! need to get rid of it. No, itertools won't make it more understandable.
        retdf = pd.DataFrame()
        for i,r in df.iterrows():       # go over all df rows. Returns index, row
            # print(f"{i}:{r}")
            retrow = dict()             # build up what we want to return
            for k,v in r.items():       # go over all key-val items in the row
                # print(f"{k}:{v}", file=sys.stderr)
                if k in mapping_tbl.keys():
                    map_to = mapping_tbl[k]
                    if map_to:
                        print(f"mapping {k} to {map_to}!")
                        retrow[map_to] = v
                    else:
                        # don't map it
                        pass
            print("retrow = %r" % retrow)
            retdf = retdf.append(pd.Series(retrow), ignore_index=True)
        # retdf[:,'leak_id'] = leak_id
        print("retdf: %s" % retdf)
        return retdf
