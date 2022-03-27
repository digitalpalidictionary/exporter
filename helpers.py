import os
import sys
from pathlib import Path
from typing import TypedDict
from datetime import date
from datetime import datetime
import subprocess
import re

from dotenv import load_dotenv

import pandas as pd
from pandas.core.frame import DataFrame

load_dotenv()


class DataFrames(TypedDict):
    words_df: DataFrame
    roots_df: DataFrame
    abbrev_df: DataFrame
    help_df: DataFrame


class ResourcePaths(TypedDict):
    output_dir: Path
    output_html_dir: Path
    output_root_html_dir: Path
    output_help_html_dir: Path
    output_share_dir: Path
    error_log_dir: Path
    compound_families_dir: Path
    frequency_dir: Path
    root_families_dir: Path
    inflections_dir: Path
    words_path: Path
    roots_path: Path
    abbrev_path: Path
    help_path: Path
    dpd_words_css_path: Path
    dpd_roots_css_path: Path
    dpd_help_css_path: Path
    buttons_js_path: Path
    gd_json_path: Path
    icon_path: Path
    output_stardict_zip_path: Path


def parse_data_frames(rsc: ResourcePaths) -> DataFrames:
    """Parse csv files into pandas data frames"""

    words_df = pd.read_csv(rsc['words_path'], sep = "\t", dtype=str)
    words_df = words_df.fillna("")

    roots_df = pd.read_csv(rsc['roots_path'], sep="\t", dtype=str)
    roots_df.fillna("", inplace=True)

    # roots_df.replace("\.0$", "", inplace=True, regex=True)
    # roots_df = roots_df[roots_df["Count"] != "0"] # remove roots with no examples
    roots_df = roots_df[roots_df["Fin"] != ""] # remove extra iines

    abbrev_df = pd.read_csv(rsc['abbrev_path'], sep="\t", dtype=str)
    abbrev_df.fillna("", inplace=True)

    help_df = pd.read_csv(rsc['help_path'], sep="\t", dtype=str)
    help_df.fillna("", inplace=True)

    return DataFrames(
        words_df = words_df,
        roots_df = roots_df,
        abbrev_df = abbrev_df,
        help_df = help_df
    )


def get_resource_paths() -> ResourcePaths:
    s = os.getenv('DPD_DIR')
    if s is None:
        print(f"{timeis()} {red}ERROR! DPD_DIR is not set.")
        sys.exit(2)
    else:
        dpd_dir = Path(s)

    rsc = ResourcePaths(
        # Project output
        output_dir = Path("./output/"),
        output_html_dir = Path("./output/html/"),
        output_root_html_dir = Path("./output/root html/"),
        output_help_html_dir = Path("./output/help html/"),
        output_share_dir = Path("./share/"),
        gd_json_path = Path("./output/gd.json"),
        output_stardict_zip_path = Path("dpd.zip"),
        error_log_dir = Path("./errorlogs/"),
        # Project assets
        dpd_words_css_path = Path("./assets/dpd-words.css"),
        dpd_roots_css_path = Path("./assets/dpd-roots.css"),
        dpd_help_css_path = Path("./assets/dpd-help.css"),
        buttons_js_path = Path("./assets/buttons.js"),
        abbrev_path = Path("./assets/abbreviations.csv"),
        help_path = Path("./assets/help.csv"),
        # Project input
        compound_families_dir = dpd_dir.joinpath("compound families generator/"),
        frequency_dir = dpd_dir.joinpath("frequency maps/"),
        root_families_dir = dpd_dir.joinpath("root families generator/"),
        inflections_dir = dpd_dir.joinpath("inflection generator/"),
        words_path = dpd_dir.joinpath("csvs/dpd-full.csv"),
        roots_path = dpd_dir.joinpath("csvs/roots.csv"),
        
        icon_path = dpd_dir.joinpath("favicon/favicon_io nu circle/favicon.ico"),
    )

    # ensure write dirs exist
    for d in [rsc['output_dir'],
              rsc['output_html_dir'],
              rsc['output_root_html_dir'],
              rsc['output_share_dir'],
              rsc['error_log_dir']]:
        d.mkdir(parents=True, exist_ok=True)

    return rsc

