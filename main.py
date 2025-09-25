#importing modules
import requests
import pandas as pd
import mysql.connector
import datetime
import time



flag=0
mydb = None
mycursor = None

def db_connect():
    global mydb, mycursor
    if mydb is None or not mydb.is_connected():
        try:
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="@BBkishore3921",
            )
            mycursor = mydb.cursor()
            mycursor.execute("CREATE DATABASE IF NOT EXISTS mydb2;")
            mycursor.execute("USE mydb2;")
        except mysql.connector.Error as err:
            with open("error.txt", "a") as fs:
                fs.write(f"{datetime.datetime.now()} Error in db_connect: {err} \n")

#featching url
def creating_table(url):
    try:
       
        # creating table dynamically
        res = requests.get(url).json()
        df = pd.json_normalize(res)
        name=url[37:-1] #name from url
        datatype=df.dtypes #featching datatype form data
        command=str(datatype).replace('\n',' ').replace('int64','int ,').replace('object','varchar(600),').replace('bool','tinyint ,').replace('address.','address_').replace('company.','company_').replace('geo.','geo_').strip()
        index=command.find('dtype')
        s=str('create table if not exists ' +name+' ('+command[:-len(command)+index])
        for i in range(len(s)):
            if(s[len(s)-i-1]==','):
                s=s[:len(s)-i-1]
                s+=');'
                break
        #creating cursor for insering data
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="@BBkishore3921"
        )
        mycursor = mydb.cursor()
        mycursor.execute("CREATE DATABASE IF NOT EXISTS mydb2;") #creating database
        mycursor.execute("USE mydb2;")
        mycursor.execute(s)  # table created

    except Exception as err:
        with open("error.txt", "a") as fs:
            fs.write(f"{datetime.datetime.now()} Error in featch: {err} \n")

def inserting_data(url):
    db_connect() # Ensure connection is active
    try:
        res = requests.get(url).json()
        df = pd.json_normalize(res)
        name = url.split('/')[-2]

        if df.empty:
            return

        columns = [f"`{col.replace('.', '_')}`" for col in df.columns]
        placeholders = ', '.join(['%s'] * len(columns))
        # Modified: Use INSERT IGNORE to handle duplicate primary keys
        insert_sql = f"INSERT IGNORE INTO `{name}` ({', '.join(columns)}) VALUES ({placeholders});"

        data_to_insert = []
        for index, row in df.iterrows():
            row_values = []
            for col in df.columns:
                val = row[col]
                if pd.isna(val): # Handle NaN values
                    row_values.append(None)
                elif isinstance(val, bool):
                    row_values.append(1 if val else 0) # Convert boolean to TINYINT
                else:
                    row_values.append(val)
            data_to_insert.append(tuple(row_values))

        mycursor.executemany(insert_sql, data_to_insert)
        mydb.commit()

    except Exception as err:
        with open("error.txt", "a") as fs:
            fs.write(f"{datetime.datetime.now()} Error in inserting_data for {url}: {err} \n")
    except Exception as err:
        with open("error.txt", "a") as fs:
            fs.write(f"{datetime.datetime.now()} Error in featch: {err} \n")


#adding constraints
def addding_constraints():
    try:
        #creating cursor for insering data
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="@BBkishore3921"
        )
        mycursor = mydb.cursor()
        mycursor.execute("CREATE DATABASE IF NOT EXISTS mydb2;") #creating database
        mycursor.execute("USE mydb2;")
        try:
            mycursor.execute("ALTER TABLE users ADD PRIMARY KEY (id);")
            mycursor.execute("ALTER TABLE posts ADD PRIMARY KEY (id);")
            mycursor.execute("ALTER TABLE comments ADD PRIMARY KEY (id);")
            mycursor.execute("ALTER TABLE albums ADD PRIMARY KEY (id);")
            mycursor.execute("ALTER TABLE photos ADD PRIMARY KEY (id);")
            mycursor.execute("ALTER TABLE todos ADD PRIMARY KEY (id);")
        except mysql.connector.Error as err:
            pass
        try:
            mycursor.execute("ALTER TABLE posts ADD CONSTRAINT fk_posts_userid FOREIGN KEY (userId) REFERENCES users(id);")
            mycursor.execute("ALTER TABLE comments ADD CONSTRAINT fk_comments_postid FOREIGN KEY (postId) REFERENCES posts(id);")
            mycursor.execute("ALTER TABLE albums ADD CONSTRAINT fk_albums_userid FOREIGN KEY (userId) REFERENCES users(id);")
            mycursor.execute("ALTER TABLE photos ADD CONSTRAINT fk_photos_albumid FOREIGN KEY (albumId) REFERENCES albums(id);")
            mycursor.execute("ALTER TABLE todos ADD CONSTRAINT fk_todos_userid FOREIGN KEY (userId) REFERENCES users(id);")
        except mysql.connector.Error as err:
            pass
    except Exception as err:
        with open("error.txt", "a") as fs:
            fs.write(f"{datetime.datetime.now()} Error in featch: {err} \n")

try:
    l=['users','posts','comments','albums','photos','todos']
    base_link='https://jsonplaceholder.typicode.com/'
    urls=[]
    for x in l:
        link=base_link+x+'/'
        urls.append(link)
    for url in urls:
        creating_table(url)
    addding_constraints()
    for url in urls:
        inserting_data(url)

    
    while(True):
        for url in urls:
            inserting_data(url)
            time.sleep(60*60)

except Exception as err:
        with open("error.txt", "a") as fs:
            fs.write(f"{datetime.datetime.now()} Error in featch: {err} \n")
