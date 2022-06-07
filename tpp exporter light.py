import re
import pandas as pd
import os
import shutil

from datetime import date
from helpers import DpdWord
from timeis import timeis, yellow, green, blue, line
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from helpers import DpdWord, get_resource_paths, parse_data_frames

def generate_tpp_html():
	rsc = get_resource_paths()

	data = parse_data_frames(rsc)
	today = date.today()

	print(f"{timeis()} {yellow}generate tpp html and json")
	print(f"{timeis()} {line}")
	print(f"{timeis()} {green}generating dpd light html for tpp")

	# the big for loop

	df = data['words_df']
	df_length = data['words_df'].shape[0]

	with open("assets/tpp light.css", "r") as f:
		tpp_css = f.read()

	with open("output/tpp.js", "w") as f:
		f.write("var pv1 = {\n")
	
	f = open("output/tpp.js", "a")
	
	last_headword = ""
	
	for row in range(df_length):  # df_length

		html_string = ""

		w = DpdWord(df, row)
		pali_clean = re.sub(" \d*$", "", w.pali)

		if re.findall("\d", w.pali):
			number = re.sub("(.+ )(\d*$)", "\\2", w.pali)
		else:
			number = ""
		
		if row % 5000 == 0:
			print(f"{timeis()} {row}/{df_length}\t{w.pali}")
		
		if pali_clean != last_headword and row == 0:
			f.write(f"""'{pali_clean}':'""")
			html_string += tpp_css
			html_string += f"""<span class="dpd_headword">{pali_clean}</span><body><div class="dpd"><table class="dpd">"""
		
		if pali_clean != last_headword and row != 0:
			f.write(f"""</table></div></body>',\n""")
			f.write(f"""'{pali_clean}':'""")
			html_string += tpp_css
			html_string += f"""<span class="dpd_headword">{pali_clean}</span><body><div class="dpd"><table class="dpd">"""

		# here it is

		if w.meaning == "" and number != "":
			html_string += f"""<tr><th>{number}</th><td>{w.pos}. <b>{w.buddhadatta}</b> [***]</td>"""

		elif w.meaning == "" and number == "":
			html_string += f"""<tr><td>{w.pos}. <b>{w.buddhadatta}</b> [***]</td>"""

		else:

			if number != "":
				html_string += f"""<tr><th>{number}</th><td>{w.grammar}. """
			
			if number == "":
				html_string += f"""<tr><td>{w.grammar}. """

			if w.case != "":
				html_string += f"""({w.case}) """
			
			html_string += f"""<b>{w.meaning}</b>"""

			if w.lit != "":
				html_string += f"""; lit. {w.lit}"""

			if w.base == "":
				construction_simple = re.sub(r" \[.+\] \+", "", w.construction)
				construction_simple = re.sub("> .+? ", "", construction_simple)
				construction_simple = re.sub("<br/>.+", "", construction_simple)
				if construction_simple != "":
					html_string += f""" [{construction_simple}]</td></tr>"""

			if w.base != "":
				family_plus = re.sub(" ", " + ", w.family)
				construction_oneline = re.sub("<br/>.+", "", w.construction)
				construction_truncated = re.sub(r"(.+)(\+ .{1,7}$)", "\\2", construction_oneline)
				if re.match("^na ", w.construction):
					construction_na = re.sub("^(na )(.+)$", "\\1 + ", w.construction)
				else:
					construction_na = ""

				construction_reconstructed = f"{construction_na}{family_plus} + {w.root_sign} {construction_truncated}"
				html_string += f""" [{construction_reconstructed}]</td></tr>"""
			
			if w.construction == "":
				html_string += """</td></tr>"""

		html_string = re.sub("'", "’", html_string)
		f.write(f"""{html_string}""")
		last_headword = pali_clean

	# f.write(f"""</table></div></body>'\n""")
	f.write(f"""</table></div></body>',\n""")

	# add roots

	print(f"{timeis()} {green}generating roots html for tpp")

	roots_df = data['roots_df']
	roots_df_length = len(roots_df)

	with open("assets/tpp-roots light.css", "r") as fr:
		tpp_roots_css = fr.read()

	f = open("output/tpp.js", "a")

	last_root = ""
	root_number = 0

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
			if root != last_root and row == 0:
				f.write(f"""'{root_clean}':'""")
				html_string += tpp_roots_css
				html_string += f"""<span class="dpd_root">{root}</span><body><div class="dpd_root"><table class="dpd_root">"""
			
			if root != last_root and row != 0:
				f.write(f"""</table></div></body>',\n""")
				f.write(f"""'{root_clean}':'""")
				html_string += tpp_roots_css
				html_string += f"""<span class="dpd_root">{root}</span><body><div class="dpd_root"><table class="dpd_root">"""
			
			html_string += f"""<tr><th>{root}</th><td><sup>{root_has_verb}</sup>{root_group} {root_sign} ({root_meaning})</td></tr>"""

			f.write(f"""{html_string}""")
			last_root = root
	
	f.write(f"""</table></div></body>',\n""")

	# sandhi-splitter

	print(f"{timeis()} {green}generating sandhi html for tpp")

	matches_df = pd.read_csv(
		"../inflection generator/output/sandhi/matches sorted.csv", dtype=str, sep="\t")

	sandhi_dict = {}

	for row in range(len(matches_df)):
		word = matches_df.loc[row, 'word']
		split = matches_df.loc[row, 'split']

		if word not in sandhi_dict.keys():
				sandhi_dict.update({word: [f"{split}"]})

		if word in sandhi_dict.keys() and \
			len(sandhi_dict[word]) < 5 and \
			f"{split}" not in sandhi_dict[word]:
			sandhi_dict[word].append(f"{split}")

	matches_df = pd.DataFrame(sandhi_dict.items(), dtype=str)
	matches_df.rename({0: "word", 1: "split"}, axis='columns', inplace=True)
	matches_df.astype(str)

	matches_df["split"] = matches_df["split"].str.replace("-", " + ")
	matches_df["split"] = matches_df["split"].str.replace("[", "")
	matches_df["split"] = matches_df["split"].str.replace("]", "")
	matches_df["split"] = matches_df["split"].str.replace("'", "")
	matches_df["split"] = matches_df["split"].str.replace(r", ", "<br>")
	matches_df["split"] = matches_df["split"].str.replace(", ", ",")

	with open("assets/tpp-sandhi light.css", "r") as fr:
		tpp_sandhi_css = fr.read()

	for row in range(len(matches_df)):
		html_string = ""
		sandhi = matches_df.iloc[row, 0]
		split = matches_df.iloc[row, 1]
		html_string += tpp_sandhi_css
		html_string += f"""<span class="dpd_sandhi">{sandhi}</span>"""
		html_string += f"""<body><div class="dpd_sandhi"><p class = dpd_sandhi >{split}</p></div></body>"""

		if row != len(matches_df)-1:
			html_string += f"""',\n"""
		else:
			html_string += f"""'\n"""
		
		f.write(f"""'{sandhi}':'{html_string}""")

	f.write("};")
	f.close()


def copy_file_to_tpp_folder():
	print(f"{timeis()} {green}file management")
	
	os.popen('mv "output/tpp.js" "output/pv1_Pali_Viet_Dictionary_by_ngaiBuuChon_stardict.js"')
	os.popen('mv "output/pv1_Pali_Viet_Dictionary_by_ngaiBuuChon_stardict.js" "/home/bhikkhu/git/Tipitaka-Pali-Projector/tipitaka_projector_data/dictionary/pv1_Pali_Viet_Dictionary_by_ngaiBuuChon_stardict.js"')
	os.popen('nemo "/home/bhikkhu/git/Tipitaka-Pali-Projector/tipitaka_projector_data/dictionary"')
	os.popen('code "/home/bhikkhu/git/Tipitaka-Pali-Projector/tipitaka_projector_data/dictionary/pv1_Pali_Viet_Dictionary_by_ngaiBuuChon_stardict.js"')
	os.popen('code "/home/bhikkhu/git/Tipitaka-Pali-Projector/tipitaka_projector_data/js/preferences.single.page.js"')
	print(f"{timeis()} {line}")

generate_tpp_html()
copy_file_to_tpp_folder()

