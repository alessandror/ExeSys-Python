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

import redis
import pprint
import cPickle
import math
import operator

class Searcher():
    
    def __init__( self ):
        self.corpus_doc_average_len = 0
        self.cur_search = {}

        self.cur_redis_0_rev_index = redis.Redis(host='localhost', port=6379, db=0) #rev_index
        self.cur_redis_1_doc_len = redis.Redis(host='localhost', port=6379, db=1) # Doc : len 
       
        self.cur_doc_list = self.cur_redis_1_doc_len.smembers( "__ALLDOCS__" )
        self.tot_doc_in_corpus = len(self.cur_doc_list)
        self.corpus_doc_avg_len = self.calc_corpus_doc_average_len() 

    def init_query(self, query_word_list):
        self.doc_set = []
        self.doc_set = self.cur_redis_0_rev_index.sunion(query_word_list)
        self.query_word_list = query_word_list
        
    def dbm25f(self, k1=2.0, b=0.75):
        doc_score = {}
        kvalue0 = k1+1
        kvalue1 = k1*(1-b+b*(self.tot_doc_in_corpus / self.corpus_doc_avg_len ) )
        for doc in self.doc_set:
            ii = cPickle.loads( doc )
            filename = ii.keys()[0]
            score = 0.0
            for query_word in self.query_word_list:
                word_idf = self.calc_idf( query_word )
                word_fqd = float( ii[filename] )
                if word_fqd != None:
                    num = ( float( word_fqd )* kvalue0)
                    den = ( float( word_fqd )+ kvalue1) 
                    score = score + word_idf * ( num / den )
            doc_score[filename] = score
            sorted_doc_score = sorted(doc_score.iteritems(), key=operator.itemgetter(1), reverse = True) 
            self.cur_search["query_results"] = sorted_doc_score
        #pprint.pprint( self.cur_search )
                  
    def calc_idf(self,term):
        cur_doc_list = self.cur_redis_0_rev_index.smembers(term)
        num_item_in_cur_doc_list_with_term = len( cur_doc_list )
        num = ( float(self.tot_doc_in_corpus) - float(num_item_in_cur_doc_list_with_term) + 0.5 )
        den = ( float(float(num_item_in_cur_doc_list_with_term) + 0.5 ))
        idf = math.log( (num/den) )
        if idf <= 0: 
            return 0
        else:
            return idf    
    
    def calc_corpus_doc_average_len(self):
        cur_size = 0
        for i in self.cur_doc_list:
            cur_set_value = self.cur_redis_1_doc_len.smembers(i) 
            if len(cur_set_value) > 0:
                cur_size = cur_size + int( cur_set_value.pop() )
        return cur_size
    
    def get_sorted_results(self):
        return  self.cur_search
    
if __name__ == '__main__':
    print "-> start search test"
    cur_searcher = Searcher(  ) 
    cur_searcher.init_query( ["testword0","testword1"] ) 
    print "--> searching..."
    cur_searcher.dbm25f()
    print "--> print results"
    results = cur_searcher.get_sorted_results()
    pprint.pprint(results)

    
    