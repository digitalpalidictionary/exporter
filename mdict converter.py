#!/usr/bin/env python3
# coding: utf-8

import json
from functools import reduce
from timeis import timeis, yellow, line, white, green, red

#only if you don't want to install writemdict library
import sys
sys.path.insert(1, './writemdict') 

from writemdict import MDictWriter
import re

ifo = {
            "bookname": "Digital Pāḷi Dictionary",
            "author": "Bodhirasa",
            "description": "Digital Pāḷi Dictionary",
            "website": "https://digitalpalidictionary.github.io",
        }

def synonyms(all_items, item):
    all_items.append((item['word'], item['definition_html']))
    for word in item['synonyms']:
        if word != item['word']:
            all_items.append((word, f"""@@@LINK={item["word"]}"""))
    return all_items

def convert_to_mdict(json_data):
    print(f"{timeis()} {green}writing mdict")
    dpd_data = reduce(synonyms, json_data, [])
    writer = MDictWriter(dpd_data, title=ifo['bookname'], description = f"<p>by {ifo['author']} </p> <p>For more infortmation, please visit <a href=\"{ifo['website']}\">{ifo['description']}</a></p>")
    outfile = open('share/dpd.mdx', 'wb')
    writer.write(outfile)
    outfile.close()

if __name__ == '__main__':
    print(f"{timeis()}{line}")
    print(f"{timeis()} {yellow}converting to mdict")
    print(f"{timeis()}{line}")
    json_data = json.load(open('output/gd.json'))
    convert_to_mdict(json_data)

