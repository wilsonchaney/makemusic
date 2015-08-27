import os

PATH = "/media/wilson/DATA//Dropbox/Dev/python/algo_composition"

def addToClipBoard(text):
    command = 'echo ' + text.strip() + '| clip'
    os.system(command)

def count_lines():
    result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(PATH) for f in filenames if os.path.splitext(f)[1] == '.py']
    return sum([file_len(file) for file in result])
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

print count_lines()

