import pickle
import re
import shutil
import os
import json

from datetime import date
from helpers import DpdWord
from timeis import timeis, white, yellow, green, line, tic, toc
from helpers import DpdWord, get_resource_paths, parse_data_frames
from html_components import render_word_meaning
from zipfile import ZipFile, ZIP_DEFLATED

def generate_tpp_data():
	rsc = get_resource_paths()
	data = parse_data_frames(rsc)
	today = date.today()

	print(f"{timeis()} {yellow}generate tpp data")
	print(f"{timeis()} {line}")
	print(f"{timeis()} {green}generating dpd data for tpp")

	# the big for loop

	df = data['words_df']
	df_length = data['words_df'].shape[0]

	f = open("output/dpd-for-tpp.js", "w")
	f.write("var pe9 = {\n")

	all_headwords_clean = []
	
	for row in range(df_length):  # df_length
		w = DpdWord(df, row)

		all_headwords_clean.append(w.pali_clean)

		if row % 5000 == 0 or row % df_length == 0:
			print(f"{timeis()} {row}/{df_length}\t{w.pali}")
		
		# headword
		html_string = f"""<span class="dpd">{w.pali}</span>"""
		html_string += "<body>"
		r = render_word_meaning(w)
		html_string += r['html']
		html_string = re.sub("""<span class\\="g.+span>""", "", html_string)

		# no meaning in context
		if w.meaning == "":
			html_string = re.sub(fr'<div class="content"><p>', fr'<div class="dpd"><p class = "dpd"><b>• {w.pali}</b>: ', html_string)
		
		# has meaning in context
		if w.meaning != "":
			html_string = re.sub(fr'<div class="content"><p>', fr'<div class="dpd"><details class="dpd"><summary class="dpd"><b>{w.pali}</b>: ', html_string)
			html_string = re.sub(fr'</p></div>', fr'</summary>', html_string)

			# grammar
			html_string += f"""<table class="dpdtable"><tr><th>Pāḷi</th><td>{w.pali2}</td></tr>"""
			html_string += f"""<tr><th>Grammar</th><td>{w.grammar}"""

			if w.neg != "":
				html_string += f""", {w.neg}"""

			if w.verb != "":
				html_string += f""", {w.verb}"""

			if w.trans != "":
				html_string += f""", {w.trans}"""

			if w.case != "":
				html_string += f""", {w.trans}"""

			html_string += f"""</td></tr>"""
			html_string += f"""<tr><th>Meaning</th><td><b>{w.meaning}</b>"""

			if w.lit != "":
				html_string += f"""; lit. {w.lit}"""
			html_string += f"""</td></tr>"""

			if w.root != "":
				html_string += f"""<tr><th>Root</th><td>{w.root_clean}<sup>{w.root_verb}</sup>{w.root_grp} {w.root_sign} ({w.root_meaning})</td></tr>"""

			if w.root_in_comps != "" and w.root_in_comps != "0":
				html_string += f"""<tr><th>√ in comps</th><td>{w.root_in_comps}</td></tr>"""

			if w.base != "":
				html_string += f"""<tr><th>Base</th><td>{w.base}</td></tr>"""

			if w.construction != "":
				html_string += f"""<tr><th>Construction</th><td>{w.construction}</td></tr>"""
				construction_text = re.sub("<br/>", ", ", w.construction)

			if w.derivative != "":
				html_string += f"""<tr><th>Derivative</th><td>{w.derivative} ({w.suffix})</td></tr>"""

			if w.pc != "":
				html_string += f"""<tr><th>Phonetic</th><td>{w.pc}</td></tr>"""

			if w.comp != "" and re.findall(r"\d", w.comp) == []:
				html_string += f"""<tr><th>Compound</th><td>{w.comp} ({w.comp_constr})</td></tr>"""

			if w.ant != "":
				html_string += f"""<tr><th>Antonym</th><td>{w.ant}</td></tr>"""

			if w.syn != "":
				html_string += f"""<tr><th>Synonym</th><td>{w.syn}</td></tr>"""

			if w.var != "":
				html_string += f"""<tr><th>Variant</th><td>{w.var}</td></tr>"""

			if w.comm != "":
				html_string += f"""<tr><th>Commentary</th><td>{w.comm}</td></tr>"""

			if w.notes != "":
				html_string += f"""<tr><th>Notes</th><td>{w.notes}</td></tr>"""

			if w.cognate != "":
				html_string += f"""<tr><th>Cognate</th><td>{w.cognate}</td></tr>"""

			if w.link != "":
				html_string += f"""<tr><th>Link</th><td><a class ="dpdlink" href="{w.link}">{w.link}</a></td></tr>"""

			if w.non_ia != "":
				html_string += f"""<tr><th>Non IA</th><td>{w.non_ia}</td></tr>"""

			if w.sk != "":
				html_string += f"""<tr><th>Sanskrit</th><td><i>{w.sk}</i></td></tr>"""

			sk_root_mn = re.sub("'", "", w.sk_root_mn)
			if w.sk_root != "":
				html_string += f"""<tr><th>Sanskrit Root</th><td><i>{w.sk_root} {w.sk_root_cl} ({sk_root_mn})</i></td></tr>"""


			html_string += f"""<tr><td colspan="2"><p class="dpdspam">✎ <a class="dpdlink" href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.1433863141=TPP {today}" target="_blank">Submit a correction</a></p></td></tr>"""
			html_string += f"""</table>"""
			html_string += f"""</details></div>"""

		html_string = re.sub("'", "’", html_string)
		f.write(f"""'{w.pali}':'{html_string}',\n""")

	# add roots
	print(f"{timeis()} {green}generating roots data")
	
	roots_df = data['roots_df']
	roots_df_length = len(roots_df)

	for row in range(roots_df_length):

		html_string = ""
		root_count = roots_df.iloc[row, 1]
		root = roots_df.iloc[row, 2]
		root_clean = re.sub(" \\d.*$", "", root)
		root_no_sign = re.sub("√", "", root_clean)
		root_ = "_" + re.sub(" ", "_", root)
		root_ = re.sub("√", "", root_)
		root_has_verb = roots_df.iloc[row, 4]
		root_group = roots_df.iloc[row, 5]
		root_sign = roots_df.iloc[row, 6]
		root_meaning = roots_df.iloc[row, 8]
		root_meaning_ = re.sub(",", "", root_meaning)
		root_meaning_ = re.sub(" ", "_", root_meaning_)

		if root_count != "0":
			html_string += f"""'{root}':'"""
			html_string += f"""<span class="dpdroot">{root_clean}</span><body><div class="dpdroot"><table class="dpdroot">"""
			html_string += f"""<tr><th>{root_clean}</th><td><sup>{root_has_verb}</sup>{root_group} {root_sign} ({root_meaning})</td></tr>"""
			html_string += f"""</table></div>',\n"""
			f.write(f"""{html_string}""")

	# sandhi splitter
	print(f"{timeis()} {green}generating sandhi for tpr")
	
	with open("../inflection generator/output/sandhi dict", "rb") as pf:
		sandhi_dict = pickle.load(pf)
		
	for key, value in sandhi_dict.items():
		key_clean = re.sub(" \\d.*$", "", key)
		# key_clean = re.sub('\\/', "", key_clean)
		# value = json.dumps(value, ensure_ascii=False)
		if key_clean not in all_headwords_clean:
			html_string = f"""<span class="dpd">{key_clean}</span>"""
			html_string += f"""<body><div class ="dpd"><p class="dpd">{value}</p></div>"""
			f.write(f"""'{key_clean}':'{html_string}',\n""")

	f.write("};")
	f.close()

	with ZipFile('share/dpd-for-tpp.zip', 'w', ZIP_DEFLATED) as zipfile:
		zipfile.write("output/dpd-for-tpp.js", "pe9_dpd.js")
		# zipfile.write("output/dpd-for-tpp.css", "dpd.css")
		zipfile.write("../inflection generator/output/inflection to headwords dict.tsv",
		              "dpd_inflections_to_headwords.tsv")


