import pickle
import re

from datetime import date

import pandas as pd

from helpers import DataFrames
from helpers import DpsWord
from helpers import INDECLINABLES
from helpers import ResourcePaths
from helpers import format_if
from helpers import parse_data_frames
from helpers import string_if
from html_components import render_header_tmpl
from html_components import WordTemplate
from html_components import render_word_meaning
from html_components import render_word_meaning_sbs

from timeis import timeis, yellow, green, red, line  # FIXME Use lib

GOOGLE_LINK_TEMPLATE = (
    '<a class="link" href="https://docs.google.com/forms/d/1iMD9sCSWFfJAFCFYuG9HRIyrr9KFRy0nAOVApM998wM/viewform?'
    'usp=pp_url&{args}" target="_blank">{text}</a>')

ENCODING = 'UTF-8'


def _full_text_dps_entry(word: DpsWord) -> str:
    comm_text = re.sub('<br/>', ' ', word.comm)
    comm_text = re.sub('<b>', '', comm_text)
    comm_text = re.sub('</b>', '', comm_text)

    construction_text = re.sub('<br/>', ', ', word.construction)

    result = ''
    # FIXME Seems conditions is broken when word.russian != ''
    result += string_if(not word.russian, f'{word.pali}. {word.pos}. {word.meaning}. [в процессе]')
    result += string_if(word.pos, f'{word.pali}. {word.pos}')

    for i in [word.grammar, word.derived, word.neg, word.verb, word.trans]:
        result += string_if(i, f', {i}')

    result += string_if(word.case, f' ({word.case})')
    result += f'. {word.meaning}'
    result += string_if(word.russian, f'. {word.russian}')
    result += string_if(word.root, f'. корень: {word.root}')
    result += format_if(word.base, '. основа: {}')

    result += format_if(construction_text, '. образование: {}')

    result += format_if(word.var, 'вариант: {}')
    result += format_if(comm_text, '. комментарий: {}')
    result += format_if(word.notes, '. заметки: {}')
    result += format_if(word.sk, '. санскрит: {}')
    result += format_if(word.sk_root, '. санск. корень: {}')
    result += '\n'

    return result


# TODO SBS
def _full_text_sbs_entry(word: DpsWord) -> str:
    comm_text = re.sub('<br/>', ' ', word.comm)
    comm_text = re.sub('<b>', '', comm_text)
    comm_text = re.sub('</b>', '', comm_text)

    construction_text = re.sub('<br/>', ', ', word.construction)

    result = ''
    # FIXME Seems conditions is broken when word.russian != ''
    result += string_if(not word.russian, f'{word.pali}. {word.pos}. {word.meaning}. [в процессе]')
    result += string_if(word.pos, f'{word.pali}. {word.pos}')

    for i in [word.grammar, word.derived, word.neg, word.verb, word.trans]:
        result += string_if(i, f', {i}')

    result += string_if(word.case, f' ({word.case})')
    result += f'. {word.meaning}'
    result += string_if(word.russian, f'. {word.russian}')
    result += string_if(word.root, f'. корень: {word.root}')
    result += format_if(word.base, '. основа: {}')

    result += format_if(construction_text, '. образование: {}')

    result += format_if(word.var, 'вариант: {}')
    result += format_if(comm_text, '. комментарий: {}')
    result += format_if(word.notes, '. заметки: {}')
    result += format_if(word.sk, '. санскрит: {}')
    result += format_if(word.sk_root, '. санск. корень: {}')
    result += '\n'

    return result


