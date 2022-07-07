import re

from datetime import date
from typing import TypedDict
from helpers import DpsWord
from mako.template import Template

header_tmpl = Template(filename='./assets/templates/header.html')
feedback_tmpl = Template(filename='./assets/templates/feedback.html')
feedback_tmpl_sbs = Template(filename='./assets_sbs/templates/feedback.html')


def render_header_tmpl(css: str, js: str) -> str:
    return str(header_tmpl.render(css=css, js=js))


def render_feedback_tmpl(w: DpsWord) -> str:
    today = date.today()
    return str(feedback_tmpl.render(w=w, today=today))


def render_feedback_tmpl_sbs(w: DpsWord) -> str:
    today = date.today()
    return str(feedback_tmpl_sbs.render(w=w, today=today))


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