def copy_file_to_tpp_folder():
	print(f"{timeis()} {green}copying json")
	shutil.copy(
		"output/dpd-for-tpp.js",
	    "output/pe9_dpd.js")
	shutil.move(
		"output/pe9_dpd.js",
	    "../Tipitaka-Pali-Projector/tipitaka_projector_data/dictionary/pe9_dpd.js")
	shutil.copy(
		"../inflection generator/output/inflection to headwords dict.tsv",
	    "../Tipitaka-Pali-Projector/tipitaka_projector_data/dictionary/dpd_inflections_to_headwords.tsv")


def update_preferences_info():
	print(f"{timeis()} {green}getting file info")

	# get filesize

	filestat = os.stat('output/dpd-for-tpp.js')
	filesize = f"{filestat.st_size/1000/1000:.1f}"
	print(f"{timeis()} {green}filezise {white}{filesize} MB")

	# get number of lines

	with open('output/dpd-for-tpp.js')as f:
		readme = f.read()
		linecounter = len(re.findall("\n", readme))-1
	print(f"{timeis()} {green}lines {white}{linecounter}")

	# write to file

	f = open("output/preferences.single.page.js", "r")
	text = f.read()
	text = re.sub(f"""PE9: \\[\\d.*entries - \\d*\\.\\d """,
	              fr"""PE9: [{linecounter:,} entries - {filesize} """, text)
	f.close()
	f = open("output/preferences.single.page.js", "w")
	f.write(text)
	f.close()

	# copy file
	print(f"{timeis()} {green}copying preferences")
	shutil.copy("output/preferences.single.page.js",
	            "../Tipitaka-Pali-Projector/tipitaka_projector_data/js/preferences.single.page.js")


if __name__ == "__main__":
	tic()
	generate_tpp_data()
	copy_file_to_tpp_folder()
	update_preferences_info()
	toc()