def copy_goldendict(src_path: Path, dest_dir: Path):
    print(f"{timeis()} {green}copying goldendict to share")

    today = date.today()

    # file name without .zip suffix
    dest_base = src_path.name.replace(src_path.suffix, '')

    dest_path = dest_dir.joinpath(f"{dest_base}-{today}.zip")

    try:
        subprocess.run(
            ['mv', '--backup=numbered', src_path, dest_path],
            check=True)
    except Exception as e:
        print(f"{timeis()} {red}{e}")
        sys.exit(2)


class DpdWord:
    def __init__(self, df: DataFrame, row: int):
        self.pali: str = df.loc[row, "Pāli1"]
        self.pali_: str = "_" + re.sub(" ", "_", self.pali)
        self.pali2: str = df.loc[row, "Pāli2"]
        self.pali_clean: str = re.sub(r" \d*$", "", self.pali)
        self.pos: str = df.loc[row, "POS"]
        self.grammar: str = df.loc[row, "Grammar"]
        self.neg: str = df.loc[row, "Neg"]
        self.verb: str = df.loc[row, "Verb"]
        self.trans: str = df.loc[row, "Trans"]
        self.case: str = df.loc[row, "Case"]
        self.meaning: str = df.loc[row, "Meaning IN CONTEXT"]
        self.lit: str = df.loc[row, "Literal Meaning"]
        self.buddhadatta: str = df.loc[row, "Buddhadatta"]
        self.non_ia: str = df.loc[row, "Non IA"]
        self.sk: str = df.loc[row, "Sanskrit"]
        self.sk_root: str = df.loc[row, "Sk Root"]
        self.sk_root_mn: str = df.loc[row, "Sk Root Mn"]
        self.sk_root_cl: str = df.loc[row, "Cl"]
        self.root: str = df.loc[row, "Pāli Root"]
        self.root_in_comps: str = df.loc[row, "Root In Comps"]
        self.root_verb: str = df.loc[row, "V"]
        self.root_grp: str = df.loc[row, "Grp"]
        self.root_sign: str = df.loc[row, "Sgn"]
        self.root_meaning: str = df.loc[row, "Root Meaning"]
        self.base: str = df.loc[row, "Base"]
        self.family: str = df.loc[row, "Family"]
        self.family2: str = df.loc[row, "Family2"]
        self.construction: str =  df.loc[row, "Construction"]
        self.derivative: str = df.loc[row, "Derivative"]
        self.suffix: str = df.loc[row, "Suffix"]
        self.pc: str = df.loc[row, "Phonetic Changes"]
        self.comp: str = df.loc[row, "Compound"]
        self.comp_constr: str = df.loc[row, "Compound Construction"]
        self.source1: str = df.loc[row, "Source1"]
        self.sutta1: str = df.loc[row, "Sutta1"]
        self.eg1: str = df.loc[row, "Example1"]
        self.source2: str = df.loc[row, "Source 2"]
        self.sutta2: str = df.loc[row, "Sutta2"]
        self.eg2: str = df.loc[row, "Example 2"]
        self.ant: str = df.loc[row, "Antonyms"]
        self.syn: str = df.loc[row, "Synonyms – different word"]
        self.var: str = df.loc[row, "Variant – same constr or diff reading"]
        self.comm: str = df.loc[row, "Commentary"]
        self.comm: str = re.sub(r"(.+)\.$", "\\1", self.comm)
        self.notes: str = df.loc[row, "Notes"]
        self.cognate: str = df.loc[row, "Cognate"]
        self.category: str = df.loc[row, "Category"]
        self.stem: str = df.loc[row, "Stem"]
        self.metadata: str = df.loc[row, "Metadata"]
        self.link: str = df.loc[row, "Link"]

def timeis():
	global blue
	global yellow
	global green
	global red
	global white

	blue = "\033[38;5;33m" #blue
	green = "\033[38;5;34m" #green
	red= "\033[38;5;160m" #red
	yellow = "\033[38;5;220m" #yellow
	white = "\033[38;5;251m" #white
	now = datetime.now()
	current_time = now.strftime("%Y-%m-%d %H:%M:%S")
	return (f"{blue}{current_time}{white}")
timeis()