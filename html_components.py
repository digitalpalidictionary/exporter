from datetime import date
from typing import TypedDict

from mako import exceptions
from mako.template import Template

import helpers
import timeis

from helpers import DpsWord

header_tmpl = Template(filename='./assets/templates/header.html')
feedback_tmpl_sbs = Template(filename='./assets/templates/feedback-sbs.html')
feedback_tmpl_test = Template(filename='./assets/templates/feedback-test.html')
word_dps_tmpl = Template(filename='./assets/templates/word-dps.html')


def _render(template: Template, **kwargs) -> str:
    try:
        return template.render(**kwargs)
    except Exception as error:
        print(f'{timeis.red} Template exception')
        print(exceptions.text_error_template().render())
        print(f'{timeis.line}{timeis.white}')
        raise error from None


def render_header_tmpl(css: str, js: str) -> str:
    return str(header_tmpl.render(css=css, js=js))


def render_feedback_tmpl_sbs(w: DpsWord) -> str:
    today = date.today()
    return str(feedback_tmpl_sbs.render(w=w, today=today))


def render_feedback_tmpl_test(w: DpsWord) -> str:
    today = date.today()
    return str(feedback_tmpl_test.render(w=w, today=today))


def render_word_dps_tmpl(word: DpsWord, table_data_read: str) -> str:
    return _render(
        word_dps_tmpl,
        conjugations=helpers.CONJUGATIONS,
        declensions=helpers.DECLENSIONS,
        indeclinables=helpers.INDECLINABLES,
        table_data_read=table_data_read,
        today=date.today(),
        word=word)


class RenderResult(TypedDict):
    html: str
    full: str
    concise: str


def render_word_meaning(w: DpsWord) -> RenderResult:
    text_concise = ""

    if w.russian == "":
        text_concise += f"""{w.pali}. {w.pos}. {w.meaning}."""

    else:
        if w.pos != "":
            text_concise += f"{w.pali}. {w.pos}."

        text_concise += f""" {w.russian}"""


    return RenderResult(
        html = '',  # TODO Deprecate
        full = '',  # TODO Deprecate
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
