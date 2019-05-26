import itertools
from prettytable import PrettyTable
import re


class Gob(object):
    pass


class Truths(object):
    mapping = {}

    def __init__(self, base=None, phrases=None, ints=True, mapping={}):
        if not base:
            raise Exception("Base items are required")
        self.base = base
        self.phrases = phrases or []
        self.ints = ints
        self.mapping = mapping
        self.phrases_transformed = [
            mapping[key] if key in mapping else key for key in phrases
        ]

        # generate the sets of booleans for the bases
        self.base_conditions = list(
            itertools.product([False, True], repeat=len(base))
        )

        # regex to match whole words defined in self.bases
        # used to add object context to variables in self.phrases
        self.p = re.compile(r"(?<!\w)(" + "|".join(self.base) + ")(?!\w)")

    def calculate(self, *args):
        # store bases in an object context
        g = Gob()
        for a, b in zip(self.base, args):
            setattr(g, a, b)

        # add object context to any base variables in self.phrases
        # then evaluate each
        eval_phrases = []
        for item in self.phrases:
            item = self.p.sub(r"g.\1", item)
            eval_phrases.append(eval(item))

        # add the bases and evaluated phrases to create a single row
        row = [getattr(g, b) for b in self.base] + eval_phrases
        if self.ints:
            return [int(item) for item in row]
        else:
            return row

    def __str__(self):
        t = PrettyTable(self.base + self.phrases_transformed)
        t.add_row(self.base + self.phrases)
        for conditions_set in self.base_conditions:
            t.add_row(self.calculate(*conditions_set))
        return str(t)
