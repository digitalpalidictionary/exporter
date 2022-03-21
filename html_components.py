import re

from datetime import date
from typing import TypedDict
from helpers import DpdWord
from mako.template import Template

header_tmpl = Template(filename='./assets/templates/header.html')
feedback_tmpl = Template(filename='./assets/templates/feedback.html')

def render_header_tmpl(css: str, js: str) -> str:
    return str(header_tmpl.render(css=css, js=js))

def render_feedback_tmpl(w: DpdWord) -> str:
    today = date.today()
    return str(feedback_tmpl.render(w=w, today=today))

class RenderResult(TypedDict):
  html: str
  full: str
  concise: str

def render_word_meaning(w: DpdWord) -> RenderResult:
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

        #     if w.fin == "n":
        #         html_string += f""" [{w.fin}]."""
        #         text_concise += f""" [{w.fin}]."""

        #     if w.fin == "nn":
        #         html_string += f""" [{w.fin}]."""
        #         text_concise += f""" [{w.fin}]."""

        #     if w.fin == "np":
        #         html_string += f""" [{w.fin}]."""
        #         text_concise += f""" [{w.fin}]."""

        #     if w.fin == "ns":
        #         html_string += f""" [{w.fin}]."""
        #         text_concise += f""" [{w.fin}]."""

        #     if w.fin == "pn":
        #         html_string += f""" [{w.fin}]."""
        #         text_concise += f""" [{w.fin}]."""

        #     if w.fin == "s":
        #         html_string += f""" [{w.fin}]."""
        #         text_concise += f""" [{w.fin}]."""

        html_string += f""" <b>{w.russian}</b>"""
        text_concise += f""" {w.russian}"""

        html_string += f"""</p></div>"""

    return RenderResult(
        html = html_string,
        full = text_full,
        concise = text_concise,
    )
