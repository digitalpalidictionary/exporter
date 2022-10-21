from datetime import date
from pathlib import Path
from typing import Any
from typing import TypedDict

import os
import re
import subprocess
import sys

import pandas as pd

from dotenv import load_dotenv
from pandas.core.frame import DataFrame
from timeis import timeis, green, red


load_dotenv()


INDECLINABLES = {"abbrev", "abs", "ger", "ind", "inf", "prefix", "sandhi", "idiom"}
CONJUGATIONS = {"aor", "cond", "fut", "imp", "imperf", "opt", "perf", "pr"}
DECLENSIONS = {
    "adj", "card", "cs", "fem", "letter", "masc", "nt", "ordin", "pp", "pron",
    "prp", "ptp", "root", "suffix", "ve"
}


class DataFrames(TypedDict):
    words_df: DataFrame
    abbrev_df: DataFrame
    help_df: DataFrame


class ResourcePaths(TypedDict):
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
    word_template_path: Path


def parse_data_frames(rsc: ResourcePaths) -> DataFrames:
    """Parse csv files into pandas data frames"""

    words_df = pd.read_csv(rsc['words_path'], sep="\t", dtype=str)
    words_df = words_df.fillna("")

    abbrev_df = pd.read_csv(rsc['abbrev_path'], sep="\t", dtype=str)
    abbrev_df.fillna("", inplace=True)

    help_df = pd.read_csv(rsc['help_path'], sep="\t", dtype=str)
    help_df.fillna("", inplace=True)

    return DataFrames(
        words_df=words_df,
        abbrev_df=abbrev_df,
        help_df=help_df
    )


def get_resource_paths_dps() -> ResourcePaths:
    s = os.getenv('DPS_DIR')
    if s is None:
        print(f"{timeis()} {red}ERROR! DPS_DIR is not set.")
        sys.exit(2)
    else:
        dps_dir = Path(s)

    rsc = ResourcePaths(
        # Project output
        output_dir=Path("./output/"),
        output_html_dir=Path("./output/html/"),
        output_help_html_dir=Path("./output/help html/"),
        output_share_dir=Path("./share/"),
        gd_json_path=Path("./output/gd.json"),
        output_stardict_zip_path=Path("ru-pali-dictionary.zip"),
        error_log_dir=Path("./errorlogs/"),
        # Project assets
        dict_words_css_path=Path("./assets/words-dps.css"),
        dict_help_css_path=Path("./assets/help.css"),
        definition_css_path=Path("./assets/rpd.css"),
        buttons_js_path=Path("./assets/buttons-dps.js"),
        abbrev_path=Path("./assets/abbreviations.csv"),
        help_path=Path("./assets/help.csv"),
        # Project input
        inflections_dir=dps_dir.joinpath("inflection/"),
        words_path=dps_dir.joinpath("spreadsheets/dps-full.csv"),
        icon_path=Path("./logo/book.bmp"),
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
        print(f"{timeis()} {red}ERROR! DPS_DIR is not set.")
        sys.exit(2)
    else:
        dps_dir = Path(s)

    rsc = ResourcePaths(
        # Project output
        output_dir=Path("./output/"),
        output_html_dir=Path("./output/html/"),
        output_help_html_dir=Path("./output/help html/"),
        output_share_dir=Path("./share/"),
        gd_json_path=Path("./output/gd.json"),
        output_stardict_zip_path=Path("sbs-pd.zip"),
        error_log_dir=Path("./errorlogs/"),
        # Project assets
        dict_words_css_path=Path("./assets/words-sbs.css"),
        dict_help_css_path=Path("./assets/help.css"),
        definition_css_path=Path("./assets/epd.css"),
        buttons_js_path=Path("./assets/buttons-sbs.js"),
        abbrev_path=Path("./assets/abbreviations.csv"),
        help_path=Path("./assets/help.csv"),
        # Project input
        inflections_dir=dps_dir.joinpath("inflection/"),
        words_path=dps_dir.joinpath("spreadsheets/sbs-pd.csv"),
        icon_path=Path("./logo/head_brown.bmp"),
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
    print(f"{timeis()} {green}copying goldendict to share")

    today = date.today()

    # file name without .zip suffix
    dest_base = src_path.name.replace(src_path.suffix, '')

    dest_path = dest_dir.joinpath(f"{dest_base}.zip")

    try:
        subprocess.run(
            ['mv', '--backup=numbered', src_path, dest_path],
            check=True)
    except Exception as e:
        print(f"{timeis()} {red}{e}")
        sys.exit(2)


class DpsWord:
    def __init__(self, df: DataFrame, row: int):
        self.pali: str = df.loc[row, "Pāli1"]
        self.pali_: str = "_" + re.sub(" ", "_", self.pali)
        self.pali_clean: str = re.sub(r" \d*$", "", self.pali)
        self.fin: str = df.loc[row, "Fin"]
        self.pos: str = df.loc[row, "POS"]
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
