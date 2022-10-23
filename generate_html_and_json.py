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
            synonyms = ''

        # data compiling
        html_data_list += [[f"{w.pali}", f'{html_string}', '', synonyms]]
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

    if inflection_table_error_string != '':
        print(f"{timeis()} {red}inflection table errors: {inflection_table_error_string}")

    if synonyms_error_string != '':
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
        generate_roots_html_and_json(data, rsc, html_data_list, kind=kind)

# TODO Implement templates
# TODO Fix ugly kind arg
# TODO Split
def generate_roots_html_and_json(data: DataFrames, rsc: ResourcePaths, html_data_list, kind: str):
    # html list > dataframe
    pali_data_df = pd.DataFrame(html_data_list)
    pali_data_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]

    abbrev_data_list = _generate_abbreviations_html(data, rsc, kind)
    help_data_list = _generate_help_html(data, rsc, kind)
    definition_data_list = _generate_definition_html(data, rsc, kind)

    # roots > dataframe > json
    print(f"{timeis()} {green}generating json")

    abbrev_data_df = pd.DataFrame(abbrev_data_list)
    abbrev_data_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]

    help_data_df = pd.DataFrame(help_data_list)
    help_data_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]

    definition_data_df = pd.DataFrame(definition_data_list)
    definition_data_df.columns = ["word", "definition_html", "definition_plain", "synonyms"]
    pali_data_df = pd.concat([pali_data_df, abbrev_data_df, help_data_df, definition_data_df])

    print(f"{timeis()} {green}saving html to json")

    pali_data_df.to_json(rsc['gd_json_path'], force_ascii=False, orient="records", indent=6)

    print(f"{timeis()} {line}")


# TODO Declaration
def _generate_abbreviations_html(data, rsc, kind):
    print(f"{timeis()} {green}generating abbreviations html")

    abbrev_data_list = []

    today = date.today()

    with open(rsc['dict_help_css_path'], 'r') as f:
        abbrev_css = f.read()

    abbrev_df = data['abbrev_df']
    abbrev_df_length = len(abbrev_df)

    for row in range(abbrev_df_length):

        html_string = ''

        abbrev = abbrev_df.iloc[row, 0]
        meaning = abbrev_df.iloc[row, 1]
        pali_meaning = abbrev_df.iloc[row, 2]
        ru_meaning = abbrev_df.iloc[row, 3]
        examp = abbrev_df.iloc[row, 4]
        expl = abbrev_df.iloc[row, 5]

        css = f"{abbrev_css}"
        html_string += render_header_tmpl(css=css, js='')

        html_string += "<body>"

        # summary

        html_string += f'<div class="help"><p>abbreviation. <b>{abbrev}</b>. {meaning}. '

        if pali_meaning != '':
            html_string += f'{pali_meaning}. '

        if kind == 'dps':
            if ru_meaning != '':
                html_string += f'{ru_meaning}. '

        if examp != '':
            html_string += f'<br>e.g. {examp}. '

        if expl != '':
            html_string += f'<br>{expl}.'

        html_string += '</p></div>'

        if kind == 'dps':
            html_string += (
                '<p>' +
                GOOGLE_LINK_TEMPLATE.format(
                    args=f'entry.438735500={abbrev}&entry.1433863141=GoldenDict {today}',
                    text='Сообщить об ошибке.') +
                '</p>')
        else:
            # TODO
            html_string += f"""<p><a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLScNC5v2gQbBCM3giXfYIib9zrp-WMzwJuf_iVXEMX2re4BFFw/viewform?usp=pp_url&entry.438735500={abbrev}&entry.1433863141=GoldenDict {today}" target="_blank">Report a mistake.</a></p>"""

        part_file = rsc['output_help_html_dir'].joinpath(f"{abbrev}.html")

        rsc['output_help_html_dir'].mkdir(parents=True, exist_ok=True)  # TODO Move out of the loop
        with open(part_file, 'w') as f:
            f.write(html_string)

        # compile root data into list
        synonyms = [abbrev, meaning]
        abbrev_data_list += [[f"{abbrev}", f'{html_string}', '', synonyms]]

    return abbrev_data_list


