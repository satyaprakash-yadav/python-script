# Version: $Revision: 1.11 $	Released: $Date: 2022/09/07 12:20:47 $

################### MODIFY XML FILE IN PYTHON ###################

import sys
import os
import re
import time
import calendar

# cmd :- py D:\Project\SMARTEDIT\Conversion\JATS\SJ_NLM2JATS_JP_OASIS\SJS_SubArticle\AAP_SubArt1.py D:\Project\KV-AAP-PEDS210345_NLM.xml

if len(sys.argv) != 2:
    print("Please pass xml filename as argument\n")
    exit()

else:
    infile = sys.argv[1]

fileserver = "\\\\mumnasprod"

outfile = infile
outfile = re.sub("(?:\_NLM|\_JATS)?\.xml$","_JATS.xml",outfile)

currentyear = time.strftime('%Y')
exepath = os.path.realpath(__file__)
ini_path = os.path.abspath(os.path.join(exepath,'../..'))
jrnl_ini_path = ini_path + "\\INI_Files\\JournalMeta.ini"
#print(jrnl_ini_path)

filename = infile
filename = re.sub(".+[\\\/]","",filename)
filename = re.sub("(?:\_NLM)?\.\w+$","",filename)
result = re.search("^[A-Z]+-([A-Z]+)-([A-Z]+)\d+",filename)
cust = result.group(1)
jrnl = result.group(2)
#print(cust)
#print(jrnl)

jf = open(jrnl_ini_path, "r" , encoding="utf-8")
jrnl_meta = jf.read()
jf.close()
   
regex = "<" + jrnl + ">(.*?)</" + jrnl + ">"
mat = re.search(regex, jrnl_meta , re.M | re.S)
if mat:
    jrnl_info = mat.group(1)
regex = "(<journal-meta>.*?</journal-meta>)"
matjm = re.search(regex , jrnl_info , re.M | re.S)
if matjm:
    j_data = matjm.group(1)
    #print(j_data)

def main():
    global signal_data
    global vol
    global iss
    signal_data = get_signal_data(infile)
    #print("signal_data" + signal_data)
    regex = "<iss>(\d+):(\d+)<\/iss>"
    matjm = re.search(regex , signal_data , re.M | re.S)
    if matjm:
        vol = matjm.group(1)
        iss = matjm.group(2)
        #print(iss)
    iss="Supplement_3"

    global arttitle
    reg1 = "<ArticleTitle>(.*?)\s*<\/ArticleTitle>"
    mat = re.search(reg1 , signal_data)
    if mat:
        arttitle = mat.group(1)
        
    # Input File (NLM) :-
    f = open(infile , "r" , encoding="utf-8")
    xmlbuff = f.read()              
    f.close()

    # common points :-
    reg = "(<article\s.*?</article>)"
    pat = re.compile(reg, re.M | re.S)
    xmlbuff = re.sub(pat , convert_artdata , xmlbuff)
    
    reg1 = "(<)(article\ )"
    pat1 = re.compile(reg1 , re.M | re.S)
    rep1 = "\\1main-\\2"
    xmlbuff = re.sub(pat1 , rep1 , xmlbuff , count=1)
    reg1 = "(</)(article>\\s*\Z)"
    rep1 = "\\1main-\\2"
    #pat1 = re.compile(reg1 , re.M | re.S)
    xmlbuff = re.sub(reg1 , rep1 , xmlbuff) 
    reg1 = "(<)(article\ )"
    rep1 = "\\1sub-\\2"
    pat1 = re.compile(reg1 , re.M | re.S)
    xmlbuff = re.sub(pat1 , rep1 , xmlbuff)
    reg1 = "(</)(article>)"
    rep1 = "\\1sub-\\2"
    pat1 = re.compile(reg1 , re.M | re.S)
    xmlbuff = re.sub(pat1 , rep1 , xmlbuff)
    reg1 = "(?:<back>\\s*</back>\\s*)(</sub-article>)"
    rep1 = "\\1"
    pat1 = re.compile(reg1 , re.M | re.S)
    xmlbuff = re.sub(pat1 , rep1 , xmlbuff)
    reg1 = "(</sub-article>\\s*)(<sub-article\ .*</body>\\s*)"
    rep1 = "\\2\\1"
    pat1 = re.compile(reg1 , re.M | re.S)
    xmlbuff = re.sub(pat1 , rep1 , xmlbuff)
    reg1 = "(<\/?)main-(article)\\b"                     
    rep1 = "\\1\\2"
    pat1 = re.compile(reg1 , re.M | re.S)
    xmlbuff = re.sub(pat1 , rep1 , xmlbuff)

    global main_art
    global history
    main_art = "<article xml:lang=\"en\" article-type=\"abstract\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:oasis=\"http://www.niso.org/standards/z39-96/ns/oasis-exchange/table\" xsi:schemaLocation=\"JATS-journalpublishing-oasis-article1.xsd JATS-journalpublishing-oasis-article1.xsd\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">"
    reg1 = "(<history_meca>\\s*(.*?)\\s*<\/history_meca>)"
    pat1 = re.compile(reg1 , re.M |re.S)
    mat1 = re.search(pat1 , xmlbuff)
    if mat1:
    	history = mat1.group(1)
    xmlbuff = re.sub(pat1, "", xmlbuff)
    history = re.sub(pat1, convert_history, history)
    #print(history)

    reg1 = "(<article\ .*?)(?=<sub-article )"
    pat1 = re.compile(reg1 , re.M | re.S)
    xmlbuff = re.sub(pat1 , convert_mainartdata , xmlbuff)

    global subartcounts
    global subartcount
    global affcount
    global arttype_prev
    global artsubtype_prev
    subartcounts = 1
    subartcount=1
    affcount=1
    arttype_prev = ""
    artsubtype_prev = ""
    reg1 = "(<sub-article\\ .*?</sub-article>)"
    pat1 = re.compile(reg1 , re.M | re.S)
    xmlbuff = re.sub(pat1 , convert_subart , xmlbuff)
    #print(xmlbuff)

    # Output File (JATS):-  
    fo = open(outfile , "w" , encoding="utf-8")
    fo.write(xmlbuff)
    fo.close()
    
