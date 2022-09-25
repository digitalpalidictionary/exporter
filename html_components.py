import re

from mako.template import Template
from mako import exceptions

from datetime import date
from typing import TypedDict
from helpers import DpsWord

import timeis

header_tmpl = Template(filename='./assets/templates/header.html')
feedback_tmpl = Template(filename='./assets/templates/feedback-dps.html')
feedback_tmpl_sbs = Template(filename='./assets/templates/feedback-sbs.html')
feedback_tmpl_test = Template(filename='./assets/templates/feedback-test.html')
word_dps_tmpl = Template(filename='./assets/templates/word-dps.html')


def render_header_tmpl(css: str, js: str) -> str:
    return str(header_tmpl.render(css=css, js=js))


def render_feedback_tmpl(w: DpsWord) -> str:
    today = date.today()
    return str(feedback_tmpl.render(w=w, today=today))


def render_feedback_tmpl_sbs(w: DpsWord) -> str:
    today = date.today()
    return str(feedback_tmpl_sbs.render(w=w, today=today))


def render_feedback_tmpl_test(w: DpsWord) -> str:
    today = date.today()
    return str(feedback_tmpl_test.render(w=w, today=today))


def render_word_dps_tmpl(word: DpsWord, meaning: str) -> str:
    indeclinables = ["abbrev", "abs", "ger", "ind", "inf", "prefix", "sandhi", "idiom"]
    conjugations = ["aor", "cond", "fut", "imp", "imperf", "opt", "perf", "pr"]
    declensions = [
        "adj", "card", "cs", "fem", "letter", "masc", "nt", "ordin", "pp", "pron",
        "prp", "ptp", "root", "suffix", "ve"
    ]
    try:
        return word_dps_tmpl.render(
            conjugations=conjugations,
            declensions=declensions,
            indeclinables=indeclinables,
            meaning=meaning,
            today=date.today(),
            word=word)
    except:
        print(f'{timeis.red} Template exception')
        print(exceptions.text_error_template().render())
        print(f'{timeis.line}{timeis.white}')



class RenderResult(TypedDict):
    html: str
    full: str
    concise: str


def render_word_meaning(w: DpsWord) -> RenderResult:
    html_string = ""
    text_full = ""
    text_concise = ""

    if w.russian == "":
        html_string += f"""<div class="content_dps"><p>{w.pos}. <b>{w.meaning}</b> [в процессе]</p></div>"""
        text_full += f"""{w.pali}. {w.pos}. {w.meaning}. [в процессе]"""
        text_concise += f"""{w.pali}. {w.pos}. {w.meaning}."""

    else:
        html_string += f"""<div class="content_dps"><p>"""

        if w.pos != "":
            html_string += f"""{w.pos}."""
            text_concise += f"{w.pali}. {w.pos}."

        html_string += f""" <b>{w.russian}</b>"""
        text_concise += f""" {w.russian}"""

        html_string += f"""</p></div>"""

    return RenderResult(
        html = html_string,
        full = text_full,
        concise = text_concise,
    )


def render_word_meaning_sbs(w: DpsWord) -> RenderResult:
    html_string = ""
    text_full = ""
    text_concise = ""

    html_string += '<div class="content_sbs"><p>'
    text_concise += f"{w.pali}."

    if w.ex != "":
        html_string += f"""<b>(cl.{w.ex}) | </b>"""

    if w.pos != "":
        html_string += f"{w.pos}."
        text_concise += f"{w.pos}."

    if w.sbs_meaning != "":
        html_string += f" <b>{w.sbs_meaning}</b>"
        text_concise += f" {w.sbs_meaning}"

    if w.sbs_meaning == "":
        html_string += f" <b>{w.meaning}</b>"
        text_concise += f" {w.meaning}"

    html_string += "</p></div>"

    return RenderResult(
        html=html_string,
        full=text_full,
        concise=text_concise,
    )

def render_word_meaning_test(w: DpsWord) -> RenderResult:
    html_string = ""
    text_full = ""
    text_concise = ""

    html_string += f"""<div class="content_test"><p>"""

    if w.ex != "":
        html_string += f"""<b>(ex.{w.ex}) | </b>"""

        if w.count != "":
            html_string += f"""#{w.count}. | """

        html_string += f"""{w.pos}. <b>{w.meaning}</b>"""

        if w.chapter2 != "":
            html_string += f""" | <i>[sbs]</i>"""
    
    else:
        if w.count != "":
            html_string += f"""(cl.{w.cl}).#{w.count}. | """

        html_string += f"""{w.pos}. <b>{w.meaning}</b>"""

        if w.chapter2 != "":
            html_string += f""" | <i>[sbs]</i>"""

    html_string += f"""</p>"""

    if w.russian != "":
        html_string += f"""<p>{w.russian}</p>"""

    html_string += f"""</div>"""

    return RenderResult(
        html = html_string,
        full = text_full,
        concise = text_concise,
    )
