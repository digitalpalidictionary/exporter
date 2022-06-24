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
from timeis import timeis, yellow, green, blue, line, tic, toc

from helpers import DataFrames, DpdWord, ResourcePaths, get_resource_paths, parse_data_frames
from html_components import render_header_tmpl, render_feedback_tmpl, render_word_meaning
from zipfile import ZipFile, ZIP_DEFLATED

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

	with open("output/dpd-for-tpp.js", "w") as f:
		f.write("var pv1 = {\n")
	
	f = open("output/dpd-for-tpp.js", "a")

	for row in range(df_length): #df_length

		w = DpdWord(df, row)
		pali_clean = re.sub(" \d*$", "", w.pali)

		if row % 5000 == 0 or row % df_length == 0:
			print(f"{timeis()} {row}/{df_length}\t{w.pali}")

		html_string = f"""<span class="dpd">{w.pali}</span>"""
		html_string += "<body>"
		r = render_word_meaning(w)
		html_string += r['html']
        
		# all headwords list
		all_headwords_clean = []
		all_headwords_clean.append(w.pali_clean)

		# grammar

		if w.meaning == "":
			html_string = re.sub(fr'<div class="content"><p>', fr'<div class="dpd"><p class = "dpd">', html_string)
			
		if w.meaning != "":

			html_string = re.sub(fr'<div class="content"><p>', fr'<div class="dpd"><details class="dpd"><summary class="dpd">', html_string)
			html_string = re.sub(fr'</p></div>', fr'</summary>', html_string)

			html_string += f"""<table class="dpdtable"><tr><th>Pāḷi</th><td>{w.pali2}</td></tr>"""
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
				html_string += f"""<tr valign="top"><th>Link</th><td><a class ="dpdlink" href="{w.link}">{w.link}</a></td></tr>"""

			if w.non_ia != "":
				html_string += f"""<tr valign="top"><th>Non IA</th><td>{w.non_ia}</td></tr>"""

			if w.sk != "":
				html_string += f"""<tr valign="top"><th>Sanskrit</th><td><i>{w.sk}</i></td></tr>"""

			sk_root_mn = re.sub("'", "", w.sk_root_mn)
			if w.sk_root != "":
				html_string += f"""<tr valign="top"><th>Sanskrit Root</th><td><i>{w.sk_root} {w.sk_root_cl} ({sk_root_mn})</i></td></tr>"""

			html_string += f"""</table>"""
			html_string += f"""<p class="dpd">Did you spot a mistake? <a class="dpdlink" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.1433863141=GoldenDict {today}" target="_blank">Correct it here.</a></p>"""
			html_string += f"""</details></div>"""

		html_string = re.sub("'", "’", html_string)
		f.write(f"""'{w.pali}':'{html_string}',\n""")
	
	# sandhi splitter

	print(f"{timeis()} {green}generating sandhi html for tpp")
	
	with open("../inflection generator/output/sandhi dict", "rb") as pf:
		sandhi_dict = pickle.load(pf)
		
	for key, value in sandhi_dict.items():
		key_clean = re.sub(" \d*$", "", key)
		if key_clean not in all_headwords_clean:
			html_string = f"""<span class="dpdsandhi">{key_clean}</span>"""
			html_string += f"""<body><div class ="dpdsandhi"><p class="dpdsandhi">{value}</p></div>"""
			f.write(f"""'{key_clean}':'{html_string}',\n""")

	# add roots

	print(f"{timeis()} {green}generating roots html for tpp")

	roots_df = data['roots_df']
	roots_df_length = len(roots_df)
	last_root = ""

	for row in range(roots_df_length):
		
		html_string = ""
		root_count = roots_df.iloc[row,1]
		root = roots_df.iloc[row, 2]
		root_clean = re.sub("√", "", root)
		root_ = "_" + re.sub(" ", "_", root)
		root_ = re.sub("√", "", root_)
		root_has_verb = roots_df.iloc[row, 4]
		root_group = roots_df.iloc[row, 5]
		root_sign = roots_df.iloc[row, 6]
		root_meaning = roots_df.iloc[row, 8]
		root_meaning_ = re.sub(",", "", root_meaning)
		root_meaning_ = re.sub(" ", "_", root_meaning_)

		if root_count != "0":		
			if root != last_root and row == 0:
				f.write(f"""'{root_clean}':'""")
				html_string +=f"""<span class="dpdroot">{root}</span><body><div class="dpdroot"><table class="dpdroot">"""

			if root != last_root and row != 0:
				f.write(f"""</table></div></body>',\n""")
				f.write(f"""'{root_clean}':'""")
				html_string += f"""<span class="dpdroot">{root}</span><body><div class="dpdroot"><table class="dpdroot">"""

			html_string += f"""<tr><th>{root}</th><td><sup>{root_has_verb}</sup>{root_group} {root_sign} ({root_meaning})</td></tr>"""

			f.write(f"""{html_string}""")
			last_root = root

	f.write(f"""</table></div></body>'\n""")

	f.write("""};""")
	f.close()
	
	with ZipFile('share/dpd-for-tpp.zip', 'w', ZIP_DEFLATED) as zipfile:
		zipfile.write("output/dpd-for-tpp.js", "Digital_Pāḷi_Dicitonary.js")
		zipfile.write("output/dpd-for-tpp.css", "dpd.css")
		zipfile.write("../inflection generator/output/inflection to headwords dict.csv", "dpd_inflections_to_headwords.csv")


def copy_file_to_tpp_folder():
	print(f"{timeis()} {green}file management")
	os.popen('code "output/dpd-for-tpp.js"')
	shutil.copy("output/dpd-for-tpp.js", "output/pv1_Pali_Viet_Dictionary_by_ngaiBuuChon_stardict.js")
	shutil.move("output/pv1_Pali_Viet_Dictionary_by_ngaiBuuChon_stardict.js", "/home/bhikkhu/git/Tipitaka-Pali-Projector/tipitaka_projector_data/dictionary/pv1_Pali_Viet_Dictionary_by_ngaiBuuChon_stardict.js")
	os.popen('nemo "/home/bhikkhu/git/Tipitaka-Pali-Projector/tipitaka_projector_data/dictionary"')
	os.popen('code "/home/bhikkhu/git/Tipitaka-Pali-Projector/tipitaka_projector_data/js/preferences.single.page.js"')


tic()
generate_tpp_html()
copy_file_to_tpp_folder()
toc()