# TODO Delete kind or make Enum
def generate_html_and_json(rsc, kind: str, generate_roots: bool = True):
    data = parse_data_frames(rsc)

    print(f"{timeis()} {yellow}generate html and json")
    print(f"{timeis()} {line}")
    print(f"{timeis()} {green}generating dps html")

    error_log = ''

    html_data_list = []
    text_data_full = ''
    text_data_concise = ''

    inflection_table_error_string = ''
    synonyms_error_string = ''

    df = data['words_df']
    df_length = data['words_df'].shape[0]

    with open(rsc['dict_words_css_path'], 'r', encoding=ENCODING) as f:
        words_css = f.read()

    with open(rsc['buttons_js_path'], 'r', encoding=ENCODING) as f:
        buttons_js = f.read()

    word_template = WordTemplate(rsc['word_template_path'])

    for row in range(df_length):
        w = DpsWord(df, row)

        if row % 5000 == 0 or row % df_length == 0:
            print(f"{timeis()} {row}/{df_length}\t{w.pali}")

        html_string = ''
        if kind == 'dps':
            text_full = _full_text_dps_entry(word=w)
        elif kind == 'sbs':
            text_full = _full_text_sbs_entry(word=w)

        text_concise = ''

        # html head & style
        html_string += render_header_tmpl(css=words_css, js=buttons_js)

        # summary
        if kind == 'dps':
            r = render_word_meaning(w)
        elif kind == 'sbs':
            r = render_word_meaning_sbs(w)

        text_concise += r['concise']

        # inflection table
        if w.pos not in INDECLINABLES:
            table_path = rsc['inflections_dir'].joinpath("output/html tables/").joinpath(w.pali + ".html")

            table_data_read = ''
            try:
                with open(table_path) as f:
                    table_data_read = f.read()
            except FileNotFoundError:
                inflection_table_error_string += w.pali + ", "
                error_log += f'error reading inflection table: {w.pali}.html\n'

        html_string += word_template.render(w, table_data_read=table_data_read)
        html_string += '</html>'

        inflections_path = rsc['inflections_dir'].joinpath("output/inflections translit/").joinpath(w.pali)

        if inflections_path.exists():
            with open(inflections_path, "rb") as syn_file:
                synonyms = pickle.load(syn_file)
                synonyms = (synonyms)
        else:
            synonyms_error_string += w.pali + ', '
            error_log += f'error reading synonyms - {w.pali}\n'
            synonyms = ""

        # data compiling
        html_data_list += [[f"{w.pali}", f'{html_string}', "", synonyms]]
        text_data_full += text_full
        text_data_concise += f"{text_concise}\n"

        # TODO Delete before merge
        if w.pali == 'akata 1':
            with open('output/cur.html', 'w') as f:
                f.write(html_string)

        if row % 100 == 0:
            p = rsc['output_html_dir'].joinpath(f"{w.pali} (sample).html")
            with open(p, "w", encoding="utf-8") as f:
                f.write(html_string)

    error_log_path = rsc['error_log_dir'].joinpath("exporter errorlog.txt")
    with open(error_log_path, 'w', encoding=ENCODING) as error_log_file:
        error_log_file.write(error_log)

    if inflection_table_error_string != "":
        print(f"{timeis()} {red}inflection table errors: {inflection_table_error_string}")

    if synonyms_error_string != "":
        print(f"{timeis()} {red}synonym errors: {synonyms_error_string}")

    # convert ṃ to ṁ
    text_data_full = re.sub('ṃ', 'ṁ', text_data_full)
    text_data_concise = re.sub('ṃ', 'ṁ', text_data_concise)

    # write text versions
    p = rsc['output_share_dir'].joinpath('dps_full.txt')
    with open(p, 'w', encoding='UTF-8') as f:
        f.write(text_data_full)

    p = rsc['output_share_dir'].joinpath('dps_concise.txt')
    with open(p, 'w', encoding='UTF-8') as f:
        f.write(text_data_concise)

    if generate_roots:
        if kind == 'dps':
            generate_roots_html_and_json(data, rsc, html_data_list)
        elif kind == 'sbs':
            generate_roots_html_and_json_sbs(data, rsc, html_data_list)

