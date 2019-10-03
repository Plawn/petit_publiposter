import copy
import json
from typing import Dict, List, Tuple

from ..constants import FIELD_NAME_OPTION, INFO_FIELD_NAME, PREV_TOKEN
from ..ReplacerMiddleware import MultiReplacer
from . import utils
from .utils import ThisFallbackAction


class Model:
    """To safely replace with jinja2 template
    """

    start = '{{'
    end = '}}'
    sep = '.'

    def __init__(self, strings: List[str], replacer: MultiReplacer):
        self.structure = None
        self.replacer = replacer
        self.fallback_action = ThisFallbackAction(
            FIELD_NAME_OPTION, self.replacer)

        self.load(strings, self.replacer)

    def load(self, strings_and_info: List[Tuple[str, Dict[str, str]]], replacer: MultiReplacer):
        """
        Makes a model for a given list of string like :

        mission.document.name => {
            mission: {
                document: {
                    name: "{{mission.document.name}}"
                }
            }
        }
        This way we will merge the model with the input in order to ensure that placeholder are replaced with what we want
        """
        res = {}
        for string, infos in strings_and_info:
            l = string.split(self.sep)
            previous = []
            end = len(l) - 1
            for i, item in enumerate(l):
                d = res
                last_node = None
                last_prev = None
                for prev in previous[:-1]:
                    d = d[prev]
                    last_node = d
                    last_prev = prev

                if len(previous) > 0:
                    d = d[previous[-1]]
                    last_prev = previous[-1]

                if item not in d:
                    if i != end:
                        d[item] = {}
                    else:
                        if not PREV_TOKEN in infos:
                            d[item] = {
                                FIELD_NAME_OPTION: f'{self.start}{replacer.to_doc(string)}{self.end}',
                                INFO_FIELD_NAME: infos
                            }
                        else:
                            del infos[PREV_TOKEN]
                            d[item] = {
                                FIELD_NAME_OPTION: f'{self.start}{replacer.to_doc(string)}{self.end}'}
                            if INFO_FIELD_NAME not in last_node[last_prev]:
                                last_node[last_prev] = {INFO_FIELD_NAME: infos}
                            else:
                                last_node[last_prev][INFO_FIELD_NAME].update(
                                    infos)
                previous.append(item)
        self.structure = res

    def merge(self, _input: dict, ensure_keys=True) -> dict:
        """
        """
        d1 = copy.deepcopy(self.structure)
        utils.merge_dict(d1, _input)
        if ensure_keys:
            utils.ensure_keys(d1, self.fallback_action)
        return d1

    def to_json(self) -> dict:
        return self.structure
