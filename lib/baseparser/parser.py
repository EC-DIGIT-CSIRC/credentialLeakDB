"""Base Parser definitions. Purely abstrat."""

import pandas as pd

from models.idf import InternalDataFormat

class BaseParser:
    def __init__(self):
        pass

    def parse(self, df: pd.DataFrame) -> InternalDataFormat:
        pass