import requests
import pandas as pd
import mysql.connector
import datetime
import time

    
#a function for feaching data from api
def fetch_data(url,mycursor,fs):
    try:
        res = requests.get(url).json()
        df = pd.json_normalize(res)
        name=url[37:-1]
        datatype=df.dtypes
        command=str(datatype).replace('\n',' ').replace('int64','int ,').replace('object','varchar(600),').replace('bool','tinyint ,').replace('address.','address_').replace('company.','company_').replace('geo.','geo_').strip()
        index=command.find('dtype')
        s=str('create table if not exists ' +name+' ('+command[:-len(command)+index])
        for i in range(len(s)):
            if(s[len(s)-i-1]==','):
                s=s[:len(s)-i-1]
                s+=');'
                break
        columns=list(df.columns.values)
        vals=""
        for column in columns:
            vals+=column+","
        vals=vals[:-1]+')'

        st = ""
        columns = df.columns.tolist()

        for i in range(len(df)):
            sst = "("
            for column in columns:
                val = df.iloc[i][column]
                if isinstance(val, str):
                    val = val.replace("'", "''")  # escape quotes
                    sst += f"'{val}',"
                else:
                    sst += f"{val},"
            sst = sst[:-1] + ")"  # remove last comma and close parenthesis
            st += sst + ","

        st = st[:-1] + ";"  # remove last comma and add semicolon
        st=st.replace('True','1').replace('False','0')
        cmd=("insert into "+name+" ("+vals+' values ').replace('int64','int ,').replace('object','varchar(600),').replace('bool','bool ,').replace('address.','address_').replace('company.','company_').replace('geo.','geo_')+st
        mycursor.execute(cmd)

    except Exception as err:
        fs.write(f"{datetime.datetime.now()} Error in featch: {err} \n")

def main():
    with open("error.txt", "a") as fs:
        try:
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="@BBkishore3921"
            )
            mycursor = mydb.cursor()
            mycursor.execute("CREATE DATABASE IF NOT EXISTS mydb2;")
            mycursor.execute("USE mydb2;")
        except mysql.connector.Error as err:
            fs.write(f"{datetime.datetime.now()}. Error in dbconnect: {err} \n")
        # urls
        l=['users','posts','comments','albums','photos','todos']
        # l=['users']
        base_link='https://jsonplaceholder.typicode.com/'
        urls=[]
        for x in l:
            link=base_link+x+'/'
            urls.append(link)
        while True:
            for url in urls:
                fetch_data(url,mycursor,fs)    
                time.sleep(5)

main()

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="@BBkishore3921"
)
mycursor = mydb.cursor()
mycursor.execute("USE mydb2;")
mycursor.execute("ALTER TABLE users ADD PRIMARY KEY (id);")
mycursor.execute("ALTER TABLE posts ADD PRIMARY KEY (id);")
mycursor.execute("ALTER TABLE comments ADD PRIMARY KEY (id);")
mycursor.execute("ALTER TABLE albums ADD PRIMARY KEY (id);")
mycursor.execute("ALTER TABLE photos ADD PRIMARY KEY (id);")
mycursor.execute("ALTER TABLE todos ADD PRIMARY KEY (id);")

mycursor.execute("ALTER TABLE posts ADD CONSTRAINT fk_posts_userid FOREIGN KEY (userid) REFERENCES users(id);")
mycursor.execute("ALTER TABLE comments ADD CONSTRAINT fk_comments_postid FOREIGN KEY (postid) REFERENCES posts(id);")
mycursor.execute("ALTER TABLE albums ADD CONSTRAINT fk_albums_userid FOREIGN KEY (userid) REFERENCES users(id);")
mycursor.execute("ALTER TABLE photos ADD CONSTRAINT fk_photos_albumid FOREIGN KEY (albumid) REFERENCES albums(id);")
mycursor.execute("ALTER TABLE todos ADD CONSTRAINT fk_todos_userid FOREIGN KEY (userid) REFERENCES users(id);")


