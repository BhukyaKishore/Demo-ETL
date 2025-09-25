
import requests
import pandas as pd
import mysql.connector
import datetime
import time

# Global database connection variables
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
                database="mydb2"
            )
            mycursor = mydb.cursor()
            # Ensure the database exists, then use it
            mycursor.execute("CREATE DATABASE IF NOT EXISTS mydb2;")
            mydb.database = "mydb2" # Set the database for the connection
        except mysql.connector.Error as err:
            with open("error.txt", "a") as fs:
                fs.write(f"{datetime.datetime.now()} Error in db_connect: {err} \n")
            # Exit or raise exception if connection fails
            exit(1)

def db_close():
    global mydb, mycursor
    if mycursor:
        mycursor.close()
    if mydb and mydb.is_connected():
        mydb.close()

def creating_table(url):
    db_connect() # Ensure connection is active
    try:
        res = requests.get(url).json()
        df = pd.json_normalize(res)
        name = url.split('/')[-2] # Extract table name more robustly

        # Generate CREATE TABLE statement
        columns_sql = []
        for col, dtype in df.dtypes.items():
            col_name = col.replace('.', '_') # Replace dots for valid SQL column names
            if 'int' in str(dtype):
                columns_sql.append(f"`{col_name}` INT")
            elif 'object' in str(dtype):
                columns_sql.append(f"`{col_name}` VARCHAR(600)")
            elif 'bool' in str(dtype):
                columns_sql.append(f"`{col_name}` TINYINT") # MySQL uses TINYINT for boolean
            else:
                columns_sql.append(f"`{col_name}` TEXT") # Default for other types
        
        create_table_sql = f"CREATE TABLE IF NOT EXISTS `{name}` ({', '.join(columns_sql)});"
        
        mycursor.execute(create_table_sql)
        mydb.commit() # Commit the table creation

    except Exception as err:
        with open("error.txt", "a") as fs:
            fs.write(f"{datetime.datetime.now()} Error in creating_table for {url}: {err} \n")

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

def addding_constraints():
    db_connect() # Ensure connection is active
    try:
        # Define primary keys and foreign keys for each table
        constraints = {
            'users': {'pk': 'id'},
            'posts': {'pk': 'id', 'fk': {'userId': 'users(id)'}},
            'comments': {'pk': 'id', 'fk': {'postId': 'posts(id)'}},
            'albums': {'pk': 'id', 'fk': {'userId': 'users(id)'}},
            'photos': {'pk': 'id', 'fk': {'albumId': 'albums(id)'}},
            'todos': {'pk': 'id', 'fk': {'userId': 'users(id)'}}
        }

        for table, details in constraints.items():
            # Add Primary Key
            if 'pk' in details:
                try:
                    mycursor.execute(f"ALTER TABLE `{table}` ADD PRIMARY KEY (`{details['pk']}`);")
                    mydb.commit()
                except mysql.connector.Error as err:
                    # Ignore error if primary key already exists or is a duplicate entry
                    if "Duplicate entry" not in str(err) and "Multiple primary key defined" not in str(err) and "Can't write; duplicate key in table" not in str(err):
                        print(f"Warning: Could not add primary key to {table}: {err}")

            # Add Foreign Keys
            if 'fk' in details:
                for col, ref in details['fk'].items():
                    try:
                        fk_name = f"fk_{table}_{col}"
                        mycursor.execute(f"ALTER TABLE `{table}` ADD CONSTRAINT `{fk_name}` FOREIGN KEY (`{col}`) REFERENCES `{ref}`;")
                        mydb.commit()
                        print(f"Foreign key '{fk_name}' added to '{table}'.")
                    except mysql.connector.Error as err:
                        # Ignore error if foreign key already exists or is incorrectly formed (e.g., due to missing referenced table/column)
                        if "Foreign key constraint is incorrectly formed" not in str(err) and "Cannot add foreign key constraint" not in str(err) and "Duplicate foreign key constraint name" not in str(err):
                            print(f"Warning: Could not add foreign key {fk_name} to {table}: {err}")

    except Exception as err:
        with open("error.txt", "a") as fs:
            fs.write(f"{datetime.datetime.now()} Error in addding_constraints: {err} \n")
        print(f"Error adding constraints: {err}")


def main():
    urls_to_process = ['users', 'posts', 'comments', 'albums', 'photos', 'todos']
    base_link = 'https://jsonplaceholder.typicode.com/'
    urls = [base_link + x + '/' for x in urls_to_process]

    try:
        db_connect() # Establish connection once at the beginning

        for url in urls:
            creating_table(url)
        
        addding_constraints()

        for url in urls:
            inserting_data(url)


    except Exception as e:
        with open("error.txt", "a") as fs:
            fs.write(f"{datetime.datetime.now()} An unexpected error occurred in main: {e} \n")
        print(f"An unexpected error occurred: {e}")
    finally:
        db_close() 

if __name__ == "__main__":
    main()


