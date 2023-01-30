import os
from os import times
import pickle
import re
import sqlite3
import pandas as pd
import json

from datetime import date
from helpers import DpdWord
from timeis import timeis, white, yellow, green, red, line, tic, toc
from helpers import DpdWord, get_resource_paths, parse_data_frames
from html_components import render_word_meaning
from zipfile import ZipFile, ZIP_DEFLATED

def generate_tpr_data():
	rsc = get_resource_paths()
	data = parse_data_frames(rsc)
	today = date.today()

	print(f"{timeis()} {yellow}generate tpr data")
	print(f"{timeis()} {line}")
	print(f"{timeis()} {green}generating dpd data for tpr")

	# the big for loop

	df = data['words_df']
	df_length = data['words_df'].shape[0]

	f = open("output/dpd-for-tpr.tsv", "w")
	f.write(f"word\tdefinition\tbook_id\n")

	all_headwords_clean = []

	for row in range(df_length):  # df_length
		w = DpdWord(df, row)

		all_headwords_clean.append(w.pali_clean)

		if row % 5000 == 0 or row % df_length == 0:
			print(f"{timeis()} {row}/{df_length}\t{w.pali}")
		
		# headword
		html_string = ""
		r = render_word_meaning(w)
		html_string += r['html']
		html_string = re.sub("""<span class\\="g.+span>""", "", html_string)

		# no meaning in context
		if w.meaning == "":
			html_string = re.sub(fr'<div class="content"><p>', fr'<div><p><b>• {w.pali}</b>: ', html_string)

		# has meaning in context
		if w.meaning != "":
			html_string = re.sub(fr'<div class="content"><p>', fr'<div><details><summary><b>{w.pali}</b>: ', html_string)
			html_string = re.sub(fr'</p></div>', fr'</summary>', html_string)

			# grammar
			html_string += f"""<table><tr><th valign="top">Pāḷi</th><td>{w.pali2}</td></tr>"""
			html_string += f"""<tr><th valign="top">Grammar</th><td>{w.grammar}"""

			if w.neg != "":
				html_string += f""", {w.neg}"""

			if w.verb != "":
				html_string += f""", {w.verb}"""

			if w.trans != "":
				html_string += f""", {w.trans}"""

			if w.case != "":
				html_string += f""", {w.trans}"""

			html_string += f"""</td></tr>"""
			html_string += f"""<tr><th valign="top">Meaning</th><td><b>{w.meaning}</b>. """

			if w.lit != "":
				html_string += f"""lit. {w.lit}"""
			html_string += f"""</td></tr>"""

			if w.root != "":
				html_string += f"""<tr><th valign="top">Root</th><td>{w.root_clean} {w.root_grp} {w.root_sign} ({w.root_meaning})</td></tr>"""

			if w.root_in_comps != "" and w.root_in_comps != "0":
				html_string += f"""<tr><th valign="top">√ in comps</th><td>{w.root_in_comps}</td></tr>"""

			if w.base != "":
				html_string += f"""<tr><th valign="top">Base</th><td>{w.base}</td></tr>"""

			if w.construction != "":
				# <br/> is causing an extra line, replace with div
				construction_no_br = re.sub("(<br\\/>)(.+)", "<div>\\2</div>", w.construction)
				html_string += f"""<tr><th valign="top">Construction</th><td>{construction_no_br}</td></tr>"""

			if w.derivative != "":
				html_string += f"""<tr><th valign="top">Derivative</th><td>{w.derivative} ({w.suffix})</td></tr>"""

			if w.pc != "":
				html_string += f"""<tr><th valign="top">Phonetic</th><td>{w.pc}</td></tr>"""

			if w.comp != "" and re.findall(r"\d", w.comp) == []:
				comp_constr_no_formatting = re.sub("<b>|<\\/b>|<i>|<\\/i>", "", w.comp_constr)
				html_string += f"""<tr><th valign="top">Compound</th><td>{w.comp} ({comp_constr_no_formatting})</td></tr>"""

			if w.ant != "":
				html_string += f"""<tr><th valign="top">Antonym</th><td>{w.ant}</td></tr>"""

			if w.syn != "":
				html_string += f"""<tr><th valign="top">Synonym</th><td>{w.syn}</td></tr>"""

			if w.var != "":
				html_string += f"""<tr><th valign="top">Variant</th><td>{w.var}</td></tr>"""

			if w.comm != "":
				commentary_no_formatting = re.sub("<b>|<\\/b>|<i>|<\\/i>", "", w.comm)
				commentary_no_formatting = re.sub("<br\\/>", " ", commentary_no_formatting)
				html_string += f"""<tr><th valign="top">Commentary</th><td>{commentary_no_formatting}</td></tr>"""

			if w.notes != "":
				notes_no_formatting = re.sub("<b>|<\\/b>|<i>|<\\/i>", "", w.notes)
				notes_no_formatting = re.sub("<br\\/>", ". ", notes_no_formatting)
				html_string += f"""<tr><th valign="top">Notes</th><td>{notes_no_formatting}</td></tr>"""

			if w.cognate != "":
				html_string += f"""<tr><th valign="top">Cognate</th><td>{w.cognate}</td></tr>"""

			if w.link != "":
				link_no_br = re.sub("<br\\/>", " ", w.link)
				html_string += f"""<tr><th valign="top">Link</th><td><a href="{w.link}">{link_no_br}</a></td></tr>"""

			if w.non_ia != "":
				html_string += f"""<tr><th valign="top">Non IA</th><td>{w.non_ia}</td></tr>"""

			if w.sk != "":
				html_string += f"""<tr><th valign="top">Sanskrit</th><td>{w.sk}</td></tr>"""

			sk_root_mn = re.sub("'", "", w.sk_root_mn)
			if w.sk_root != "":
				html_string += f"""<tr><th valign="top">Sanskrit Root</th><td>{w.sk_root} {w.sk_root_cl} ({sk_root_mn})</td></tr>"""


			html_string += f"""<tr><td colspan="2"><a href="https://docs.google.com/forms/d/e/1FAIpQLSf9boBe7k5tCwq7LdWgBHHGIPVc4ROO5yjVDo1X5LDAxkmGWQ/viewform?usp=pp_url&entry.438735500={w.pali}&entry.1433863141=TPR {today}" target="_blank">Submit a correction</a></td></tr>"""
			html_string += f"""</table>"""
			html_string += f"""</details></div>"""

		html_string = re.sub("'", "’", html_string)
		f.write(f"""{w.pali}\t<p>{html_string}</p>\t11\n""")

	# add roots
	print(f"{timeis()} {green}generating roots data")
	
	roots_df = data['roots_df']
	filter = roots_df["Count"] != "0"
	roots_df = roots_df[filter]

	roots_df_length = len(roots_df)
	html_string = ""
	new_root = True

	for row in range(roots_df_length):
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
			if new_root:
				html_string += f"""<div><p>"""
			html_string += f"""<b>{root_clean}</b> {root_group} {root_sign} ({root_meaning})"""

			try:
				next_root = roots_df.iloc[row+1, 2]
				next_root = re.sub(" \\d.*$", "", next_root)
			except:
				next_root = ""
			if root_clean == next_root:
				html_string += "<br>"
				new_root = False
			else:
				html_string += f"""</div>"""
				f.write(f"""{root}\t<p>{html_string}<p>\t11\n""")
				html_string = ""
				new_root = True


	# sandhi splitter
	print(f"{timeis()} {green}generating sandhi for tpr")
	
	with open("../inflection generator/output/sandhi dict", "rb") as pf:
		sandhi_dict = pickle.load(pf)
		
	for key, value in sandhi_dict.items():
		key_clean = re.sub(" \\d.*$", "", key)
		if key_clean not in all_headwords_clean:
			value_clean = re.sub("<br>", "<div>", value)
			value_clean = re.sub(fr"<i>|</i>", "", value_clean)
			html_string = f"""<div><p>{value_clean}</p></div>"""
			f.write(f"""{key_clean}\t<p>{html_string}</p>\t11\n""")

	f.close()

	print(f"{timeis()} {green}zipping files", end=" ")

	try:
		with ZipFile('share/dpd-for-tpr.zip', 'w', ZIP_DEFLATED) as zipfile:
			zipfile.write("output/dpd-for-tpr.tsv", "dpd.tsv")
			zipfile.write("../inflection generator/output/inflection to headwords dict.tsv",
						"dpd_inflections_to_headwords.tsv")
		print(f"{white}ok")
	
	except:
		print(f"{red} an error occurred zipping")


