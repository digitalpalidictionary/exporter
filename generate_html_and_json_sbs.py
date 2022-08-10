import pickle
import re
from datetime import date
from datetime import datetime
import stat
import time
import pandas as pd
import os
from timeis import timeis, yellow, green, red, line

from helpers import DataFrames, DpsWord, ResourcePaths, get_resource_paths_sbs, parse_data_frames
from html_components import render_header_tmpl, render_feedback_tmpl_sbs, render_word_meaning_sbs


def generate_html_and_json_sbs(generate_roots: bool = True):
    rsc = get_resource_paths_sbs()

    data = parse_data_frames(rsc)
    today = date.today()

    print(f"{timeis()} {yellow}generate html and json")
    print(f"{timeis()} {line}")
    print(f"{timeis()} {green}generating dps html")

    error_log = open(rsc['error_log_dir'].joinpath("exporter errorlog.txt"), "w")

    html_data_list = []
    text_data_full = ""
    text_data_concise = ""

    inflection_table_error_string = ""
    synonyms_error_string = ""

    # the big for loop

    df = data['words_df']
    df_length = data['words_df'].shape[0]

    with open(rsc['dict_words_css_path'], 'r') as f:
        words_css = f.read()

    with open(rsc['buttons_js_path'], 'r') as f:
        buttons_js = f.read()

    for row in range(df_length):

        w = DpsWord(df, row)

        if row % 5000 == 0 or row % df_length == 0:
            print(f"{timeis()} {row}/{df_length}\t{w.pali}")

        indeclinables = ["abbrev", "abs", "ger", "ind", "inf", "prefix", "sandhi", "idiom"]
        conjugations = ["aor", "cond", "fut", "imp", "imperf", "opt", "perf", "pr"]
        declensions = ["adj", "card", "cs", "fem", "letter", "masc", "nt", "ordin", "pp", "pron", "prp", "ptp", "root", "suffix", "ve"]

        html_string = ""
        text_full = ""
        text_concise = ""

        # html head & style

        html_string += render_header_tmpl(css=words_css, js=buttons_js)

        html_string += "<body>"

        # summary

        r = render_word_meaning_sbs(w)
        html_string += r['html']
        text_full += r['full']
        text_concise += r['concise']

        # buttons

        html_string += f"""<div class="button-box">"""

        if w.meaning != "":
            html_string += f"""<a class="button_sbs" href="javascript:void(0);" onclick="button_click(this)" data-target="grammar_sbs_{w.pali_}">grammar</a>"""

        if w.eg1 != "" and w.eg2 == "":
            html_string += f"""<a class="button_sbs" href="javascript:void(0);" onclick="button_click(this)" data-target="example_sbs_{w.pali_}">example</a>"""

        if w.eg1 == "" and w.eg2 != "" and w.eg3 == "":
            html_string += f"""<a class="button_sbs" href="javascript:void(0);" onclick="button_click(this)" data-target="example_sbs_{w.pali_}">example</a>"""

        if w.eg1 == "" and w.eg2 != "" and w.eg3 != "":
            html_string += f"""<a class="button_sbs" href="javascript:void(0);" onclick="button_click(this)" data-target="example_sbs_{w.pali_}">examples</a>"""

        if w.eg1 != "" and w.eg2 != "":
            html_string += f"""<a class="button_sbs" href="javascript:void(0);" onclick="button_click(this)" data-target="example_sbs_{w.pali_}">examples</a>"""

        if w.pos in conjugations:
            html_string += f"""<a class="button_sbs" href="javascript:void(0);" onclick="button_click(this)" data-target="conjugation_sbs_{w.pali_}">conjugation</a>"""

        if w.pos in declensions:
            html_string += f"""<a class="button_sbs" href="javascript:void(0);" onclick="button_click(this)" data-target="declension_sbs_{w.pali_}">declension</a>"""

        html_string += f"""<a class="button_sbs" href="javascript:void(0);" onclick="button_click(this)" data-target="feedback_sbs_{w.pali_}">feedback</a>"""
        html_string += f"""</div>"""

        # grammar

        html_string += f"""<div id="grammar_sbs_{w.pali_}" class="content_sbs hidden">"""
        html_string += f"""<table class = "table1_sbs">"""
        if w.pos != "":
            html_string += f"""<tr><th>Grammar</th><td>{w.pos}"""
            text_full += f"{w.pali}. {w.pos}"

        if w.grammar != "":
            html_string += f""", {w.grammar}"""
            text_full += f""", {w.grammar}"""

        if w.derived != "":
            html_string += f""", from {w.derived}"""
            text_full += f""", from {w.derived}"""

        if w.neg != "":
            html_string += f""", {w.neg}"""
            text_full += f""", {w.neg}"""

        if w.verb != "":
            html_string += f""", {w.verb}"""
            text_full += f""", {w.verb}"""

        if w.trans != "":
            html_string += f""", {w.trans}"""
            text_full += f""", {w.trans}"""

        if w.case != "":
            html_string += f""" ({w.case})"""
            text_full += f""" ({w.case})"""

        html_string += f"""</td></tr>"""
        html_string += f"""<tr valign="top"><th>Meaning</th><td><b>{w.meaning}</b>"""
        text_full += f""". {w.meaning}"""

        if w.russian != "":
            html_string += f"""</td></tr>"""
            html_string += f"""<tr valign="top"><th>Russian</th><td><b>{w.russian}</b>"""
            text_full += f""". {w.russian}"""

        html_string += f"""</td></tr>"""

        if w.root != "":
            html_string += f"""<tr valign="top"><th>Root</th><td>{w.root}</td></tr>"""
            text_full += f""". root: {w.root}"""

        if w.base != "":
            html_string += f"""<tr valign="top"><th>Base</th><td>{w.base}</td></tr>"""
            text_full += f""". base: {w.base}"""

        if w.construction != "":
            html_string += f"""<tr valign="top"><th>Construction</th><td>{w.construction}</td></tr>"""
            construction_text = re.sub("<br/>", ", ", w.construction)
            text_full += f""". construction: {construction_text}"""

        if w.var != "":
            html_string += f"""<tr valign="top"><th>Variant</th><td>{w.var}</td></tr>"""
            text_full += f"""variant: {w.var}"""

        if w.comm != "":
            html_string += f"""<tr valign="top"><th>Commentary</th><td>{w.comm}</td></tr>"""
            comm_text = re.sub("<br/>", " ", w.comm)
            comm_text = re.sub("<b>", "", comm_text)
            comm_text = re.sub("</b>", "", comm_text)
            text_full += f""". commentary: {comm_text}"""

        if w.notes != "":
            html_string += f"""<tr valign="top"><th>Notes</th><td>{w.notes}</td></tr>"""
            text_full += f""". notes: {w.notes}"""

        if w.sk != "":
            html_string += f"""<tr valign="top"><th>Sanskrit</th><td><i>{w.sk}</i></td></tr>"""
            text_full += f""". sanskrit: {w.sk}"""

        if w.sk_root != "":
            html_string += f"""<tr valign="top"><th>Sk root</th><td><i>{w.sk_root}</i></td></tr>"""
            text_full += f""". sk root: {w.sk_root}"""

        html_string += f"""</table>"""
        html_string += f"""<p><a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLScNC5v2gQbBCM3giXfYIib9zrp-WMzwJuf_iVXEMX2re4BFFw/viewform?usp=pp_url&entry.438735500={w.pali}&entry.1433863141=GoldenDict {today}" target="_blank">Report a mistake.</a></p>"""
        html_string += f"""</div>"""

        # examples

        if w.eg1 != "" and w.eg2 != "":

            html_string += f"""<div id="example_sbs_{w.pali_}" class="content_sbs hidden">"""

            html_string += f"""<p>{w.eg1}<p class="sutta_sbs">{w.source1} {w.sutta1}</p>"""
            html_string += f"""<p>{w.eg2}<p class="sutta_sbs">{w.source2} {w.sutta2}"""

            if w.chapter2 != "":
                html_string += f"""<br>{w.chapter2}"""
                if w.sbs_pali_chant2 != "":
                    html_string += f""", {w.sbs_pali_chant2}"""
                if w.sbs_eng_chant2 != "":
                    html_string += f""", {w.sbs_eng_chant2}"""
                html_string += f"""</p>"""
                

            if w.chapter3 != "":
                html_string += f"""<p>{w.eg3}<p class="sutta_sbs">{w.source3} {w.sutta3}"""
                html_string += f"""<br>{w.chapter3}"""
                if w.sbs_pali_chant3 != "":
                    html_string += f""", {w.sbs_pali_chant3}"""
                if w.sbs_eng_chant3 != "":
                    html_string += f""", {w.sbs_eng_chant3}"""
                html_string += f"""</p>"""

            html_string += f"""</div>"""

        elif w.eg1 != "" and w.eg2 == "":

            html_string += f"""<div id="example_sbs_{w.pali_}" class="content_sbs hidden">"""

            html_string += f"""<p>{w.eg1}<p class="sutta_sbs">{w.source1} {w.sutta1}</p>"""
            html_string += f"""</div>"""

        elif w.eg1 == "" and w.eg2 != "":

            html_string += f"""<div id="example_sbs_{w.pali_}" class="content_sbs hidden">"""

            html_string += f"""<p>{w.eg2}<p class="sutta_sbs">{w.source2} {w.sutta2}"""

            if w.chapter2 != "":
                html_string += f"""<br>{w.chapter2}"""
                if w.sbs_pali_chant2 != "":
                    html_string += f""", {w.sbs_pali_chant2}"""
                if w.sbs_eng_chant2 != "":
                    html_string += f""", {w.sbs_eng_chant2}"""
                html_string += f"""</p>"""

            if w.chapter3 != "":
                html_string += f"""<p>{w.eg3}<p class="sutta_sbs">{w.source3} {w.sutta3}"""
                html_string += f"""<br>{w.chapter3}"""
                if w.sbs_pali_chant3 != "":
                    html_string += f""", {w.sbs_pali_chant3}"""
                if w.sbs_eng_chant3 != "":
                    html_string += f""", {w.sbs_eng_chant3}"""
                html_string += f"""</p>"""

            html_string += f"""</div>"""

        # inflection table

        if w.pos not in indeclinables:
            table_path = rsc['inflections_dir'] \
                .joinpath("output/html tables/") \
                .joinpath(w.pali + ".html")

            if table_path.exists():
                with open(table_path) as f:
                    table_data_read = f.read()

            else:
                inflection_table_error_string += w.pali + ", "
                error_log.write(f"error reading inflection table: {w.pali}.html\n")

            if w.pos in declensions:

                html_string += f"""<div id="declension_sbs_{w.pali_}" class="content_sbs hidden">"""

            if w.pos in conjugations:

                html_string += f"""<div id="conjugation_sbs_{w.pali_}" class="content_sbs hidden">"""

            html_string += f"""{table_data_read}"""

            if w.pos != "sandhi" and w.pos != "idiom":

                if w.pos in declensions:

                    html_string += f"""<p>Have a suggestion?"""
                    html_string += f"""<p><a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLScNC5v2gQbBCM3giXfYIib9zrp-WMzwJuf_iVXEMX2re4BFFw/viewform?usp=pp_url&entry.438735500={w.pali}&entry.1433863141=GoldenDict {today}" target="_blank">Report a mistake.</a></p>"""

                if w.pos in conjugations:

                    html_string += f"""<p>Have a suggestion?"""
                    html_string += f"""<p><a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLScNC5v2gQbBCM3giXfYIib9zrp-WMzwJuf_iVXEMX2re4BFFw/viewform?usp=pp_url&entry.438735500={w.pali}&entry.1433863141=GoldenDict {today}" target="_blank">Report a mistake.</a></p>"""
            html_string += f"""</div>"""

        html_string += render_feedback_tmpl_sbs(w)

        html_string += f"""</body></html>"""

        # write gd.json

        inflections_path = rsc['inflections_dir'] \
            .joinpath("output/inflections translit/") \
            .joinpath(w.pali)

        if inflections_path.exists():
            with open(inflections_path, "rb") as syn_file:
                synonyms = pickle.load(syn_file)
                synonyms = (synonyms)

        else:
            synonyms_error_string += w.pali +", "
            error_log.write(f"error reading synonyms - {w.pali}\n")
            synonyms = ""

        # data compiling

        html_data_list += [[f"{w.pali}", f"""{html_string}""", "", synonyms]]
        text_data_full += f"{text_full}\n"
        text_data_concise += f"{text_concise}\n"

        if row % 100 == 0:
            p = rsc['output_html_dir'].joinpath(f"{w.pali} (sample).html")
            with open(p, "w", encoding="utf-8") as f:
                f.write(html_string)

    error_log.close()

    if inflection_table_error_string != "":
        print(f"{timeis()} {red}inflection table errors: {inflection_table_error_string}")

    if synonyms_error_string != "":
        print(f"{timeis()} {red}synonym errors: {synonyms_error_string}")
        