def convert_artdata(mat):
    artdata = mat.group(1)
    global signal_data
    global vol
    global iss
    global arttitle
    reg1 = "(<journal-meta>.*?</journal-meta>)"
    pat1 = re.compile(reg1, re.M | re.S)
    artdata = re.sub(pat1 , j_data , artdata)
    reg1 = "<article-id pub-id-type=\"doi\">(.*?)<\/article-id>"
    doi = re.search(reg1, artdata).group()
    pubid = doi
    pat1 = r"\d+-\d+"
    pubid = re.search(pat1 , pubid).group()
    pubid = "<article-id pub-id-type=\"publisher-id\">" + pubid + "</article-id>"
    add = pubid +"\n" + doi + "\n"
    reg1 = "<article-id pub-id-type=.*?</article-id>\n?"
    pat1 = re.compile(reg1, re.M | re.S)
    artdata = re.sub(pat1, "", artdata)
    artdata = re.sub("(<article-meta>)\n?", "<article-meta>\n" + add, artdata)
        
    reg1 = "(<contrib-group>.*?</contrib-group>)"
    pat1 = re.compile(reg1, re.M | re.S)
    artdata = re.sub(pat1, convert_contribgrp, artdata)

    reg1 = "(<fn-group>.*?</fn-group>)"
    pat = re.compile(reg1 , re.M |re.S)
    pat1 = re.search(pat , artdata)
    fngroup=""
    if pat1:
        fngroup = pat1.group(1)
    artdata = re.sub(pat, "", artdata)
    fngroup = re.sub("(<\/?)fn-group(>)" ,"\\1author-notes\\2" , fngroup)
    #print("fngroup\n--\n" + fngroup)

    reg1 = "(<fn\ .*?</fn>)"
    pat1 = re.compile(reg1, re.M | re.S)
    fngroup = re.sub(pat1, convert_fngroup, fngroup)
        
    if fngroup:
        rep1 = "\\1\n" + fngroup
        artdata = re.sub("(</contrib-group>)", rep1, artdata, count=1)

    reg1 = "<pub-date pub-type=\"epub\">.*?<\/pub-date>\n"
    pat1 = re.compile(reg1 , re.M | re.S)
    artdata = re.sub(pat1 , "" , artdata)
       
    reg1 = "(<pub-date\ pub-type=\"pub\">.*?<\/pub-date>)"
    pat1 = re.compile(reg1 , re.M | re.S)
    artdata = re.sub(pat1 , convert_pubdate , artdata)
        
    reg1 = "(<\/pub-date>\\s*<volume>)\\d*(<\/volume>)"
    rep1 = "\\g<1>"+vol+"\\2"
    pat1 = re.compile(reg1 , re.M | re.S)
    artdata = re.sub(pat1 ,rep1, artdata)
        
    reg1 = "(<\/pub-date>\\s*<volume>\\d*<\/volume>\\s*<issue>)\\d*(<\/issue>)"
    rep1 = "\\g<1>"+iss+"\\2<issue-title>"+arttitle+"</issue-title>"
    pat1 = re.compile(reg1 , re.M | re.S)
    artdata = re.sub(pat1 ,rep1, artdata)
        
    reg1 = "(<permissions>.*?<\/permissions>)"
    pat1 = re.compile(reg1 , re.M | re.S)
    artdata = re.sub(pat1 , convert_perm , artdata)

    reg1 = "(<self-uri\\ [^>]*?>)\n?"
    pat1 = re.compile(reg1 , re.M | re.S)
    artdata = re.sub(pat1 , convert_selfuri , artdata)

    reg1 = "(<sec>\\s*<title>.*?</title>\\s*)"
    pat1 = re.compile(reg1 , re.M | re.S)
    artdata = re.sub(pat1 , convert_sectitle , artdata)
        
    reg1 = "(<product>.*?<\/product>)"
    pat1 = re.compile(reg1 , re.M | re.S)
    artdata = re.sub(pat1 , convert_product , artdata)
    return artdata