# TODO Implement templates
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

        abbrev = abbrev_df.iloc[row, 0]
        meaning = abbrev_df.iloc[row, 1]
        pali_meaning = abbrev_df.iloc[row, 2]
        ru_meaning = abbrev_df.iloc[row, 3]
        examp = abbrev_df.iloc[row, 4]
        expl = abbrev_df.iloc[row, 5]

        css = f"{abbrev_css}"
        html_string += render_header_tmpl(css=css, js="")

        html_string += "<body>"

        # summary

        html_string += f'<div class="help"><p>abbreviation. <b>{abbrev}</b>. {meaning}. '

        if pali_meaning != "":
            html_string += f'{pali_meaning}. '

        if ru_meaning != "":
            html_string += f'{ru_meaning}. '

        if examp != "":
            html_string += f'<br>e.g. {examp}. '

        if expl != "":
            html_string += f'<br>{expl}.'

        html_string += '</p></div>'

        html_string += (
            '<p>' +
            GOOGLE_LINK_TEMPLATE.format(
                args=f'entry.438735500={abbrev}&entry.1433863141=GoldenDict {today}',
                text='Сообщить об ошибке.') +
            '</p>')

        part_file = rsc['output_help_html_dir'].joinpath(f"{abbrev}.html")

        rsc['output_help_html_dir'].mkdir(parents=True, exist_ok=True)  # TODO Move out of the loop
        with open(part_file, 'w') as f:
            f.write(html_string)

        # compile root data into list
        synonyms = [abbrev, meaning]
        abbrev_data_list += [[f"{abbrev}", f'{html_string}', "", synonyms]]


  # generate help html
    print(f"{timeis()} {green}generating help html")

    help_data_list = []

    try:
        with open(rsc['dict_help_css_path'], 'r') as f:
            help_css = f.read()
    except FileNotFoundError:
        help_css = ''

    help_df = data['help_df']
    help_df_length = len(help_df)

    for row in range(help_df_length):

        html_string = ""

        help_title = help_df.iloc[row, 0]
        meaning = help_df.iloc[row, 1]

        html_string += render_header_tmpl(css=help_css, js="")

        html_string += "<body>"

        # summary

        html_string += f'<div class="help"><p>помощь. <b>{help_title}</b>. {meaning}</p></div>'

        p = rsc['output_help_html_dir'].joinpath(f"{help_title}.html")

        with open(p, 'w') as f:
            f.write(html_string)

        # compile root data into list
        synonyms = [help_title]
        help_data_list += [[f"{help_title}", f'{html_string}', "", synonyms]]


    # generate rpd html
    print(f"{timeis()} {green}generating rpd html")

    df = data['words_df']
    df_length = data['words_df'].shape[0]
    pos_exclude_list = ["abbrev", "cs", "letter", "root", "suffix", "ve"]

    rpd = {}

    for row in range(df_length):  # df_length
        w = DpsWord(df, row)
        meanings_list = []
        w.russian = re.sub(r'\?\?', "", w.russian)

        if row % 10000 == 0:
            print(f"{timeis()} {row}/{df_length}\t{w.pali}")

        if w.russian != "" and w.pos not in pos_exclude_list:

            meanings_clean = re.sub(fr" \(.+?\)", "", w.russian)          # remove all space brackets
            meanings_clean = re.sub(fr"\(.+?\) ", "", meanings_clean)     # remove all brackets space
            meanings_clean = re.sub(fr"(^ | $)", "", meanings_clean)      # remove space at start and fin
            meanings_clean = re.sub(fr"  ", " ", meanings_clean)          # remove double spaces
            meanings_clean = re.sub(fr" ;|; ", ";", meanings_clean)       # remove space around ;
            meanings_clean = re.sub(fr"\(комм\).+$", "", meanings_clean)  # remove commentary meanings
            meanings_clean = re.sub(fr"досл.+$", "", meanings_clean)      # remove lit meanings
            meanings_list = meanings_clean.split(";")

            for russian in meanings_list:
                if russian in rpd.keys() and w.case == "":
                    rpd[russian] = f"{rpd[russian]}<br><b>{w.pali_clean}</b> {w.pos}. {w.russian}"
                if russian in rpd.keys() and w.case != "":
                    rpd[russian] = f"{rpd[russian]}<br><b>{w.pali_clean}</b> {w.pos}. {w.russian} ({w.case})"
                if russian not in rpd.keys() and w.case == "":
                    rpd.update({russian: f"<b>{w.pali_clean}</b> {w.pos}. {w.russian}"})
                if russian not in rpd.keys() and w.case != "":
                    rpd.update({russian: f"<b>{w.pali_clean}</b> {w.pos}. {w.russian} ({w.case})"})

    with open(rsc['rpd_css_path'], 'r') as f:
        rpd_css = f.read()

    rpd_data_list = []

    for key, value in rpd.items():
        html_string = ""
        html_string = rpd_css
        html_string += f"<body><div class ='rpd'><p>{value}</p></div></body></html>"
        rpd_data_list += [[f"{key}", f'{html_string}', "", ""]]

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

# TODO Merge to generate_html_and_json()
def generate_roots_html_and_json_sbs(data: DataFrames, rsc: ResourcePaths, html_data_list):
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
        # ru_meaning = abbrev_df.iloc[row,3]
        examp = abbrev_df.iloc[row,4]
        expl = abbrev_df.iloc[row,5]

        css = f"{abbrev_css}"
        html_string += render_header_tmpl(css=css, js="")

        html_string += "<body>"

        # summary

        html_string += f"""<div class="help"><p>abbreviation. <b>{abbrev}</b>. {meaning}. """

        if pali_meaning != "":
            html_string += f"""{pali_meaning}. """

        # if ru_meaning != "":
        #     html_string += f"""{ru_meaning}. """

        if examp != "":
            html_string += f"""<br>e.g. {examp}. """

        if expl != "":
            html_string += f"""<br>{expl}."""

        html_string += f"""</p></div>"""

        html_string += f"""<p><a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLScNC5v2gQbBCM3giXfYIib9zrp-WMzwJuf_iVXEMX2re4BFFw/viewform?usp=pp_url&entry.438735500={abbrev}&entry.1433863141=GoldenDict {today}" target="_blank">Report a mistake.</a></p>"""

        rsc['output_help_html_dir'].mkdir(parents=True, exist_ok=True)  # TODO Move out of the loop
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

        html_string += render_header_tmpl(css=help_css, js='')

        html_string += "<body>"

        # summary

        html_string += f"""<div class="help"><p>help. <b>{help_title}</b>. {meaning}</p></div>"""

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
