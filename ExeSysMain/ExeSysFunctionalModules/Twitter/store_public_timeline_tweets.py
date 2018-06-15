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

# -*- coding: utf-8 -*-
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler

from tweepy import Stream
import json
import redis
import cPickle
import ExeSysMain.environment as env

import ExeSysMain.ExeSysFunctionalModules.Common.erunner as er

# from os import sys, path
# sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
# import Common.erunner


debug = True


class TweetStreamGrabber(StreamListener):
    def __init__(self,
                 redis_ip=env.REDISIP,
                 redis_port=env.REDISPORT,
                 redis_data_db=env.REDISDATASERVERDB,
                 redis_runner_db=env.REDISRUNNERDB):
        self.redis_ip = redis_ip
        self.redis_port = redis_port
        self.redis_data_db = redis_data_db
        self.redis_runner_db = redis_runner_db
        self.consumer_key = "swi8FzUfPs6tD7JJjH4Fw"
        self.consumer_secret = "0NGqXiY6SO0UZ7weE1sxFuqkoYYDRRrkHiSteeSQ"
        self.access_token = "143502022-l5r7dguE6dfHOKXHGwUyINniqnPGJMhpcBNr3PlV"
        self.access_token_secret = "gut32U6hcqc85VW7fIziyx3Fq8UtotQhKvqjmcHmgBU"
        self.oauth_set()
        self.redis_connect()

    def oauth_set(self):
        self.auth = OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_token, self.access_token_secret)

    def redis_connect(self):
        self.pool_data = redis.ConnectionPool(host=self.redis_ip,
                                              port=self.redis_port,
                                              db=self.redis_data_db)
        self.redis_data_conn = redis.Redis(connection_pool=self.pool_data)
        self.pool_runner = redis.ConnectionPool(host=self.redis_ip,
                                                port=self.redis_port,
                                                db=self.redis_runner_db)
        self.redis_runner_conn = redis.Redis(connection_pool=self.pool_runner)

    def stream_run_on_topic(self, stream_topic):
        self.stream = Stream(self.auth, self)
        self.stream.filter(track=stream_topic)  # this starts Stream collector thread

    def uuid_set(self, uuid):
        self.uuid = uuid

    def stop_collecting(self):
        self.stream.disconnect()
        print "--->STOP COLLECTING"
        return self.get_return_resp('store_public_timeline_tweets_ENDED')

    def get_return_resp(self, resp_text):
        resp = {'EOJ': {resp_text : self.uuid}}
        return resp

    def on_data(self, data):
        tweet_data = json.loads(data)
        # tweeet
        user_id = tweet_data["id"]
        self.redis_data_conn.hset(user_id, 'created_at', tweet_data["created_at"])
        self.redis_data_conn.hset(user_id, 'user', tweet_data["user"]["id_str"])
        self.redis_data_conn.hset(user_id, 'lang', tweet_data["user"]["lang"])
        self.redis_data_conn.hset(user_id, 'text', tweet_data["text"].encode('utf-8'))
        self.redis_data_conn.hset(user_id, 'timestamp_ms', tweet_data['timestamp_ms'])
        self.redis_data_conn.hset(user_id, 'place', cPickle.dumps(tweet_data["place"]))
        self.redis_data_conn.hset(user_id, 'coordinates', cPickle.dumps(tweet_data["coordinates"]))
        self.redis_data_conn.hset(user_id, 'retweet_count', tweet_data["retweet_count"])
        self.redis_data_conn.hset(user_id, 'source', tweet_data["source"])
        #entities
        self.redis_data_conn.hset(user_id, 'hashtags', cPickle.dumps(tweet_data["entities"]["hashtags"]))
        self.redis_data_conn.hset(user_id, 'symbols', cPickle.dumps(tweet_data["entities"]["symbols"]))
        self.redis_data_conn.hset(user_id, 'trends', cPickle.dumps(tweet_data["entities"]["trends"]))
        self.redis_data_conn.hset(user_id, 'urls', cPickle.dumps(tweet_data["entities"]["urls"]))
        self.redis_data_conn.hset(user_id, 'user_mentions', cPickle.dumps(tweet_data["entities"]["user_mentions"]))

        if debug:
            print data
            print tweet_data["id"]
            print tweet_data["created_at"]
            print tweet_data["user"]["id_str"]
            print tweet_data["user"]["lang"]
            print tweet_data["text"].encode('utf-8')
        return True

    def on_error(self, status):
        print status


def start_tweet_stream_crawler(filter_data, cuuid):
    stream = TweetStreamGrabber()
    type = "TwitterCrawler"
    stream.uuid_set(cuuid)
    stream.redis_runner_conn.set("run:" + type + ":" + str(cuuid), "1")
    crunner = er.Runner(stream,
                        type,
                        str(cuuid))
    crunner.start()
    stream.stream_run_on_topic(filter_data)
    return stream.get_return_resp('store_public_timeline_tweets_STARTED')

def stop_tweet_stream_crawler(cuuid):
    stream = TweetStreamGrabber()
    stream.redis_runner_conn.set("run:" + type + ":" + cuuid, "0")


if __name__ == '__main__':
    import uuid
    ret = start_tweet_stream_crawler(['Berlusconi'],uuid.uuid4())
    print "--->END RUNNER: %s" % ret