def copy_to_sqlite_db():
	print(f"{timeis()} {green}copying data to tpr db", end=" ")

	try:
		conn = sqlite3.connect(
			'../../../../.local/share/tipitaka_pali_reader/tipitaka_pali.db')
		c = conn.cursor()

		# dpd table
		c.execute("DROP TABLE if exists dpd")
		c.execute("CREATE TABLE dpd (word, definition, book_id)")
		dpd = pd.read_csv(
			"../exporter/output/dpd-for-tpr.tsv", 
			sep="\t")
		dpd.to_sql('dpd', conn, if_exists='append', index=False)

		# dpd_inflections_to_headwords
		c.execute("DROP TABLE if exists dpd_inflections_to_headwords")
		c.execute("CREATE TABLE dpd_inflections_to_headwords (inflection, headwords)")
		dpd_inflections_to_headwords = pd.read_csv(
			"../inflection generator/output/inflection to headwords dict.tsv",
			sep="\t")
		dpd_inflections_to_headwords.to_sql(
			'dpd_inflections_to_headwords',
			conn,
			if_exists='append',
			index=False)
		print(f"{white}ok")

	except:
		print(f"{red} an error occurred copying to db")

	return dpd, dpd_inflections_to_headwords


def tpr_updater():
	print(f"{timeis()} {green}making tpr updater")

	# Open a file to write the exported data to
	with open("output/dpd.sql", "w") as f:
		f.write("BEGIN TRANSACTION;\n")
		f.write("DELETE FROM dpd_inflections_to_headwords;\n")
		f.write("DELETE FROM dpd;\n")
		f.write("COMMIT;\n")
		f.write("BEGIN TRANSACTION;\n")

		print(f"{timeis()} {green}writing inflections to headwords")

		for row in range(len(dpd_inflections_to_headwords)):
			inflection = dpd_inflections_to_headwords.iloc[row, 0]
			headword = dpd_inflections_to_headwords.iloc[row, 1]
			headword = headword.replace("'", "''")
			if row % 50000 == 0:
				print(f"{timeis()} {row}/{len(dpd_inflections_to_headwords)}\t{inflection}")
			f.write(f"""INSERT INTO "dpd_inflections_to_headwords" ("inflection", "headwords") VALUES ('{inflection}', '{headword}');\n""")
		
		print(f"{timeis()} {green}writing dpd")

		for row in range(len(dpd_tsv_df)):
			word = dpd_tsv_df.iloc[row, 0]
			definition = dpd_tsv_df.iloc[row, 1]
			definition = definition.replace("'", "''")
			book_id = dpd_tsv_df.iloc[row, 2]
			if row % 5000 == 0:
				print(f"{timeis()} {row}/{len(dpd_tsv_df)}\t{word}")
			f.write(f"""INSERT INTO "dpd" ("word","definition","book_id") VALUES ('{word}', '{definition}', {book_id});\n""")
			
		f.write("COMMIT;\n")

def zip_it_up():

	file_path = os.path.join("output", "dpd.sql")
	file_name = os.path.basename(file_path)
	with ZipFile('share/dpd.zip', 'w', ZIP_DEFLATED) as zipfile:
		zipfile.write(file_path, file_name)



if __name__ == "__main__":
	tic()
	generate_tpr_data()
	dpd_tsv_df, dpd_inflections_to_headwords = copy_to_sqlite_db()
	tpr_updater()
	zip_it_up()
	toc()
