import pickle
import re
from datetime import date
from datetime import datetime
import stat
import time
import pandas as pd
import os

from helpers import DataFrames, DpdWord, ResourcePaths, get_resource_paths, parse_data_frames, timeis, red, yellow, green
from html_components import render_header_tmpl, render_feedback_tmpl, render_word_meaning


def generate_html_and_json(generate_roots: bool = True):
    rsc = get_resource_paths()

    data = parse_data_frames(rsc)
    today = date.today()

    print(f"{timeis()} {yellow}generate html and json")
    print(f"{timeis()} ----------------------------------------")
    print(f"{timeis()} {green}generating dpd html")

    error_log = open(rsc['error_log_dir'].joinpath("exporter errorlog.txt"), "w")

    html_data_list = []
    text_data_full = ""
    text_data_concise = ""

    compound_family_error_string = ""
    inflection_table_error_string = ""
    subfamily_error_string = ""
    synonyms_error_string = ""
    frequency_error_string = ""

    # setup compound families list to search

    with open(rsc['compound_families_dir'].joinpath("compound_family_list.csv"), "r") as cfl:
        cfl = cfl.read()
        cf_master_list = cfl.split()

    # the big for loop

    df = data['words_df']
    df_length = data['words_df'].shape[0]

    with open(rsc['dpd_words_css_path'], 'r') as f:
        words_css = f.read()

    with open(rsc['buttons_js_path'], 'r') as f:
        buttons_js = f.read()

    for row in range(df_length): #df_length

        w = DpdWord(df, row)

        if row % 5000 == 0 or row % df_length == 0:
            print(f"{timeis()} {row}/{df_length}\t{w.pali}")

        # colour1 #00A4CC #dark blue
        # colour2 #65DBFF #inbetween for rollover
        # colour3 #E2FFFF #light blue

        # root_colour0 #AB3C00
        # root_colour2 #F95700
        # root_colour3 #FFE2D2

        # x_colour0 #AB3C00
        # x_colour2 #F95700
        # x_colour3 #FFE2D2

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

        html_string += f"""<div class="button-box">"""

        if w.meaning != "":
            html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="grammar_{w.pali_}">grammar</a>"""

        if w.meaning != "" and w.eg1 != "" and w.eg2 == "":
            html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="example_{w.pali_}">example</a>"""

        if w.meaning != "" and w.eg1 != "" and w.eg2 != "":
            html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="example_{w.pali_}">examples</a>"""

        if w.pos in conjugations:
            html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="conjugation_{w.pali_}">conjugation</a>"""

        if w.pos in declensions:
            html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="declension_{w.pali_}">declension</a>"""

        if w.family != "" and w.metadata == "":
            html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="root_family_{w.pali_}">root family</a>"""

        if (w.family2 != "" and w.meaning != "" and w.metadata == "") or (w.pali_clean in cf_master_list and w.meaning != "" and w.metadata == ""):
            html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="compound_family_{w.pali_}">compound family</a>"""

        if w.pos != "idiom":
            html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="frequency_{w.pali_}">frequency</a>"""

        html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="feedback_{w.pali_}">feedback</a>"""
        html_string += f"""</div>"""

        # grammar

        html_string += f"""<div id="grammar_{w.pali_}" class="content hidden"><a class="button close" href="javascript:void(0);" onclick="button_click(this)" data-target="grammar_{w.pali_}">close</a>"""

        html_string += f"""<table class = "table1"><tr><th>Pāḷi</th><td>{w.pali2}</td></tr>"""
        html_string += f"""<tr><th>Grammar</th><td>{w.grammar}"""
        text_full += f"{w.pali}. {w.grammar}"

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

        if w.lit != "":
            html_string += f"""; lit. {w.lit}"""
            text_full += f"""; lit. {w.lit}"""
        html_string += f"""</td></tr>"""

        if w.root != "":
            html_string += f"""<tr valign="top"><th>Root</th><td>{w.root}<sup>{w.root_verb}</sup>{w.root_grp} {w.root_sign} ({w.root_meaning})</td></tr>"""
            text_full += f""". root: {w.root} {w.root_grp} {w.root_sign} ({w.root_meaning})"""

        if w.root_in_comps != "" and w.root_in_comps != "0":
            html_string += f"""<tr valign="top"><th>√ in comps</th><td>{w.root_in_comps}</td></tr>"""
            text_full += f""", {w.root_in_comps} in comps"""

        if w.base != "":
            html_string += f"""<tr valign="top"><th>Base</th><td>{w.base}</td></tr>"""
            text_full += f""". base: {w.base}"""

        if w.construction != "":
            html_string += f"""<tr valign="top"><th>Construction</th><td>{w.construction}</td></tr>"""
            construction_text = re.sub("<br/>", ", ", w.construction)
            text_full += f""". constr: {construction_text}"""

        if w.derivative != "":
            html_string += f"""<tr valign="top"><th>Derivative</th><td>{w.derivative} ({w.suffix})</td></tr>"""
            text_full += f""". derivative: {w.derivative} ({w.suffix})"""

        if w.pc != "":
            html_string += f"""<tr valign="top"><th>Phonetic</th><td>{w.pc}</td></tr>"""
            pc_text = re.sub("<br/>", ", ", w.pc)
            text_full += f""". phonetic: {pc_text}"""

        if w.comp != "" and re.findall(r"\d", w.comp) == []:
            html_string += f"""<tr valign="top"><th>Compound</th><td>{w.comp} ({w.comp_constr})</td></tr>"""
            text_full += f""". compound: {w.comp} ({w.comp_constr})"""

        if w.ant != "":
            html_string += f"""<tr valign="top"><th>Antonym</th><td>{w.ant}</td></tr>"""
            text_full += f""". antonym: {w.ant}"""

        if w.syn != "":
            html_string += f"""<tr valign="top"><th>Synonym</th><td>{w.syn}</td></tr>"""
            text_full += f""". synonym: {w.syn}"""

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

        if w.cognate != "":
            html_string += f"""<tr valign="top"><th>Cognate</th><td>{w.cognate}</td></tr>"""
            text_full += f""". eng cognate: {w.cognate}"""

        if w.link != "":
            html_string += f"""<tr valign="top"><th>Link</th><td><a href="{w.link}">{w.link}</a></td></tr>"""
            text_full += f""". link: {w.link}"""

        if w.non_ia != "":
            html_string += f"""<tr valign="top"><th>Non IA</th><td>{w.non_ia}</td></tr>"""
            text_full += f""". non IA: {w.non_ia}"""

        if w.sk != "":
            html_string += f"""<tr valign="top"><th>Sanskrit</th><td><i>{w.sk}</i></td></tr>"""
            text_full += f""". sanskrit: {w.sk}"""

        sk_root_mn = re.sub("'", "", w.sk_root_mn)
        if w.sk_root != "":
            html_string += f"""<tr valign="top"><th>Sanskrit Root</th><td><i>{w.sk_root} {w.sk_root_cl} ({sk_root_mn})</i></td></tr>"""
            text_full += f""". sk root: {w.sk_root} {w.sk_root_cl} ({sk_root_mn})"""

        html_string += f"""</table>"""
        html_string += f"""<p>Did you spot a mistake? <a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.1433863141=GoldenDict {today}" target="_blank">Correct it here.</a></p>"""
        html_string += f"""</div>"""

        # examples

        if w.meaning != "" and w.eg1 != "" and w.eg2 != "":

            html_string += f"""<div id="example_{w.pali_}" class="content hidden"><a class="button close" href="javascript:void(0);" onclick="button_click(this)" data-target="example_{w.pali_}">close</a>"""

            html_string += f"""<p>{w.eg1}<p class="sutta">{w.source1} {w.sutta1}</p>"""
            html_string += f"""<p>{w.eg2}<p class="sutta">{w.source2} {w.sutta2}</p>"""
            html_string += f"""<p>Can you think of a better example? <a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.326955045=Example1&entry.1433863141=GoldenDict {today}" target="_blank">Add it here.</a></p>"""
            html_string += f"""</div>"""

        elif w.meaning != "" and w.eg1 != "" and w.eg2 == "":

            html_string += f"""<div id="example_{w.pali_}" class="content hidden"><a class="button close" href="javascript:void(0);" onclick="button_click(this)" data-target="example_{w.pali_}">close</a>"""

            html_string += f"""<p>{w.eg1}<p class="sutta">{w.source1} {w.sutta1}</p>"""
            html_string += f"""<p>Can you think of a better example? <a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.326955045=Example1&entry.1433863141=GoldenDict {today}" target="_blank">Add it here.</a></p>"""
            html_string += f"""</div>"""

        # inflection table

        if w.pos not in indeclinables and w.metadata == "":
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

                html_string += f"""<div id="declension_{w.pali_}" class="content hidden"><a class="button close" href="javascript:void(0);" onclick="button_click(this)" data-target="declension_{w.pali_}">close</a>"""

            if w.pos in conjugations:

                html_string += f"""<div id="conjugation_{w.pali_}" class="content hidden"><a class="button close" href="javascript:void(0);" onclick="button_click(this)" data-target="conjugation_{w.pali_}">close</a>"""

            html_string += f"""{table_data_read}"""

            if w.pos != "sandhi" and w.pos != "idiom":

                if w.pos in declensions:

                    html_string += f"""<p>Spot a mistake in the declension table? Something missing? """
                    html_string += f"""<a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSdAL2PzavyrtXgGmtNrZAMyh3hV6g3fU0chxhWFxunQEZtH0g/viewform?usp=pp_url&entry.1932605469={w.pali}&entry.1433863141=GoldenDict+{today}" target="_blank">Report it here.</a>"""

                if w.pos in conjugations:

                    html_string += f"""<p>Spot a mistake in the conjugation table? Something missing? """
                    html_string += f"""<a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSdAL2PzavyrtXgGmtNrZAMyh3hV6g3fU0chxhWFxunQEZtH0g/viewform?usp=pp_url&entry.1932605469={w.pali}&entry.1433863141=GoldenDict+{today}" target="_blank">Report it here.</a>"""
            html_string += f"""</div>"""

        # root family

        subfamily_path = rsc['root_families_dir'] \
            .joinpath("output/subfamily html/") \
            .joinpath(f"{w.root} {w.root_grp} {w.root_meaning} {w.family}.html")

        if subfamily_path.exists():
            with open(subfamily_path) as f:
                table_data_read = f.read()

        elif w.root != "" and w.metadata == "":
            subfamily_error_string += w.pali +", "
            error_log.write(f"""error reading subfamily - {w.pali} - {w.root} {w.root_grp} {w.root_meaning} {w.family}\n""")

        if w.family != "" and w.metadata == "":

            html_string += f"""<div id="root_family_{w.pali_}" class="content hidden"><a class="button close" href="javascript:void(0);" onclick="button_click(this)" data-target="root_family_{w.pali_}">close</a>"""

            html_string += f"""<p class ="heading"><b>{w.pali_clean}</b> belongs to the root family <b>{w.family}</b> ({w.root_meaning})</p>"""
            html_string += f"""<table class = "table1">{table_data_read}</table>"""
            html_string += f"""<p>Something out of place? <a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.326955045=Root+Family&entry.1433863141=GoldenDict {today}" target="_blank">Report it here</a>.</p>"""
            html_string += f"""</div>"""

        # compound families

        if w.family2 != "" and w.meaning != "" and w.metadata == "":

            html_string += f"""<div id="compound_family_{w.pali_}" class="content hidden"><a class="button close" href="javascript:void(0);" onclick="button_click(this)" data-target="compound_family_{w.pali_}">close</a>"""

            compound_family_list = []
            compound_family_list = list(w.family2.split())

            for cf in compound_family_list:
                cf_path = rsc['compound_families_dir'] \
                    .joinpath("output/") \
                    .joinpath(f"{cf}.html")

                if cf_path.exists():
                    with open(cf_path, "r") as f:
                        data_read = f.read()
                        html_string += f"""<p class="heading">compounds which contain <b>{cf}</b></p>"""
                        html_string += f"""<table class = "table1">{data_read}</table>"""

                elif w.family2 != "":
                    compound_family_error_string += w.pali +", "
                    error_log.write(f"""error reading compound family - {w.pali} - {cf}\n""")

            html_string += f"""<p>Some word out of place? <a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.326955045=Compound+Family&entry.1433863141=GoldenDict {today}" target="_blank">Report it here</a>.</p>"""
            html_string += f"""</div>"""

        if w.family2 == "" and w.meaning != "" and w.pali_clean in cf_master_list:

            html_string += f"""<div id="compound_family_{w.pali_}" class="content hidden"><a class="button close" href="javascript:void(0);" onclick="button_click(this)" data-target="compound_family_{w.pali_}">close</a>"""

            cf_path = rsc['compound_families_dir'] \
                .joinpath("output/") \
                .joinpath(f"{w.pali_clean}.html")

            if cf_path.exists():
                with open(cf_path, "r") as f:
                    data_read = f.read()
                    html_string += f"""<p class="heading">compounds which contain <b>{w.pali_clean}</b></p>"""
                    html_string += f"""<table class = "table1">{data_read}</table>"""

            elif w.family2 != "":
                compound_family_error_string += w.pali +", "
                error_log.write(f"""error reading compound family - {w.pali} - {w.family2}\n""")

            html_string += f"""<p>Did you spot a mistake? Something missing? <a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.326955045=Compound+Family&entry.1433863141=GoldenDict {today}" target="_blank">Correct it here.</a></p>"""
            html_string += f"""</div>"""

        # frequency

        if w.pos != "idiom":

            html_string += f"""<div id="frequency_{w.pali_}" class="content hidden"><a class="button close" href="javascript:void(0);" onclick="button_click(this)" data-target="frequency_{w.pali_}">close</a>"""

            if w.pos in indeclinables or re.match(r"^!", w.stem):
                
                html_string += f"""<p class="heading">exact matches of the word <b>{w.pali_clean}</b> in the Chaṭṭha Saṅgāyana corpus.</b></p>"""

            elif w.pos in conjugations:

                html_string += f"""<p class="heading">exact matches of <b>{w.pali_clean} and its conjugations</b> in the Chaṭṭha Saṅgāyana corpus.</b></p>"""

            elif w.pos in declensions:

                html_string += f"""<p class="heading">exact matches of <b>{w.pali_clean} and its declensions</b> in the Chaṭṭha Saṅgāyana corpus.</b></p>"""

            elif w.metadata == "":
                print(f"{timeis()} {red}problem in frequency heading: {w.pali}")

            frequency_path = rsc['frequency_dir'] \
                .joinpath("output/html") \
                .joinpath(f"{w.pali}.html")

            if frequency_path.exists():
                with open(frequency_path, "r") as f:
                    data_read = f.read()

                    # remove unused classes and ids
                    
                    data_read = re.sub(r"-1", "", data_read)
                    data_read = re.sub(r"\b0\b", "-", data_read)
                    data_read = re.sub(r"</style>", "td { text-align: center; }</style>", data_read)
                    data_read = re.sub(r'.+\n.+#f7fbff;\n.+\n.+', "", data_read)
                    data_read = re.sub(r'th class.\[^>\]+', "th", data_read)
                    data_read = re.sub(r'th id.\[^>\]+', "th", data_read)
                    data_read = re.sub(r'(td id.+) class.\[^>\]+', r"\\1", data_read)
                    
                    html_string += f"""{data_read}"""
                    html_string += f"""<p>For a detailed explanation of how this word frequency chart is calculated, it's accuracies and inaccuracies, refer to """
                    html_string += f"""<a class="link" href="https://digitalpalidictionary.github.io/frequency.html">this webpage</a>. Something look out of place? <a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.326955045=Frequency&entry.1433863141=GoldenDict {today}" target="_blank">Log it here.</a></p>"""
                    
            else:
                frequency_error_string += w.pali +", "
                error_log.write(f"""error reading frequency for {w.pali}\n""")
        
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

    if compound_family_error_string != "":
        print(f"{timeis()} {red}compound family errors: {compound_family_error_string}")
    if inflection_table_error_string != "":
        print(f"{timeis()} {red}inflection table errors: {inflection_table_error_string}")
    if subfamily_error_string != "":
        print(f"{timeis()} {red}root subfamily errors: {subfamily_error_string}")
    if synonyms_error_string != "":
       print(f"{timeis()} {red}synonym errors: {synonyms_error_string}")

    # convert ṃ to ṁ

    text_data_full = re.sub("ṃ", "ṁ", text_data_full)
    text_data_concise = re.sub("ṃ", "ṁ", text_data_concise)


    # write text versions

    p = rsc['output_share_dir'].joinpath("dpd_full.txt")
    with open(p, "w", encoding ="utf-8") as f:
        f.write(text_data_full)

    p = rsc['output_share_dir'].joinpath("dpd_concise.txt")
    with open(p, "w", encoding ="utf-8") as f:
        f.write(text_data_concise)

    if generate_roots:
        generate_roots_html_and_json(data, rsc, html_data_list)
        # delete_unused_html_files()

