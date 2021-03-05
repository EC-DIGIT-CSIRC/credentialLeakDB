#!/usr/bin/env python3
"""Spycloud parser"""

import logging
from pathlib import Path

import pandas as pd
# from parser import BaseParser
from .parser import BaseParser


class SpycloudParser(BaseParser):
    """Parse Spycloud CSVs"""
    def parse_file(self, fname: Path, csv_dialect='excel') -> pd.DataFrame:
        """Parse the Spycloud CSV files, which are in the form:

            breach_title,spycloud_publish_date,breach_date,email,domain,username,password,salt,target_domain,target_url,password_plaintext,sighting,severity,status,password_type,cc_number,infected_path,infected_machine_id,email_domain,cc_expiration,cc_last_four,email_username,user_browser,infected_time,ip_addresses

        Returns:
            a DataFrame
            number of errors while parsing
        """
        logging.debug("Parsing SPYCLOUD file %s...", fname)
        try:
            df = pd.read_csv(fname, dialect=csv_dialect, header=1, error_bad_lines=False, warn_bad_lines=True)
            logging.debug(df.head())
            return df

        except Exception as ex:
            logging.error("could not pandas.read_csv(%s). Reason: %s. Skipping file." %(fname, str(ex)))
            return None

    def normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Bring the pandas DataFrame into an internal data format."""
        return df