# convert ṃ to ṁ

    text_data_full = re.sub("ṃ", "ṁ", text_data_full)
    text_data_concise = re.sub("ṃ", "ṁ", text_data_concise)

# write text versions

    p = rsc['output_share_dir'].joinpath("sbs_full.txt")
    with open(p, "w", encoding ="utf-8") as f:
        f.write(text_data_full)

    p = rsc['output_share_dir'].joinpath("sbs_concise.txt")
    with open(p, "w", encoding ="utf-8") as f:
        f.write(text_data_concise)

    if generate_roots:
        generate_roots_html_and_json(data, rsc, html_data_list)
        # delete_unused_html_files()

def generate_roots_html_and_json(data: DataFrames, rsc: ResourcePaths, html_data_list):

    # html list > dataframe

    pali_data_df = pd.DataFrame(html_data_list)
    pali_data_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]


        # generate abbreviations html

    print(f"{timeis()} {green}generating abbreviations html")

    abbrev_data_list = []

    with open(rsc['dict_help_css_path'], 'r') as f:
        abbrev_css = f.read()

    abbrev_df = data['abbrev_df']
    abbrev_df_length = len(abbrev_df)

    for row in range(abbrev_df_length):

        html_string = ""

        abbrev = abbrev_df.iloc[row,0]
        meaning = abbrev_df.iloc[row,1]
        pali_meaning = abbrev_df.iloc[row,2]
        ru_meaning = abbrev_df.iloc[row,3]
        examp = abbrev_df.iloc[row,4]
        expl = abbrev_df.iloc[row,5]

        css = f"{abbrev_css}"
        html_string += render_header_tmpl(css=css, js="")

        html_string += "<body>"

        # summary

        html_string += f"""<div class="help_test"><p>abbreviation. <b>{abbrev}</b>. {meaning}. """

        if pali_meaning != "":
            html_string += f"""{pali_meaning}. """

        # if ru_meaning != "":
        #     html_string += f"""{ru_meaning}. """

        if examp != "":
            html_string += f"""<br>e.g. {examp}. """

        if expl != "":
            html_string += f"""<br>{expl}."""

        html_string += f"""</p></div>"""

        p = rsc['output_help_html_dir'].joinpath(f"{abbrev}.html")

        with open(p, 'w') as f:
            f.write(html_string)

        # compile root data into list
        synonyms = [abbrev, meaning]
        abbrev_data_list += [[f"{abbrev}", f"""{html_string}""", "", synonyms]]
        
