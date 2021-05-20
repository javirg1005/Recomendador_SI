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

def recomendacion():

    print('Yo recomiendo')

def prediccion():

    print('Yo predizco')

def obtenerNumPelis():
    con = sqlite3.connect("Movies.db")
    cur = con.cursor()
    cur.execute("SELECT count(*) FROM movies")
    userMovies = cur.fetchall()
    con.commit()
    con.close()
    return userMovies

def obtenerMaxIdPeli():
    con = sqlite3.connect("Movies.db")
    cur = con.cursor()
    cur.execute("SELECT max(movieId) FROM movies")
    userMovies = cur.fetchall()
    con.commit()
    con.close()
    return userMovies

def obtenerRatings():
    con = sqlite3.connect("Movies.db")
    cur = con.cursor()
    cur.execute(" ")
    rating = cur.fetchall()
    con.commit()
    con.close()
    return rating

def obtenerUsuarios():
    con = sqlite3.connect("Movies.db")
    cur = con.cursor()
    cur.execute(" ")
    userMovies = cur.fetchall()
    con.commit()
    con.close()
    return userMovies

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
'''

def ajustarMedia(df, n_users, n_items, user_rows, item_columns, movie_list):
    df = df.replace(0, np.NaN)
    df_u = df.mean(axis = 1)
    dif_matrix = np.zeros((n_users + 1, n_items + 1))

    for i, row in df.iterrows():
        #print("Media de fila " + str(i) + ": " + str(df_u[i]))
        for j, value in row.iteritems():
            dif_matrix[i][j] = value - df_u[i]
    
    dif_matrix = pd.DataFrame(dif_matrix)
    dif_matrix = dif_matrix.drop(index=0)
    dif_matrix = dif_matrix.drop(columns=0)

    dif_matrix.index = user_rows
    dif_matrix.columns = item_columns
    dif_matrix = dif_matrix[movie_list]

    user_rows = list(range(0, n_users))
    item_columns = list(range(0, obtenerNumPelis()[0][0]))

    dif_matrix.index = user_rows
    dif_matrix.columns = item_columns

    return dif_matrix

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
#filtrado_contenido(df_rate, df_movies, 1)

n_users = df_rate.userId.unique().shape[0]
n_items = obtenerMaxIdPeli()
n_items = n_items[0][0]

user_rows = list(range(1, n_users + 1))
item_columns = list(range(1, n_items + 1))

data_matrix = np.zeros((n_users, n_items))
for line in df_rate.itertuples():
    data_matrix[line[1]-1, line[2]-1] = line[3]

data_matrix = pd.DataFrame(data_matrix, index=user_rows, columns=item_columns)

movie_list = df_movies['movieId'].tolist()
data_matrix = data_matrix[movie_list]

dif_matrix = ajustarMedia(data_matrix, n_users, n_items, user_rows, item_columns, movie_list)

print(dif_matrix.head(10))