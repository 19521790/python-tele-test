from flask import Flask, request
import telepot
import urllib3
import sqlite3



connection = sqlite3.connect("replyForwardId.db")
cursor = connection.cursor()
cursor.execute(
    "create table if not exists replyId (id integer primary key,source_id integer, des_id integer, source_message_id integer, des_message_id integer)")

connection.close()

proxy_url = "http://proxy.server:3128"
telepot.api._pools = {
    'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),
}
telepot.api._onetime_pool_spec = (urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))

secret = "67c4f026-15f5-4269-97e0-853041792eea"
bot = telepot.Bot('5505684344:AAE98Odd40aqZiIAi8CtmtDUcfjdqxaompk')
bot.setWebhook("https://telegram-test-long.herokuapp.com/{}".format(secret), max_connections=1)
    
app = Flask(__name__)

@app.route('/{}'.format(secret), methods=["POST"])
def telegram_webhook():
    
    try:
        update = request.get_json()
        print(update)




        if "message" in update:
            type= "message"
        elif "channel_post" in update:
            type= "channel_post"
        else:
            return "OK"


        connection = sqlite3.connect("replyForwardId.db")
        cursor = connection.cursor()

        source_id = update[type]["chat"]["id"]
        if source_id== -1001642572065:
            destination_id = -1001112294077

        elif source_id== -1001735866288:
            destination_id = -1001155176622

        elif source_id== -743101910:
            destination_id = -1001720920647

        elif source_id== -1001885511655:
            destination_id = -1001639924840

        else:
            return "OK"

        source_reply_id = update[type]["message_id"]
        #handle photo
        if "photo" in update[type]:

            photo_id= update[type]['photo'][2]['file_id']
            if "caption" in update[type]:

                destination_rely_id= bot.sendPhoto(chat_id= destination_id, photo=photo_id,caption= update[type]['caption'])["message_id"]
            else:
                destination_rely_id= bot.sendPhoto(chat_id= destination_id, photo=photo_id)["message_id"]


        #handle text

        elif "text" in update[type]:
            text= update[type]["text"]
            try:
                reply_message_id_from_source = update[type]["reply_to_message"]["message_id"]
            except:
                reply_message_id_from_source = None

            if reply_message_id_from_source:
                cursor.execute(
                    "Select des_message_id from replyId where source_id= ? and des_id=? and source_message_id =?",
                    (source_id, destination_id, reply_message_id_from_source))
                reply_message_id_from_des = cursor.fetchone()

                if reply_message_id_from_des:
                    destination_rely_id = bot.sendMessage(chat_id= destination_id, text= text, reply_to_message_id=reply_message_id_from_des[0])["message_id"]

                    # destination_rely_id = send_message(message, chat, reply_message_id_from_des[0]).message_id
                else:
                    destination_rely_id =bot.sendMessage(chat_id= destination_id, text= text)["message_id"]
                    # destination_rely_id = send_message(message, chat).message_id
            else:
                destination_rely_id =bot.sendMessage(chat_id= destination_id, text= text)["message_id"]

        #save db
        cursor.execute(
            "insert into replyId (source_id, des_id, source_message_id, des_message_id) values (?,?,?,?)",
            (source_id, destination_id, source_reply_id, destination_rely_id))

        cursor.execute("Select count(0) from replyId")

        if cursor.fetchone()[0] > 1000:
            cursor.execute("delete from replyId where id in (SELECT id FROM replyId ORDER BY id ASC LIMIT 500)")

        connection.commit()

        connection.close()


        return "OK"
    except:
        return "OK"
