import enum
import os
import subprocess
import sys

from datetime import datetime
from pathlib import Path
from typing import Any
from typing import TypedDict

import pandas as pd
import rich

from dotenv import load_dotenv
from pandas.core.frame import DataFrame

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
