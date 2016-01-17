import argparse

class smartformatter(argparse.HelpFormatter):
    """provide line breaks in argparse help"""

    def _split_lines(self, text, width):
            if text.startswith('R|'):
                return text[2:].splitlines()
            return argparse.HelpFormatter._split_lines(self,text,width)



