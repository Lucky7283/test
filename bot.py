from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton,InlineQueryResultArticle,InputTextMessageContent, ReplyKeyboardMarkup, KeyboardButton
import google.generativeai as genai
import csv,re,time,os,telebot,test
from pytubefix import YouTube

global file,chat,msg,userlist,historyuser

token,api=test.test()
print(token)
print(api)
bot=telebot.TeleBot(token)
genai.configure(api_key=api)

model = genai.GenerativeModel("gemini-2.0-pro-exp")
userid=[]
may=sb=False

def dd(message,chat):
    sb=False
    p1=r'url=([^\s]+)'
    p2=r'text=([^\s]+)'
    r=re.search(p1,message.text)
    t=re.search(p2,message.text)
    url,text=(r.group(1)), (t.group(1))
    yt = YouTube(url)
    stream = yt.streams.get_lowest_resolution()
    filepaz=stream.download(output_path="trash/")
    filepaz=filepaz.replace('\\','/')
    file_url=genai.upload_file(filepaz)
    response=chat.send_message([file_url,text])
    return response


def history(file):
    parts="parts"
    text="text"
    role="role"
    strn=[]
    try:
        with open(f"data/{file}.txt",'r',encoding='utf-8') as f:
            r=f.read()
            if r==[]:
                return
            r=re.split("parts",r)
        i=0
        say=len(r)
        while i<say:
            if "file_data {" in r[i]:
                match = re.search(r"mime_type:\s*(\S+)", r[i])
                txt_type=match[1]
                match = re.search(r"file_uri:\s*(\S+)",r[i] )
                url=match[1]
                url=re.sub(r'"',"",url)
                txt_type=re.sub(r'"',"",txt_type)
                url=url.strip()
                txt=re.search(r"text:\s*(.+)", r[i+1])[1]
                rl="user"
                a={'role': rl,'parts':[{'file_data' :{'mime_type': txt_type,'file_uri':url }},{'text':txt}]}
                i=i+2
                strn.append(a)
            else:
                txt=re.search(r"text:\s*(.+)",r[i])
                rl=re.search(r'role:\s*(.+)',r[i])
                i=i+1
                if rl!=None and txt!=None:
                    rl=rl[1]
                    txt=txt[1]
                    if 'model'in rl:
                        rl="model"
                    else:
                        rl="user"
                else:
                    continue
                a={role: rl, parts: [{text: txt}]}
                strn.append(a)
        return strn
    except Exception as e:
        print(f'Error as a:{e}')
        return strn
def loads(message):
    print("loading")
    try:
        with open(f"Prompts/{message.from_user.id}.txt","r",encoding="UTF-8") as f:
            prompt=f.read().strip()
    except:
        prompt=None
    if prompt:
        print("Промт обнаружен")
        model = genai.GenerativeModel("gemini-2.0-pro-exp",system_instruction=prompt)
    else:
        print("Промт не обнаружен")
        model = genai.GenerativeModel("gemini-2.0-pro-exp")
    histor=history(message.from_user.id)
    if histor!=' ':
        print("История обнаружена")
        chat=model.start_chat(history=histor)
    else:
        print("История не обнаружена")
        chat=model.start_chat()
    return model,chat

def times():
    day=time.strftime("%d")
    month=time.strftime("%m")
    year=time.strftime("%Y")
    hour=time.strftime("%H")
    minute=time.strftime("%M")
    second=time.strftime("%S")
    return f"{day}.{month}.{year} {hour}:{minute}:{second}"
tm=times()
def hist():
    with open("data/chathistory.csv","r",encoding="UTF-8") as f:
        historyuser=f.read()
    return historyuser
def user():
    users=[]
    with open("data/userlist.csv","r") as f:
            userlist=csv.DictReader(f,delimiter=";")
            for i in userlist:
                users.append(i["USERNAME"]+"-"+i["ID"])
    return users
