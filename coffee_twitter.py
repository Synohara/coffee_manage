#!/usr/bin/env python
# coding: utf-8

CONSUMER_KEY        = 'YuF55ZTL4tV7BYOWr5sDdb9cI'
CONSUMER_SECRET_KEY = 'TDsSGxWwBlJRRqADfJjpNU71B9480WBtf1UQSG9I0K35T1xF8l'
ACCESS_TOKEN        = '951067067465134080-LdaB7am661mu4QDMX9kHctKtqTYE0wM'
ACCESS_TOKEN_SECRET = 'f8dEgBd2MiyyIt3mS8fC7VZcyyEm8Ms02VvWHD4uaSHS8'


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

dt = datetime.now()
status = "システム起動╰(　´◔　ω　◔ `)╯ "+dt.strftime('%Y/%m/%d %H:%M:%S')
t.statuses.update(status=status) #Twitterに投稿


#DBに接続
engine = create_engine('sqlite:////tmp/coffee_manage.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

#ツイートのみ
status=["まあコーヒーでも飲めよ( ´･ω･)⊃☕️", "コーヒー( ･∀･)つ☕️ﾄﾞｿﾞｰ", "三╰( ^o^)╮-=ﾆ=☕️", "|Д`)ノ⌒☕️", "(☝️ ՞ਊ ՞)＝👉☕️)՞ਊ ՞)"] #投稿するツイート
gtp=["ぽん(´◉‿ゝ◉`)✊", "ぽん(´◉‿ゝ◉`)✌️", "ぽん(´◉‿ゝ◉`)✋"]
reaction=["せやな(´◉‿ゝ◉`)","そやな(´◉‿ゝ◉`)","それな(´◉‿ゝ◉`)","わかる(´◉‿ゝ◉`)","ほんま(´◉‿ゝ◉`)","ええんちゃう(´◉‿ゝ◉`)","あ　ほ　く　さ"]
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
                if re.search(r"(tip|モナ|もな)", msg['text']): #testの部分を(tip|モナ|もな)に変える

                    cache = re.sub(r'(@tipmona (tip|モナ|もな)|@zenytips tip) @ikedalab_coffee ', "", msg['text']) #r'(@tipmona (tip|モナ|もな)|@zenytips tip) @ikedalab_coffee '
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
                            count=0
                            for unpaid in session.query(Coffee_Count).filter_by(user_id=user.id).filter_by(check=False):
                                #print(unpaid.check)
                                unpaid.check = True
                                cup -= 1
                                count +=1
                                if cup==0:
                                    break

                            session.commit()
                            print("未払い分を入金しました")


                    if flag == False:
                        print("登録されていないアカウントです")

                    dt = datetime.now()

                    tweet = "@"+msg['user']['screen_name']+" "+str(count)+"杯分入金しました。(╹◡╹✿)"+" "+dt.strftime('%Y/%m/%d %H:%M:%S')
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

                elif re.search(r"(じゃんけん|あいこ)", msg['text']):
                    randomtweet = gtp[random.randrange(len(gtp))]
                    tweet = "@"+msg['user']['screen_name']+" "+randomtweet
                    t.statuses.update(status=tweet,in_reply_to_status_id=msg['id'])
                    print(tweet)

                elif re.search(r"どう(思|おも|かな|です|よ)", msg['text']):
                    randomtweet = reaction[random.randrange(len(reaction))]
                    tweet = "@"+msg['user']['screen_name']+" "+randomtweet
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
