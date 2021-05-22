import sqlite3
from sre_constants import JUMP
import pandas as pd
import numpy as np
import csv
from scipy.spatial.distance import cosine

global parche

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

def obtenerRatings(usu, movie):
    con = sqlite3.connect("Movies.db")
    cur = con.cursor()
    cur.execute("SELECT rating FROM ratings WHERE userId = "+ str(usu)+" AND movieId = "+str(movie))
    rating = cur.fetchone()
    con.commit()
    con.close()
    return rating[0]

def obtenerUsuarios():
    con = sqlite3.connect("Movies.db")
    cur = con.cursor()
    cur.execute("SELECT userId FROM ratings GROUP BY userId")
    userMovies = cur.fetchall()
    con.commit()
    con.close()
    return userMovies

def obtenerPelis(usu):
    con = sqlite3.connect("Movies.db")
    cur = con.cursor()
    cur.execute("SELECT ratings.movieId, movies.title FROM ratings JOIN movies ON ratings.movieId = movies.movieId WHERE ratings.userId == " + str(usu) + " GROUP BY ratings.movieId ORDER BY movies.movieId ASC")
    userMovies = cur.fetchall()
    cur.execute("SELECT movieId, title FROM movies ORDER BY movieId ASC")
    moviesList = cur.fetchall()
    movies_not_seen = [movie for movie in moviesList if movie not in userMovies]
    con.commit()
    con.close()
    return movies_not_seen

def obtenerIdPelis(usu):
    con = sqlite3.connect("Movies.db")
    cur = con.cursor()
    cur.execute("SELECT movieId FROM ratings WHERE userId = "+ str(usu))
    userMovies = cur.fetchall()
    movieids = []
    for movie in userMovies:
        movieids.append(movie[0])
    con.commit()
    con.close()
    return movieids

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
    '''
    user_rows = list(range(0, n_users))
    item_columns = list(range(0, obtenerNumPelis()[0][0]))

    dif_matrix.index = user_rows
    dif_matrix.columns = item_columns
    '''
    global parche 
    parche = dif_matrix
    return dif_matrix

#VAR: pelii = peli interes, usuario = userid == usuario, df = dataframe
def pred(pelii, usuario, df):
    #calcular la similitud
    movieids = obtenerIdPelis(usuario)
    numerador = 0 #sumatorio
    denominador = 0 #sumatorio
    for rmovie in movieids: #hacer algo para evitar el NaN
        coseno = similitud_coseno(df, rmovie, pelii)
        if coseno == np.NaN:
            print('salta')
        else:
            rateUsu = obtenerRatings(usuario, rmovie)
            aux = coseno * rateUsu
            numerador += aux
            denominador += coseno
            #print('suma')

    calculo = numerador / denominador
    return calculo



def similitud_coseno(df, colum1, colum2): #FALLA EN NaN hay que quitarlos
    aux = df.replace(np.NaN,0)
    scoreDistance = cosine(aux[colum1], aux[colum2])
    return scoreDistance


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

def get_dataframe():
    aux = parche
    return aux