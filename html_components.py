from datetime import date
from pathlib import Path
from typing import TypedDict

from mako import exceptions
from mako.template import Template

import helpers
import timeis

from helpers import DpsWord

HEADER_TMPL = Template(filename='./assets/templates/header.html')


def _render(template: Template, **kwargs) -> str:
    try:
        return template.render(**kwargs)
    except Exception as error:
        print(f'{timeis.red} Template exception')
        print(exceptions.text_error_template().render())
        print(f'{timeis.line}{timeis.white}')
        raise error from None


def render_header_tmpl(css: str, js: str) -> str:
    return str(HEADER_TMPL.render(css=css, js=js))


class WordTemplate:
    def __init__(self, template_path: Path):
        self._template = Template(filename=str(template_path))

    def render(self, word: DpsWord, table_data_read: str) -> str:
        return _render(
            self._template,
            conjugations=helpers.CONJUGATIONS,
            declensions=helpers.DECLENSIONS,
            indeclinables=helpers.INDECLINABLES,
            table_data_read=table_data_read,
            today=date.today(),
            word=word)


def render_word_meaning(word: DpsWord) -> str:
    text_concise = ''

    if word.russian == '':
        text_concise += f'{word.pali}. {word.pos}. {word.meaning}.'
    else:
        if word.pos != '':
            text_concise += f"{word.pali}. {word.pos}."
        text_concise += f' {word.russian}'

    return text_concise


def render_word_meaning_sbs(word: DpsWord) -> str:
    text_concise = f'{word.pali}.'

    if word.pos != '':
        text_concise += f"{word.pos}."

    if word.sbs_meaning != '':
        text_concise += f" {word.sbs_meaning}"

    if word.sbs_meaning == '':
        text_concise += f" {word.meaning}"

    return text_concise