def convert_contribgrp(mat):
    contrbgrp = mat.group(1)
    reg1 = "<\/degrees>\\s*<\/contrib>\\s*(?:<x>)?(,? )(?:<\/x>)\\s*<contrib>\\s*<degrees>"
    pat1 = re.compile(reg1, re.M | re.S)
    contrbgrp = re.sub(pat1 , "\\1" , contrbgrp)
    #print("contrbgrp\n--\n" + contrbgrp)
    reg1 = "<x>,? <\/x>\n?"
    contrbgrp = re.sub(reg1 , "" , contrbgrp)
    #print("contrbgrp\n==\n" + contrbgrp)
    
    reg1 = "(<contrib\ .*?<\/contrib>)"
    pat1 = re.compile(reg1, re.M | re.S)
    contrbgrp = re.sub(pat1, convert_contrib, contrbgrp)
    
    reg2 = "(<aff\ .*?<\/aff>)"
    pat2 = re.compile(reg2 , re.M | re.S)
    contrbgrp = re.sub(pat2, convert_aff, contrbgrp)
    return contrbgrp

def convert_contrib(mat):
    contrb = mat.group(1)
    #print ("contrb\n---\nn" + contrb)
    reg1 = "\\s*(<given-names>.*?</given-names>)\\s*(<surname>.*?</surname>)\\s*"
    rep1 = "\\2\\1"
    pat1 = re.compile(reg1, re.M | re.S)
    contrb = re.sub(pat1, rep1, contrb)
    contrb = re.sub("\n" , "" , contrb)
    #print("contrb\n==\n" + contrb)
    return contrb

def convert_aff(mat):
    aff = mat.group(1)
    #print("aff\n---\nn" + aff)
    reg1 = "<\/?(?:city|state)>"
    #pat1 = re.compile(reg1, re.M | re.S)
    aff = re.sub(reg1, "", aff)
    #print(aff)
    
    aff = re.sub("<institution>" , '<institution content-type="university">' , aff)
    aff = re.sub("\n" , "" , aff)
    #print(aff)
    return aff

