import pickle
import re
import stat
import time
import pandas as pd
import os
import shutil

from datetime import date
from datetime import datetime
from typing import TypedDict
from helpers import DpdWord
from mako.template import Template
from timeis import timeis, yellow, green, blue, line

from helpers import DataFrames, DpdWord, ResourcePaths, get_resource_paths, parse_data_frames
from html_components import render_header_tmpl, render_feedback_tmpl, render_word_meaning

def generate_tpp_html():
	rsc = get_resource_paths()

	data = parse_data_frames(rsc)
	today = date.today()

	print(f"{timeis()} {line}")
	print(f"{timeis()} {yellow}generate tpp html and json")
	print(f"{timeis()} {line}")
	print(f"{timeis()} {green}generating dpd html for tpp")

	# the big for loop

	df = data['words_df']
	df_length = data['words_df'].shape[0]

	with open(rsc['tpp_css_path'], 'r') as f:
		tpp_css = f.read()

	with open("output/tpp.js", "w") as f:
		f.write("var pv1 = {\n")
	
	f = open("output/tpp.js", "a")

	for row in range(df_length): #df_length

		w = DpdWord(df, row)
		pali_clean = re.sub(" \d*$", "", w.pali)

		if row % 5000 == 0 or row % df_length == 0:
			print(f"{timeis()} {row}/{df_length}\t{w.pali}")

		html_string = ""
		html_string += tpp_css
		html_string += "<body>"
		r = render_word_meaning(w)
		html_string += r['html']
		
		# grammar

		if w.meaning != "":
			
			html_string += f"""<input class="dpd" type="checkbox"  id="grammar{w.pali_}" /><label class = "dpd" for="grammar{w.pali_}">grammar</label>"""
			html_string += f"""<div class="content"><table class = "table1"><tr><th>Pāḷi</th><td>{w.pali2}</td></tr>"""
			html_string += f"""<tr><th>Grammar</th><td>{w.grammar}"""

			if w.neg != "":
				html_string += f""", {w.neg}"""

			if w.verb != "":
				html_string += f""", {w.verb}"""
			
			if w.trans != "":
				html_string += f""", {w.trans}"""
			
			if w.case != "":
				html_string += f""" ({w.case})"""

			html_string += f"""</td></tr>"""
			html_string += f"""<tr valign="top"><th>Meaning</th><td><b>{w.meaning}</b>"""

			if w.lit != "":
				html_string += f"""; lit. {w.lit}"""
			html_string += f"""</td></tr>"""

			if w.root != "":
				html_string += f"""<tr valign="top"><th>Root</th><td>{w.root}<sup>{w.root_verb}</sup>{w.root_grp} {w.root_sign} ({w.root_meaning})</td></tr>"""

			if w.root_in_comps != "" and w.root_in_comps != "0":
				html_string += f"""<tr valign="top"><th>√ in comps</th><td>{w.root_in_comps}</td></tr>"""

			if w.base != "":
				html_string += f"""<tr valign="top"><th>Base</th><td>{w.base}</td></tr>"""

			if w.construction != "":
				html_string += f"""<tr valign="top"><th>Construction</th><td>{w.construction}</td></tr>"""
				construction_text = re.sub("<br/>", ", ", w.construction)

			if w.derivative != "":
				html_string += f"""<tr valign="top"><th>Derivative</th><td>{w.derivative} ({w.suffix})</td></tr>"""

			if w.pc != "":
				html_string += f"""<tr valign="top"><th>Phonetic</th><td>{w.pc}</td></tr>"""
				pc_text = re.sub("<br/>", ", ", w.pc)

			if w.comp != "" and re.findall(r"\d", w.comp) == []:
				html_string += f"""<tr valign="top"><th>Compound</th><td>{w.comp} ({w.comp_constr})</td></tr>"""

			if w.ant != "":
				html_string += f"""<tr valign="top"><th>Antonym</th><td>{w.ant}</td></tr>"""

			if w.syn != "":
				html_string += f"""<tr valign="top"><th>Synonym</th><td>{w.syn}</td></tr>"""

			if w.var != "":
				html_string += f"""<tr valign="top"><th>Variant</th><td>{w.var}</td></tr>"""

			if w.comm != "":
				html_string += f"""<tr valign="top"><th>Commentary</th><td>{w.comm}</td></tr>"""
				comm_text = re.sub("<br/>", " ", w.comm)
				comm_text = re.sub("<b>", "", comm_text)
				comm_text = re.sub("</b>", "", comm_text)

			if w.notes != "":
				html_string += f"""<tr valign="top"><th>Notes</th><td>{w.notes}</td></tr>"""

			if w.cognate != "":
				html_string += f"""<tr valign="top"><th>Cognate</th><td>{w.cognate}</td></tr>"""

			if w.link != "":
				html_string += f"""<tr valign="top"><th>Link</th><td><a href="{w.link}">{w.link}</a></td></tr>"""

			if w.non_ia != "":
				html_string += f"""<tr valign="top"><th>Non IA</th><td>{w.non_ia}</td></tr>"""

			if w.sk != "":
				html_string += f"""<tr valign="top"><th>Sanskrit</th><td><i>{w.sk}</i></td></tr>"""

			sk_root_mn = re.sub("'", "", w.sk_root_mn)
			if w.sk_root != "":
				html_string += f"""<tr valign="top"><th>Sanskrit Root</th><td><i>{w.sk_root} {w.sk_root_cl} ({sk_root_mn})</i></td></tr>"""

			html_string += f"""</table>"""
			html_string += f"""<p>Did you spot a mistake? <a class="link" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.1433863141=GoldenDict {today}" target="_blank">Correct it here.</a></p>"""
			html_string += f"""</div>"""

		html_string = re.sub("'", "’", html_string)

		if row < df_length-1:
			f.write(f"""'{pali_clean}':'{w.pali}{html_string}',\n""")
		if row == df_length-1:
			f.write(f"""'{pali_clean}':'{w.pali}</b>{html_string}'\n""")

	f.write("""};""")
	f.close()
	os.popen('code "output/tpp.js"')

def copy_file_to_tpp_folder():
	print(f"{timeis()} {green} file management") 
	yn = input(f"{timeis()} copy to tpp? (y/n) {blue}")
	if yn == "y":
		shutil.copy("output/tpp.js", "output/pv1_Pali_Viet_Dictionary_by_ngaiBuuChon_stardict.js")
		shutil.move("output/pv1_Pali_Viet_Dictionary_by_ngaiBuuChon_stardict.js", "/home/bhikkhu/git/Tipitaka-Pali-Projector/tipitaka_projector_data/dictionary/pv1_Pali_Viet_Dictionary_by_ngaiBuuChon_stardict.js")
		os.popen('nemo "/home/bhikkhu/git/Tipitaka-Pali-Projector/tipitaka_projector_data/dictionary"')
		os.popen('code "/home/bhikkhu/git/Tipitaka-Pali-Projector/tipitaka_projector_data/js/preferences.single.page.js"')

	else:
		print(f"{timeis()} ok") 
	print(f"{timeis()} {line}")


generate_tpp_html()
copy_file_to_tpp_folder()

