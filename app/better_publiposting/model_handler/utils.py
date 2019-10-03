from collections.abc import Mapping
from typing import List

from ..ReplacerMiddleware import MultiReplacer


class FallbackAction:
    def __init__(self, field_name: str, replacer: MultiReplacer):
        self.field_name = field_name

    def prepare_fallback(self, _dict: dict, key: str) -> None:
        pass


# ugly name i know
class ThisFallbackAction(FallbackAction):
    def __init__(self, field_name: str, replacer: MultiReplacer):
        super().__init__(field_name, replacer)
        self.replacer = replacer

    def prepare_fallback(self, _dict: dict, key: str) -> None:
        new_key = self.replacer.to_doc(key)
        _dict[new_key] = _dict[key][self.field_name]
        if key != new_key:
            del _dict[key]


def merge_dict(d1: dict, d2: dict):
    """
    Modifies d1 in-place to contain values from d2.  If any value
    in d1 is a dictionary (or dict-like), *and* the corresponding
    value in d2 is also a dictionary, then merge them in-place.
    """
    for key, v2 in d2.items():
        v1 = d1.get(key)  # returns None if v1 has no value for this key
        if (isinstance(v1, Mapping) and isinstance(v2, Mapping)):
            merge_dict(v1, v2)
        else:
            d1[key] = v2


def ensure_keys(d: dict, fallback_action: FallbackAction):
    for key, item in d.items():
        if isinstance(item, Mapping) and fallback_action.field_name in item:
            fallback_action.prepare_fallback(d, key)
        else:
            if isinstance(item, Mapping):
                ensure_keys(item, fallback_action)