def convert_fngroup(mat):
    fndata = mat.group(1)
    #print(fndata)
    
    reg1 = "<fn (?:new)?id=\"FN(\d+)\"[^>]*?>"
    #pat1 = re.compile(reg1, re.M | re.S)
    fndata = re.sub(reg1 , "<fn id=\"FM\\1\">" , fndata)
    #print(fndata)
    
    if (re.search("\\b(?:Funding|Grant)", fndata, re.I)):
        reg1 = "(<fn id=\"FM\\d+\")>"
        #pat1 = re.compile(reg1, re.M | re.S)
        fndata = re.sub(reg1 , "\\1 fn-type=\"funder\">" , fndata)
        #print(fndata)
        
    elif (re.search("\\b(?:Supplement)", fndata, re.I)):
        reg1 = "(<fn id=\"FM\\d+\")>"
        #pat1 = re.compile(reg1, re.M | re.S)
        fndata = re.sub(reg1 , "\\1 fn-type=\"supplementary-material\">" , fndata)
        #print(fndata)

    else:
        reg1 = "(<fn id=\"FM\d+\")>"
        #pat1 = re.compile(reg1, re.M | re.S)
        fndata = re.sub(reg1 , "\\1 fn-type=\"other\">" , fndata)
        #print(fndata)
    return fndata

def convert_pubdate(mat):
    ppub = mat.group(1)
    reg1 = "(\ pub-type=\")(pub\")"
    rep1 = "\\1p\\2"
    pat1 = re.compile(reg1 , re.M | re.S)
    ppub = re.sub(pat1 , rep1 , ppub)
    reg1 = "<day>\d*<\/day>"
    ppub = re.sub(reg1 , "" , ppub)
    reg3 = "<month>\d*<\/month>"
    ppub = re.sub(reg3 , "<month>12</month>" , ppub)
    reg4 = "<year>\d*<\/year>\n"
    ppub = re.sub(reg4 , "<year>"+currentyear+"</year>" , ppub)
    ppub = re.sub("\n" , "" , ppub)
    #print(ppub)
    return ppub

def convert_perm(mat):
    perm = mat.group(1)
    reg1 = "<license\ .*?<\/license>\n?"
    pat1 = re.compile(reg1 , re.M | re.S)
    perm = re.sub(pat1 , "" , perm)
    reg1 = "(<copyright-statement>Copyright &\#x0*A9; )\d\d\d\d"
    pat1 = re.compile(reg1 , re.M |re.S)
    rep1 = "\\g<1>"+currentyear
    perm = re.sub(pat1 , rep1 , perm)
    reg1 = "\\s*<copyright-year\/>"
    pat1 = re.compile(reg1 , re.M | re.S)
    perm = re.sub(pat1 , "\n<copyright-year>"+currentyear+"</copyright-year>" ,perm)
    #print(perm)
    return perm

def convert_selfuri(mat):
    selfuri = mat.group(1)
    reg1 = " content-type=\"pdf\""
    selfuri = re.sub(reg1 , "", selfuri)
    reg1 = "( xlink:href=\")\d+.\d+\/"
    rep1 = "\\1"
    selfuri = re.sub(reg1 , rep1 , selfuri)
    #print(selfuri)
    return selfuri

def convert_sectitle(mat):
    sectitle = mat.group(1)
    reg1 = "</?bold>"
    sectitle = re.sub(reg1 , "" , sectitle)
    reg1 = "(<title>)\\s*"
    sectitle = re.sub(reg1 , "\\1" , sectitle , count=1)
    reg1 = "\\s*(</title>)\\s*"
    sectitle = re.sub(reg1 , "\\1\n" , sectitle,count=1)
    #print(sectitle)
    return sectitle

def convert_product(mat):
    product = mat.group(1)
    reg1 = "\n"
    pat1 = re.compile(reg1 , re.M | re.S)
    product = re.sub(pat1 , "" , product)
    reg1 = "<product>"
    rep1 = "<product product-type=\"journal\">\n"
    product = re.sub(reg1 , rep1 , product , count=1)
    reg1 = "<contrib contrib-type=\"author\">"
    pat1 = re.compile(reg1 , re.M | re.S)
    rep1 = "<name>"
    product = re.sub(pat1 , rep1 , product)
    reg1 = "</contrib>"
    pat1 = re.compile(reg1 , re.M | re.S)
    rep1 = "</name>"
    product = re.sub(pat1 , rep1 , product)
    reg1 = "(</name>)\\s*(?:<x>)?, ?(?:</x>)?\\s*"
    pat1 = re.compile(reg1 , re.M | re.S)
    rep1 = "\\1"
    product = re.sub(pat1 , rep1 , product)
    reg1 = "(</surname>) (<given-names>)"
    pat1 = re.compile(reg1 , re.M | re.S)
    rep1 = "\\1\\2"
    product = re.sub(pat1 , rep1 , product)
    reg1 = "(<name>)"
    rep1 = "<person-group person-group-type=\"author\">"+"\\1"
    product = re.sub(reg1 , rep1 , product ,count = 1)
    reg1 = "(\. ?)(</etal>)"
    rep1 = "\\2\\1"
    product = re.sub(reg1 , rep1 , product , count=1)
    reg1 = "((?s:.*)</name>(?:,? ?<etal>et\\.? al\\.?</etal>)?)"
    rep1 = "\\1"+"</person-group>"
    pat1 = re.compile(reg1 , re.M | re.I)
    product = re.sub(pat1 , rep1 , product)
    #print(product)
    return product

