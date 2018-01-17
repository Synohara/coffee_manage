#!/usr/bin/env python
# coding: utf-8

CONSUMER_KEY        = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
CONSUMER_SECRET_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
ACCESS_TOKEN        = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
ACCESS_TOKEN_SECRET = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

from twitter import *
import re
import random
import json
from datetime import datetime, timedelta
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app import User, Coffee_Count
auth=OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET_KEY)
t = Twitter(auth=auth)


#起動ツイート
"""
dt = datetime.now()
status = "システム起動╰(　´◔　ω　◔ `)╯ "+dt.strftime('%Y/%m/%d %H:%M:%S')
t.statuses.update(status=status) #Twitterに投稿
"""

#DBに接続
engine = create_engine('sqlite:////tmp/coffee_manage.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

#ツイートのみ
status=["まあコーヒーでも飲めよ( ´･ω･)⊃☕️", "コーヒー( ･∀･)つ☕️ﾄﾞｿﾞｰ", "三╰( ^o^)╮-=ﾆ=☕️", "|Д`)ノ⌒☕️", "(☝️ ՞ਊ ՞)＝👉☕️)՞ਊ ՞)"] #投稿するツイート
noreply_list = ["ikedalab_coffee", "zenytips", "tipmona"]
#t.statuses.update(status=status) #Twitterに投稿

mona_rate = 0.02 #コーヒー1杯分をモナコインで換算

t_userstream = TwitterStream(auth=auth,domain='userstream.twitter.com')

for msg in t_userstream.user():

    try:
        for v in msg['entities'].get('user_mentions'):
            print(v)
            if v.get('screen_name') == "ikedalab_coffee" and (msg['user']['screen_name'] not in noreply_list):
                print(msg['text'])
                print(msg['user']['screen_name'])
                if re.search(r"(test|テスト|てすと)", msg['text']): #testの部分を(tip|モナ|もな)に変える

                    cache = re.sub(r'@\w+ (test|テスト|てすと) @ikedalab_coffee ', "", msg['text']) #r'(@tipmona (tip|モナ|もな)|@zenytips tip) @ikedalab_coffee '
                    #print(cache)
                    cup = int(float(cache) / mona_rate)
                    #print(cup)
                    users = []
                    users = session.query(User.twitter).all() #users = [(twitter_id1,), (twitter_id2,), ...]
                    #print(users)
                    flag = False #登録済みアカウントの判定フラッグ
                    for name in users:
                        if msg['user']['screen_name'] == name[0]:
                            flag = True
                            print("登録済みアカウントです")
                            user = session.query(User).filter_by(twitter = msg['user']['screen_name']).first()

                            for unpaid in session.query(Coffee_Count).filter_by(user_id=user.id).filter_by(check=False):
                                unpaid.check = True
                                cup -= 1
                                if cup==0:
                                    break

                            session.commit()
                            print("未払い分を入金しました")


                    if flag == False:
                        print("登録されていないアカウントです")

                    dt = datetime.now()

                    tweet = "@"+msg['user']['screen_name']+" "+str(cup)+"杯分入金しました。(╹◡╹✿)"+" "+dt.strftime('%Y/%m/%d %H:%M:%S')
                    if cup > 0:
                        tweet += "\n\n※入金額が未払い分を越えている可能性があります。管理者にお問い合わせください。"
                    t.statuses.update(status=tweet,in_reply_to_status_id=msg['id'])
                    print(tweet)


                elif re.search("フォロー", msg['text']):
                    print(t.friendships.lookup(screen_name=msg['user']['screen_name'])[0]["connections"][0])

                    if t.friendships.lookup(screen_name=msg['user']['screen_name'])[0]["connections"][0]!="following":
                        t.friendships.create(screen_name=msg['user']['screen_name'])
                        tweet = "@"+msg['user']['screen_name']+" "+"フォローしました！ (๑˃̵ᴗ˂̵)و "
                        t.statuses.update(status=tweet,in_reply_to_status_id=msg['id'])
                        print(tweet)
                    else:
                        tweet = "@"+msg['user']['screen_name']+" "+"フォロー済みです！ヽ(•̀ω•́ )ゝ✧"
                        t.statuses.update(status=tweet,in_reply_to_status_id=msg['id'])
                        print(tweet)

                else:
                    randomtweet = status[random.randrange(len(status))]
                    tweet = "@"+msg['user']['screen_name']+" "+randomtweet
                    t.statuses.update(status=tweet,in_reply_to_status_id=msg['id'])
                    print(tweet)


    except KeyboardInterrupt:
        # CTRL+C
        dt = datetime.now()
        status =('システム終了 ✋( ͡° ͜ʖ ͡°) ')+dt.strftime('%Y/%m/%d %H:%M:%S')
        t.statuses.update(status=status) #Twitterに投稿
        break
    except:
        pass    # 例外全部無視してループさせる
