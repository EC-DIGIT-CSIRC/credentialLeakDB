"""Purely abstract base enricher class."""

from models.idf import InternalDataFormat

class BaseEnricher:
    def __init__(self):
        pass

    def enrich(self, idf: InternalDataFormat) -> InternalDataFormat:
        return idf