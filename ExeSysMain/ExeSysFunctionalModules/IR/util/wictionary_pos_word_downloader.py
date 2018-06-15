"""
Copyright 2018 Alex Redaelli <a.redaelli at gmail dot com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, 
modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the 
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR 
THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

#-*- coding: utf-8 -*-

import sys
import os

from pattern.web import URL, DOM, plaintext

from ExeSysMain import environment as env

sys.path.insert(0, os.path.join("..", "../ExeSysMain/") )
import re
import redis
import multiprocessing as mp

class WictionaryPos():
    def __init__(self):
        self.pool = redis.ConnectionPool(host=env.WDIP, port=env.WDPORT, db=0)
        self.redisconn = redis.Redis(connection_pool=self.pool)
        self.THROTTLE = 1
        self.url = "http://en.wiktionary.org/wiki/Index:Italian/"
        self.stopiter = 0
        self.letter_to_process = ''
        self.response = ''
        
    def set_stop_iter(self,num):
        self.stopiter = num
    
    def set_letter_to_process(self,letter):
        self.letter_to_process= letter
    
    def get_letter_to_process(self):
        return self.letter_to_process
        
# -- search for word inflections 
    def inflect(self,word, language="italian"):
        #print "-> search for inflection word: %s" % word
        self.redisconn.set('processing', word)
        inflections = {}
        url = "http://en.wiktionary.org/wiki/" + word.replace(" ", "_") 
        dom = DOM(URL(url).download(throttle=self.THROTTLE, cached=False))
        pos = ""
        # Search the header that marks the start for the given language: <h2><span class="mw-headline" id="Italian">Italian</span></h2>
        e = dom("#" + language)[0].parent
        while e is not None: # e = e.next_sibling
            if e.type == "element":
                if e.tag == "hr": # Horizontal line = next language
                    break
                if e.tag == "h3": # <h3>Adjective [edit]</h3>
                    pos = plaintext(e.content.lower())
                    pos = pos.replace("[edit]", "").strip()[:3].rstrip("ouer") + "-"
                # Parse inflections, using regular expressions.
                s = plaintext(e.content)
                if s.startswith(word):
                    for gender, regexp, i in (
                      ("m" , r"(" + word + r") m", 1),
                      ("f" , r"(" + word + r") f", 1),
                      ("m" , r"(" + word + r") (mf|m and f)", 1),
                      ("f" , r"(" + word + r") (mf|m and f)", 1),
                      ("m" , r"masculine:? (\S*?)(,|\))", 1),
                      ("f" , r"feminine:? (\S*?)(,|\))", 1),
                      ("m" , r"(\(|, )m(asculine)? (\S*?)(,|\))", 3),
                      ("f" , r"(\(|, )f(eminine)? (\S*?)(,|\))", 3),
                      ("mp", r"(\(|, )m(asculine)? plural (\S*?)(,|\))", 3),
                      ("fp", r"(\(|, )f(eminine)? plural (\S*?)(,|\))", 3),
                      ( "p", r"(\(|, )plural (\S*?)(,|\))", 2),
                      ( "p", r"m and f plural (\S*?)(,|\))", 1)):
                        m = re.search(regexp, s, re.I)
                        if m is not None:
                            inflections[pos + gender] = m.group(i) # {"adj-m": "affetto", "adj-fp": "affette"}
            e = e.next_sibling
        return inflections

        
    def process_lexicon(self):
        
        if self.letter_to_process != None:
            
            lexicon = {}
            for ch in self.letter_to_process:
                #print ch, len(lexicon)
                # Download the HTML source of each Wiktionary page (a-z).
                html = URL(self.url + ch).download(throttle=self.THROTTLE, cached=False)
                dom = DOM(html)
                # Iterate through the list of words and parse the part-of-speech tags.
                # Each word is a list item:
                # <li><a href="/wiki/additivo">additivo</a><i>n adj</i></li>
                stop = 0
                for li in dom("li"):
                    if self.stopiter > 0:
                            print "--> stop: %d" % stop
                            stop = stop+ 1
                            if stop > self.stopiter: 
                                break
                    try:
                        word = li("a")[0].content
                        pos = li("i")[0].content.split(" ")
                        
                        if any(tag in pos for tag in ("n", "v", "adj")):
                            #print "-> process inflect"
                            for pg, w in self.inflect(word).items():
                                #print pg,w
                                p, g = pg.split("-") # pos + gender: ("adj", "f")
                                if w not in lexicon:
                                    lexicon[w] = []
                                if p not in lexicon[w]:
                                    lexicon[w].append(p)
                                    
                        if word not in lexicon:
                            lexicon[word] = []
                        lexicon[word].extend(pos)
                    except:
                        pass
                    
            for punctuation, tag in (
              (u".", "."), (u'"', '"'), (u"+", "SYM"), (u"#", "#"),
              (u"?", "."), (u'“', '"'), (u"-", "SYM"), (u"$", "$"),
              (u"!", "."), (u'”', '"'), (u"*", "SYM"), (u"&", "CC"),
              (u"¡", "."), (u"(", "("), (u"=", "SYM"), (u"/", "CC"),
              (u":", ":"), (u")", ")"), (u"<", "SYM"), (u"%", "CD"),
              (u";", ":"), (u",", ","), (u">", "SYM"), (u"@", "IN"), (u"...", ".")):
                lexicon[punctuation] = tag
                    
            PENN = {  "n": "NN",
                      "v": "VB",
                    "adj": "JJ",
                    "adv": "RB",
                "article": "DT",
                   "prep": "IN",
                   "conj": "CC",
                    "num": "CD",
                    "int": "UH",
                "pronoun": "PRP",
                 "proper": "NNP"
            }
            
                  
            SPECIAL = ["abbr", "contraction"]
            special = set()
             
            #csv = Datasheet()
            for word, pos in lexicon.items():
                if " " not in word:
                    # Map to Penn Treebank II tagset
                    penn  = [PENN[tag] for tag in pos if tag in PENN]
                    penn += [tag] if tag in ("SYM",".",",",":","\"","(",")","#","$") else [] 
                    penn  = ", ".join(penn)
                    
                    # Collect tagged words in the .csv file and in redis
                    #csv.append((word, penn))
                    key = "wdmain:" + word + ":it:0:1"
                    self.redisconn.rpush(key,penn)
                    
                    # Collect special words for post-processing.
                    for tag in SPECIAL:
                        if tag in pos:
                            special.add(word)
                            key = "wdmain:" + word + ":it:0:0"
                            self.redisconn.rpush(key,'')
                            
            #csv.columns[0].sort(reverse=True)
            #csv.save("it-lexicon.csv")
            
            print '--> done letter ' + ch
            print special
            self.redisconn.set('processing', 'none')
            return 'done letter ' + ch
        
class Worker(mp.Process):
 
    def __init__(self, s, result_queue):
 
        mp.Process.__init__(self)
        self.result_queue = result_queue
 
    def run(self):
        print("-------------------------------------Starting " + str(s.get_letter_to_process()) + " ...")
        result = s.process_lexicon()
        self.result_queue.put(result)

if __name__ == "__main__":
    letters = "abcdefghijklmnopqrstuvwxyz0"

    result_queue = mp.Queue()
   
    for ch in letters: 
        s = WictionaryPos()
        s.set_stop_iter(0)
        s.set_letter_to_process(ch)

        worker = Worker(s, result_queue)
        worker.start()

    results = []
    for i in range(len(letters)):
        print(result_queue.get())
        