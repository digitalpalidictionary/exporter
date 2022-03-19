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
        html_string += f"""<div class="content_dps"><p>{w.pos}"""
        text_concise += f"{w.pali}. {w.pos}."

        if w.fin == "n":
            html_string += f""" [{w.fin}]"""
            text_concise += f""" [{w.fin}]"""

        if w.fin == "nn":
            html_string += f""" [{w.fin}]"""
            text_concise += f""" [{w.fin}]"""

        if w.fin == "np":
            html_string += f""" [{w.fin}]"""
            text_concise += f""" [{w.fin}]"""

        if w.fin == "ns":
            html_string += f""" [{w.fin}]"""
            text_concise += f""" [{w.fin}]"""

        if w.fin == "pn":
            html_string += f""" [{w.fin}]"""
            text_concise += f""" [{w.fin}]"""

        if w.fin == "s":
            html_string += f""" [{w.fin}]"""
            text_concise += f""" [{w.fin}]"""

        # if w.case != "":
        #     html_string += f""" ({w.case})"""
        #     text_concise += f""" ({w.case})"""

        html_string += f""". <b>{w.russian}</b>"""
        text_concise += f""". {w.russian}"""

        # if w.base == "":
        #     construction_simple = re.sub(r" \[.+\] \+", "", w.construction)
        #     construction_simple = re.sub("> .+? ", "", construction_simple)
        #     construction_simple = re.sub("<br/>.+", "", construction_simple)
        #     if construction_simple != "":
        #         html_string += f""". [{construction_simple}]"""
        #         text_concise += f""". [{construction_simple}]"""

        # if w.base != "":
        #     family_plus = re.sub(" ", " + ", w.family)
        #     construction_oneline = re.sub("<br/>.+", "", w.construction)
        #     construction_truncated = re.sub(r"(.+)(\+ .{1,7}$)", "\\2", construction_oneline)
        #     if re.match("^na ", w.construction):
        #         construction_na = re.sub("^(na )(.+)$", "\\1 + ", w.construction)
        #     else:
        #         construction_na = ""

        #     construction_reconstructed = f"{construction_na}{family_plus} + {w.root_sign} {construction_truncated}"
        #     html_string += f""" [{construction_reconstructed}]"""
        #     text_concise += f""" [{construction_reconstructed}]"""

        html_string += f"""</p></div>"""

    return RenderResult(
        html = html_string,
        full = text_full,
        concise = text_concise,
    )
