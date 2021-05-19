"""Base, abstract Output class"""

from models.outdf import Answer


class BaseOutput:
    def __init__(self):
        pass

    def process(self, output_data: Answer) -> bool:
        """
        Process the output_data and do something with it.

        :returns bool... True on success.
        """
        return True