def generate_roots_html_and_json(data: DataFrames, rsc: ResourcePaths, html_data_list):

    print(f"{timeis()} {green}generating roots html")
    today = date.today()

    # html list > dataframe

    pali_data_df = pd.DataFrame(html_data_list)
    pali_data_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]

    root_data_list = []
    root_html_error_string = ""

    with open(rsc['dpd_words_css_path'], 'r') as f:
        words_css = f.read()

    with open(rsc['dpd_roots_css_path'], 'r') as f:
        roots_css = f.read()

    with open(rsc['buttons_js_path'], 'r') as f:
        buttons_js = f.read()

    roots_df = data['roots_df']
    roots_df_length = len(roots_df)

    for row in range(roots_df_length):

        html_string = ""

        root_count = roots_df.iloc[row,1]
        root = roots_df.iloc[row, 2]
        root_ = "_" + re.sub(" ", "_", root)
        root_ = re.sub("√", "", root_)
        root_in_comps = roots_df.iloc[row, 3]
        root_has_verb = roots_df.iloc[row, 4]
        root_group = roots_df.iloc[row, 5]
        root_sign = roots_df.iloc[row, 6]
        root_meaning = roots_df.iloc[row, 8]
        root_meaning_ = re.sub(",", "", root_meaning)
        root_meaning_ = re.sub(" ", "_", root_meaning_)
        root_id = root_group + "_" + root_meaning_

        if root_count != "0":

            if row % 100 == 0 or row % roots_df_length == 0:
                print(f"{timeis()} {row}/{roots_df_length}\t{root} {root_group} {root_meaning}")

            css = f"{words_css}\n\n{roots_css}"
            html_string += render_header_tmpl(css=css, js=buttons_js)

            html_string += "<body>"

            # summary

            html_string += f"""<div class="root_content"><p>root. <b>{root}</b><sup>{root_has_verb}</sup>{root_group} {root_sign} ({root_meaning})</p></div>"""

            # buttons

            html_string += f"""<div class="root-button-box">"""

            html_string += f"""<a class="button root" href="javascript:void(0);" onclick="button_click(this)" data-target="root_info_{root_}_{root_id}">root info</a>"""

            p = rsc['root_families_dir'] \
                .joinpath("output/families/") \
                .joinpath(f"{root} {root_group} {root_meaning}.csv")

            if p.exists():
                root_families_df = pd.read_csv(p, sep="\t", header=None)
                root_families_length = root_families_df.shape[0]
            else:
                root_families_df = None

            if root_families_df is not None:
                for line in range(root_families_length):
                    subfamily_button = root_families_df.iloc[line, 0]
                    subfamily_button_ = "_" + re.sub(" ", "_", subfamily_button)
                    subfamily_button_ = re.sub("√", "", subfamily_button_)

                    html_string += f"""<a class="button root" href="javascript:void(0);" onclick="button_click(this)" data-target="root_family_{subfamily_button_}_{root_id}">{subfamily_button}</a>"""

            html_string += f"""</div>"""

            # root info

            html_string += f"""<div id="root_info_{root_}_{root_id}" class="root_content hidden"><a class="button root close" href="javascript:void(0);" onclick="button_click(this)" data-target="root_info_{root_}_{root_id}">close</a>"""

            p = rsc['root_families_dir'] \
                .joinpath("output/root info/") \
                .joinpath(f"{root} {root_group} {root_meaning}.html")

            if p.exists():
                with open(p, 'r') as f:
                    root_info_read = f.read()

                    html_string += f"""<table class="root_table">{root_info_read}</table>"""
                    html_string += f"""<p>Did you spot a mistake? <a class="rootlink" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={root} {root_group} {root_meaning}&entry.326955045=Root+Info&entry.1433863141=GoldenDict {today}" target="_blank">Correct it here.</a></p>"""
                    html_string += """</div>"""

            # root families

            if root_families_df is not None:
                for line in range(root_families_length):
                    subfamily = root_families_df.iloc[line, 0]
                    subfamily_ = "_" + re.sub(" ", "_", subfamily)
                    subfamily_ = re.sub("√", "", subfamily_)

                    html_string += f"""
                    <div id="root_family_{subfamily_}_{root_id}" class="root_content hidden"><a class="button root close" href="javascript:void(0);" onclick="button_click(this)" data-target="root_family_{subfamily_}_{root_id}">close</a>"""

                    html_string += f"""<p class= "root_heading">all words which belong to the root family <b>{subfamily}</b> ({root_meaning})</p>"""

                    p = rsc['root_families_dir'] \
                        .joinpath("output/subfamily html/") \
                        .joinpath(f"{root} {root_group} {root_meaning} {subfamily}.html")

                    if p.exists():
                        with open(p, 'r') as f:
                            subfamily_html_read = f.read()
                            html_string += f"""<table class="root_table">{subfamily_html_read}</table>"""
                    else:
                        # FIXME pali is undefined
                        # root_html_error_string += pali +", "
                        root_html_error_string += "unknown" +", "
                        print(f"{timeis()} {red}error\t{root} {root_group} {root_meaning} {subfamily}.html")

                    html_string += f"""<p>Does something look wrong? <a class="rootlink" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={subfamily} {root_group} {root_meaning}&entry.326955045=Root+Family&entry.1433863141=GoldenDict {today}" target="_blank">Report it here</a>.</p>"""
                    html_string += "</div>"

            html_string += f"""</body></html>"""

            # writing html and compiling

            p = rsc['output_root_html_dir'].joinpath(f"{root} {root_group} {root_meaning} (sample).html")
            with open(p, 'w') as f:
                f.write(html_string)

            root_clean = re.sub("√", "", root)
            synonyms = [root,root_clean]

            # compile root data into list
            root_data_list += [[f"{root}", f"""{html_string}""", "", synonyms]]

    if root_html_error_string != "":
        print(f"{timeis()} {red}root html errors: {root_html_error_string}")