# generate help html

    print(f"{timeis()} {green}generating help html")

    help_data_list = []

    with open(rsc['dict_help_css_path'], 'r') as f:
        help_css = f.read()

    help_df = data['help_df']
    help_df_length = len(help_df)

    for row in range(help_df_length):

        html_string = ""

        help_title = help_df.iloc[row,0]
        meaning = help_df.iloc[row,1]

        css = f"{help_css}"
        html_string += render_header_tmpl(css=css, js="")

        html_string += "<body>"

        # summary

        html_string += f"""<div class="help_sbs"><p>help. <b>{help_title}</b>. {meaning}</p></div>"""

        p = rsc['output_help_html_dir'].joinpath(f"{help_title}.html")

        with open(p, 'w') as f:
            f.write(html_string)
        
        # compile root data into list
        synonyms = [help_title]
        help_data_list += [[f"{help_title}", f"""{html_string}""", "", synonyms]]


        # generate epd html

    print(f"{timeis()} {green}generating epd html")
    
    df = data['words_df']
    df_length = data['words_df'].shape[0]
    pos_exclude_list = ["abbrev", "cs", "letter","root", "suffix", "ve"]

    epd = {}

    for row in range(df_length): #df_length
        w = DpsWord(df, row)
        meanings_list = []
        w.meaning = re.sub("\?\?", "", w.meaning)

        if row % 10000 == 0:
            print(f"{timeis()} {row}/{df_length}\t{w.pali}")      

        if w.meaning != "" and \
        w.pos not in pos_exclude_list:

            meanings_clean = re.sub(fr" \(.+?\)", "", w.meaning)                    # remove all space brackets
            meanings_clean = re.sub(fr"\(.+?\) ", "", meanings_clean)           # remove all brackets space
            meanings_clean = re.sub(fr"(^ | $)", "", meanings_clean)            # remove space at start and fin
            meanings_clean = re.sub(fr"  ", " ", meanings_clean)                    # remove double spaces
            meanings_clean = re.sub(fr" ;|; ", ";", meanings_clean)                 # remove space around ;
            meanings_clean = re.sub(fr"\(comm\).+$", "", meanings_clean)   # remove commentary meanings
            meanings_clean = re.sub(fr"lit.+$", "", meanings_clean)         # remove lit meanings
            meanings_list = meanings_clean.split(";")

            for meaning in meanings_list:
                if meaning in epd.keys() and w.case =="":
                    epd[meaning] = f"{epd[meaning]}<br><b>{w.pali_clean}</b> {w.pos}. {w.meaning}"
                if meaning in epd.keys() and w.case !="":
                    epd[meaning] = f"{epd[meaning]}<br><b>{w.pali_clean}</b> {w.pos}. {w.meaning} ({w.case})"
                if meaning not in epd.keys() and w.case =="":
                    epd.update({meaning: f"<b>{w.pali_clean}</b> {w.pos}. {w.meaning}"})
                if meaning not in epd.keys() and w.case !="":
                    epd.update({meaning: f"<b>{w.pali_clean}</b> {w.pos}. {w.meaning} ({w.case})"})

    with open(rsc['epd_css_path'], 'r') as f:
        epd_css = f.read()

    epd_data_list = []

    for key, value in epd.items():
        html_string = ""
        html_string = epd_css
        html_string += f"<body><div class ='epd_sbs'><p>{value}</p></div></body></html>"
        epd_data_list += [[f"{key}", f"""{html_string}""", "", ""]]

    # roots > dataframe > json

    print(f"{timeis()} {green}generating json")

    abbrev_data_df = pd.DataFrame(abbrev_data_list)
    abbrev_data_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]

    help_data_df = pd.DataFrame(help_data_list)
    help_data_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]

    epd_data_df = pd.DataFrame(epd_data_list)
    epd_data_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]

    pali_data_df = pd.concat([pali_data_df, abbrev_data_df, help_data_df, epd_data_df])

    print(f"{timeis()} {green}saving html to json")

    pali_data_df.to_json(rsc['gd_json_path'], force_ascii=False, orient="records", indent=6)

    print(f"{timeis()} {line}")


