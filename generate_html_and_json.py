import pickle
import re
from datetime import date
import pandas as pd
import minify_html
import markdown
import shutil

from timeis import timeis, white, yellow, green, red, line, tic, toc
from helpers import DataFrames, DpdWord, ResourcePaths, get_resource_paths, parse_data_frames
from html_components import render_header_tmpl, render_feedback_tmpl, render_word_meaning
from superscripter import superscripter

def generate_html_and_json(generate_roots: bool = True):
    tic()
    rsc = get_resource_paths()

    data = parse_data_frames(rsc)
    today = date.today()

    print(f"{timeis()} {yellow}generate html and json")
    print(f"{timeis()} {line}")
    print(f"{timeis()} {green}generating dpd html")

    error_log = open(rsc['error_log_dir'].joinpath("exporter errorlog.txt"), "w")

    html_data_list = []
    html_light_data_list = []
    text_data_full = ""
    text_data_concise = ""

    compound_family_error_string = ""
    inflection_table_error_string = ""
    subfamily_error_string = ""
    wordfamily_error_string = ""
    synonyms_error_string = ""
    frequency_error_string = ""

    with open(rsc['all_inflections_dict_path'], "rb") as f:
        all_inflections_dict = pickle.load(f)

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

    indeclinables = ["abbrev", "abs", "ger", "ind", "inf", "prefix", "sandhi", "suffix", "idiom", "var"]
    conjugations = ["aor", "cond", "fut", "imp", "imperf", "opt", "perf", "pr"]
    declensions = ["adj", "card", "cs", "fem", "letter", "masc", "nt", "ordin", "pp", "pron", "prp", "ptp", "root", "ve"]

    # colour1 #00A4CC #dark blue
    # colour2 #65DBFF #inbetween for rollover
    # colour3 #E2FFFF #light blue

    # root_colour0 #AB3C00
    # root_colour2 #F95700
    # root_colour3 #FFE2D2

    # x_colour0 #AB3C00
    # x_colour2 #F95700
    # x_colour3 #FFE2D2

    # ✓∼✗

    for row in range(df_length):  # df_length

        w = DpdWord(df, row)

        if row % 5000 == 0 or row % df_length == 0:
            print(f"{timeis()} {row}/{df_length}\t{w.pali}")

        html_string = ""
        html_light = ""
        text_full = ""
        text_concise = ""

        # all headwords list
        global all_headwords_clean
        all_headwords_clean = []
        all_headwords_clean.append(w.pali_clean)

        # html head & style

        html_string += render_header_tmpl(css=words_css, js=buttons_js)
        html_string += "<body>"

        html_light += render_header_tmpl(css=words_css, js=buttons_js)
        html_light += "<body>"

        # summary

        r = render_word_meaning(w)
        html_string += r['html']
        html_light += r['html']
        text_full += r['full']
        text_concise += r['concise']

        # buttons

        html_string += f"""<div class="button-box">"""
        html_light += f"""<div class="button-box">"""

        if w.meaning != "":
            html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="grammar_{w.pali_}">grammar</a>"""
            html_light += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="grammar_{w.pali_}">grammar</a>"""

        if w.meaning != "" and w.eg1 != "" and w.eg2 == "":
            html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="example_{w.pali_}">example</a>"""
            html_light += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="example_{w.pali_}">example</a>"""

        if w.meaning != "" and w.eg1 != "" and w.eg2 != "":
            html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="example_{w.pali_}">examples</a>"""
            html_light += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="example_{w.pali_}">examples</a>"""

        if w.pos in conjugations:
            html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="conjugation_{w.pali_}">conjugation</a>"""

        if w.pos in declensions:
            html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="declension_{w.pali_}">declension</a>"""

        if w.family != "":
            html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="root_family_{w.pali_}">root family</a>"""

        if w.word_family != "":
            if " " in w.word_family:
                html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="word_family_{w.pali_}">word families</a>"""
            else:
                html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="word_family_{w.pali_}">word family</a>"""

        exclude_from_cf = ["abbrev", "cs", "letter", "prefix", "suffix", "ve"]

        if (w.family2 != "" and w.meaning != "") or (w.pali_clean in cf_master_list and w.meaning != ""):
            if w.pos not in exclude_from_cf:
                if " " in w.family2:
                    html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="compound_family_{w.pali_}">compound families</a>"""
                else:
                    html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="compound_family_{w.pali_}">compound family</a>"""
            
        exclude_from_sets = ["dps", "ncped", "pass1", "sandhi"]

        if w.sets != "" and w.meaning != "" and w.sets not in exclude_from_sets:
            if re.findall(";", w.sets):
                html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="sets_{w.pali_}">sets</a>"""
            else:
                html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="sets_{w.pali_}">set</a>"""

        exclude_from_freq = ["abbrev", "cs", "idiom", "letter", "prefix", "root", "suffix", "ve" ]

        if w.pos not in exclude_from_freq:
            html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="frequency_{w.pali_}">frequency</a>"""

        html_string += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="feedback_{w.pali_}">feedback</a>"""
        html_light += f"""<a class="button" href="javascript:void(0);" onclick="button_click(this)" data-target="feedback_{w.pali_}">feedback</a>"""

        html_string += f"""</div>"""
        html_light += f"""</div>"""

        # grammar

        if w.meaning != "":

            html_string += f"""<div id="grammar_{w.pali_}" class="content hidden">"""
            html_light += f"""<div id="grammar_{w.pali_}" class="content hidden">"""

            html_string += f"""<table class = "table1"><tr><th>Pāḷi</th><td>{w.pali2}</td></tr>"""
            html_light += f"""<table class = "table1"><tr><th>Pāḷi</th><td>{w.pali2}</td></tr>"""

            html_string += f"""<tr><th>Grammar</th><td>{w.grammar}"""
            html_light += f"""<tr><th>Grammar</th><td>{w.grammar}"""
            
            text_full += f"{w.pali}. {w.grammar}"

            if w.neg != "":
                html_string += f""", {w.neg}"""
                html_light += f""", {w.neg}"""
                text_full += f""", {w.neg}"""

            if w.verb != "":
                html_string += f""", {w.verb}"""
                html_light += f""", {w.verb}"""
                text_full += f""", {w.verb}"""

            if w.trans != "":
                html_string += f""", {w.trans}"""
                html_light += f""", {w.trans}"""
                text_full += f""", {w.trans}"""

            if w.case != "":
                html_string += f""" ({w.case})"""
                html_light += f""" ({w.case})"""
                text_full += f""" ({w.case})"""

            html_string += f"""</td></tr>"""
            html_light += f"""</td></tr>"""

            html_string += f"""<tr><th>Meaning</th><td><b>{w.meaning}</b>"""
            html_light += f"""<tr><th>Meaning</th><td><b>{w.meaning}</b>"""
            text_full += f""". {w.meaning}"""

            if w.lit != "":
                html_string += f"""; lit. {w.lit}"""
                html_light += f"""; lit. {w.lit}"""
                text_full += f"""; lit. {w.lit}"""
            html_string += f"""</td></tr>"""
            html_light += f"""</td></tr>"""

            if w.family != "":
                html_string += f"""<tr><th>Root Family</th><td>{w.family}</td></tr>"""
                text_full += f""". root family: {w.family}"""

            if w.root != "":
                html_string += f"""<tr><th>Root</th><td>{w.root_clean}<sup>{w.root_verb}</sup>{w.root_grp} {w.root_sign} ({w.root_meaning})</td></tr>"""
                html_light += f"""<tr><th>Root</th><td>{w.root_clean}<sup>{w.root_verb}</sup>{w.root_grp} {w.root_sign} ({w.root_meaning})</td></tr>"""
                text_full += f""". root: {w.root_clean} {w.root_grp} {w.root_sign} ({w.root_meaning})"""

            if w.root_in_comps != "" and w.root_in_comps != "0":
                html_string += f"""<tr><th>√ in comps</th><td>{w.root_in_comps}</td></tr>"""
                html_light += f"""<tr><th>√ in comps</th><td>{w.root_in_comps}</td></tr>"""
                text_full += f""", {w.root_in_comps} in comps"""

            if w.base != "":
                html_string += f"""<tr><th>Base</th><td>{w.base}</td></tr>"""
                html_light += f"""<tr><th>Base</th><td>{w.base}</td></tr>"""
                text_full += f""". base: {w.base}"""

            if w.construction != "":
                html_string += f"""<tr><th>Construction</th><td>{w.construction}</td></tr>"""
                html_light += f"""<tr><th>Construction</th><td>{w.construction}</td></tr>"""
                construction_text = re.sub("<br/>", ", ", w.construction)
                text_full += f""". constr: {construction_text}"""

            if w.derivative != "":
                html_string += f"""<tr><th>Derivative</th><td>{w.derivative} ({w.suffix})</td></tr>"""
                html_light += f"""<tr><th>Derivative</th><td>{w.derivative} ({w.suffix})</td></tr>"""
                text_full += f""". derivative: {w.derivative} ({w.suffix})"""

            if w.pc != "":
                html_string += f"""<tr><th>Phonetic</th><td>{w.pc}</td></tr>"""
                html_light += f"""<tr><th>Phonetic</th><td>{w.pc}</td></tr>"""
                pc_text = re.sub("<br/>", ", ", w.pc)
                text_full += f""". phonetic: {pc_text}"""

            if w.comp != "" and re.findall(r"\d", w.comp) == []:
                html_string += f"""<tr><th>Compound</th><td>{w.comp} ({w.comp_constr})</td></tr>"""
                html_light += f"""<tr><th>Compound</th><td>{w.comp} ({w.comp_constr})</td></tr>"""
                text_full += f""". compound: {w.comp} ({w.comp_constr})"""

            if w.ant != "":
                html_string += f"""<tr><th>Antonym</th><td>{w.ant}</td></tr>"""
                html_light += f"""<tr><th>Antonym</th><td>{w.ant}</td></tr>"""
                text_full += f""". antonym: {w.ant}"""

            if w.syn != "":
                html_string += f"""<tr><th>Synonym</th><td>{w.syn}</td></tr>"""
                html_light += f"""<tr><th>Synonym</th><td>{w.syn}</td></tr>"""
                text_full += f""". synonym: {w.syn}"""

            if w.var != "":
                html_string += f"""<tr><th>Variant</th><td>{w.var}</td></tr>"""
                html_light += f"""<tr><th>Variant</th><td>{w.var}</td></tr>"""
                text_full += f"""variant: {w.var}"""

            if w.comm != "":
                html_string += f"""<tr><th>Commentary</th><td>{w.comm}</td></tr>"""
                html_light += f"""<tr><th>Commentary</th><td>{w.comm}</td></tr>"""

                comm_text = re.sub("<br/>", " ", w.comm)
                comm_text = re.sub("<b>", "", comm_text)
                comm_text = re.sub("</b>", "", comm_text)
                text_full += f""". commentary: {comm_text}"""

            if w.notes != "":
                html_string += f"""<tr><th>Notes</th><td>{w.notes}</td></tr>"""
                html_light += f"""<tr><th>Notes</th><td>{w.notes}</td></tr>"""
                text_full += f""". notes: {w.notes}"""

            if w.cognate != "":
                html_string += f"""<tr><th>English Cognate</th><td>{w.cognate}</td></tr>"""
                html_light += f"""<tr><th>English Cognate</th><td>{w.cognate}</td></tr>"""
                text_full += f""". eng cognate: {w.cognate}"""

            if w.link != "":
                html_string += f"""<tr><th>Link</th><td><a href="{w.link}">{w.link}</a></td></tr>"""
                html_light += f"""<tr><th>Link</th><td><a href="{w.link}">{w.link}</a></td></tr>"""
                text_full += f""". link: {w.link}"""

            if w.non_ia != "":
                html_string += f"""<tr><th>Non IA</th><td>{w.non_ia}</td></tr>"""
                html_light += f"""<tr><th>Non IA</th><td>{w.non_ia}</td></tr>"""
                text_full += f""". non IA: {w.non_ia}"""

            if w.sk != "":
                html_string += f"""<tr><th>Sanskrit</th><td><i>{w.sk}</i></td></tr>"""
                html_light += f"""<tr><th>Sanskrit</th><td><i>{w.sk}</i></td></tr>"""
                text_full += f""". sanskrit: {w.sk}"""

            sk_root_mn = re.sub("'", "", w.sk_root_mn)
            if w.sk_root != "":
                html_string += f"""<tr><th>Sanskrit Root</th><td><i>{w.sk_root} {w.sk_root_cl} ({sk_root_mn})</i></td></tr>"""
                html_light += f"""<tr><th>Sanskrit Root</th><td><i>{w.sk_root} {w.sk_root_cl} ({sk_root_mn})</i></td></tr>"""
                text_full += f""". sk root: {w.sk_root} {w.sk_root_cl} ({sk_root_mn})"""

            html_string += f"""</table>"""
            html_light += f"""</table>"""

            html_string += f"""<p>Did you spot a mistake? <a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.1433863141=GoldenDict {today}" target="_blank">Correct it here.</a></p>"""
            html_light += f"""<p>Did you spot a mistake? <a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.1433863141=GoldenDict Light {today}" target="_blank">Correct it here.</a></p>"""
            
            html_string += f"""</div>"""
            html_light += f"""</div>"""

        # examples

        if w.meaning != "" and w.eg1 != "" and w.eg2 != "":

            html_string += f"""<div id="example_{w.pali_}" class="content hidden">"""
            html_string += f"""<p>{w.eg1}<p class="sutta">{w.source1} {w.sutta1}</p>"""
            html_string += f"""<p>{w.eg2}<p class="sutta">{w.source2} {w.sutta2}</p>"""
            html_string += f"""<p>Can you think of a better example? <a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.326955045=Example1&entry.1433863141=GoldenDict {today}" target="_blank">Add it here.</a></p>"""
            html_string += f"""</div>"""

            html_light += f"""<div id="example_{w.pali_}" class="content hidden">"""
            html_light += f"""<p>{w.eg1}<p class="sutta">{w.source1} {w.sutta1}</p>"""
            html_light += f"""<p>{w.eg2}<p class="sutta">{w.source2} {w.sutta2}</p>"""
            html_light += f"""<p>Can you think of a better example? <a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.326955045=Example1&entry.1433863141=GoldenDict Light {today}" target="_blank">Add it here.</a></p>"""
            html_light += f"""</div>"""

        elif w.meaning != "" and w.eg1 != "" and w.eg2 == "":

            html_string += f"""<div id="example_{w.pali_}" class="content hidden">"""
            html_string += f"""<p>{w.eg1}<p class="sutta">{w.source1} {w.sutta1}</p>"""
            html_string += f"""<p>Can you think of a better example? <a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.326955045=Example1&entry.1433863141=GoldenDict {today}" target="_blank">Add it here.</a></p>"""
            html_string += f"""</div>"""

            html_light += f"""<div id="example_{w.pali_}" class="content hidden">"""
            html_light += f"""<p>{w.eg1}<p class="sutta">{w.source1} {w.sutta1}</p>"""
            html_light += f"""<p>Can you think of a better example? <a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.326955045=Example1&entry.1433863141=GoldenDict Light {today}" target="_blank">Add it here.</a></p>"""
            html_light += f"""</div>"""

        # inflection table

        if w.pos not in indeclinables:
            table_path = rsc['inflections_dir'] \
                .joinpath("output/html tables/") \
                .joinpath(w.pali + ".html")

            if table_path.exists():
                with open(table_path) as f:
                    table_data_read = f.read()
                    table_data_read = re.sub('border="1"', '', table_data_read)

                if w.pos in declensions:

                    html_string += f"""<div id="declension_{w.pali_}" class="content hidden">"""

                if w.pos in conjugations:

                    html_string += f"""<div id="conjugation_{w.pali_}" class="content hidden">"""

                html_string += f"""{table_data_read}"""

                if w.pos != "sandhi" and w.pos != "idiom":
                    if re.findall("gray", table_data_read):
                        html_string += f"""<p>Inflections not found in the Chaṭṭha Saṅgāyana corpus, or within processed sandhi compounds are <span class='gray'>grayed out</span>. They might still occur elsewhere, within compounds or in other versions of the Pāḷi texts.</p>"""

                    if w.pos in declensions:
                        html_string += f"""<p>Did you spot a mistake in the declension table? Something missing? """
                        html_string += f"""<a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSfKUBx-icfRCWmhHqUwzX60BVQE21s_NERNfU2VvbjEfE371A/viewform?usp=pp_url&entry.1370304754={w.pali}&entry.1433863141=GoldenDict+{today}" target="_blank">Report it here.</a></p>"""

                    if w.pos in conjugations:
                        html_string += f"""<p>Did you spot a mistake in the conjugation table? Something missing? """
                        html_string += f"""<a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSdAL2PzavyrtXgGmtNrZAMyh3hV6g3fU0chxhWFxunQEZtH0g/viewform?usp=pp_url&entry.1932605469={w.pali}&entry.1433863141=GoldenDict+{today}" target="_blank">Report it here.</a></p>"""

                html_string += f"""</div>"""

            else:
                inflection_table_error_string += w.pali + ", "
                error_log.write(f"error reading inflection table: {w.pali}.html\n")
            

        # root family

        subfamily_path = rsc['root_families_dir'] \
            .joinpath("output/subfamily html/") \
            .joinpath(f"{w.root_clean} {w.root_grp} {w.root_meaning} {w.family}.html")

        if subfamily_path.exists():
            with open(subfamily_path) as f:
                table_data_read = f.read()
                subfamily_count = int(re.findall("</table>(\\d*)", table_data_read)[0])
                table_data_read = re.sub("</table>\\d*", "</table>", table_data_read)

            if w.family != "":

                html_string += f"""<div id="root_family_{w.pali_}" class="content hidden">"""
                # html_string += f"""<p class="heading"><b>{w.pali_clean}</b> belongs to the root family <b>{w.family}</b> ({w.root_meaning})</p>"""

                if subfamily_count == 1:
                    html_string += f"""<p class="heading"><b>{subfamily_count}</b> word belongs to the root family <b>{w.family}</b> ({w.root_meaning})</p>"""
                else:
                    html_string += f"""<p class="heading"><b>{subfamily_count}</b> words belongs to the root family <b>{w.family}</b> ({w.root_meaning})</p>"""

                html_string += f"""{table_data_read}"""
                html_string += f"""<p>Something out of place? <a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.326955045=Root+Family&entry.1433863141=GoldenDict {today}" target="_blank">Report it here</a>.</p>"""
                html_string += f"""</div>"""

        elif w.root != "":
            subfamily_error_string += w.pali +", "
            error_log.write(f"""error reading subfamily - {w.pali} - {w.root_clean} {w.root_grp} {w.root_meaning} {w.family}\n""")

       # word family
        
        if w.word_family != "":

            # word family list
            wfl = w.word_family.split()
            
            html_string += f"""<div id="word_family_{w.pali_}" class="content hidden">"""
            
            wf = wfl[-1]
            wf_path = rsc['word_families_dir'] \
                .joinpath("output/html/") \
                .joinpath(f"{wf}.html")

            if wf_path.exists():
                with open(wf_path) as f:
                    table_data_read = f.read()

                html_string += f"""<p class="heading">words which belong to the <b>{wf}</b> family</p>"""
                html_string += f"""{table_data_read}"""
                html_string += f"""<p>Something out of place? <a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.326955045=Word+Family&entry.1433863141=GoldenDict {today}" target="_blank">Report it here</a>.</p>"""
                    
            elif w.word_family != "":
                wordfamily_error_string += w.pali +", "
                error_log.write(f"""error reading word family - {w.pali} - {wf}\n""")
            
            html_string += f"""</div>"""
        
        # compound families

        test1 = w.family2 != ""
        test2 = w.meaning != ""
        test3 = len(w.pali_clean) < 30
        test4 = w.pos not in exclude_from_cf

        if test1 & test2 & test3 & test4:

            html_string += f"""<div id="compound_family_{w.pali_}" class="content hidden">"""

            if " " in w.family2:
                html_string += f"""<p class="heading">compound families: <b>{w.family2}</b></p>"""
            
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
                    html_string += f"""<p class="family">{data_read}</p>"""

                    if cf == compound_family_list[-1]:
                        html_string += f"""<p>Spot a mistake? <a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.326955045=Compound+Family&entry.1433863141=GoldenDict {today}" target="_blank">Fix it here</a>.</p>"""

                elif w.family2 != "":
                    compound_family_error_string += w.pali +", "
                    error_log.write(f"""error reading compound family - {w.pali} - {cf}\n""")
                
            html_string += f"""</div>"""

        elif (w.family2 == "" and
        w.meaning != "" and
        w.pali_clean in cf_master_list and
        len(w.pali_clean) < 30):

            html_string += f"""<div id="compound_family_{w.pali_}" class="content hidden">"""

            cf_path = rsc['compound_families_dir'] \
                .joinpath("output/") \
                .joinpath(f"{w.pali_clean}.html")

            if cf_path.exists():
                with open(cf_path, "r") as f:
                    data_read = f.read()

                html_string += f"""<p class="heading">compounds which contain <b>{w.pali_clean}</b></p>"""
                html_string += f"""<p class="family">{data_read}</p>"""
                html_string += f"""<p>Did you spot a mistake? Something missing? <a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.326955045=Compound+Family&entry.1433863141=GoldenDict {today}" target="_blank">Correct it here.</a></p>"""
                
            elif w.family2 != "":
                compound_family_error_string += w.pali +", "
                error_log.write(f"""error reading compound family - {w.pali} - {w.family2}\n""")

            html_string += f"""</div>"""

        # sets

        if w.sets != "" and w.meaning != "":
            
            html_string += f"""<div id="sets_{w.pali_}" class="content hidden">"""
            
            sets_list = []
            sets_list = list(w.sets.split(";"))
            
            for set in sets_list:
                set = re.sub("^ ", "", set)
                set_path = rsc['sets_dir'] \
                .joinpath("output/html/") \
                .joinpath(f"{set}.html")

                if set_path.exists():
                    
                    with open(set_path) as f:
                        set_data_read = f.read()

                    html_string += f"""<p class="heading"><b>{w.pali_clean}</b> belongs to the set of <b>{set}</b></p>"""
                    html_string += f"""{set_data_read}"""

                    if set == sets_list[-1]:
                        html_string += f"""<p>Spot a mistake? Can you think of a set you'd like to see here? <a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.1433863141=GoldenDict {today}" target="_blank">Note it here</a>.</p>"""
                       
                else:
                    if set not in exclude_from_sets:
                        print(f"{timeis()} {red}{row}/{df_length}\t{w.pali} set dir not found for {set}.html")
            
            html_string += f"""</div>"""

        # frequency map
        if w.pos not in exclude_from_freq:
        
            frequency_path = rsc['frequency_dir'] \
                .joinpath("output/html") \
                .joinpath(f"{w.pali}.html")

            if frequency_path.exists():
                with open(frequency_path, "r") as f:
                    data_read = f.read()

                html_string += f"""<div id="frequency_{w.pali_}" class="content hidden">"""

                html_string += f"""{data_read}"""

                html_string += f"""<p>For a detailed explanation of how this word frequency chart is calculated, it's accuracies and inaccuracies, please refer to """
                html_string += f"""<a class="link" href="https://digitalpalidictionary.github.io/frequency.html">this webpage</a>. If something looks out of place, <a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.326955045=Frequency&entry.1433863141=GoldenDict {today}" target="_blank">log it here.</a></p>"""
                
            else:
                frequency_error_string += w.pali +", "
                error_log.write(f"""error reading frequency for {w.pali}\n""")
                print(f"{timeis()} {red}frequency file not found for {w.pali}")

            html_string += f"""</div>"""
            

        # feedback

        html_string += render_feedback_tmpl(w)
        html_string += f"""</body></html>"""

        html_light += render_feedback_tmpl(w)
        html_light += f"""</body></html>"""

        html_string = minify_html.minify(html_string, minify_js=True, remove_processing_instructions=True)

        # synonyms
        # add ṁ
        
        synonyms = list(all_inflections_dict[w.pali]["inflections"])

        for synoym in synonyms:
            if re.findall("ṃ", synoym):
                synoym1 = re.sub("ṃ", "ṁ", synoym)
                synonyms.append(synoym1)
                synoym2 = re.sub("ṃ", "ŋ", synoym)  
                synonyms.append(synoym2)
            
        synonyms += list(all_inflections_dict[w.pali]["sinhala"])
        synonyms += list(all_inflections_dict[w.pali]["devanagari"])
        synonyms += list(all_inflections_dict[w.pali]["thai"])

        # data compiling

        html_data_list += [[f"{w.pali_super}", f"""{html_string}""", "", synonyms]]
        html_light_data_list += [[f"{w.pali_super}", f"""{html_light}""", "", synonyms]]
        text_data_full += f"{text_full}\n"
        text_data_concise += f"{text_concise}\n"

        if row % 100 == 0:
            p = rsc['output_html_dir'].joinpath(f"{w.pali} (sample).html")
            with open(p, "w", encoding="utf-8") as f:
                f.write(html_string)

    error_log.close()

    if wordfamily_error_string != "":
        print(f"{timeis()} {red}word family errors: {wordfamily_error_string}")
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
        generate_roots_html_and_json(
            data, 
            rsc, 
            html_data_list, 
            html_light_data_list,
            all_inflections_dict)

        # delete_unused_html_files()


