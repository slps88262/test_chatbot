#!/usr/bin/env python
# coding: utf-8

# In[1]:


#get_ipython().system('pip install PyMySQL')


# In[ ]:


from flask import (Flask, request, abort, jsonify, render_template)

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, FollowEvent, TextSendMessage, TextMessage, ImageSendMessage, StickerSendMessage,
    StickerMessage,TemplateSendMessage, ButtonsTemplate,MessageAction,URIAction,ImagemapSendMessage,BaseSize,
    URIImagemapAction,ImagemapArea,MessageImagemapAction
)
import datetime
import pymysql
from threading import Thread
import json
import random

#--使用json讀取secretFile.txt
secretFile = json.load(open("./secretFile.txt",'r'))
#--從secretFile.txt取得channelAccessToken
channelAccessToken = secretFile['channelAccessToken']
#--透過channelAccessToken連線LINE機器人
line_bot_api = LineBotApi(channelAccessToken)
#--從secretFile.txt取得channelSecret
channelSecret = secretFile['channelSecret']
#--透過channelSecret連線WebhookHandler
handler = WebhookHandler(channelSecret)

#--設定SQL位置等資料
config = {
          'host':secretFile['host'],
          'port':secretFile['port'],
          'user':secretFile['user'],
          'password':secretFile['passwd'],
          'db':secretFile['db'],
          }

#--創建一個連線資料庫的class，並啟動多執行序
class dbcnn(Thread):
    #--宣告一個連線資料庫事件
    def fun_db_open(self):
        #--繼承db,cursor,secretFile 變數
        global db,cursor,secretFile
        #--使用pymysql.connect 連線資料庫
        db = pymysql.connect(**config)
        #--建立遊標 ，cursor是處理數據的一種方法，為了查看或者處理結果集中的數據，游標提供了在結果集中一次一行或者多行前進或向後瀏覽數據的能力。可以把游標當作一個指針，它可以指定結果中的任何位置，然後允許用戶對指定位置的數據進行處理
        #--通俗來說就是，操作數據和獲取數據庫結果都要通過游標來操作。
        cursor = db.cursor();
    
    #--宣告一個中斷連線資料庫事件
    def fun_db_close(self):
        #--繼承db,cursor 變數
        global db,cursor
        #--關閉遊標
        cursor.close(); 
        #--關閉連線
        db.close(); 

#--將class實體化
dbcnn=dbcnn()

def SQL_commit(SQL):
    dbcnn.fun_db_open();
    cursor.execute(SQL);db.commit();dbcnn.fun_db_close();

def SQL_select(SQL):
    dbcnn.fun_db_open();
    cursor.execute(SQL);
    data = cursor.fetchone();
    dbcnn.fun_db_close();
    return data

def SQL_select_all(SQL):
    dbcnn.fun_db_open();
    cursor.execute(SQL);
    data = cursor.fetchall();
    dbcnn.fun_db_close();
    return data

def chk_user(UID):
    SQL="select Line_UID,cName from userdata where Del_YN='N' and Line_UID='"+UID+"'";
    data=SQL_select(SQL);
    return data

def chk_student_ID(UID):
    SQL="select Student_ID from userdata where Del_YN='N' and Line_UID='"+UID+"'";
    data=SQL_select(SQL);data=data[0];
    return data

def chk_class(student_ID):
    SQL="select class from basic_info where Del_YN='N' and student_ID='"+student_ID+"'";
    data=SQL_select(SQL);data=data[0];
    return data

def chk_cName(student_ID):
    SQL="select cName from basic_info where Del_YN='N' and student_ID='"+student_ID+"'";
    data=SQL_select(SQL);data=data[0];
    return data

app = Flask(__name__,static_url_path = "/static" , static_folder = "./static/")

@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(FollowEvent)
def handle_follow(event):
    sendMessage = [
                TextSendMessage(text='首次加入的朋友，請先註冊才能進行查詢及申請。'),
                ImagemapSendMessage(
                    base_url='https://dc10101.serveo.net/static/1/',
                    alt_text='1',
                    base_size=BaseSize(height=1040, width=1040),
                    actions=[
                        URIImagemapAction(
                            link_uri='https://dc10101.serveo.net/static/1/1040.png',
                            area=ImagemapArea(
                                x=0, y=0, width=1040, height=1040
                            )
                        ),
                        MessageImagemapAction(
                            text='註冊',
                            area=ImagemapArea(
                                x=520, y=0, width=50, height=50
                            )
                        )
                    ]
                )
                ]
    line_bot_api.reply_message(event.reply_token,sendMessage)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #--將使用者發送的訊息儲存再msg變數
    msg = event.message.text
    msglist = event.message.text.split()
    #--透過datetime取的目前UTC+8的時間，並且編排樣式
    nowTime = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    today = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d")
    week = (datetime.datetime.utcnow() + datetime.timedelta(hours=8) + datetime.timedelta(days=6)).strftime("%Y-%m-%d");
    #--透過LINE API取的使用者ID
    UID = event.source.user_id
    #--透過LINE API和使用者ID取的使用者資料
    profile = line_bot_api.get_profile(UID)
    #--透過使用者資料取得使用者的名稱
    displayName = profile.display_name
    #--透過使用者資料取的使用者的照片
    pictureUrl = profile.picture_url
    #--尚未註冊訊息回復
    Not_registered=[TextSendMessage(text="尚未註冊!"),ImagemapSendMessage(
                    base_url='https://dc10101.serveo.net/static/1/',
                    alt_text='1',
                    base_size=BaseSize(height=1040, width=1040),
                    actions=[
                        URIImagemapAction(
                            link_uri='https://dc10101.serveo.net/static/1/1040.png',
                            area=ImagemapArea(
                                x=0, y=0, width=1040, height=1040
                            )
                        ),
                        MessageImagemapAction(
                            text='註冊',
                            area=ImagemapArea(
                                x=520, y=0, width=50, height=50
                            )
                        )
                    ]
                )]
    if msg=="註冊":
        if len(UID) > 0:
            data=chk_user(UID);
            if data is None:
                sendMessage = [
                TextSendMessage(text='尚未註冊!'),
                ImagemapSendMessage(
                    base_url='https://dc10101.serveo.net/static/1/',
                    alt_text='1',
                    base_size=BaseSize(height=1040, width=1040),
                    actions=[
                        URIImagemapAction(
                            link_uri='https://dc10101.serveo.net/static/1/1040.png',
                            area=ImagemapArea(
                                x=0, y=0, width=1040, height=1040
                            )
                        ),
                        MessageImagemapAction(
                            text='註冊',
                            area=ImagemapArea(
                                x=520, y=0, width=50, height=50
                            )
                        )
                    ]
                )
                ]
                line_bot_api.reply_message(event.reply_token,sendMessage)
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="已經註冊過!"))
                
    elif msglist[0]=="$註冊":
        data=chk_user(UID);
        if data is None:
            if len(msglist) ==3:
                SQL="select Student_ID from basic_info where Del_YN='N' and cName='"+msglist[1]+"' and Student_ID='"+msglist[2]+"'";
                data=SQL_select(SQL);
                if data is not None:
                    SQL="INSERT INTO userdata (Line_UID,cName,Student_ID,AddDate) VALUES ('"+UID +"',N'" + msglist[1] + "','" + msglist[2] + "','" + nowTime +"')";
                    SQL_commit(SQL);
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text="已完成註冊! 請在手機使用選單功能~"))
                else:
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text="您不符合註冊資格!"))
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="資料不完整!"))
        else:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="已經註冊過!"))
    
    elif msg=="課表查詢":
        data=chk_user(UID);
        if data is not None:
            student_ID=chk_student_ID(UID);
            Class=chk_class(student_ID);
            SQL="select Class,Date,Course,T_course from course_table where Del_YN='N' and Class='"+Class+"' and Date between '" + today + "' and '" + week + "' order BY Date";
            data=SQL_select_all(SQL);
            if data is not None:
                Date="";
                for x in range(0,len(data)):
                    data2=data[x]; 
                    T_course=list(str(data2[3])); T_course_type=""; 
                    for y in range(0,len(T_course)):
                        if T_course[y]=="1":
                            T_course_type=T_course_type+"上午 ";
                        elif T_course[y]=="2":
                            T_course_type=T_course_type+"下午 ";
                        elif T_course[y]=="3":
                            T_course_type=T_course_type+"夜間 ";
                    Date=Date + "日期：" + str(data2[1].strftime("%Y-%m-%d")) + "\n" + "課程名稱：" + str(data2[2]) + " " + T_course_type + "\n\n";
                content="班級：" + str(Class) + "\n" + Date;
                line_bot_api.reply_message(event.reply_token,TextSendMessage(content))
            else:
                content=str(today)+"~"+str(week)+" 沒課";
                line_bot_api.reply_message(event.reply_token,TextSendMessage(content))
        else:
            line_bot_api.reply_message(event.reply_token,Not_registered)
        
    elif msg=="缺勤查詢":
        data=chk_user(UID);
        if data is not None:
            student_ID=chk_student_ID(UID);
            cName=data[1];
            SQL="select Hours,status from missing_class where Del_YN='N' and student_ID='"+student_ID+"'";
            data=SQL_select_all(SQL);
            if data is not None:
                Absentee=0;sick=0;Casual=0;Statutory=0;Maternity=0;Funeral=0;
                for x in range(0,len(data)):
                    data2=data[x]; 
                    if data2[1]==0:
                        Absentee=int(Absentee) + int(data2[0]);
                    elif  data2[1]==1:
                        sick=int(sick) + int(data2[0]);
                    elif  data2[1]==2:
                        Casual=int(Casual) + int(data2[0]);
                    elif  data2[1]==3:
                        Statutory=int(Statutory) + int(data2[0]);
                    elif  data2[1]==4:
                        Maternity=int(Maternity) + int(data2[0]);
                    elif  data2[1]==5:
                        Funeral=int(Funeral) + int(data2[0]);
                Count=int(Absentee)*2 + int(sick) + int(Casual) + int(Statutory) + int(Maternity) + int(Funeral);
                content="查詢人：" + cName + "\n" +"曠課時數：" + str(Absentee) + "\n" + "病假時數：" + str(sick) + "\n" + "事假時數：" + str(Casual) + "\n";
                content=content + "公假時數：" + str(Statutory) + "\n" + "娩假時數：" + str(Maternity) + "\n" + "喪假時數：" + str(Funeral) + "\n" + "缺勤總時數：" + str(Count);
                line_bot_api.reply_message(event.reply_token,TextSendMessage(content));
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="無缺勤紀錄!"))
        else:
            line_bot_api.reply_message(event.reply_token,Not_registered)
            
    elif msg=="維修申請":
        data=chk_user(UID);
        if data is not None:
            buttons_template_message = TemplateSendMessage(
            alt_text='維修申請選單',
            template=ButtonsTemplate(
                #thumbnail_image_url='',
                title='維修申請選單',
                text='請選擇',
                actions=[
                        MessageAction(
                            label='報修紀錄查詢',
                            text='報修紀錄查詢'
                        ),
                        MessageAction(
                            label='申請設備維修',
                            text='申請設備維修'
                        )
                ]))
            line_bot_api.reply_message(event.reply_token,buttons_template_message)
        else:
            line_bot_api.reply_message(event.reply_token,Not_registered)
            
    elif msg=="報修紀錄查詢":
        data=chk_user(UID);
        if data is not None:
            student_ID=chk_student_ID(UID);
            SQL="select Class,Student_ID,Device,Remark,Room,Seat,AddDate from device_service where Del_YN='N' and student_ID='"+student_ID+"' order BY AddDate desc";
            data=SQL_select(SQL);
            if data is not None:
                cName_apply=chk_cName(data[1]);
                content="最新一筆紀錄如下\n申請人班級：" + str(data[0]) + "\n" + "申請者：" + str(cName_apply) + "\n" + "報修設備：" + str(data[2]) + "\n";
                content=content +"設備徵狀：" + str(data[3]) + "\n" + "教室：" + str(data[4]) + "\n" + "座位座標：" + str(data[5]) + "\n" + "申請日期：" + str(data[6].strftime("%Y-%m-%d"));
                line_bot_api.reply_message(event.reply_token,TextSendMessage(content))
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="無報修紀錄!"))
        else:
            line_bot_api.reply_message(event.reply_token,Not_registered)
    
    elif msg=="申請設備維修":
        data=chk_user(UID);
        if data is not None:
            sendMessage = [
                ImagemapSendMessage(
                    base_url='https://dc10101.serveo.net/static/3/',
                    alt_text='3',
                    base_size=BaseSize(height=1040, width=1040),
                    actions=[
                        URIImagemapAction(
                            link_uri='https://dc10101.serveo.net/static/3/1040.png',
                            area=ImagemapArea(
                                x=0, y=0, width=1040, height=1040
                            )
                        ),
                        MessageImagemapAction(
                            text='維修',
                            area=ImagemapArea(
                                x=520, y=0, width=50, height=50
                            )
                        )
                    ]
                )
            ]
            line_bot_api.reply_message(event.reply_token,sendMessage)
        else:
            line_bot_api.reply_message(event.reply_token,Not_registered)
            
    elif msglist[0]=="$維修":
        data=chk_user(UID);
        if data is not None:
            if len(msglist) ==5:
                student_ID=chk_student_ID(UID);
                Class=chk_class(student_ID);
                SQL="INSERT INTO device_service (Class,Student_ID,Device,Remark,Room,Seat,AddDate) VALUES ('"+ Class +"','" + student_ID + "','" + msglist[1]+ "','" + msglist[2]  + "','" + msglist[3]  + "','" + msglist[4]  + "','" + nowTime +"')";
                SQL_commit(SQL);
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="報修成功!"))
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="資料不完整!"))
        else:
            line_bot_api.reply_message(event.reply_token,Not_registered)

    elif msg=="機房申請":
        data=chk_user(UID);
        if data is not None:
            sendMessage = [
                ImagemapSendMessage(
                    base_url='https://dc10101.serveo.net/static/5/',
                    alt_text='5',
                    base_size=BaseSize(height=1040, width=1040),
                    actions=[
                        URIImagemapAction(
                            link_uri='https://dc10101.serveo.net/static/5/1040.png',
                            area=ImagemapArea(
                                x=0, y=0, width=1040, height=1040
                            )
                        ),
                        MessageImagemapAction(
                            text='辦法',
                            area=ImagemapArea(
                                x=520, y=0, width=50, height=50
                            )
                        )
                    ]
                ),
                TemplateSendMessage(
                alt_text='機房申請選單',
                template=ButtonsTemplate(
                #thumbnail_image_url='https://lh3.googleusercontent.com/p4LcxNthdIgZ1ZE0aqOgrhl-ppUZjIq4m8vhcmD62B29T3kAcIydLNj8eqOVUbCPirCQvvBeTv-MNcyCmpZp0L3O2iEe8n4Nelz8_s58Ypp4lRCG9A8cqGSor5rxHHeaUQC6U0EBCNv20puOgMmjxHT0s_ViDKIGJrH_sd16G8RNmtd6Ip-7WWUPPgwLgHkHxxOJlGkCscurTY-uF812L5TkXG6u2fiiBqZgCVxCr-9ZKzZnpV_mBlNncFexR18uQgptxOdkuEIMWvpNYO8uQyzTlYPAe-3pipqX8h9UcGTfpbhn-Eh5a8iUOFKni1go6ycDmr9OfzMsThfHCfwRQjJiOe0-QphR2omLHhhvGiXC22dQ0CWKKbiQhkX2Ji5vKT04lyGbiSVqpyVTo-RXBGoZYmn6zUDJ9NLT0azXSVLi3hjFm9o1yHoUQVjeTdCUc1qaXg3FtaHewvQ1g-mYbw-atlnsy_aIFjSdl8KOOgwsJuJaBvJ-5shvcqMoBdNcjPWHblSBEtV5XpkfIgrHmQdPUDv5wPBgYzAqy3tlGPzQr2FR2IVslx4VfHaaXxq92gG9IXZLi3tFy6vpCVl544qpDhdPFuEz79w8paCf39Tl7fwzujfUq9Uh9NcVRPF7dum9CheV5F_llIYEWVdcFKyQAncVD80=w1693-h767-no',
                title='機房申請選單',
                text='請選擇',
                actions=[
                        MessageAction(
                            label='機房申請查詢',
                            text='機房申請查詢'
                        ),
                        MessageAction(
                            label='申請機房使用',
                            text='申請機房使用'
                        ),
                        URIAction(
                            label='機房借用情況一覽表',
                            uri='http://bit.ly/2E7emtS'
                        )
                ]))]
            line_bot_api.reply_message(event.reply_token,sendMessage)
        else:
            line_bot_api.reply_message(event.reply_token,Not_registered)
            
    elif msg=="機房申請查詢":
        data=chk_user(UID);
        if data is not None:
            student_ID=chk_student_ID(UID);
            Class=chk_class(student_ID);
            SQL="select Class,Student_ID,Date,Room,Pepole,AddDate from room_apply where Del_YN='N' and Class='"+Class+"' and Date>='" + today + "' order BY Date";
            data=SQL_select(SQL);
            if data is not None:
                cName_apply=chk_cName(data[1]);Date=data[2].strftime("%Y-%m-%d");
                content="離本日最近一筆紀錄如下\n申請人班級：" + str(data[0]) + "\n" + "申請者：" + str(cName_apply) + "\n" + "使用日期：" + str(Date) + "\n";
                content=content +"申請機房：" + str(data[3]) + "\n" + "使用人數：" + str(data[4]) + "\n" + "申請日期：" + str(data[5].strftime("%Y-%m-%d"));
                line_bot_api.reply_message(event.reply_token,TextSendMessage(content))
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="無機房申請紀錄!"))
        else:
            line_bot_api.reply_message(event.reply_token,Not_registered)
    
    elif msg=="申請機房使用":
        data=chk_user(UID);
        if data is not None:
            sendMessage = [
                ImagemapSendMessage(
                    base_url='https://dc10101.serveo.net/static/4/',
                    alt_text='4',
                    base_size=BaseSize(height=1040, width=1040),
                    actions=[
                        URIImagemapAction(
                            link_uri='https://dc10101.serveo.net/static/4/1040.png',
                            area=ImagemapArea(
                                x=0, y=0, width=1040, height=1040
                            )
                        ),
                        MessageImagemapAction(
                            text='機房',
                            area=ImagemapArea(
                                x=520, y=0, width=50, height=50
                            )
                        )
                    ]
                )
            ]
            line_bot_api.reply_message(event.reply_token,sendMessage)
        else:
            line_bot_api.reply_message(event.reply_token,Not_registered)
            
    elif msglist[0]=="$機房":
        data=chk_user(UID);
        if data is not None:
            if len(msglist) ==4:
                student_ID=chk_student_ID(UID);
                Class=chk_class(student_ID);
                if msglist[1] >= today:
                    if msglist[1] <= week:
                        if int(msglist[3]) > 5:
                            SQL="select Date from room_apply where Del_YN='N' and Class='" + Class + "' and Date='" + msglist[1] + "' and Room='" + msglist[2] +"'";
                            data=SQL_select(SQL);
                            if data is None:
                                SQL="INSERT INTO room_apply (Class,Student_ID,Date,Room,Pepole,AddDate) VALUES ('"+ Class +"','" + student_ID + "','" + msglist[1]+ "','" + msglist[2]  + "','" + msglist[3]  + "','" + nowTime +"')";
                                SQL_commit(SQL);
                                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="機房申請成功!"))
                            else:
                                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="此日期的機房已被申請!"))
                        else:
                            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="使用人數不得小於6人!"))
                    else:
                        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="僅能申請一周內日期!"))
                else:
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text="不可申請過去日期!"))
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="資料不完整!"))
        else:
            line_bot_api.reply_message(event.reply_token,Not_registered)
            
    elif msg=="意見回饋":
        data=chk_user(UID);
        if data is not None:
            sendMessage = [
                ImagemapSendMessage(
                    base_url='https://dc10101.serveo.net/static/2/',
                    alt_text='2',
                    base_size=BaseSize(height=1040, width=1040),
                    actions=[
                        URIImagemapAction(
                            link_uri='https://dc10101.serveo.net/static/2/1040.png',
                            area=ImagemapArea(
                                x=0, y=0, width=1040, height=1040
                            )
                        ),
                        MessageImagemapAction(
                            text='意見',
                            area=ImagemapArea(
                                x=520, y=0, width=50, height=50
                            )
                        )
                    ]
                )
            ]
            line_bot_api.reply_message(event.reply_token,sendMessage)
        else:
            line_bot_api.reply_message(event.reply_token,Not_registered)
    
    elif msglist[0]=="$意見":
        data=chk_user(UID);
        if data is not None:
            if len(msglist) >=2:
                student_ID=chk_student_ID(UID);
                Class=chk_class(student_ID);
                cName=data[1]; content=msg[4:];
                SQL="SELECT COUNT(Student_ID) from feedback where Del_YN='N' and Student_ID='" + student_ID + "' AND DATE_FORMAT(AddDate, '%Y-%m-%d')='" + today + "'";
                data=SQL_select(SQL);
                if data[0] < 4:
                    SQL="INSERT INTO feedback (Line_UID,Class,Student_ID,cName,content,AddDate) VALUES ('" + UID + "','" + Class +"','" + student_ID + "','" + cName+ "',N'" + content + "','"  + nowTime +"')";
                    SQL_commit(SQL);
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text="意見發送成功!"))
                else:
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text="當日意見不可超過5次!"))
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="資料不完整!"))
        else:
            line_bot_api.reply_message(event.reply_token,Not_registered)

    elif msg=="test":
        data=chk_user(UID);
        if data is not None:
            sendMessage = [
                ImagemapSendMessage(
                    base_url='https://dc10101.serveo.net/static/1/',
                    alt_text='1',
                    base_size=BaseSize(height=1040, width=1040),
                    actions=[
                        URIImagemapAction(
                            link_uri='https://dc10101.serveo.net/static/1/1040.png',
                            area=ImagemapArea(
                                x=0, y=0, width=1040, height=1040
                            )
                        ),
                        MessageImagemapAction(
                            text='註冊',
                            area=ImagemapArea(
                                x=520, y=0, width=50, height=50
                            )
                        )
                    ]
                )
            ]
            line_bot_api.reply_message(event.reply_token,sendMessage)
        else:
            line_bot_api.reply_message(event.reply_token,Not_registered)
            
    else:
        data=chk_user(UID);
        if data is None:
            line_bot_api.reply_message(event.reply_token,Not_registered)
        else:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="請使用功能選單!"))
        
@handler.add(MessageEvent,message = StickerMessage)
def stickerMessage(event):
    # 隨機抽取貼圖編號
    stickerId = str(random.randint(51626494,51626533))
    sendMessage = [
        # 文字消息1
        #TextSendMessage("package_id="+event.message.package_id+",sticker_id="+event.message.sticker_id
        #),
        # 貼圖消息
        StickerSendMessage(
            package_id='11538',
            sticker_id=stickerId
        )
    ]
    line_bot_api.reply_message(event.reply_token,sendMessage)
        
@app.route('/info',methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0')

