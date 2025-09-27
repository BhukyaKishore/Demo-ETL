# Database Population Script Documentation

This script is designed to fetch data from a JSON API frim ( JSONPlaceholder) and populate a MySQL database with the retrieved information. It dynamically creates tables based on the JSON structure and inserts data, handling potential duplicate entries and setting up primary and foreign key constraints.

## Table of Contents
1.  [Prerequisites](#prerequisites)
2.  [Script Overview](#script-overview)
3.  [Functions](#functions)
    *   [`db_connect()`](#db_connect)
    *   [`db_close()`](#db_close)
    *   [`creating_table(url)`](#creating_tableurl)
    *   [`inserting_data(url)`](#inserting_dataurl)
    *   [`addding_constraints()`](#addding_constraints)
    *   [`main()`](#main)
4.  [How to Use](#how-to-use)
5.  [Error Handling](#error-handling)

## Prerequisites
Before running this script, ensure you have the following:
*   **Python 3.x** installed.
*   **MySQL Server** running and accessible. The script assumes `localhost` as the host, `root` as the user, and `admin` as the password. **You should change these credentials to match your MySQL setup.**
*   The following Python libraries installed:
    *   `requests`
    *   `pandas`
    *   `mysql-connector-python`

You can install these libraries using pip:
```bash
pip install requests pandas mysql-connector-python
```

## Script Overview
The script performs the following main tasks:
1.  Establishes a connection to a MySQL database (`mydb`). If `mydb` does not exist, it will be created.
2.  Fetches data from a list of specified JSONPlaceholder API endpoints.
3.  For each API endpoint, it dynamically creates a corresponding table in the database, inferring column names and data types from the JSON structure.
4.  Inserts the fetched data into the newly created or existing tables, using `INSERT IGNORE` to prevent errors from duplicate primary keys.
5.  Adds primary key and foreign key constraints to the tables to maintain data integrity.

## Functions

### `db_connect()`
Establishes a global connection to the MySQL database. It attempts to connect to `mydb`. If the database does not exist, it creates it. If a connection already exists and is active, it reuses it. Errors during connection are logged to `error.txt` and the script exits.

### `db_close()`
Closes the global database connection and cursor if they are open.

### `creating_table(url)`
*   **Purpose**: Fetches JSON data from the given URL, normalizes it into a pandas DataFrame, and dynamically creates a MySQL table based on the DataFrame's structure.
*   **Parameters**:
    *   `url` (str): The API endpoint URL to fetch data from.
*   **Details**:
    *   Extracts the table name from the URL.
    *   Infers SQL data types (`INT`, `VARCHAR(600)`, `TINYINT`, `TEXT`) from pandas DataFrame dtypes.
    *   Replaces dots (`.`) in column names with underscores (`_`) to ensure valid SQL identifiers.
    *   Executes a `CREATE TABLE IF NOT EXISTS` statement.
    *   Commits the transaction.

### `inserting_data(url)`
*   **Purpose**: Fetches JSON data, normalizes it, and inserts it into the corresponding MySQL table. It uses `INSERT IGNORE` to skip rows that would cause duplicate primary key errors.
*   **Parameters**:
    *   `url` (str): The API endpoint URL to fetch data from.
*   **Details**:
    *   Handles `NaN` values by inserting `NULL` into the database.
    *   Converts Python `bool` values to `TINYINT` (0 or 1) for MySQL.
    *   Uses `executemany` for efficient bulk insertion.
    *   Commits the transaction.

### `addding_constraints()`
*   **Purpose**: Defines and applies primary key and foreign key constraints to the tables.
*   **Details**:
    *   A dictionary `constraints` specifies the primary and foreign keys for each table (`users`, `posts`, `comments`, `albums`, `photos`, `todos`).
    *   It attempts to add primary keys to the specified columns. Errors related to duplicate primary keys or already existing primary keys are ignored.
    *   It attempts to add foreign keys, linking related tables. Errors related to incorrectly formed constraints, non-existent referenced tables/columns, or duplicate foreign key names are ignored.

### `main()`
*   **Purpose**: The main execution flow of the script.
*   **Details**:
    *   Defines a list of API endpoints to process.
    *   Calls `db_connect()` once at the beginning.
    *   Iterates through the URLs to call `creating_table()` for each.
    *   Calls `addding_constraints()` to set up relationships.
    *   Iterates through the URLs again to call `inserting_data()` for each.
    *   Includes a `try...except...finally` block to ensure `db_close()` is always called.

## How to Use
1.  **Save the script**: Save the provided Python code as `main.py` (or any other `.py` extension).
2.  **Install prerequisites**: Ensure all required Python libraries are installed (`requests`, `pandas`, `mysql-connector-python`).
3.  **Configure MySQL**: Update the `host`, `user`, and `password` in the `db_connect()` function to match your MySQL server credentials.
4.  **Run the script**: Execute the script from your terminal:
    ```bash
    python3 main.py
    ```

## Error Handling
*   The script includes `try-except` blocks in each major function to catch exceptions.
*   Errors are logged to a file named `error.txt` with a timestamp.
*   Database connection errors in `db_connect()` will cause the script to exit.
*   `INSERT IGNORE` is used in `inserting_data()` to gracefully handle duplicate primary key violations without stopping the script.
*   Constraint addition in `addding_constraints()` includes specific error handling to ignore common errors that occur if constraints already exist or are temporarily invalid due to data state.

