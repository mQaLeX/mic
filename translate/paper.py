import GoogleTrans

def rmet(str):
    prgs = str.split('.\n')
    rt = ''
    for prg in prgs:
        rt += prg.replace('\r', '').replace('\n', ' ')
        rt += '.\n\n'
    return rt[:-3]

with open('paper.txt', 'r') as f:
    textList = rmet(f.read()).split('\n\n')

wf = open('paper-zh.txt', 'w')

for text in textList:
    _, _, targetText, _ = GoogleTrans.GoogleTrans().query(text, lang_to='zh-CN')
    wf.write(targetText)
    wf.write('\n\n')

wf.close()