# generate abbreviations html

    print(f"{timeis()} {green}generating abbreviations html")

    abbrev_data_list = []

    with open(rsc['dpd_help_css_path'], 'r') as f:
        abbrev_css = f.read()

    abbrev_df = data['abbrev_df']
    abbrev_df_length = len(abbrev_df)

    for row in range(abbrev_df_length):
        
        html_string = ""

        abbrev = abbrev_df.iloc[row,0]
        meaning = abbrev_df.iloc[row,1]
        
        css = f"{abbrev_css}"
        html_string += render_header_tmpl(css=css, js="")

        html_string += "<body>"

        # summary

        # html_string += f"""<div class="help"><p>Abbreviation. <b>{abbrev}</b>. {meaning}</p></div>"""
        html_string += f"""<div class="help"><p>Abbreviation: {meaning}</p></div>"""
        
        p = rsc['output_help_html_dir'].joinpath(f"{abbrev}.html")

        with open(p, 'w') as f:
            f.write(html_string)
        
        # compile root data into list
        synonyms = [abbrev,meaning]
        abbrev_data_list += [[f"{abbrev}", f"""{html_string}""", "", synonyms]]

# generate help html

    print(f"{timeis()} {green}generating help html")

    help_data_list = []

    with open(rsc['dpd_help_css_path'], 'r') as f:
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

        # html_string += f"""<div class="help"><p>Help. <b>{help_title}</b>. {meaning}</p></div>"""
        html_string += f"""<div class="help"><p>{meaning}</p></div>"""
        
        p = rsc['output_help_html_dir'].joinpath(f"{help_title}.html")

        with open(p, 'w') as f:
            f.write(html_string)
        
        # compile root data into list
        synonyms = [help_title]
        help_data_list += [[f"{help_title}", f"""{html_string}""", "", synonyms]]

    # roots > dataframe > json
    print(f"{timeis()} {green}saving html to json")

    root_data_df = pd.DataFrame(root_data_list)
    root_data_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]

    abbrev_data_df = pd.DataFrame(abbrev_data_list)
    abbrev_data_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]

    help_data_df = pd.DataFrame(help_data_list)
    help_data_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]

    pali_data_df = pd.concat([pali_data_df, root_data_df, abbrev_data_df, help_data_df])
    pali_data_df.to_json(rsc['gd_json_path'], force_ascii=False, orient="records", indent=6)

    print(f"{timeis()} ----------------------------------------")


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