def w(message):
    with open("data/chathistory.csv","a",encoding="UTF-8") as f:
        if message.from_user.username:
            f.write(f"{message.from_user.username};{message.text};{message.content_type};{message.date};{tm} \n")
        else:
            f.write(f"{message.from_user.id};{message.text};{message.content_type};{message.date};{tm} \n")

@bot.message_handler(commands=["start"])
def start(message):
    global msg,bllist
    file=str(message.from_user.id)+".txt"
    userlist=user()
    usr=f"{message.from_user.username}-{message.from_user.id}"

    if usr not in userlist:
        with open("data/userlist.csv",'a',encoding="UTF-8") as d:
            d.write(f'{message.from_user.username};{message.from_user.first_name};{message.from_user.last_name};{message.from_user.id}\n')
    if message.from_user.id==1440683925:
        msg=message
        markup=InlineKeyboardMarkup(row_width=3)
        button1=InlineKeyboardButton("Userlist",callback_data="userlist")
        button2=InlineKeyboardButton("History",callback_data="history")
        button3=InlineKeyboardButton("Message",callback_data="message")
        button4=InlineKeyboardButton("Clear trash",callback_data="trash")
        markup.add(button1,button2,button3,button4)

        bot.send_message(text="select action",chat_id=message.chat.id,reply_markup=markup)
    else:
        w(message)
        bot.reply_to(message,"Hello I'm gemini ai bot")
@bot.message_handler(commands=["YTwatch"])
def watch(message):
    global sb
    sb=True
    bot.send_message(message.chat.id,"Отправьте ссылку\nSend the link")
@bot.message_handler(commands=["prompt"])
def promt(message):
    global may
    may=True
    with open(f"Prompts/{message.from_user.id}.txt",'r',encoding='UTF-8') as f:
        promt=f.read().strip()
        if promt:
            bot.send_message(message.chat.id,"Текущий промпт:\nCurrent prompt:")
            bot.send_message(message.chat.id,f"<b>{promt}</b>",parse_mode="HTML")
        else:
            bot.send_message(message.chat.id,"Промпт отсутствует\nPrompt is emty")
    bot.send_message(message.chat.id,"Введите новый промпт\nSend new prompt")



@bot.message_handler(commands=["clear"])
def clear(message):
    with open(f"data/{message.from_user.id}.txt","w",encoding="UTF-8") as f:
        f.write(" ")
    bot.send_message(message.chat.id,"История чата очищена\nChat history cleared")

@bot.callback_query_handler(func=lambda call:True)
def allback(call):

    if call.data=="history":
        historyuser=hist()
        if len(historyuser)>4096:
            bot.send_document("1440683925",open("data/chathistory.csv","r"))
        else:
            bot.send_message(call.message.chat.id,historyuser)
    elif call.data=="userlist":
        userlist=user()
        bot.send_message(call.message.chat.id,"\n".join(userlist))
    elif call.data=="message":
        bot.send_message(call.message.chat.id,msg)
    elif call.data=="trash":
        for i in os.listdir("trash"):
            os.remove(f"trash/{i}")
        bot.send_message(call.message.chat.id,"Корзина очищена")


def format(res):
    txt1=res.split("```")
    txt2=re.findall(r"```(.*?)```",res,re.DOTALL)
    if txt2==[]:
        res=res.strip('"')
        res=re.sub(r"<+",r'&lt;',res,flags=re.DOTALL)
        res=re.sub(r">+",r"&gt;",res,flags=re.DOTALL)
        res=re.sub(r"\*\*\s*(.*?)\s*\*\*", r" \1 ", res,flags=re.DOTALL)
        res=re.sub(r"\*(\S.*?)\*(?!\w)", r"  \1  ", res)
        res=re.sub(r"^\s*\*", r"•", res, flags=re.MULTILINE)
        res=re.sub(r"\\n", "\n", res,flags=re.DOTALL)
        res = re.sub(r"^\s*```(\w*)\n(.*?)\n\s*```$", r"<pre><code class='\1'>\2</code></pre>", res, flags=re.DOTALL | re.MULTILINE)
        res=re.sub(r"\`(.*?)\`", r"<code>\1</code>", res,flags=re.DOTALL)
        return res
    txt=''
    for i in txt1:
        print(i)
        if i in txt2:
            print("cod")
            i=re.sub(r"\\n", "\n", i,flags=re.DOTALL)
            i = re.sub(r"^.*\n", "", i, 1)
            i=re.sub(r"<+",r'&lt;',i,flags=re.DOTALL)
            i=re.sub(r">+",r"&gt;",i,flags=re.DOTALL)
            txt+=f"<pre>\n{i}\n</pre>"
        elif i:
            i=i.strip('"')
            i=re.sub(r"<+",r'&lt;',i,flags=re.DOTALL)
            i=re.sub(r">+",r"&gt;",i,flags=re.DOTALL)
            i=re.sub(r"\*\*\s*(.*?)\s*\*\*", r" \1 ", i,flags=re.DOTALL)
            i=re.sub(r"\*(\S.*?)\*(?!\w)", r" \1 ", i)
            i=re.sub(r"^\s*\*", r"•", i, flags=re.MULTILINE)
            i=re.sub(r"\\n", "\n", i,flags=re.DOTALL)
            i = re.sub(r"^\s*```(\w*)\n(.*?)\n\s*```$", r"<pre><code class='\1'>\2</code></pre>", i, flags=re.DOTALL | re.MULTILINE)
            i=re.sub(r"\`(.*?)\`", r"<code>\1</code>", i,flags=re.DOTALL)
            txt+=i
    return txt

try:
    @bot.message_handler(content_types=["text"])
    def text(message):
        global may,sb
        print(sb)
        model,chat=loads(message)
        bot.send_chat_action(message.chat.id, "typing")
        if may:
            with open(f"Prompts/{message.from_user.id}.txt","r",encoding="UTF-8") as f:
                prompt=f.read().strip()
                if prompt:
                    bol=True
                else:
                    bol=False

            with open(f"Prompts/{message.from_user.id}.txt","w",encoding="UTF-8") as f:
                f.write(message.text)
            may=False
            if bol:
                bot.send_message(message.chat.id,"Промпт успешно обнавлен\nPrompt refresh succes")
            else:
                bot.send_message(message.chat.id,"Промпт успешно добавлен\nPrompt add succes")

            return
        
        if sb:
            response=dd(message=message,chat=chat)

        

        w(message)

        try:
            question=message.text
            try:
                response = chat.send_message(question)
            except:
                chat=model.start_chat()
                response = chat.send_message(question)
            print(message.text)
            resp=response.text
            response=format(response.text).strip('"').strip('\n')
            while response[-1]=='\n' or response[-1]=='"':
                    response=response.strip('"').strip('\n')
            response=re.sub(r"^\s*\*", r"•", response, flags=re.MULTILINE)

            if not resp:
                response = chat.send_message(question)
                resp=response.text
                response=response.text
                response=format(response)
                while response[-1]=='\n' or response[-1]=='"':
                    response=response.strip('"').strip('\n')
                response=re.sub(r"^\s*\*", r"•", response, flags=re.MULTILINE)
                bot.send_message(message.chat.id,response,parse_mode='HTML')
                bot.send_message(1440683925,resp)

            elif len(response)>4096:
                cunt=4096
                try:
                    for i in range(0,len(response),4096):
                        bot.send_message(message.chat.id, response[i:cunt],parse_mode='HTML')
                        cunt+=4096
                except Exception as e:
                    bot.send_message(message.chat.id,response[cunt:],parse_mode="HTML")

            else:
                bot.reply_to(message,response,parse_mode="HTML")
            print(1)
        except Exception as e:
            resp=resp.strip('"')
            resp=re.sub(r"\*\*\s*(.*?)\s*\*\*", r" \1 ", resp,flags=re.DOTALL)
            resp=re.sub(r"\*(\S.*?)\*(?!\w)", r"  \1  ", resp)
            resp=re.sub(r"^\s*\*", r"•", resp, flags=re.MULTILINE)
            resp=re.sub(r"\\n", "\n", resp,flags=re.DOTALL)
            resp = re.sub(r"^\s*```\n(.*?)\n\s*```$", r"\n\n\n \1 \n\n\n", resp, flags=re.DOTALL | re.MULTILINE)

            cunt=4096
            bot.send_message(message.chat.id,f"{e}")
            try:
                for i in range(0,len(resp),4096):

                    bot.send_message(1440683925, resp[i:cunt])

                    bot.send_message(message.chat.id, resp[i:cunt])

                    cunt+=4096
            except Exception as e:
                print(e)

                bot.send_message(1440683925,resp[cunt:])
                bot.send_message(message.chat.id,resp[cunt:])
                bot.send_message(1440683925,f"Произошла ошибка: {e}")

        try:
            with open("data/"+str(message.from_user.id)+".txt","w",encoding="UTF-8") as f:
                txt=re.sub(r"\\(?!n)", "", f"{chat.history}")
                f.write(txt)

        except Exception as e:
            print(f"Ошибка: {e}")

    @bot.message_handler(content_types=['photo',])
    def photo(message):
        print(2)
        bot.send_chat_action(message.chat.id, "typing")
        w(message)
        model,chat=loads(message)

        try:
            fileid = message.photo[-1].file_id
            file_paz = bot.get_file(fileid).file_path
            fayl = bot.download_file(file_paz)
            filepaz = file_paz.split("/")[-1]

            with open(f"trash/{filepaz}", 'wb') as f:
                f.write(fayl)
            faylink = genai.upload_file(f"trash/{filepaz}")
            print(faylink)

            if message.caption:

                response = chat.send_message([faylink,  message.caption])
            else:
                response = chat.send_message([faylink,"что можешь сказать на счет фото"])

            response=format(response.text)

            if len(response)>4096:
                cunt=4096
                try:
                    for i in range(0,len(response),4096):
                        bot.reply_to(message, response[i:cunt])
                        cunt+=4096
                except Exception as e:
                    bot.reply_to(message,response[cunt:])
            else:
                bot.reply_to(message, response)

        except Exception as e:
            bot.reply_to(message, f"Произошла ошибка: {e}")

        with open("data/"+str(message.from_user.id)+".txt","w",encoding="UTF-8") as f:
                txt=re.sub(r"\\(?!n)", "", f"{chat.history}")
                f.write(txt)

    @bot.message_handler(content_types=["audio","voice"])
    def audio(message):
        print(3)
        bot.send_chat_action(message.chat.id,"typing")
        w(message)
        model,chat=loads(message)
        try:
            if message.content_type=="audio":
                audioid=message.audio.file_id
                audiopaz=bot.get_file(audioid).file_path
                fayl=bot.download_file(audiopaz)
                paz = audiopaz.split("/")[-1]

            elif message.content_type=="voice":
                voiceid=message.voice.file_id
                voicepaz=bot.get_file(voiceid).file_path
                fayl=bot.download_file(voicepaz)
                paz = voicepaz.split("/")[-1]
            with open(f"trash/{paz}", 'wb') as f:
                f.write(fayl)
            faylink = genai.upload_file(f"trash/{paz}")

            if message.caption:
                response = chat.send_message([faylink,  message.caption] )
            elif message.content_type=="voice":
                response = chat.send_message([faylink,"послушай"])
            elif message.content_type=="audio":
                response = chat.send_message([faylink,"что можешь сказать на счет аудио"])
            response=format(response.text)
            if len(response)>4096:
                cunt=4096
                try:
                    for i in range(0,len(response),4096):
                        bot.reply_to(message, response[i:cunt])
                        cunt+=4096
                except Exception as e:
                    bot.reply_to(message,response[cunt:])
            else:
                bot.reply_to(message, response)

        except Exception as e:
            bot.reply_to(message, f"Произошла ошибка: {e}")

        with open("data/"+str(message.from_user.id)+".txt","w",encoding="UTF-8") as f:
                txt=re.sub(r"\\(?!n)", "", f"{chat.history}")
                f.write(txt)

    @bot.message_handler(content_types=["document"])
    def fayl(message):
        print(4)
        w(message)
        bot.send_chat_action(message.chat.id,"typing")
        model,chat=loads(message)
        try:
            fileid=message.document.file_id
            filepaz=bot.get_file(fileid)
            filepaz=filepaz.file_path
            file=bot.download_file(filepaz)
            filepaz=filepaz.split("/")[-1]
            print(f'file:{file}')
            with open(f"trash/{filepaz}",'wb') as d:
                d.write(file)
            with open(f"trash/{filepaz}",'rb') as d:
                print(d.read())
            faylink = genai.upload_file(f"trash/{filepaz}")
            if message.caption:
                response = chat.send_message([faylink, message.caption] )
            else:
                response = chat.send_message([faylink,"что можешь сказать на счет файла"])
            response=response.text
            print(response)
            if len(response)>4096:
                cunt=4096
                try:
                    for i in range(0,len(response),4096):
                        bot.reply_to(message, response[i:cunt])
                        cunt+=4096
                except Exception as e:
                    bot.reply_to(message,response[cunt:])
            else:
                bot.reply_to(message, response)


        except Exception as e:
            bot.reply_to(message, f"Произошла ошибка: {e}")
        with open("data/"+str(message.from_user.id)+".txt","w",encoding="UTF-8") as f:
                txt=re.sub(r"\\(?!n)", "", f"{chat.history}")
                f.write(txt)

    @bot.message_handler(content_types=["video","video_note"])
    def video(message):
        print(5)
        w(message)
        bot.send_chat_action(message.chat.id,"typing")
        model,chat=loads(message)
        try:
            if message.content_type=="video":
                fileid=message.video.file_id
                filepaz=bot.get_file(fileid)
                filepaz=filepaz.file_path
                file=bot.download_file(filepaz)
                filepaz=filepaz.split("/")[-1]
            elif message.content_type=="video_note":
                fileid=message.video_note.file_id
                filepaz=bot.get_file(fileid)
                filepaz=filepaz.file_path
                file=bot.download_file(filepaz)
                filepaz=filepaz.split("/")[-1]

            with open(f"trash/{filepaz}",'wb') as d:
                d.write(file)
            faylink = genai.upload_file(f"trash/{filepaz}" )
            if message.caption:
                response = chat.send_message([faylink, message.caption] )
            elif message.content_type=="video":
                response = chat.send_message([faylink,"что можешь сказать на счет видео"])
            elif message.content_type=="video_note":
                response = chat.send_message([faylink,"посмотри"])
            response=format(response.text)
            if len(response)>4096:
                cunt=4096
                try:
                    for i in range(0,len(response),4096):
                        bot.reply_to(message, response[i:cunt])
                        cunt+=4096
                except Exception as e:
                    bot.reply_to(message,response[cunt:])
            else:
                bot.reply_to(message, response)
                #print(response.text)

        except Exception as e:
            print(e)
            bot.reply_to(message, "Файл слишком большой отправте файл размером до 20mb")

        with open("data/"+str(message.from_user.id)+".txt","w",encoding="UTF-8") as f:
                txt=re.sub(r"\\(?!n)", "", f"{chat.history}")
                f.write(txt)

except Exception as e:
    bot.send_message(1440683925,f"Произошла ошибка: {e}")



bot.polling(non_stop=True)