def generate_roots_html_and_json(data: DataFrames, rsc: ResourcePaths, html_data_list, html_light_data_list, all_inflections_dict):

    print(f"{timeis()} {green}generating roots html")
    today = date.today()

    # html list > dataframe

    pali_data_df = pd.DataFrame(html_data_list)
    pali_data_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]

    pali_light_data_df = pd.DataFrame(html_light_data_list)
    pali_light_data_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]

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
        root_clean = re.sub(" \\d.*$", "", root)
        root_super = superscripter(root)
        root_ = "_" + re.sub(" ", "_", root_clean)
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

            css = f"{words_css}\n\n{roots_css}"
            html_string += render_header_tmpl(css=css, js=buttons_js)
            html_string += "<body>"

            # summary

            html_string += f"""<div class="root_content"><p>root. <b>{root_clean}</b><sup>{root_has_verb}</sup>{root_group} {root_sign} ({root_meaning}) {root_count}</p></div>"""

            # buttons

            html_string += f"""<div class="root-button-box">"""
            html_string += f"""<a class="button root" href="javascript:void(0);" onclick="button_click(this)" data-target="root_info_{root_}_{root_id}">root info</a>"""
            html_string += f"""<a class="button root" href="javascript:void(0);" onclick="button_click(this)" data-target="root_matrix_{root_}_{root_id}">root matrix</a>"""

            p = rsc['root_families_dir'] \
                .joinpath("output/families/") \
                .joinpath(f"{root_clean} {root_group} {root_meaning}.csv")

            if p.exists():
                root_families_df = pd.read_csv(p, sep="\t", header=None)
                root_families_length = root_families_df.shape[0]
            else:
                root_families_df = None

            if root_families_df is not None:
                for line_no in range(root_families_length):
                    subfamily_button = root_families_df.iloc[line_no, 0]
                    subfamily_button_ = "_" + re.sub(" ", "_", subfamily_button)
                    subfamily_button_ = re.sub("√", "", subfamily_button_)

                    html_string += f"""<a class="button root" href="javascript:void(0);" onclick="button_click(this)" data-target="root_family_{subfamily_button_}_{root_id}">{subfamily_button}</a>"""

            html_string += f"""</div>"""

            # root info

            html_string += f"""<div id="root_info_{root_}_{root_id}" class="root_content hidden">"""
            
            p = rsc['root_families_dir'] \
                .joinpath("output/root info/") \
                .joinpath(f"{root_clean} {root_group} {root_meaning}.html")

            if p.exists():
                with open(p, 'r') as f:
                    root_info_read = f.read()

                    html_string += f"""<table class="root_table">{root_info_read}</table>"""
                    html_string += f"""<p>Did you spot a mistake? <a class="rootlink" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={root_clean} {root_group} {root_meaning}&entry.326955045=Root+Info&entry.1433863141=GoldenDict {today}" target="_blank">Correct it here.</a></p>"""
            
            html_string += """</div>"""

            # root matrix

            html_string += f"""<div id="root_matrix_{root_}_{root_id}" class="root_content hidden">"""

            p = rsc['root_families_dir'] \
                .joinpath("output/matrix/") \
                .joinpath(f"{root_clean} {root_group} {root_meaning}.html")

            if p.exists():
                with open(p, 'r') as f:
                    root_matrix_read = f.read()
                    root_counter = re.findall("</table>(.+)$", root_matrix_read)
                    root_counter = root_counter[0]
                    root_matrix_read = re.sub("</table>.+$", "</table>", root_matrix_read)
                    
                    if root_counter == "1":
                        html_string += f"""<p class = 'root_heading'><b>{root_counter}</b> word is derived from the root <b>{root_clean}</b> {root_group}<sup>{root_has_verb}</sup>{root_sign} ({root_meaning})</p>"""
                    else:
                        html_string += f"""<p class = 'root_heading'><b>{root_counter}</b> words are derived from the root <b>{root_clean}</b> {root_group}<sup>{root_has_verb}</sup>{root_sign} ({root_meaning})</p>"""
                    html_string += f"""{root_matrix_read}"""
                    if re.findall("✗", root_matrix_read):
                        html_string += f"""<p>Words still under construction (<span class="g3">✗</span>) cannot be automatically categorised as <i>causative</i>, <i>passive</i>, etc. and will be manually assigned in due course."""
                    html_string += f"""<p>Are there any other categories you would like to see here? Did you spot a mistake? <a class="rootlink" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={root_clean} {root_group} {root_meaning}&entry.326955045=Root+Info&entry.1433863141=GoldenDict {today}" target="_blank">Log it here.</a></p>"""
            
            html_string += """</div>"""

            # root families

            if root_families_df is not None:
                for line_no in range(root_families_length):
                    subfamily = root_families_df.iloc[line_no, 0]
                    subfamily_ = "_" + re.sub(" ", "_", subfamily)
                    subfamily_ = re.sub("√", "", subfamily_)

                    html_string += f"""<div id="root_family_{subfamily_}_{root_id}" class="root_content hidden">"""
                    # <a class="button root close" href="javascript:void(0);" onclick="button_click(this)" data-target="root_family_{subfamily_}_{root_id}">close</a>"""

                    p = rsc['root_families_dir'] \
                        .joinpath("output/subfamily html/") \
                        .joinpath(f"{root_clean} {root_group} {root_meaning} {subfamily}.html")

                    if p.exists():
                        with open(p, 'r') as f:
                            subfamily_html_read = f.read()
                            subfamily_html_read = re.sub("table1", "root_table", subfamily_html_read)
                            subfamily_count = int(re.findall("</table>(\\d*)", subfamily_html_read)[0])
                            subfamily_html_read = re.sub("</table>\\d*", "</table>", subfamily_html_read)

                            if subfamily_count == 1 :
                                html_string += f"""<p class="root_heading"><b>{subfamily_count}</b> word belongs to the root family <b>{subfamily}</b> ({root_meaning})</p>"""
                            else:
                                html_string += f"""<p class="root_heading"><b>{subfamily_count}</b> words belong to the root family <b>{subfamily}</b> ({root_meaning})</p>"""
                            html_string += f"""{subfamily_html_read}"""

                    else:
                        print(
                            f"{timeis()} {red}error\t{root_clean} {root_group} {root_meaning} {subfamily}.html")

                    html_string += f"""<p>Does something look wrong? <a class="rootlink" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={subfamily} {root_group} {root_meaning}&entry.326955045=Root+Family&entry.1433863141=GoldenDict {today}" target="_blank">Report it here</a>.</p>"""
                    html_string += "</div>"

            html_string += f"""</body></html>"""

            # html_string = minify_html.minify(html_string, minify_js=True, remove_processing_instructions=True)

            # writing html and compiling

            p = rsc['output_root_html_dir'].joinpath(f"{root_clean} {root_group} {root_meaning} (sample).html")
            with open(p, 'w') as f:
                f.write(html_string)

            root_no_sign = re.sub("√", "", root_clean)
            synonyms = [root_clean, root_no_sign]

            for synonym in synonyms:
                if re.findall("ṃ", synonym):
                    synonym1 = re.sub("ṃ", "ṁ", synonym)
                    synonyms.append(synonym1)
                    synonym2 = re.sub("ṃ", "ŋ", synonym)
                    synonyms.append(synonym2)

            # compile root data into list
            root_data_list += [[f"{root_super}", f"""{html_string}""", "", synonyms]]

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

        abbrev = abbrev_df.iloc[row, 0]
        meaning = abbrev_df.iloc[row, 1]
        pali = abbrev_df.iloc[row, 2]
        example = abbrev_df.iloc[row, 3]
        info = abbrev_df.iloc[row, 4]
        
        css = f"{abbrev_css}"
        html_string += render_header_tmpl(css=css, js="")

        html_string += "<body>"

        # summary

        html_string += f"""<div class="help"><table class="help">"""
        html_string += f"""<tr><th>Abbreviation</th>"""
        html_string += f"""<td><b>{abbrev}</b></td></tr>"""
        html_string += f"""<tr><th>Meaning</th>"""
        html_string += f"""<td>{meaning}</td></tr>"""
        if pali != "":
            html_string += f"""<tr><th>Pāḷi</th>"""
            html_string += f"""<td>{pali}</td></tr>"""
        if example != "":
            html_string += f"""<tr><th>Example</th>"""
            html_string += f"""<td>{example}</td></tr>"""
        if info != "":
            html_string += f"""<tr><th>Information</th>"""
            html_string += f"""<td>{info}</td></tr>"""
        html_string += f"""</table></div>"""
        
        html_string = minify_html.minify(html_string, minify_js=True, remove_processing_instructions=True)
        
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

        html_string += f"""<div class="help"><p>help. <b>{help_title}</b> = {meaning}</p></div>"""

        html_string = minify_html.minify(html_string, minify_js=True, remove_processing_instructions=True)
        
        p = rsc['output_help_html_dir'].joinpath(f"{help_title}.html")

        with open(p, 'w') as f:
            f.write(html_string)
        
        # compile root data into list
        synonyms = [help_title]
        help_data_list += [[f"{help_title}", f"""{html_string}""", "", synonyms]]
    

    # add bibliography

    print(f"{timeis()} {green}adding bibliography", end=" ")
    source = "assets/bibliograhy.md"
    destination = "../digitalpalidictionary-website-source/src/bibliography.md"
    
    with open(source) as f:
        md = f.read()

    try:
        shutil.copy(source, destination)
        print(f"{white} ok")
    except PermissionError:
        print(f"{red}permission denied") 
    except:
        print(f"{red} an error occurred while copying")

    css = f"{help_css}"
    html_string = render_header_tmpl(css=css, js="")
    html_string += "<body>"
    html_string += f"""<div class="help">"""
    html_string += markdown.markdown(md)
    html_string += f"</div></body>"

    synonyms = ["dpd bibliography", "bibliography", "bib"]
    help_data_list += [[f"bibliography", f"""{html_string}""", "", synonyms]]

    # add thanks

    print(f"{timeis()} {green}adding thanks", end=" ")
    source = "assets/thanks.md"
    destination = "../digitalpalidictionary-website-source/src/thanks.md"

    with open(source) as f:
        md = f.read()

    try:
        shutil.copy(source, destination)
        print(f"{white} ok")
    except PermissionError:
        print(f"{red}permission denied")
    except:
        print(f"{red} an error occurred while copying")

    css = f"{help_css}"
    html_string = render_header_tmpl(css=css, js="")
    html_string += "<body>"
    html_string += f"""<div class="help">"""
    html_string += markdown.markdown(md)
    html_string += f"</div></body>"

    synonyms = ["dpd thanks", "thankyou", "thanks","anumodana"]
    help_data_list += [[f"thanks", f"""{html_string}""", "", synonyms]]

    # generate epd html

    print(f"{timeis()} {green}generating epd html")
    
    df = data['words_df']
    df_length = data['words_df'].shape[0]
    pos_exclude_list = ["abbrev", "cs", "letter","root", "suffix", "ve"]

    epd = {}

    for row in range(df_length):  # df_length
        w = DpdWord(df, row)
        meanings_list = []
        lit_meaning_list = []
        w.meaning = re.sub("\\?\\?", "", w.meaning)

        if row % 10000 == 0:
            print(f"{timeis()} {row}/{df_length}\t{w.pali}")

        if w.meaning != "" and \
        w.pos not in pos_exclude_list:
            
            meanings_clean = re.sub(fr" \(.+?\)", "", w.meaning)                    # remove all space brackets
            meanings_clean = re.sub(fr"\(.+?\) ", "", meanings_clean)           # remove all brackets space
            meanings_clean = re.sub(fr"(^ | $)", "", meanings_clean)            # remove space at start and fin
            meanings_clean = re.sub(fr"  ", " ", meanings_clean)                    # remove double spaces
            meanings_clean = re.sub(fr" ;|; ", ";", meanings_clean)                 # remove space around ;
            meanings_clean = re.sub(fr"i\.e\. ", "", meanings_clean)               # remove i.e.
            meanings_clean = re.sub(fr"!", "", meanings_clean)                      # remove !
            meanings_clean = re.sub(fr"\\?", "", meanings_clean)                      # remove ?
            meanings_list = meanings_clean.split(";")

            for meaning in meanings_list:
                if meaning in epd.keys() and w.case =="":
                    epd[meaning] = f"{epd[meaning]}<br><b class = 'epd'>{w.pali_clean}</b> {w.pos}. {w.meaning}"
                if meaning in epd.keys() and w.case !="":
                    epd[meaning] = f"{epd[meaning]}<br><b class = 'epd'>{w.pali_clean}</b> {w.pos}. {w.meaning} ({w.case})"
                if meaning not in epd.keys() and w.case =="":
                    epd.update({meaning: f"<b class = 'epd'>{w.pali_clean}</b> {w.pos}. {w.meaning}"})
                if meaning not in epd.keys() and w.case !="":
                    epd.update({meaning: f"<b class = 'epd'>{w.pali_clean}</b> {w.pos}. {w.meaning} ({w.case})"})
    
    print(f"{timeis()} {green}adding roots to epd html")
    for row in range(roots_df_length):

        root_count = roots_df.iloc[row, 1]
        root = roots_df.iloc[row, 2]
        root_clean = re.sub(" \\d.*$", "", root)
        root_has_verb = roots_df.iloc[row, 4]
        root_group = roots_df.iloc[row, 5]
        root_sign = roots_df.iloc[row, 6]
        root_meanings = roots_df.iloc[row, 8]
        root_meanings_list = root_meanings.split(", ")

        if row % 250 == 0:
            print(f"{timeis()} {row}/{roots_df_length}\t{root}")

        if root_count != "0":
            for root_meaning in root_meanings_list:
                if root_meaning in epd.keys():
                    epd[root_meaning] = f"{epd[root_meaning]}<br><b class = 'epd'>{root}</b> root. {root_meanings}"
                if root_meaning not in epd.keys():
                    epd.update({root_meaning: f"<b class = 'epd'>{root}</b> root. {root_meanings}"})

    with open(rsc['epd_css_path'], 'r') as f:
        epd_css = f.read()
    
    epd_data_list = []

    for key, value in epd.items():
        html_string = ""
        html_string = epd_css
        html_string += f"<body><div class ='epd'><p>{value}</p></div></body></html>"

        html_string = minify_html.minify(html_string, minify_js=True, remove_processing_instructions=True)

        epd_data_list += [[f"{key}", f"""{html_string}""", "", ""]]

    # add compound deconstruction and sandhi splitter

    print(f"{timeis()} {green}generating sandhi html")

    with open("../inflection generator/output/sandhi dict", "rb") as pf:
        sandhi_dict = pickle.load(pf)
    
    with open(rsc['sandhi_css_path'], 'r') as f:
        sandhi_css = f.read()

    sandhi_data_list = []

    for key, value in sandhi_dict.items():
        key_clean = re.sub(" \\d.*$", "", key)
        if key_clean not in all_headwords_clean:

            html_string = ""
            html_string = sandhi_css
            html_string += f"""<body><div class ='sandhi'>"""
            html_string += f"""<a class="sandhi_feedback" href = "https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={key}&entry.326955045=Sandhi+Splitting&entry.1433863141=GoldenDict {today}" target = "_blank" ><abbr title="These splits are machine generated, please report any problems.">👍👎</abbr></a>"""
            html_string += f"""<p class='sandhi'>{value}</p></div></body></html>"""

            html_string = minify_html.minify(html_string, minify_js=True, remove_processing_instructions=True)

            # synonyms
            # add ṁ

            synonyms = list(all_inflections_dict[key]["inflections"])

            for synonym in synonyms:
                if re.findall("ṃ", synonym):
                    synonym1 = re.sub("ṃ", "ṁ", synonym)
                    synonyms.append(synonym1)
                    synonym2 = re.sub("ṃ", "ŋ", synonym)  
                    synonyms.append(synonym2)
                
            synonyms += list(all_inflections_dict[key]["sinhala"])
            synonyms += list(all_inflections_dict[key]["devanagari"])
            synonyms += list(all_inflections_dict[key]["thai"])

            sandhi_data_list += [[f"{key}", f"""{html_string}""", "", synonyms]]

    # roots > dataframe > json

    print(f"{timeis()} {green}generating data df")

    root_data_df = pd.DataFrame(root_data_list)
    root_data_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]

    abbrev_data_df = pd.DataFrame(abbrev_data_list)
    abbrev_data_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]

    help_data_df = pd.DataFrame(help_data_list)
    help_data_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]

    epd_data_df = pd.DataFrame(epd_data_list)
    epd_data_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]

    sandhi_df = pd.DataFrame(sandhi_data_list)
    sandhi_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]

    pali_data_df = pd.concat([pali_data_df, root_data_df, abbrev_data_df, help_data_df, epd_data_df, sandhi_df])
    pali_light_data_df = pd.concat([pali_light_data_df, root_data_df, abbrev_data_df, help_data_df, epd_data_df, sandhi_df])

    print(f"{timeis()} {green}saving html to pickle")
    with open ("output/dpd data", "wb") as pf:
        pickle.dump(pali_data_df, pf)

    with open("output/dpd light data", "wb") as pf:
        pickle.dump(pali_light_data_df, pf)

    toc()

if __name__ == "__main__":
    generate_html_and_json()
