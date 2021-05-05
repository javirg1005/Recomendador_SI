import sqlite3
import pandas as pd
import numpy as np
import csv

def insert_csv_to_table(table_name, n_col, rows):
    con = sqlite3.connect('Movies.db')
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM " + table_name)
    result = cur.fetchall()
    values = ""
    i = 0
    for i in range(n_col):
        values = values + "?,"
    values = values[:-1]
    print(values)
    if result[0][0] == 0:
        cur.executemany("INSERT INTO " + table_name + " VALUES ("+ values + ")", rows)

con = sqlite3.connect("Movies.db")
cur = con.cursor()
file = open("ml-latest-small\\links.csv")
rows = csv.reader(file)
insert_csv_to_table("links", 3, rows)
file = open("ml-latest-small\\movies.csv")
rows = csv.reader(file)
insert_csv_to_table("movies", 3, rows)
file = open("ml-latest-small\\ratings.csv")
rows = csv.reader(file)
insert_csv_to_table("ratings", 4, rows)
file = open("ml-latest-small\\tags.csv")
rows = csv.reader(file)
insert_csv_to_table("tags", 4, rows)

# GET movies
cur.execute("SELECT * FROM ratings")
ratings = cur.fetchall()
con.close()

df_rate = pd.DataFrame(ratings, columns=['userId', 'movieId', 'rating', 'timestamp'])
print(df_rate)

n_users = df_rate.userId.unique().shape[0]
n_movies = df_rate.movieId.unique().shape[0]