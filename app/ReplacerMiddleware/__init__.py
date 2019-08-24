"""
Will Handle on the fly conversions

"""
from typing import Tuple, List
from .BaseReplacer import BaseReplacer
from .FuncReplacer import FuncReplacer
from .ListReplacer import ListReplacer
# Not really performant for now


class MultiReplacer:
    def __init__(self, replacers: List[BaseReplacer]):
        self.replacers = replacers

    def from_doc(self, text: str) -> Tuple[str, dict]:
        res = {}
        for replacer in self.replacers:
            text, addtional_infos = replacer.from_doc(text)
            res.update(addtional_infos)
        return text, res

    def to_doc(self, text: str)-> Tuple[str, dict]:
        res = {}
        for replacer in self.replacers:
            text, addtional_infos = replacer.to_doc(text)
            res.update(addtional_infos)
        return text, res
