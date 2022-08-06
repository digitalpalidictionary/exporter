#!/usr/bin/env python3
# coding: utf-8

import json

import typer

from timeis import timeis, yellow, green, line
from generate_html_and_json import generate_html_and_json
from generate_html_and_json_sbs import generate_html_and_json_sbs
from generate_html_and_json_test import generate_html_and_json_test
from helpers import ResourcePaths
from helpers import copy_goldendict, get_resource_paths, get_resource_paths_sbs, get_resource_paths_test


app = typer.Typer()

RSC = get_resource_paths()


@app.command()
def run_generate_html_and_json(generate_roots: bool = True):
    generate_html_and_json(generate_roots)


@app.command()
def run_generate_html_and_json_sbs(generate_roots: bool = True):
    generate_html_and_json_sbs(generate_roots)


@app.command()
def run_generate_html_and_json_test(generate_roots: bool = True):
    generate_html_and_json_test(generate_roots)



def _run_generate_goldendict(rsc: ResourcePaths, ifo: 'StarDictIfo', move_to_dest: bool = True):
    """Generate a Stardict-format .zip for GoldenDict."""

    # importing Simsapa here so other commands don't have to load it and its numerous dependencies
    from simsapa.app.stardict import export_words_as_stardict_zip, DictEntry

    print(f"{timeis()} {yellow}generate goldendict")
    print(f"{timeis()} {line}")

    print(f"{timeis()} {green}reading json")

    with open(rsc['gd_json_path'], "r") as f:
        gd_data_read = json.load(f)

    print(f"{timeis()} {green}parsing json")

    def item_to_word(x):
        return DictEntry(
            word=x["word"],
            definition_html=x["definition_html"],
            definition_plain=x["definition_plain"],
            synonyms=x["synonyms"],
        )

    words = list(map(item_to_word, gd_data_read))

    print(f"{timeis()} {green}writing goldendict")
    export_words_as_stardict_zip(words, ifo, rsc['output_stardict_zip_path'], rsc['icon_path'])

    if move_to_dest:
        copy_goldendict(rsc['output_stardict_zip_path'], rsc['output_share_dir'])

    print(f"{timeis()} {line}")


@app.command()
def run_generate_goldendict(move_to_dest: bool = True):
    from simsapa.app.stardict import ifo_from_opts, StarDictIfo

    rsc = get_resource_paths()

    ifo = ifo_from_opts({
            "bookname": "Пали Словарь",
            "author": "Бхиккху Дэвамитта",
            "description": "Русско-Пали и Пали-Русский Словарь",
            "website": "devamitta@sasanarakkha.org",
    })

    return _run_generate_goldendict(rsc, ifo, move_to_dest)


@app.command()
def run_generate_goldendict_sbs(move_to_dest: bool = True):
    from simsapa.app.stardict import ifo_from_opts, StarDictIfo

    rsc = get_resource_paths_sbs()

    ifo = ifo_from_opts({
        "bookname": "SBS Pāḷi Dictionary",
        "author": "Devamitta Bhikkhu",
        "description": "words from the SBS Pāḷi-English Recitation",
        "email": "sasanarakkha.org",
    })

    return _run_generate_goldendict(rsc, ifo, move_to_dest)


@app.command()
def run_generate_goldendict_test(move_to_dest: bool = True):
    from simsapa.app.stardict import ifo_from_opts, StarDictIfo

    rsc = get_resource_paths_test()

    ifo = ifo_from_opts({
        "bookname": "DPS Pāḷi Dictionary",
        "author": "Devamitta Bhikkhu",
        "description": "words from the Devamitta Pāḷi Study",
        "email": "devamitta@sasanarakkha.org",
    })

    return _run_generate_goldendict(rsc, ifo, move_to_dest)



def main():
    # Process cli with typer.
    app()


if __name__ == "__main__":
    main()
