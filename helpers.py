import csv
import enum
import logging
import os
import re
import subprocess
import sys

from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Dict
from typing import TypedDict

import pandas as pd
import rich

from dotenv import load_dotenv
from pandas.core.frame import DataFrame

_LOGGER = logging.getLogger(__name__)

ENCODING = 'UTF-8'
INDECLINABLES = {'abbrev', 'abs', 'ger', 'ind', 'inf', 'prefix', 'sandhi', 'idiom'}
CONJUGATIONS = {'aor', 'cond', 'fut', 'imp', 'imperf', 'opt', 'perf', 'pr'}
DECLENSIONS = {
    'adj', 'card', 'cs', 'fem', 'letter', 'masc', 'nt', 'ordin', 'pp', 'pron',
    'prp', 'ptp', 'root', 'suffix', 've'
}

load_dotenv()


def timeis() -> str:
    """ Returns rich formatted date and time
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return f'[blue]{current_time}[/blue]'


def line(length=40) -> str:
    return '-' * length


class Kind(enum.Enum):
    """ Marks type of building dict
    """
    SBS = enum.auto()
    DPS = enum.auto()


class DataFrames(TypedDict):
    words_df: DataFrame
    abbrev_df: DataFrame
    help_df: DataFrame


class ResourcePaths(TypedDict):
    kind: Kind
    output_dir: Path
    output_html_dir: Path
    output_help_html_dir: Path
    output_share_dir: Path
    error_log_dir: Path
    inflections_dir: Path
    words_path: Path
    abbrev_path: Path
    help_path: Path
    dict_words_css_path: Path
    dict_help_css_path: Path
    definition_css_path: Path
    buttons_js_path: Path
    gd_json_path: Path
    icon_path: Path
    output_stardict_zip_path: Path
    abbreviation_template_path: Path
    word_template_path: Path


def parse_data_frames(rsc: ResourcePaths) -> DataFrames:
    """Parse csv files into pandas data frames"""

    words_df = pd.read_csv(rsc['words_path'], sep="\t", dtype=str)
    words_df = words_df.fillna('')

    abbrev_df = pd.read_csv(rsc['abbrev_path'], sep="\t", dtype=str)
    abbrev_df.fillna('', inplace=True)

    help_df = pd.read_csv(rsc['help_path'], sep="\t", dtype=str)
    help_df.fillna('', inplace=True)

    return DataFrames(
        words_df=words_df,
        abbrev_df=abbrev_df,
        help_df=help_df
    )


def get_resource_paths_dps() -> ResourcePaths:
    s = os.getenv('DPS_DIR')
    if s is None:
        rich.print(f"{timeis()} [red]ERROR! DPS_DIR is not set.")
        sys.exit(2)
    else:
        dps_dir = Path(s)

    rsc = ResourcePaths(
        kind=Kind.DPS,
        # Project output
        output_dir=Path('./output/'),
        output_html_dir=Path('./output/html/'),
        output_help_html_dir=Path('./output/help html/'),
        output_share_dir=Path('./share/'),
        gd_json_path=Path('./output/gd.json'),
        output_stardict_zip_path=Path('ru-pali-dictionary.zip'),
        error_log_dir=Path('./errorlogs/'),
        # Project assets
        dict_words_css_path=Path('./assets/words-dps.css'),
        dict_help_css_path=Path('./assets/help.css'),
        definition_css_path=Path('./assets/rpd.css'),
        buttons_js_path=Path('./assets/buttons-dps.js'),
        abbrev_path=Path('./assets/abbreviations.csv'),
        help_path=Path('./assets/help.csv'),
        # Project input
        abbreviation_template_path=Path('./assets/templates/abbreviation-dps.html'),
        inflections_dir=dps_dir.joinpath('inflection/'),
        words_path=dps_dir.joinpath('spreadsheets/dps-full.csv'),
        icon_path=Path('./logo/book.bmp'),
        word_template_path=Path('./assets/templates/word-dps.html'),
    )

    # ensure write dirs exist
    for d in [rsc['output_dir'],
              rsc['output_html_dir'],
              rsc['output_share_dir'],
              rsc['error_log_dir']]:
        d.mkdir(parents=True, exist_ok=True)

    return rsc


def get_resource_paths_sbs() -> ResourcePaths:
    s = os.getenv('DPS_DIR')
    if s is None:
        rich.print(f"{timeis()} [red]ERROR! DPS_DIR is not set.")
        sys.exit(2)
    else:
        dps_dir = Path(s)

    rsc = ResourcePaths(
        kind=Kind.SBS,
        # Project output
        output_dir=Path('./output/'),
        output_html_dir=Path('./output/html/'),
        output_help_html_dir=Path('./output/help html/'),
        output_share_dir=Path('./share/'),
        gd_json_path=Path('./output/gd.json'),
        output_stardict_zip_path=Path('sbs-pd.zip'),
        error_log_dir=Path('./errorlogs/'),
        # Project assets
        dict_words_css_path=Path('./assets/words-sbs.css'),
        dict_help_css_path=Path('./assets/help.css'),
        definition_css_path=Path('./assets/epd.css'),
        buttons_js_path=Path('./assets/buttons-sbs.js'),
        abbrev_path=Path('./assets/abbreviations.csv'),
        help_path=Path('./assets/help.csv'),
        # Project input
        inflections_dir=dps_dir.joinpath('inflection/'),
        words_path=dps_dir.joinpath('spreadsheets/sbs-pd.csv'),
        icon_path=Path('./logo/head_brown.bmp'),
        abbreviation_template_path=Path('./assets/templates/abbreviation-sbs.html'),
        word_template_path=Path('./assets/templates/word-sbs.html'),
    )

    # ensure write dirs exist
    for d in [rsc['output_dir'],
              rsc['output_html_dir'],
              rsc['output_share_dir'],
              rsc['error_log_dir']]:
        d.mkdir(parents=True, exist_ok=True)

    return rsc


def copy_goldendict(src_path: Path, dest_dir: Path):
    rich.print(f"{timeis()} [green]copying goldendict to share")

    # file name without .zip suffix
    dest_base = src_path.name.replace(src_path.suffix, '')

    dest_path = dest_dir.joinpath(f"{dest_base}.zip")

    try:
        subprocess.run(
            ['mv', '--backup=numbered', src_path, dest_path],
            check=True)
    except Exception as e:
        rich.print(f'{timeis()} [red]{e}[/red]')
        sys.exit(2)


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
    for key in sorted(result, key=lambda lex: len(lex), reverse=True):
        sorted_result[key] = result[key]

    _LOGGER.debug('Got En-Ru abbreviations dict: %s', sorted_result)
    return sorted_result


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


def string_if(condition: Any, string: str) -> str:
    """ Get the second arg if the first is true, empty string otherwise
    """
    if condition:
        return string
    return ''


def format_if(string: str, template: str) -> str:
    """ Format the second arg with the first if not empty

    :param string: any text
    :param template: template in form of 'string with a placeholder {}'
    :return: formatted template if the string is not empty or empty string
    """
    if len(string) > 0:
        return template.format(string)
    return ''