def convert_history(mat):
    history = mat.group(1)
    reg1 = "<history_meca>\s*(.*?)\s*<\/history_meca>"
    rep1 = "\\1"
    history = re.sub(reg1 , rep1 , history)
    reg1 = "(\\bAccepted for publication\\b ?)"
    pat1 = re.compile(reg1 , re.M | re.I)
    history = re.sub(pat1 , "<date date-type=\"accepted\"><x>\\1</x>" , history)
    reg1 = "(</x>)([A=Za-z][A=Za-z]+) (\d?\d), ?(\d\d\d\d)\\b"
    pat1 = re.compile(reg1 , re.M | re.S)
    rep1 = "\\1<month>\\2</month><x> </x><day>\\3</day><x>, </x><year>\\4</year></date>"
    history = re.sub(pat1 , rep1 , history)
    reg1 = "(<month>)([A=Za-z]+)(<\/month>)"
    pat1 = re.compile(reg1 , re.M | re.S)
    rep1 = "\\1"
    mat = re.search(pat1 , history).group(2)
    history = re.sub(pat1 , rep1+get_monthnamefull(mat)+"\\3" , history)
    reg1 = "^(.+?)$"
    pat1 = re.compile(reg1 , re.M | re.S)
    rep1 = "<history>\n\\1\n</history>\n"
    history = re.sub(pat1 , rep1 , history , count=1)
    return history


def convert_mainartdata(mat):
    mainartdata = mat.group(1)
    reg1 = "<article\\ [^>]*?>"
    rep1 = main_art
    pat1 = re.compile(reg1 , re.M | re.S)
    mainartdata = re.sub(pat1 , rep1 , mainartdata)

    reg1 = "<counts>.*?<\/counts>"
    pat1 = re.compile(reg1 , re.M | re.S)
    mainartdata = re.sub(pat1 , convert_counts , mainartdata)

    global seccount
    seccount = 1
    reg1 = "(\s*<sec>.*?<\/sec>)"
    pat1 = re.compile(reg1 , re.M | re.S)
    mainartdata = re.sub(pat1 , convert_sec , mainartdata)

    reg1 = "<history>.*?<\/history>\\n?"
    rep1 = history
    pat1 = re.compile(reg1 , re.M | re.S)
    mainartdata = re.sub(pat1 , rep1 , mainartdata)
    #print(mainartdata)
    return mainartdata
    

def convert_counts(mat):
    counts = mat.group()
    reg1 = "(<(?:fig|table|equation|word)-count) count=\"\d*\"/>\\n?"
    counts = re.sub(reg1 , "" , counts)
    reg1 = "( count=\")(\"/>)"
    counts = re.sub(reg1 , "\\g<1>0\\2" , counts)
    return counts

def convert_sec(mat):
    sec = mat.group(1)
    reg1 = "\\s*<sec>"
    global seccount
    sec = re.sub(reg1 , "\\n<sec id=\"s"+str(seccount)+"\">" , sec , count=1)
    seccount += 1
    return sec
    
