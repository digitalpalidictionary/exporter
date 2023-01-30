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

    if w.meaning == "":
        html_string += f"""<div class="content"><p>{w.pos}. <b>{w.buddhadatta}</b> <span class="g3">✗</span></p></div>"""
        text_full += f"""{w.pali}. {w.grammar}. {w.buddhadatta}. [under construction]"""
        text_concise += f"""{w.pali}. {w.pos}. {w.buddhadatta}."""

    else:
        html_string += f"""<div class="content"><p>{w.pos}. """
        text_concise += f"{w.pali}. {w.pos}. "

        if w.case != "":
            html_string += f"""({w.case}) """
            text_concise += f"""({w.case}) """

        html_string += f"""<b>{w.meaning}</b>"""
        text_concise += f"""{w.meaning}"""

        if w.lit != "":
            html_string += f"""; lit. {w.lit}"""
            text_concise += f"""; lit. {w.lit}"""

        if w.base == "":
            construction_simple = re.sub("<br/>.+$", "", w.construction) # remove line2
            construction_simple = re.sub(r" \[.+\] \+", "", construction_simple) # remove [insertions]
            construction_simple = re.sub("> .+? ", "", construction_simple) # remove phonetic changes
            construction_simple = re.sub(" > .+?$", "", construction_simple) # remove phonetic changes at end

            if construction_simple != "":
                html_string += f""" [{construction_simple}]"""
                text_concise += f""" [{construction_simple}]"""

        if w.base != "":
            base_clean = re.sub(" \\(.+\\)$", "", w.base)
            base_clean = re.sub("(.+ )(.+?$)", "\\2", base_clean)
            family_plus = re.sub(" ", " + ", w.family)
            construction_oneline = re.sub("<br/>.+", "", w.construction)
            construction_truncated = re.sub(" > .[^ ]+", "", w.construction)
            construction_truncated = re.sub(f".*{base_clean}", "", construction_truncated)

            if re.match("^na ", w.construction):
                construction_na = re.sub("^(na )(.+)$", "\\1+ ", w.construction)
            else:
                construction_na = ""

            construction_reconstructed = f"{construction_na}{family_plus} + {w.root_sign}{construction_truncated}"
            html_string += f""" [{construction_reconstructed}]"""
            text_concise += f""" [{construction_reconstructed}]"""
        
        
        if w.source1 != "" and w.sutta1 != "":
            html_string += f""" <span class="g1">✓</span>"""
        elif w.source1 == "" and w.sutta1 == "":
            html_string += f""" <span class="g2">~</span>"""

        html_string += f"""</p></div>"""

    return RenderResult(
        html = html_string,
        full = text_full,
        concise = text_concise,
    )
