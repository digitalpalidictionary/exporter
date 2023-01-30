#!/usr/bin/env python3
# coding: utf-8

import json
import typer
import zipfile
from datetime import datetime
from timeis import timeis, yellow, green, line, tic, toc
import pickle

from generate_html_and_json import generate_html_and_json
from helpers import copy_goldendict, get_resource_paths


app = typer.Typer()

RSC = get_resource_paths()

@app.command()
def run_generate_html_and_json(generate_roots: bool = True):
    generate_html_and_json(generate_roots)

@app.command()
def run_generate_goldendict(move_to_dest: bool = True):
    tic()
    """Generate a Stardict-format .zip for GoldenDict."""

    rsc = get_resource_paths()

    # importing Simsapa here so other commands don't have to load it and its numerous dependencies
    from simsapa.app.stardict import export_words_as_stardict_zip, ifo_from_opts, DictEntry

    print(f"{timeis()} {yellow}generate goldendict")
    print(f"{timeis()} {line}")

    # print(f"{timeis()} {green}reading json")
    # with open(rsc['gd_json_path'], "r") as f:
    #     gd_data_read = json.load(f)
    
    print(f"{timeis()} {green}loading pickle")
    with open("output/dpd data", "rb") as f:
        pali_data_df = pickle.load(f)

    with open("output/dpd light data", "rb") as f:
        pali_light_data_df = pickle.load(f)
    
    gd_data_read = pali_data_df.to_dict(orient="records")
    gd_light_data_read = pali_light_data_df.to_dict(orient="records")

    print(f"{timeis()} {green}parsing")
    def item_to_word(x):
        return DictEntry(
            word=x["word"],
            definition_html=x["definition_html"],
            definition_plain=x["definition_plain"],
            synonyms=x["synonyms"],
        )

    words = list(map(item_to_word, gd_data_read))
    words_light = list(map(item_to_word, gd_light_data_read))

    ifo = ifo_from_opts(
        {
            "bookname": "Digital Pāḷi Dictionary",
            "author": "Bodhirasa",
            "description": "Digital Pāḷi Dictionary",
            "website": "https://digitalpalidictionary.github.io",
        }
    )

    ifo_light = ifo_from_opts(
        {
            "bookname": "Digital Pāḷi Dictionary (Light)",
            "author": "Bodhirasa",
            "description": "A light version of Digital Pāḷi Dictionary for older devices",
            "website": "https://digitalpalidictionary.github.io",
        }
    )

    print(f"{timeis()} {green}writing goldendict")
    export_words_as_stardict_zip(words, ifo, rsc['output_stardict_zip_path'], rsc['icon_path'])
    export_words_as_stardict_zip(words_light, ifo_light, rsc['output_stardict_light_zip_path'], rsc['icon_path'])

    zipfilepath = rsc['output_stardict_zip_path']
    with zipfile.ZipFile(zipfilepath, 'a') as zipf:
        source_path = rsc['icon_bmp_path']
        destination = 'dpd/android.bmp'
        zipf.write(source_path, destination)

    if move_to_dest:
        copy_goldendict(rsc['output_stardict_zip_path'], rsc['output_share_dir'], "goldendict")
        copy_goldendict(rsc['output_stardict_light_zip_path'], rsc['output_share_dir'], "goldendict light")
    
    toc()

def main():
    # Process cli with typer.
    app()

if __name__ == "__main__":
    main()

