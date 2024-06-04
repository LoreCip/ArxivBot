import urllib.request
import re
from datetime import datetime


URLS = ["https://arxiv.org/list/astro-ph/new", "https://arxiv.org/list/gr-qc/new"]
LBLS = ["AstroPH", "GRQC"]
KEYWORDS = ["Numerical relativity", "GRMHD", "Einstein Toolkit", "Lorene", "Fuka","dsr"]

def extract_arxiv_number(text):
    pattern = r'<a href ="/abs/(\d{4}\.\d{5})" title="Abstract" id="\1">'
    match = re.search(pattern, text)
    if match:
        return match.group(1), True
    return None, False

def extract_title(text):
    return text.strip()

def extract_authors(text):
    pattern = r'<a href="https://arxiv.org/search/[^"]*\?searchtype=author&amp;query=[^"]+">([^<]+)</a>'
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None

def extract_subjects(text):
    pattern = r'([\w\s-]+ \([\w-]+\))'
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None

def extract_abstract(text):
    return text.strip()

def pageParser(page):
    out = {}

    i = 0
    j = 0
    while i < len(page):
        number, exist = extract_arxiv_number(page[i].decode('utf-8'))

        if not exist:
            i = i + 1
            continue
        
        i = i + 9
        title = extract_title(page[i].decode('utf-8'))

        authors = None
        while authors is None:
            i = i + 1
            authors = extract_authors(page[i].decode('utf-8'))

        subjects = None
        while subjects is None:
            i = i + 1
            subjects = extract_subjects(page[i].decode('utf-8'))

        i = i + 4
        abstract = extract_abstract(page[i].decode('utf-8'))

        checkTitle = [kw.casefold() in title.casefold() for kw in KEYWORDS] 
        checkAbstr = [kw.casefold() in abstract.casefold() for kw in KEYWORDS] 
        checkAutho = [kw.casefold() in authors.casefold() for kw in KEYWORDS] 

        if any(checkTitle) or any(checkAbstr) or any(checkAutho):
            out[j] = {}
            out[j]['number']   = number
            out[j]['title']    = title
            out[j]['authors']  = authors
            out[j]['subjects'] = subjects
            out[j]['abstract'] = abstract

            j = j + 1
        i = i + 1

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
        fstring += f"{papers[lbl][k]['subjects'].strip()}\n\n"

        fstring += f"{papers[lbl][k]['authors'].strip()}\n\n"
        fstring += f"{papers[lbl][k]['abstract'].strip()}\n\n\n"

    fstring += "\n\n"

today = datetime.now().strftime("%Y_%m_%d")
name = f"{today}_Arxiv.txt"
with open(name, "w") as f:
    f.write(fstring)