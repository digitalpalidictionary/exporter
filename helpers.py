import os
import sys
from pathlib import Path
from typing import TypedDict
from datetime import date
from datetime import datetime
from timeis import timeis, green, red
import subprocess
import re


from dotenv import load_dotenv

import pandas as pd
from pandas.core.frame import DataFrame

load_dotenv()


class DataFrames(TypedDict):
    words_df: DataFrame
    # roots_df: DataFrame
    abbrev_df: DataFrame
    help_df: DataFrame


class ResourcePaths(TypedDict):
    output_dir: Path
    output_html_dir: Path
    # output_root_html_dir: Path
    output_help_html_dir: Path
    output_share_dir: Path
    error_log_dir: Path
    # compound_families_dir: Path
    # root_families_dir: Path
    inflections_dir: Path
    words_path: Path
    # roots_path: Path
    abbrev_path: Path
    help_path: Path
    dps_words_css_path: Path
    # dps_roots_css_path: Path
    dps_help_css_path: Path
    rpd_css_path: Path
    buttons_js_path: Path
    gd_json_path: Path
    icon_path: Path
    output_stardict_zip_path: Path


def parse_data_frames(rsc: ResourcePaths) -> DataFrames:
    """Parse csv files into pandas data frames"""

    words_df = pd.read_csv(rsc['words_path'], sep = "\t", dtype=str)
    words_df = words_df.fillna("")

    # roots_df = pd.read_csv(rsc['roots_path'], sep="\t", dtype=str)
    # roots_df.fillna("", inplace=True)

    # roots_df.replace("\.0$", "", inplace=True, regex=True)
    # roots_df = roots_df[roots_df["Count"] != "0"] # remove roots with no examples
    # roots_df = roots_df[roots_df["Fin"] != ""] # remove extra iines
    
    abbrev_df = pd.read_csv(rsc['abbrev_path'], sep="\t", dtype=str)
    abbrev_df.fillna("", inplace=True)

    help_df = pd.read_csv(rsc['help_path'], sep="\t", dtype=str)
    help_df.fillna("", inplace=True)

    return DataFrames(
        words_df = words_df,
        # roots_df = roots_df,
        abbrev_df = abbrev_df,
        help_df = help_df
    )


def get_resource_paths() -> ResourcePaths:
    s = os.getenv('DPS_DIR')
    if s is None:
        print(f"{timeis()} {red}ERROR! dps_DIR is not set.")
        sys.exit(2)
    else:
        dps_dir = Path(s)

    rsc = ResourcePaths(
        # Project output
        output_dir = Path("./output/"),
        output_html_dir = Path("./output/html/"),
        # output_root_html_dir = Path("./output/root html/"),
        output_help_html_dir = Path("./output/help html/"),
        output_share_dir = Path("./share/"),
        gd_json_path = Path("./output/gd.json"),
        output_stardict_zip_path = Path("ПалиСловарь.zip"),
        error_log_dir = Path("./errorlogs/"),
        # Project assets
        dps_words_css_path = Path("./assets/dps-words.css"),
        # dps_roots_css_path = Path("./assets/dps-roots.css"),
        dps_help_css_path = Path("./assets/dps-help.css"),
        rpd_css_path = Path("./assets/rpd.css"),
        buttons_js_path = Path("./assets/buttons.js"),
        abbrev_path = Path("./assets/abbreviations.csv"),
        help_path = Path("./assets/help.csv"),
        # Project input
        # compound_families_dir = dps_dir.joinpath("compound families generator/"),
        # root_families_dir = dps_dir.joinpath("root families generator/"),
        inflections_dir = dps_dir.joinpath("inflection/"),
        words_path = dps_dir.joinpath("spreadsheets/dps-full.csv"),
        # roots_path = dps_dir.joinpath("csvs/roots.csv"),
        icon_path = Path("./book.bmp"),
    )

    # ensure write dirs exist
    for d in [rsc['output_dir'],
              rsc['output_html_dir'],
            #   rsc['output_root_html_dir'],
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
        # self.pali2: str = df.loc[row, "Pāli2"]
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
        # self.lit: str = df.loc[row, "Literal Meaning"]
        self.russian: str = df.loc[row, "Meaning in native language"]
        self.sbs_meaning: str = df.loc[row, "Meaning in SBS-PER"]
        # self.buddhadatta: str = df.loc[row, "Buddhadatta"]
        # self.non_ia: str = df.loc[row, "Non IA"]
        self.sk: str = df.loc[row, "Sanskrit"]
        self.sk_root: str = df.loc[row, "Sk Root"]
        # self.sk_root_mn: str = df.loc[row, "Sk Root Mn"]
        # self.sk_root_cl: str = df.loc[row, "Cl"]
        self.root: str = df.loc[row, "Pāli Root"]
        # self.root_in_comps: str = df.loc[row, "Root In Comps"]
        # self.root_verb: str = df.loc[row, "V"]
        # self.root_grp: str = df.loc[row, "Grp"]
        # self.root_sign: str = df.loc[row, "Sgn"]
        # self.root_meaning: str = df.loc[row, "Root Meaning"]
        self.base: str = df.loc[row, "Base"]
        # self.family: str = df.loc[row, "Family"]
        # self.family2: str = df.loc[row, "Family2"]
        self.construction: str =  df.loc[row, "Construction"]
        # self.derivative: str = df.loc[row, "Derivative"]
        # self.suffix: str = df.loc[row, "Suffix"]
        # self.pc: str = df.loc[row, "Phonetic Changes"]
        # self.comp: str = df.loc[row, "Compound"]
        # self.comp_constr: str = df.loc[row, "Compound Construction"]
        self.source1: str = df.loc[row, "Source1"]
        self.sutta1: str = df.loc[row, "Sutta1"]
        self.eg1: str = df.loc[row, "Example1"]
        self.source2: str = df.loc[row, "Source 2"]
        self.sutta2: str = df.loc[row, "Sutta2"]
        self.eg2: str = df.loc[row, "Example 2"]
        self.sbs_pali_chant2: str = df.loc[row, "Pali chant 2"]
        self.sbs_eng_chant2: str = df.loc[row, "English chant 2"]
        self.chapter2: str = df.loc[row, "Chapter 2"]
        self.source3: str = df.loc[row, "Source 3"]
        self.sutta3: str = df.loc[row, "Sutta 3"]
        self.eg3: str = df.loc[row, "Example 3"]
        self.sbs_pali_chant3: str = df.loc[row, "Pali chant 3"]
        self.sbs_eng_chant3: str = df.loc[row, "English chant 3"]
        self.chapter3: str = df.loc[row, "Chapter 3"]
        self.sbs_index: str = df.loc[row, "Index"]
        # self.ant: str = df.loc[row, "Antonyms"]
        # self.syn: str = df.loc[row, "Synonyms – different word"]
        self.var: str = df.loc[row, "Variant"]
        self.comm: str = df.loc[row, "Commentary"]
        self.comm: str = re.sub(r"(.+)\.$", "\\1", self.comm)
        self.notes: str = df.loc[row, "Notes"]
        # self.cognate: str = df.loc[row, "Cognate"]
        # self.category: str = df.loc[row, "Category"]
        self.stem: str = df.loc[row, "Stem"]
        # self.metadata: str = df.loc[row, "Metadata"]
        # self.link: str = df.loc[row, "Link"]