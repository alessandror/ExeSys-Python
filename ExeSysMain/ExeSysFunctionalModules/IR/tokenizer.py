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

import nltk

class Tokenizer():
    
    def __init__(self,stop_word_path):
        self.stop_words_list = []
        self.stop_word_path = stop_word_path
        self.load_stop_word_list()
    
    def set_filepath_cpickle(self,save_file_path):
        self.save_file_path = save_file_path
        
    def tokenize_file(self,text):
        text_to_process = text.decode('utf-8')
        
        real_words_tokens = nltk.tokenize.word_tokenize(text_to_process.lower())

# -- remove stop words
        for a in real_words_tokens:
            print "token: %s" % a
        purged_real_word_tokens = self.remove_stop_words(real_words_tokens)
        #print purged_real_word_tokens
        
# --  return dict of bag of words
        token_dict = {}
        token_dict["word_token_list"] = purged_real_word_tokens
        token_dict["number_token_list"] = len(real_words_tokens)
        return token_dict
    
    def load_stop_word_list(self):
        file_stop_word = open(self.stop_word_path  ,"r")
        for stop_words in file_stop_word.readlines():
            sw = stop_words.decode('latin-1').encode("utf-8")
            self.stop_words_list.append(sw.rstrip())
        file_stop_word.close()
            
    def remove_stop_words(self,word_list):
        for word_list_item in word_list:
            if word_list_item.encode("utf-8") in self.stop_words_list:
                print "removed: %s " % (word_list_item.encode("utf-8"))
                word_list.remove(word_list_item)
        return word_list        
    