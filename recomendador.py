import sqlite3
import pandas as pd
import numpy as np
import csv

def fill_table(file_name, table_name, n_col):
    file = open("ml-latest-small\\" + file_name, encoding="utf8")
    rows = csv.reader(file)
    next(file)
    insert_csv_to_table(table_name, n_col, rows)

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
    if result[0][0] == 0:
        cur.executemany("INSERT INTO " + table_name + " VALUES ("+ values + ")", rows)
    con.commit()
    con.close()

def filtrado_usuarios(df_rate, df_movies):
    df_movies = df_movies.drop('genre', 1)
    print(df_movies.head())
    print(df_rate.head())


def filtrado_contenido(df_rate, df_movies):
    #Copiando el marco de datos de la pelicula en uno nuevo ya que no necesitamos la información del género por ahora.
    df_movies_g = df_movies.copy()

    #Para cada fila del marco de datos, iterar la lista de géneros y colocar un 1 en la columna que corresponda
    for index, row in df_movies.iterrows():
        for g in row['genre']:
            df_movies_g.at[index, g] = 1
    #Completar los valores NaN con 0 para mostrar que una película no tiene el género de la columna
    df_movies_g = df_movies_g.fillna(0)

    print(df_movies_g.head())

fill_table("links.csv", "links", 3)
fill_table("movies.csv", "movies", 3)
fill_table("ratings.csv", "ratings", 4)
fill_table("tags.csv", "tags", 4)

# GET movies
con = sqlite3.connect("Movies.db")
cur = con.cursor()
cur.execute("SELECT * FROM ratings")
ratings = cur.fetchall()
cur.execute("SELECT * FROM movies")
movies = cur.fetchall()
con.commit()
con.close()

df_movies = pd.DataFrame(movies, columns=['movieId', 'title', 'genre'])
df_rate = pd.DataFrame(ratings, columns=['userId', 'movieId', 'rating', 'timestamp'])

# Se separa año y titulo para un mejor filtrado
df_movies['year'] = df_movies.title.str.extract('(\(\d\d\d\d\))', expand=False)
df_movies['year'] = df_movies.year.str.extract('(\d\d\d\d)', expand=False)
df_movies['title'] = df_movies.title.str.replace('(\(\d\d\d\d\))', '')
df_movies['title'] = df_movies['title'].apply(lambda x: x.strip())

# Se elimina la columna timestamp de ratings ya que no es relevante
df_rate = df_rate.drop('timestamp', 1)

filtrado_usuarios(df_rate, df_movies)
#filtrado_contenido(df_rate, df_movies)
