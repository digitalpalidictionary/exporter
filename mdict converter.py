#!/usr/bin/env python3
# coding: utf-8

import sys
sys.path.insert(1, './writemdict')
from writemdict import MDictWriter
import json
import re
from functools import reduce
from timeis import timeis, yellow, line, white, green, red, tic, toc
import pickle

#only if you don't want to install writemdict library


ifo = {
    "bookname": "Digital Pāḷi Dictionary",
    "author": "Bodhirasa",
    "description": "Digital Pāḷi Dictionary",
    "website": "https://digitalpalidictionary.github.io",
}

ifo_light = {
    "bookname": "Digital Pāḷi Dictionary (Light)",
    "author": "Bodhirasa",
    "description": "A light version of Digital Pāḷi Dictionary for older devices",
    "website": "https://digitalpalidictionary.github.io",
}


def synonyms(all_items, item):
    all_items.append((item['word'], item['definition_html']))
    for word in item['synonyms']:
        if word != item['word']:
            all_items.append((word, f"""@@@LINK={item["word"]}"""))
    return all_items


def convert_to_mdict(dpd_data_dict, version):
    dpd_data = reduce(synonyms, dpd_data_dict, [])

    if version == "normal":
        writer = MDictWriter(
            dpd_data, title=ifo['bookname'], description=f"<p>by {ifo['author']} </p> <p>For more infortmation, please visit <a href=\"{ifo['website']}\">{ifo['description']}</a></p>")
        outfile = open('share/dpd-mdict.mdx', 'wb')
        writer.write(outfile)
        outfile.close()\

    if version == "light":
        writer = MDictWriter(
            dpd_data, title=ifo_light['bookname'], description=f"<p>by {ifo_light['author']} </p> <p>For more infortmation, please visit <a href=\"{ifo_light['website']}\">{ifo_light['description']}</a></p>")
        outfile = open('share/dpd-light-mdict.mdx', 'wb')
        writer.write(outfile)
        outfile.close()


if __name__ == '__main__':
    tic()
    print(f"{timeis()} {yellow}converting to mdict")
    print(f"{timeis()} {line}")

    print(f"{timeis()} {green}loading pickles")
    with open("output/dpd data", "rb") as f:
        pali_data_df = pickle.load(f)

    print(f"{timeis()} {green}replacing 'GoldenDict' with 'MDict'")
    pali_data_df['definition_html'] = pali_data_df['definition_html'].replace(
        "GoldenDict", "MDict", regex=True)

    print(f"{timeis()} {green}adding headword to html")
    pali_data_df['definition_html'] = "<h3>" + \
        pali_data_df['word'] + "</h3>" + pali_data_df['definition_html']

    print(f"{timeis()} {green}converting to python dict")
    dpd_data_dict = pali_data_df.to_dict(orient="records")
    del pali_data_df

    print(f"{timeis()} {green}saving MDict")
    convert_to_mdict(dpd_data_dict, "normal")
    toc()
