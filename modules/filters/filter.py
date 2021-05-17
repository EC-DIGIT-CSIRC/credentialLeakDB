
from typing import Union

from models.idf import InternalDataFormat

class Filter:
    def __init__(self):
        pass

    def filter(self, idf: InternalDataFormat) -> Union[None, InternalDataFormat]:
        """Here we could implement all kinds of filters on data elements or whole rows.
        At the moment, this is a NOP.
        """
        return idf