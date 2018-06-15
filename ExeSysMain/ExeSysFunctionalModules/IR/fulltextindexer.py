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

class Fulltextindexer():
    
    def __init__(self):
        self.cur_index = {}
    
    def rev_index_( self, cur_file, cur_text, num_tot_token_in_cur_file ):
        """build reverse index"""
        print "->indexing: %s" % cur_file
        
        for word_in_cur_text in cur_text:
            if word_in_cur_text in  self.cur_index.keys():
                file_dict =  self.cur_index[word_in_cur_text]
                if cur_file in file_dict.keys():
                    i = file_dict[cur_file]
                    i += 1
                    file_dict[cur_file] = i / num_tot_token_in_cur_file
                else:
                    file_dict[cur_file] = 0.0
                    self.cur_index[word_in_cur_text] = file_dict                
            else:
                self.cur_index[word_in_cur_text] = { cur_file : 0.0 } 
        return self.cur_index   
    
if __name__ == '__main__':
    pass