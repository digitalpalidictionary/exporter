import csv
import logging
import re

from typing import Dict

from pandas.core.frame import DataFrame
from pandas.core.frame import Series

from helpers import Kind
from helpers import ENCODING
from helpers import ResourcePaths
from helpers import get_resource_paths_dps

_LOGGER = logging.getLogger(__name__)

class DpsWord:
    abbreviations_ru = None

    def __init__(self, df: DataFrame, row: int):
        if DpsWord.abbreviations_ru is None:
            DpsWord.abbreviations_ru = _load_abbrebiations_ru(rsc=get_resource_paths_dps())  # TODO Pass rsc

        self.pali: str = df.loc[row, "Pāli1"]
        self.pali_: str = "_" + re.sub(" ", "_", self.pali)
        self.pali_clean: str = re.sub(r" \d*$", '', self.pali)
        self.fin: str = df.loc[row, "Fin"]
        self.pos: str = df.loc[row, "POS"]
        # Keeps initial value even after translate_abbreviations() call
        self.pos_orig: str = self.pos
        self.grammar: str = df.loc[row, "Grammar"]
        self.derived: str = df.loc[row, "Derived from"]
        self.neg: str = df.loc[row, "Neg"]
        self.verb: str = df.loc[row, "Verb"]
        self.trans: str = df.loc[row, "Trans"]
        self.case: str = df.loc[row, "Case"]
        self.meaning: str = df.loc[row, "Meaning IN CONTEXT"]
        self.russian: str = df.loc[row, "Meaning in native language"]
        self.sbs_meaning: str = df.loc[row, "Meaning in SBS-PER"]
        self.sk: str = df.loc[row, "Sanskrit"]
        self.sk_root: str = df.loc[row, "Sk Root"]
        self.root: str = df.loc[row, "Pāli Root"]
        self.base: str = df.loc[row, "Base"]
        self.construction: str = df.loc[row, "Construction"]
        self.source1: str = df.loc[row, "Source1"]
        self.sutta1: str = df.loc[row, "Sutta1"]
        self.eg1: str = df.loc[row, "Example1"]
        self.sbs_pali_chant1: str = df.loc[row, "Pali chant 1"]
        self.sbs_eng_chant1: str = df.loc[row, "English chant 1"]
        self.chapter1: str = df.loc[row, "Chapter 1"]
        self.source2: str = df.loc[row, "Source2"]
        self.sutta2: str = df.loc[row, "Sutta2"]
        self.eg2: str = df.loc[row, "Example2"]
        self.sbs_pali_chant2: str = df.loc[row, "Pali chant 2"]
        self.sbs_eng_chant2: str = df.loc[row, "English chant 2"]
        self.chapter2: str = df.loc[row, "Chapter 2"]
        self.source3: str = df.loc[row, "Source3"]
        self.sutta3: str = df.loc[row, "Sutta3"]
        self.eg3: str = df.loc[row, "Example3"]
        self.sbs_pali_chant3: str = df.loc[row, "Pali chant 3"]
        self.sbs_eng_chant3: str = df.loc[row, "English chant 3"]
        self.chapter3: str = df.loc[row, "Chapter 3"]
        self.sbs_index: str = df.loc[row, "Index"]
        self.var: str = df.loc[row, "Variant"]
        self.comm: str = re.sub(r"(.+)\.$", "\\1", df.loc[row, "Commentary"])
        self.notes: str = df.loc[row, "Notes"]
        self.stem: str = df.loc[row, "Stem"]
        self.ex: str = df.loc[row, "ex"]
        self.cl: str = df.loc[row, "class"]
        self.count: str = df.loc[row, "count"]

    def translate_abbreviations(self) -> None:
        # TODO Cache
        # TODO Process by lexems
        targets = [
            'pos',
            'grammar',
            'neg',
            'verb',
            'trans',
            'case',
            'base',
        ]

        for field in targets:
            for abbrev, translation in self.abbreviations_ru.items():
                val = getattr(self, field)
                setattr(self, field, val.replace(abbrev, translation))


class AbbreviationEntry:
    def __init__(self, kind: Kind, series: Series):
        self.abbrev = series.iloc[0]
        self.en_abbrev = series.iloc[0]
        self.meaning = series.iloc[1]
        self.en_meaning = series.iloc[1]
        self.pali_meaning = series.iloc[2]
        ru_meaning = series.iloc[3]
        self.example = series.iloc[4]
        self.explanation = series.iloc[5]
        ru_abbrev = series.iloc[6]

        if kind == Kind.DPS:
            if ru_abbrev:
                self.abbrev = ru_abbrev

            if ru_meaning:
                self.meaning = ru_meaning

    def __str__(self) -> str:
        return self.abbrev


def _load_abbrebiations_ru(rsc: ResourcePaths) -> Dict[str, str]:
    result = {}
    sorted_result = {}

    with open('./assets/abbreviations.csv', 'r', encoding=ENCODING) as abbrev_csv:
        reader = csv.reader(abbrev_csv, delimiter='\t')
        header = next(reader)  # Skip header
        _LOGGER.debug('Skipping abbreviations header %s', header)
        for row in reader:
            assert len(row) == 7, f'Expected 7 items in a row {row}'
            if row[6]:
                result[row[0]] = row[6]

    # Sort resulting dict from longer to shorter keys to match then long lexems first
    for key in sorted(result, key=lambda lex: len(lex), reverse=True):  # pylint: disable=unnecessary-lambda
        sorted_result[key] = result[key]

    _LOGGER.debug('Got En-Ru abbreviations dict: %s', sorted_result)
    return sorted_result
