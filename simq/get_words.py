import re

URL_REGEX = re.compile(r"(https?:\/\/[^ )]+)", re.MULTILINE)

def get_words(string):
    string = clean_str(string)
    return string.split(" ")

def clean_str(string):
    # learn from https://github.com/yoonkim/CNN_sentence/blob/master/process_data.py
    string = URL_REGEX.sub("URL", string)
    string = re.sub(r"[^A-Za-z0-9\.(),!?\']", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r"\.", " . ", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " ( ", string)
    string = re.sub(r"\)", " ) ", string)
    string = re.sub(r"\?", " ? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower()