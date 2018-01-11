#!/usr/bin/env python
# coding: utf-8

CONSUMER_KEY        = 'YuF55ZTL4tV7BYOWr5sDdb9cI'
CONSUMER_SECRET_KEY = 'TDsSGxWwBlJRRqADfJjpNU71B9480WBtf1UQSG9I0K35T1xF8l'
ACCESS_TOKEN        = '951067067465134080-LdaB7am661mu4QDMX9kHctKtqTYE0wM'
ACCESS_TOKEN_SECRET = 'f8dEgBd2MiyyIt3mS8fC7VZcyyEm8Ms02VvWHD4uaSHS8'

from twitter import *
import random
auth=OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET_KEY)
t = Twitter(auth=auth)

#ツイートのみ
status=["まあコーヒーでも飲めよ( ´･ω･)⊃☕️", "コーヒー( ･∀･)つ☕️ﾄﾞｿﾞｰ", "三╰( ^o^)╮-=ﾆ=☕️", "|Д`)ノ⌒☕️", "(☝️ ՞ਊ ՞)＝👉☕️)՞ਊ ՞)"] #投稿するツイート

#t.statuses.update(status=status) #Twitterに投稿

t_userstream = TwitterStream(auth=auth,domain='userstream.twitter.com')

for msg in t_userstream.user():
    if 'in_reply_to_screen_name' in msg and 'in_reply_to_screen_name'!="ikedalab_coffee":
        print(msg)
        if msg['text']=="クレジット":
            tweet = "@"+msg['user']['screen_name']+" "+"クレジットを追加しました (╹◡╹✿) "
            #t.statuses.update(status=tweet,in_reply_to_status_id=msg['id'])
            print(tweet)
        else:
            randomtweet = status[random.randrange(len(status))]
            tweet = "@"+msg['user']['screen_name']+" "+randomtweet
            #t.statuses.update(status=tweet,in_reply_to_status_id=msg['id'])
            print(tweet)
