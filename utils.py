import math
import os
import re
import urllib
import pandas as pd
import nltk

STEMMER = nltk.stem.porter.PorterStemmer()
LEMMATIZER = nltk.stem.wordnet.WordNetLemmatizer()
STOP_WORDS = nltk.corpus.stopwords.words("english")
STOP_WORDS.extend(
    'further chap sic act supplement resolution entituled entitled chapter section'.split())


class Bidict(dict):
    '''A python dict with a method to get a key from a value'''

    def get_key_from_val(self, val, default=None):
        ret = default
        keys = [k for k, v in self.items() if v == val]
        if keys:
            ret = keys[0]
        return ret


def read_file(path):
    ret = ''

    if os.path.exists(path):
        with open(path, 'rt', encoding='utf-8', errors='replace') as fh:
            ret = fh.read()

    return ret


def extract_text_from_pdf(pdf_path, use_tesseract=False):
    '''
    :param pdf_path: path to a pdf file
    :param use_tesseract: if True, OCR with tesseract;
        extract embedded text otherwise.
    :return: utf-8 string with the text content of the pdf
    '''
    if use_tesseract:
        import textract
        try:
            ret = textract.process(
                pdf_path,
                method='tesseract',
                language='eng',
                encoding='utf-8'
            )
            ret = ret.decode('utf8')
        except UnicodeDecodeError as e:
            ret = f'ERROR: {e}'
    else:
        import fitz  # this is pymupdf
        with fitz.open(pdf_path) as doc:
            ret = ''
            for page in doc:
                ret += page.getText()

    return ret


def repair_ocred_text(text):
    '''try to mend text OCRed from a PDF.'''
    ret = text

    # reunite hyphenated words (de-Syllabification)
    ret = re.sub(r'(\w)\s*-\s*(\w)', r'\1\2', ret)

    # quotation marks
    ret = ret.replace('”', '"').replace('“', '"')

    # 752 The Statutes at Large of Pennsylvania. [1808
    # 845 846 The Statutes at Large of Pennsylvania. [1808
    pattern = r'[(){}\s\d\[\]\.]+The Statutes at Large of Pennsylvania[(){}\s\d\[\]\.]+'
    # print(re.findall(pattern, ret))
    ret = re.sub(pattern, ' ', ret)

    # remove small bracketed content
    # e.g. {Section I.] (Section II, P. L.)
    pattern = r'[\[{(][^)}\]]{1,20}[)\]}]'
    # ms = re.findall(pattern, ret)
    # if ms:
    #     print('bracketed', ms)
    ret = re.sub(pattern, ' ', ret)

    # remove line breaks
    ret = re.sub(r'\s+', r' ', ret)

    return ret.strip()



def download(url, out_path):
    '''Download the resource at url into a file at out_path.
    If file exists, do nothing.
    Returns 1 if file already exists. 2 if downloaded. 0 on error.'''
    ret = 1

    if not os.path.exists(out_path):
        ret = 0
        try:
            with urllib.request.urlopen(url) as resp:
                with open(out_path, 'wb') as fh:
                    fh.write(resp.read())
                ret = 2
        except urllib.error.HTTPError as e:
            print(f"ERROR: {url} {e}")

    return ret


def write_file(path: str, content: str):
    with open(path, 'wt') as fh:
        fh.write(content)
