import sys

from pathlib import Path

import mako.exceptions
import rich

from mako.template import Template
from mako.lookup import TemplateLookup
from pandas.core.frame import Series

import helpers

from word import DpsWord


class TemplateBase:
    def __init__(self, template_path: Path):
        module_dir = Path(__file__).parent
        lookup = TemplateLookup(directories=[module_dir / 'assets/templates/'])  # TODO To rsc
        self._template = Template(filename=str(template_path), lookup=lookup)

    def _render_helper(self, **kwargs) -> str:
        try:
            return self._template.render(**kwargs)
        except Exception:  # pylint: disable=broad-except
            rich.print(f'{helpers.timeis()} [red]Template exception:')
            rich.print(mako.exceptions.text_error_template().render())
            sys.exit(1)


class HeaderTemplate(TemplateBase):
    def __init__(self):
        super().__init__('./assets/templates/header.html')

    def render(self, css: str, js='') -> str:
        return self._render_helper(css=css, js=js)


class WordTemplate(TemplateBase):
    def render(self, word: DpsWord, table_data_read: str) -> str:
        return self._render_helper(
            conjugations=helpers.CONJUGATIONS,
            declensions=helpers.DECLENSIONS,
            indeclinables=helpers.INDECLINABLES,
            table_data_read=table_data_read,
            word=word)


class AbbreviationTemplate(TemplateBase):
    def render(self, abbreviation: Series) -> str:
        return self._render_helper(abbreviation=abbreviation)