def convert_subart(mat):
    subartdata = mat.group(1)
    global subartcounts
    global subartcount
    global arttype_prev
    global artsubtype_prev
    global arttype
    global artsubtype
    sub_art = "<sub-article id=\"s"+str(subartcount)+"\" article-type=\"abstract\">"
    subartcount += 1

    reg1 = "<sub-article\\ [^>]*?>"
    pat1 = re.compile(reg1 , re.M | re.S)
    subartdata = re.sub(pat1 , sub_art , subartdata , count=1)
    reg1 = "<subj-group subj-group-type=\"heading\">\\s*<subject>\\s*(.*?)\\s*</subject>"
    pat1 = re.compile(reg1 , re.M | re.S)
    mat = re.search(pat1 , subartdata)
    if mat:
        arttype = mat.group(1)
    
    reg1 = "<subj-group>\\s*<subject>\\s*(.*?)\\s*</subject>"
    pat1 = re.compile(reg1 , re.M | re.S)
    mat = re.search(pat1 , subartdata)
    if mat:
        artsubtype = mat.group(1)
    #print(subartdata)
    if arttype:
        arttype_prev = arttype
    else:
        arttype = arttype_prev
    if artsubtype:
        artsubtype_prev = artsubtype
    else:
        artsubtype = artsubtype_prev
    
    subj_head = "<subj-group subj-group-type=\"heading\">\n<subject>"+arttype+"</subject>\n"
    subj_head += "<subj-group>\n"
    subj_head += "<subject>"+artsubtype+"</subject>\n"
    subj_head += "</subj-group>\n</subj-group>\n"

    reg1 = "<subj-group>.*?</subj-group>\n?"
    pat1 = re.compile(reg1 , re.M | re.S)
    subartdata = re.sub(pat1 , "" , subartdata , count=1)
       
    reg1 = "<subj-group\\ .*?</subj-group>\n?"
    pat1 = re.compile(reg1 , re.M | re.S)
    subartdata = re.sub(pat1 , "" , subartdata , count=1)

    reg1 = "<subj-group\\ [^>]*?>\n?"
    pat1 = re.compile(reg1 , re.M | re.S)
    subartdata = re.sub(pat1 , "" , subartdata , count=1)

    reg1 = "(<article-categories>)\n?"
    rep1 = "\\1\n"+subj_head
    subartdata = re.sub(reg1 , rep1 , subartdata ,count=1)
    
    reg1 = "(<contrib-group>.*?<\/contrib-group>)"
    pat1 = re.compile(reg1 , re.M | re.S)
    subartdata = re.sub(pat1 , convert_contrbgrp , subartdata)

    reg1 = "(</issue-title>\\s*<fpage>)(\d*</fpage>)"
    pat1 = re.compile(reg1 , re.M | re.S)
    rep1 = "\\g<1>S\\g<2>"
    subartdata = re.sub(pat1 , rep1 , subartdata , count=1)

    reg1 = "(</issue-title>\\s*<fpage>\\w*</fpage>\\s*<lpage>)(\d*<\/lpage>)"
    pat1 = re.compile(reg1 , re.M | re.S)
    rep1 = "\\g<1>S\\g<2>"
    subartdata = re.sub(pat1 , rep1 , subartdata , count=1)

    reg1 = "<history>.*?</history>\\n?"
    pat1 = re.compile(reg1 , re.M | re.S)
    subartdata = re.sub(pat1 , "" , subartdata)

    reg1 = "(<counts>.*?<\/counts>)"
    pat1 = re.compile(reg1 , re.M | re.S)
    subartdata = re.sub(pat1 , convert_count , subartdata)
    subartcounts += 1
    return subartdata

def convert_count(mat):
    count = mat.group(1)
    reg1 = "(<(?:word)-count) count=\"\d*\"\/>\n?"
    count = re.sub(reg1 , "" , count)
    reg1 = "(<page-count) count=\"\d*\"/>"
    rep1 = "\\1 count=\"1\"/>"
    count = re.sub(reg1 , rep1 , count)
    reg1 = "( count=\")(\"/>)"
    rep1 = "\\g<1>0"+"\\g<2>"
    count = re.sub(reg1 , rep1 , count)
    #print(count)
    return count

def convert_contrbgrp(mat):
    contrbgrp = mat.group(1) 
    reg1 = "(<aff\\ .*?<\/aff>)"
    pat1 = re.compile(reg1 , re.M | re.S)
    contrbgrp = re.sub(pat1 , convert_affc , contrbgrp)
    return contrbgrp

