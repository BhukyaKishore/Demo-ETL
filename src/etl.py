import requests
import pandas as pd
import mysql.connector
import datetime
import time

# Connecting to database and returning connection and cursor
def db_connect():
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="@BBkishore3921"
        )
        mycursor = mydb.cursor()
        mycursor.execute("CREATE DATABASE IF NOT EXISTS mydb2;")
        mycursor.execute("USE mydb2;")
        return mydb, mycursor
    except mysql.connector.Error as err:
        with open("error.txt", "a") as fs:
            fs.write(f"{datetime.datetime.now()}. Error in db_connect: {err} \n")
        return None, None

# Creating tables dynamically
def creating_table(url, mycursor, mydb):
    try:
        res = requests.get(url).json()
        df = pd.json_normalize(res)
        name = url[37:-1]  # extract table name from url
        datatype = df.dtypes
        command = str(datatype)\
            .replace('\n', ' ')\
            .replace('int64', 'int ,')\
            .replace('object', 'varchar(600),')\
            .replace('bool', 'tinyint ,')\
            .replace('address.', 'address_')\
            .replace('company.', 'company_')\
            .replace('geo.', 'geo_')\
            .strip()
        index = command.find('dtype')
        s = 'CREATE TABLE IF NOT EXISTS ' + name + ' (' + command[:index].rstrip(',') + ');'
        mycursor.execute(s)
        mydb.commit()
        print(f"Table created or exists: {name}")
    except Exception as err:
        with open("error.txt", "a") as fs:
            fs.write(f"{datetime.datetime.now()} Error in creating_table: {err} \n")

# Inserting data into tables
def inserting_data(url, mycursor, mydb):
    try:
        res = requests.get(url).json()
        df = pd.json_normalize(res)
        name = url[37:-1]
        columns = df.columns.tolist()
        cols_str = "(" + ",".join(columns) + ")"

        values_list = []
        for i in range(len(df)):
            vals = []
            for col in columns:
                val = df.iloc[i][col]
                if isinstance(val, str):
                    val = val.replace("'", "''")  # escape quotes
                    vals.append(f"'{val}'")
                elif isinstance(val, bool):
                    vals.append('1' if val else '0')
                elif pd.isna(val):
                    vals.append('NULL')
                else:
                    vals.append(str(val))
            values_list.append("(" + ",".join(vals) + ")")

        values_str = ",".join(values_list)
        cmd = f"INSERT INTO {name} {cols_str} VALUES {values_str};"
        mycursor.execute(cmd)
        mydb.commit()
        print(f"Data inserted into table: {name}")
    except Exception as err:
        with open("error.txt", "a") as fs:
            fs.write(f"{datetime.datetime.now()} Error in inserting_data: {err} \n")

# Adding primary and foreign key constraints
def adding_constraints(mycursor, mydb):
    # Each execute wrapped in try-except to ignore duplicate errors individually
    constraints = [
        ("ALTER TABLE users ADD PRIMARY KEY (id);", 1068),
        ("ALTER TABLE posts ADD PRIMARY KEY (id);", 1068),
        ("ALTER TABLE comments ADD PRIMARY KEY (id);", 1068),
        ("ALTER TABLE albums ADD PRIMARY KEY (id);", 1068),
        ("ALTER TABLE photos ADD PRIMARY KEY (id);", 1068),
        ("ALTER TABLE todos ADD PRIMARY KEY (id);", 1068),

        ("ALTER TABLE posts ADD CONSTRAINT fk_posts_userid FOREIGN KEY (userId) REFERENCES users(id);", 1826),
        ("ALTER TABLE comments ADD CONSTRAINT fk_comments_postid FOREIGN KEY (postId) REFERENCES posts(id);", 1826),
        ("ALTER TABLE albums ADD CONSTRAINT fk_albums_userid FOREIGN KEY (userId) REFERENCES users(id);", 1826),
        ("ALTER TABLE photos ADD CONSTRAINT fk_photos_albumid FOREIGN KEY (albumId) REFERENCES albums(id);", 1826),
        ("ALTER TABLE todos ADD CONSTRAINT fk_todos_userid FOREIGN KEY (userId) REFERENCES users(id);", 1826),
    ]

    for cmd, ignore_err in constraints:
        try:
            mycursor.execute(cmd)
            mydb.commit()
            print(f"Executed: {cmd}")
        except mysql.connector.Error as err:
            if err.errno == ignore_err:
                # Ignore duplicate primary key or foreign key constraint errors
                pass
            else:
                with open("error.txt", "a") as fs:
                    fs.write(f"{datetime.datetime.now()} Error in adding_constraints: {err} \n")



try:
    l = ['users', 'posts', 'comments', 'albums', 'photos', 'todos']
    base_link = 'https://jsonplaceholder.typicode.com/'
    urls = [base_link + x + '/' for x in l]

    mydb, mycursor = db_connect()
    if mydb is None or mycursor is None:
        raise Exception("Failed to connect to database")

    for url in urls:
        creating_table(url, mycursor, mydb)
        inserting_data(url, mycursor, mydb)

    adding_constraints(mycursor, mydb)

    # Updating the data with a while loop and time module
    while True:
        for url in urls:
            inserting_data(url, mycursor, mydb)
        time.sleep(3)

except Exception as err:
    with open("error.txt", "a") as fs:
        fs.write(f"{datetime.datetime.now()} Fatal error: {err} \n")
