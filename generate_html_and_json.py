import pickle
import re
from datetime import date
from datetime import datetime
import stat
import time
import pandas as pd
import os
from timeis import timeis, yellow, green, red, line

from helpers import DataFrames, DpsWord, ResourcePaths, get_resource_paths, parse_data_frames
from html_components import render_header_tmpl, render_feedback_tmpl, render_word_meaning


def generate_html_and_json(generate_roots: bool = True):
    rsc = get_resource_paths()

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

    df = data['words_df']
    df_length = data['words_df'].shape[0]

    button_template = (
        '<a class="button_dps" href="javascript:void(0);" onclick="button_click(this)"'
        ' data-target="{target}">{name}</a>')

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

        r = render_word_meaning(w)
        html_string += r['html']
        text_full += r['full']
        text_concise += r['concise']

        # buttons

        html_string += '<div class="button-box">'
        examples = [i for i in [w.eg1, w.eg2, w.eg3] if i != ""]

        if w.meaning != "":
            html_string += button_template.format(target=f'grammar_dps_{w.pali_}', name='грамматика')

        if len(examples) == 1:
            html_string += button_template.format(target=f'example_dps_{w.pali_}', name="пример")
        elif len(examples) > 1:
            html_string += button_template.format(target=f'example_dps_{w.pali_}', name='примеры')

        if w.pos in conjugations:
            html_string += button_template.format(target=f'conjugation_dps_{w.pali_}', name='спряжения')

        if w.pos in declensions:
            html_string += button_template.format(target=f'declension_dps_{w.pali_}', name='склонения')

        html_string += button_template.format(target=f'feedback_dps_{w.pali_}', name='о словаре')
        html_string += '</div>'

        # grammar

        html_string += f"""<div id="grammar_dps_{w.pali_}" class="content_dps hidden">"""
        html_string += f"""<table class = "table1_dps">"""
        if w.pos != "":
            html_string += f"""<tr><th>часть речи</th><td>{w.pos}"""
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
        html_string += f"""<tr valign="top"><th>английский</th><td><b>{w.meaning}</b>"""
        text_full += f""". {w.meaning}"""

        if w.russian != "":
            html_string += f"""</td></tr>"""
            html_string += f"""<tr valign="top"><th>русский</th><td><b>{w.russian}</b>"""
            text_full += f""". {w.russian}"""

        html_string += f"""</td></tr>"""

        if w.root != "":
            html_string += f"""<tr valign="top"><th>корень</th><td>{w.root}</td></tr>"""
            text_full += f""". корень: {w.root}"""

        if w.base != "":
            html_string += f"""<tr valign="top"><th>основа</th><td>{w.base}</td></tr>"""
            text_full += f""". основа: {w.base}"""

        if w.construction != "":
            html_string += f"""<tr valign="top"><th>образование</th><td>{w.construction}</td></tr>"""
            construction_text = re.sub("<br/>", ", ", w.construction)
            text_full += f""". образование: {construction_text}"""

        if w.var != "":
            html_string += f"""<tr valign="top"><th>вариант</th><td>{w.var}</td></tr>"""
            text_full += f"""вариант: {w.var}"""

        if w.comm != "":
            html_string += f"""<tr valign="top"><th>комментарий</th><td>{w.comm}</td></tr>"""
            comm_text = re.sub("<br/>", " ", w.comm)
            comm_text = re.sub("<b>", "", comm_text)
            comm_text = re.sub("</b>", "", comm_text)
            text_full += f""". комментарий: {comm_text}"""

        if w.notes != "":
            html_string += f"""<tr valign="top"><th>заметки</th><td>{w.notes}</td></tr>"""
            text_full += f""". заметки: {w.notes}"""

        if w.sk != "":
            html_string += f"""<tr valign="top"><th>санскрит</th><td><i>{w.sk}</i></td></tr>"""
            text_full += f""". санскрит: {w.sk}"""

        if w.sk_root != "":
            html_string += f"""<tr valign="top"><th>санск. корень</th><td><i>{w.sk_root}</i></td></tr>"""
            text_full += f""". санск. корень: {w.sk_root}"""

        html_string += f"""</table>"""
        html_string += f"""<p><a class="link" href="https://docs.google.com/forms/d/1iMD9sCSWFfJAFCFYuG9HRIyrr9KFRy0nAOVApM998wM/viewform?usp=pp_url&entry.438735500={w.pali}&entry.1433863141=GoldenDict {today}" target="_blank">Пожалуйста, сообщите об ошибке.</a></p>"""
        html_string += f"""</div>"""

        # examples

        html_string += f"""<div id="example_dps_{w.pali_}" class="content_dps hidden">"""

        html_string += f"""<p>"""

        if w.eg1 != "":

            html_string += f"""{w.eg1}<p class="sutta_dps">{w.source1} {w.sutta1}</p>"""

        if w.eg2 != "":

            html_string += f"""<p>{w.eg2}<p class="sutta_dps">{w.source2} {w.sutta2}</p>"""

        if w.eg3 != "" and w.chapter3 != "SBS":

            html_string += f"""<p> {w.eg3}<p class="sutta_dps"> {w.source3} {w.sutta3}</p>"""

        html_string += f"""<p>Пожалуйста, подскажите более подходящий <a class="link" href="https://docs.google.com/forms/d/1iMD9sCSWFfJAFCFYuG9HRIyrr9KFRy0nAOVApM998wM/viewform?usp=pp_url&entry.438735500={w.pali}&entry.326955045=Пример2&entry.1433863141=GoldenDict {today}" target="_blank">пример.</a></p>"""
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

                html_string += f"""<div id="declension_dps_{w.pali_}" class="content_dps hidden">"""

            if w.pos in conjugations:

                html_string += f"""<div id="conjugation_dps_{w.pali_}" class="content_dps hidden">"""

            html_string += f"""{table_data_read}"""

            if w.pos != "sandhi" and w.pos != "idiom":

                if w.pos in declensions:

                    html_string += f"""<p>У вас есть предложение?"""
                    html_string += f"""<a class="link" href="https://docs.google.com/forms/d/1iMD9sCSWFfJAFCFYuG9HRIyrr9KFRy0nAOVApM998wM/viewform?usp=pp_url&entry.438735500={w.pali}&entry.1433863141=GoldenDict {today}" target="_blank">Пожалуйста, сообщите об ошибке.</a></p>"""

                if w.pos in conjugations:

                    html_string += f"""<p>У вас есть предложение?"""
                    html_string += f"""<a class="link" href="https://docs.google.com/forms/d/1iMD9sCSWFfJAFCFYuG9HRIyrr9KFRy0nAOVApM998wM/viewform?usp=pp_url&entry.438735500={w.pali}&entry.1433863141=GoldenDict {today}" target="_blank">Пожалуйста, сообщите об ошибке.</a></p>"""
            html_string += f"""</div>"""

        html_string += render_feedback_tmpl(w)

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

    p = rsc['output_share_dir'].joinpath("dps_full.txt")
    with open(p, "w", encoding ="utf-8") as f:
        f.write(text_data_full)

    p = rsc['output_share_dir'].joinpath("dps_concise.txt")
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

    today = date.today()

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

        html_string += f"""<div class="help"><p>abbreviation. <b>{abbrev}</b>. {meaning}. """

        if pali_meaning != "":
            html_string += f"""{pali_meaning}. """

        if ru_meaning != "":
            html_string += f"""{ru_meaning}. """

        if examp != "":
            html_string += f"""<br>e.g. {examp}. """

        if expl != "":
            html_string += f"""<br>{expl}."""

        html_string += f"""</p></div>"""

        html_string += f"""<p><a class="link" href="https://docs.google.com/forms/d/1iMD9sCSWFfJAFCFYuG9HRIyrr9KFRy0nAOVApM998wM/viewform?usp=pp_url&entry.438735500={abbrev}&entry.1433863141=GoldenDict {today}" target="_blank">Сообщить об ошибке.</a></p>"""

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

        html_string += f"""<div class="help"><p>помощь. <b>{help_title}</b>. {meaning}</p></div>"""

        p = rsc['output_help_html_dir'].joinpath(f"{help_title}.html")

        with open(p, 'w') as f:
            f.write(html_string)

        # compile root data into list
        synonyms = [help_title]
        help_data_list += [[f"{help_title}", f"""{html_string}""", "", synonyms]]


        # generate rpd html

    print(f"{timeis()} {green}generating rpd html")

    df = data['words_df']
    df_length = data['words_df'].shape[0]
    pos_exclude_list = ["abbrev", "cs", "letter","root", "suffix", "ve"]

    rpd = {}

    for row in range(df_length): #df_length
        w = DpsWord(df, row)
        meanings_list = []
        w.russian = re.sub("\?\?", "", w.russian)

        if row % 10000 == 0:
            print(f"{timeis()} {row}/{df_length}\t{w.pali}")

        if w.russian != "" and \
        w.pos not in pos_exclude_list:

            meanings_clean = re.sub(fr" \(.+?\)", "", w.russian)                    # remove all space brackets
            meanings_clean = re.sub(fr"\(.+?\) ", "", meanings_clean)           # remove all brackets space
            meanings_clean = re.sub(fr"(^ | $)", "", meanings_clean)            # remove space at start and fin
            meanings_clean = re.sub(fr"  ", " ", meanings_clean)                    # remove double spaces
            meanings_clean = re.sub(fr" ;|; ", ";", meanings_clean)                 # remove space around ;
            meanings_clean = re.sub(fr"\(комм\).+$", "", meanings_clean)   # remove commentary meanings
            meanings_clean = re.sub(fr"досл.+$", "", meanings_clean)         # remove lit meanings
            meanings_list = meanings_clean.split(";")

            for russian in meanings_list:
                if russian in rpd.keys() and w.case =="":
                    rpd[russian] = f"{rpd[russian]}<br><b>{w.pali_clean}</b> {w.pos}. {w.russian}"
                if russian in rpd.keys() and w.case !="":
                    rpd[russian] = f"{rpd[russian]}<br><b>{w.pali_clean}</b> {w.pos}. {w.russian} ({w.case})"
                if russian not in rpd.keys() and w.case =="":
                    rpd.update({russian: f"<b>{w.pali_clean}</b> {w.pos}. {w.russian}"})
                if russian not in rpd.keys() and w.case !="":
                    rpd.update({russian: f"<b>{w.pali_clean}</b> {w.pos}. {w.russian} ({w.case})"})

    with open(rsc['rpd_css_path'], 'r') as f:
        rpd_css = f.read()

    rpd_data_list = []

    for key, value in rpd.items():
        html_string = ""
        html_string = rpd_css
        html_string += f"<body><div class ='rpd'><p>{value}</p></div></body></html>"
        rpd_data_list += [[f"{key}", f"""{html_string}""", "", ""]]

    # roots > dataframe > json

    print(f"{timeis()} {green}generating json")

    abbrev_data_df = pd.DataFrame(abbrev_data_list)
    abbrev_data_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]

    help_data_df = pd.DataFrame(help_data_list)
    help_data_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]

    rpd_data_df = pd.DataFrame(rpd_data_list)
    rpd_data_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]

    pali_data_df = pd.concat([pali_data_df, abbrev_data_df, help_data_df, rpd_data_df])

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
