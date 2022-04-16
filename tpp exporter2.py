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

	print(f"{timeis()} {yellow}generate tpp html and json")
	print(f"{timeis()} {line}")
	print(f"{timeis()} {green}generating dpd html for tpp")

	# the big for loop

	df = data['words_df']
	df_length = data['words_df'].shape[0]

	# with open(rsc['tpp_css_path'], 'r') as f:
	with open("assets/tpp2.css", "r") as f:
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

		if w.meaning == "":
			html_string = re.sub(fr'<div class="content"><p>', fr'<div class="content"><details><p><summary>', html_string)
			html_string = re.sub(fr'\[under construction\]</p></div>', fr'</p></summary><table class = "table1"><tr><td>[under construction]</td></tr></table></details></div>', html_string)
			
		if w.meaning != "":

			html_string = re.sub(fr'<div class="content"><p>', fr'<div class="content"><details><p><summary>', html_string)
			html_string = re.sub(fr'</p></div>', fr'</p></summary>', html_string)

			html_string += f"""<table class = "table1"><tr><th>Pāḷi</th><td>{w.pali2}</td></tr>"""
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
			html_string += f"""</details></div>"""

		html_string = re.sub("'", "’", html_string)
		f.write(f"""'{pali_clean}':'{w.pali}{html_string}',\n""")

	# add roots

	print(f"{timeis()} {green}generating roots html for tpp")

	roots_df = data['roots_df']
	roots_df_length = len(roots_df)

	with open("assets/tpp-roots.css", "r") as fr:
		tpp_roots_css = fr.read()

	f = open("output/tpp.js", "a")

	for row in range(roots_df_length):
		
		html_string = ""
		root_count = roots_df.iloc[row,1]
		root = roots_df.iloc[row, 2]
		root_clean = re.sub("√", "", root)
		root_ = "_" + re.sub(" ", "_", root)
		root_ = re.sub("√", "", root_)
		root_in_comps = roots_df.iloc[row, 3]
		root_has_verb = roots_df.iloc[row, 4]
		root_group = roots_df.iloc[row, 5]
		root_sign = roots_df.iloc[row, 6]
		root_meaning = roots_df.iloc[row, 8]
		root_meaning_ = re.sub(",", "", root_meaning)
		root_meaning_ = re.sub(" ", "_", root_meaning_)
		root_id = root_group + "_" + root_meaning_

		if root_count != "0":		

			html_string += f"{tpp_roots_css}<body>"
			html_string += f"""<div class="root_content"><p>root. <b>{root}</b><sup>{root_has_verb}</sup>{root_group} {root_sign} ({root_meaning})</p></div>"""

			f.write(f"""'{root_clean}':'{root}{html_string}',\n""")
	
	f.write("""};""")
	f.close()
	os.popen('code "output/tpp.js"')

def copy_file_to_tpp_folder():
	print(f"{timeis()} {green}file management") 
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

