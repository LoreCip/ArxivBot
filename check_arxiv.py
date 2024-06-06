import os
import urllib.request
import re
from datetime import datetime


URLS = ["https://arxiv.org/list/astro-ph/new", "https://arxiv.org/list/gr-qc/new"]
LBLS = ["AstroPH", "GRQC"]
KEYWORDS = ["Numerical relativity", "Full general relativity", "GRMHD", 
            "Einstein Toolkit", "Lorene", "Fuka", "GRHydro", "Cactus",
            "Binary Neutron Star", "BNS", "BBH", "Binary black holes"]
KEYAUTHORS = ["Bernuzzi", "De Pietri", "Dietrich", "Tootle", "Rezzolla", "Perego"]

OUT_PATH = "/set/a/path"

def extract_arxiv_number(text):
    pattern = r'arXiv:(\d{4}\.\d{5})'
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None

def extract_title(text):
    return text.strip()

def extract_authors(text):
    pattern = r'<a href="https://arxiv.org/search/[^"]*\?searchtype=author&amp;query=[^"]+">([^<]+)</a>'
    match = re.findall(pattern, text)
    if len(match) > 0:
        return match
    return None

def extract_subjects(text):
    pattern = r'<span class="primary-subject">([^<]+)<\/span>(?:; ([^;]+))*'
    matches = re.findall(pattern, text)
    if matches:
        primary_subject = matches[0][0]
        secondary_subjects = [match.strip() for match in re.findall(r'; ([^;]+)', text)]
        return [primary_subject, *secondary_subjects]
    return None

def extract_abstract(text):
    return text.strip()

def pageParser(page):
    out = {}

    i = 0
    j = 0
    while i < len(page):
        number = extract_arxiv_number(page[i].decode('utf-8'))
        if number is None:
            i += 1
            continue

        while "Title:" not in page[i].decode('utf-8'):
            i += 1
        i += 1
        title = extract_title(page[i].decode('utf-8'))

        while "\'list-authors\'" not in page[i].decode('utf-8'):
            i += 1
        authors = extract_authors(page[i].decode('utf-8'))

        while "Subjects:" not in page[i].decode('utf-8'):
            i += 1
        i += 1
        subjects = extract_subjects(page[i].decode('utf-8'))

        while "<p class='mathjax'>" not in page[i].decode('utf-8'):
            i += 1
        i += 1
        abstract = extract_abstract(page[i].decode('utf-8'))

        checkTitle = [kw.casefold() in title.casefold() for kw in KEYWORDS] 
        checkAbstr = [kw.casefold() in abstract.casefold() for kw in KEYWORDS] 
        checkAutho = [au.casefold() in ka.casefold() for au in authors for ka in KEYAUTHORS] 

        if any(checkTitle) or any(checkAbstr) or any(checkAutho):
            out[j] = {}
            out[j]['number']   = number
            out[j]['title']    = title
            out[j]['authors']  = authors
            out[j]['subjects'] = subjects
            out[j]['abstract'] = abstract

            j += 1
        i += 1

    return out

# Get papers
papers = {}
for url, lbl in zip(URLS, LBLS):
    f = urllib.request.urlopen(url)
    content = f.read().split(b"\n")
    papers[lbl] = pageParser(content)

# Remove duplicates
already_in = set()
to_remove = set()
for lbl in papers.keys():
    keys = papers[lbl].keys()
    for k in keys:
        if papers[lbl][k]['number'] not in already_in:
            already_in.add(papers[lbl][k]['number'])
        else:
            to_remove.add((lbl, k))

for lbl, k in to_remove:
    del papers[lbl][k]

# Print output to file
total_len = 64
fstring = ""
for lbl in papers.keys():
    keys = papers[lbl].keys()
    
    if len(keys) == 0:
        continue

    lbl_len = len(lbl)
    ws = (total_len-lbl_len) // 2

    fstring +=  f"#" * total_len + "\n"
    fstring += f"{lbl:^64}\n"
    fstring += f"#" * total_len + "\n"
    fstring += "\n\n"
    for k in keys:

        fstring += f"{papers[lbl][k]['title'].strip()}\n"
        fstring += ", ".join([subj.strip() for subj in papers[lbl][k]['subjects']]) + "\n\n"

        fstring += ", ".join([author.strip() for author in papers[lbl][k]['authors']]) + "\n\n"
        fstring += f"{papers[lbl][k]['abstract'].strip()}\n\n\n"

        fstring += f"-" * total_len + "\n\n"

    fstring += "\n\n"

today = datetime.now().strftime("%Y_%m_%d")

os.makedirs(OUT_PATH, exist_ok=True)
name = os.path.join(OUT_PATH, f"{today}_Arxiv.txt")
with open(name, "w") as f:
    f.write(fstring)