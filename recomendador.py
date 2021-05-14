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

'''
def filtrado_usuarios(df_rate, df_movies, userId):
    df_movies = df_movies.drop('genre', 1)
    con = sqlite3.connect("Movies.db")
    cur = con.cursor()
    cur.execute("SELECT movieId, rating FROM ratings WHERE userId = " + str(userId))
    userMovies = cur.fetchall()
    con.commit()
    con.close()

    df_user_movies = pd.DataFrame(userMovies, columns=['movieId', 'rating'])
    df_rate_movies = df_rate[~df_rate['userId'].isin([userId])]

    #Filtrando los usuarios que han visto las películas y guardándolas
    userSubset = df_rate_movies[df_rate_movies['movieId'].isin(df_user_movies['movieId'].tolist())]
    print(userSubset)
'''

def filtrado_contenido(df_rate, df_movies, userId):
    #Copiando el marco de datos de la pelicula en uno nuevo ya que no necesitamos la información del género por ahora.
    df_movies_g = df_movies.copy()
    df_movies_g['genre'] = df_movies_g.genre.str.split('|')

    #Para cada fila del marco de datos, iterar la lista de géneros y colocar un 1 en la columna que corresponda
    for index, row in df_movies_g.iterrows():
        for g in row['genre']:
            df_movies_g.at[index, g] = 1
    #Completar los valores NaN con 0 para mostrar que una película no tiene el género de la columna
    df_movies_g = df_movies_g.fillna(0)

    con = sqlite3.connect("Movies.db")
    cur = con.cursor()
    cur.execute("SELECT movieId, rating FROM ratings WHERE userId = " + str(userId))
    userMovies = cur.fetchall()
    con.commit()
    con.close()

    df_user_movies = pd.DataFrame(userMovies, columns=['movieId', 'rating'])
    userMovies = df_movies_g[df_movies_g['movieId'].isin(df_user_movies['movieId'].tolist())]

    #Inicializando el índice para evitar problemas a futuro
    userMovies = userMovies.reset_index(drop=True)

    #Eliminando problemas innecesarios para ahorrar memoria y evitar conflictos
    userGenreTable = userMovies.drop('movieId', 1).drop('title', 1).drop('genre', 1).drop('year', 1)

    #Producto escalar para obtener los pesos
    userProfile = userGenreTable.transpose().dot(df_user_movies['rating'])

    #Ahora llevemos los géneros de cada película al marco de datos original
    genreTable = df_movies_g.set_index(df_movies_g['movieId'])

    #Y eliminemos información innecesaria
    genreTable = genreTable.drop('movieId', 1).drop('title', 1).drop('genre', 1).drop('year', 1)
    
    #Multiplicando los géneros por los pesos para luego calcular el peso promedio
    df_reco = ((genreTable * userProfile).sum(axis=1)) / (userProfile.sum())
    
    #Ordena nuestra recomendación en orden descendente
    df_reco = df_reco.sort_values(ascending=False)

    #Tabla de recomendaciones final
    df_recomendacion = df_movies.loc[df_movies['movieId'].isin(df_reco.head(20).keys())]
    print(df_recomendacion)

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
cur.execute("SELECT userId FROM ratings GROUP BY userId")
userListMal = cur.fetchall()
userList = [item for elem in userListMal for item in elem]
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

#filtrado_usuarios(df_rate, df_movies, 1)
filtrado_contenido(df_rate, df_movies, 1)