# TODO Signature
def _generate_help_html(data, rsc, kind):
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

        html_string = ''

        help_title = help_df.iloc[row, 0]
        meaning = help_df.iloc[row, 1]

        html_string += render_header_tmpl(css=help_css, js='')

        html_string += "<body>"

        # summary

        if kind == 'dps':
            html_string += f'<div class="help"><p>помощь. <b>{help_title}</b>. {meaning}</p></div>'
        else:
            html_string += f"""<div class="help"><p>help. <b>{help_title}</b>. {meaning}</p></div>"""

        p = rsc['output_help_html_dir'].joinpath(f"{help_title}.html")

        with open(p, 'w') as f:
            f.write(html_string)

        # compile root data into list
        synonyms = [help_title]
        help_data_list += [[f"{help_title}", f'{html_string}', '', synonyms]]

    return help_data_list


# TODO Signature
def _generate_definition_html(data, rsc, kind):
    print(f"{timeis()} {green}generating definition HTML")

    df = data['words_df']
    df_length = data['words_df'].shape[0]
    pos_exclude_list = ["abbrev", "cs", "letter", "root", "suffix", "ve"]

    definition = {}

    for row in range(df_length):  # df_length
        w = DpsWord(df, row)
        meanings_list = []
        meaning_data = w.russian if kind == 'dps' else w.meaning
        meaning_data = re.sub(r'\?\?', '', meaning_data)

        if row % 10000 == 0:
            print(f"{timeis()} {row}/{df_length}\t{w.pali}")

        if meaning_data != '' and w.pos not in pos_exclude_list:

            meanings_clean = re.sub(r' \(.+?\)', '', meaning_data)       # remove all space brackets
            meanings_clean = re.sub(r'\(.+?\) ', '', meanings_clean)     # remove all brackets space
            meanings_clean = re.sub(r'(^ | $)', '', meanings_clean)      # remove space at start and fin
            meanings_clean = re.sub(r'  ', ' ', meanings_clean)          # remove double spaces
            meanings_clean = re.sub(r' ;|; ', ';', meanings_clean)       # remove space around semicolons
            meanings_clean = re.sub(r'\((комм|comm)\).+$', '', meanings_clean)  # remove commentary meanings
            meanings_clean = re.sub(r'(досл|lit).+$', '', meanings_clean)      # remove lit meanings
            meanings_list = meanings_clean.split(';')

            for meaning in meanings_list:
                if meaning in definition.keys() and w.case == '':
                    definition[meaning] = f"{definition[meaning]}<br><b>{w.pali_clean}</b> {w.pos}. {meaning_data}"
                if meaning in definition.keys() and w.case != '':
                    definition[meaning] = f"{definition[meaning]}<br><b>{w.pali_clean}</b> {w.pos}. {meaning_data} ({w.case})"
                if meaning not in definition.keys() and w.case == '':
                    definition.update({meaning: f"<b>{w.pali_clean}</b> {w.pos}. {meaning_data}"})
                if meaning not in definition.keys() and w.case != '':
                    definition.update({meaning: f"<b>{w.pali_clean}</b> {w.pos}. {meaning_data} ({w.case})"})

    with open(rsc['definition_css_path'], 'r') as f:
        definition_css = f.read()

    definition_data_list = []

    div_class = 'rpd' if kind == 'dps' else 'epd_sbs'
    for key, value in definition.items():
        html_string = ''
        html_string = definition_css
        html_string += f"<body><div class='{div_class}'><p>{value}</p></div></body></html>"
        definition_data_list += [[f"{key}", f'{html_string}', '', '']]

    return definition_data_list