def convert_affc(mat):
    affc = mat.group(1)
    reg1 = "(<aff id=\"aff)\d+(\">)"
    global affcount
    rep1 = "\\g<1>"+str(affcount)+"\\2"
    affc = re.sub(reg1 , rep1 , affc , count=1)
    affcount += 1
    #print(affc)
    return affc

def get_signal_file(infile):
    filename1 = infile
    filename1 = re.sub("(?:\_NLM)?(\.\w+)$","",filename1)
    signal_file = filename1 + ".xml"
    if not os.path.exists(signal_file):
        filename1 = re.sub(".+[\\\/]","",filename1)
        CustomerDir = get_customerdir(filename1)
        signal_file = fileserver + "\\cenpro\\Support\\Production\\" + CustomerDir + "\\XML_Signal_ToProd\\" + filename1 + ".xml"
    #print(signal_file)
    return signal_file 

def get_signal_data(infile):
    signal_file = get_signal_file(infile)
    #print ("\nsignal_file: " + signal_file)
    fs = open(signal_file, "r" )
    signal_data = fs.read()
    fs.close()

    #print ("\signal_data: " + signal_data)
    return signal_data

def get_customerdir(filename1):
    CustomerDir = jrnl
    res = re.search("^([A-Z][A-Z]-)",filename1)
    custname = res.group(1)
    if (custname == "AC-"):
       CustomerDir = "ASCE"
    elif (custname == "AE-"):
        CustomerDir = "AAEP"
    elif (custname == "AP-"):
        CustomerDir = "APA"
    elif (custname == "AJ-"):
        CustomerDir = "APS"
    elif (custname == "AM-"):
        CustomerDir = "APMA"
    elif (custname == "SM-"):
        CustomerDir = "ASM"
    elif (custname == "AN-"):
        CustomerDir = "ASNR"
    elif (custname == "CG-"):
        CustomerDir = "ACOG"
    elif (custname == "EH-"):
        CustomerDir = "NIEHS"
    elif (custname == "EM-"):
        CustomerDir = "EMERALD"
    elif (custname == "ET-"):
        CustomerDir = "ETDD"
    elif (custname == "DE-"):
        CustomerDir = "DEI"
    elif (custname == "CP-"):
        CustomerDir = "ACP"
    elif (custname == "CS-"):
        CustomerDir = "CSP"
    elif (custname == "GH-"):
        CustomerDir = "GHSP"
    elif (custname == "GP-"):
        CustomerDir = "GPL"
    elif (custname == "GT-"):
        CustomerDir = "GTLC"
    elif (custname == "JB-"):
        CustomerDir = "JABE"
    elif (custname == "JL-"):
        CustomerDir = "JAAPL"
    elif (custname == "JM-"):
        CustomerDir = "JABFM"
    elif (custname == "JP-"):
        CustomerDir = "JPHR"
    elif (custname == "JS-"):
        CustomerDir = "JAFS"
    elif (custname == "LS-"):
        CustomerDir = "JSLS"
    elif (custname == "KV-"):
        CustomerDir = "KGLVT"
    elif (custname == "MI-"):
        CustomerDir = "MSUP"
    elif (custname == "MO-"):
        CustomerDir = "MORS"
    elif (custname == "OC-"):
        CustomerDir = "OCN"
    elif (custname == "PD-"):
        CustomerDir = "PDA"
    elif (custname == "SJ-"):
        CustomerDir = "AJS"
    elif (custname == "SN-"):
        CustomerDir = "SFN"
    elif (custname == "TL-"):
        CustomerDir = "ACMJ"
    return CustomerDir

def get_monthnamefull(n):
    ch = n
    if (ch == "Jan"):
        res = "January"
    elif (ch == "Feb"):
        res = "February"
    elif (ch == "Mar"):
        res = "March"
    elif (ch == "Apr"):
        res = "April"
    elif (ch == "May"):
        res = "May"
    elif (ch == "Jun"):
        res = "June"
    elif (ch == "Jul"):
        res = "July"
    elif (ch == "Aug"):
        res = "August"
    elif (ch == "Sep"):
        res = "September"
    elif (ch == "Oct"):
        res = "October"
    elif (ch == "Nov"):
        res = "November"
    elif (ch == "Dec"):
        res = "December"        
    else:
        res = calendar.month_name[int(ch)]      
    return res

if __name__ == "__main__":
    main();