def delete_unused_html_files():
    print(f"{timeis()} {green}deleting unused html files")
    now = datetime.now()
    date = now.strftime("%d")
    for root, dirs, files in os.walk("output/html/", topdown=True):
        for file in files:
            stats = os.stat(f"output/html/{file}")
            mod_time = time.ctime (stats [stat.ST_CTIME])
            mod_time_date = re.sub("(.[^ ]+) (.[^ ]+) (.[^ ]+).+", r"\3", mod_time)
            if date != int(mod_time_date):
                try:
                    os.remove(f"output/html/{file}")
                    print(f"{timeis()} {file}")
                except:
                    print(f"{timeis()} {red}{file} not found")
    
    print(f"{timeis()} {green}deleting unused roots html files")
    for root, dirs, files in os.walk("output/root html/", topdown=True):
        for file in files:
            stats = os.stat(f"output/root html/{file}")
            mod_time = time.ctime (stats [stat.ST_CTIME])
            mod_time_date = re.sub("(.[^ ]+) (.[^ ]+) (.[^ ]+).+", r"\3", mod_time)
            if date != int(mod_time_date):
                try:
                    os.remove(f"output/root html/{file}")
                    print(f"{timeis()} {file}")
                except:
                    print(f"{timeis()} {red}{file} not found")
