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
        for j, value in row.iteritems():
            dif_matrix[i][j] = value - df_u[i]
    
    dif_matrix = pd.DataFrame(dif_matrix)
    dif_matrix = dif_matrix.drop(index=0)
    dif_matrix = dif_matrix.drop(columns=0)

    dif_matrix.index = user_rows
    dif_matrix.columns = item_columns
    dif_matrix = dif_matrix[movie_list]
    
    global parche 
    parche = dif_matrix
    return dif_matrix

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

def similitud_coseno(df, colum1, colum2): 
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
con.commit()
con.close()

df_movies = pd.DataFrame(movies, columns=['movieId', 'title', 'genre'])
df_rate = pd.DataFrame(ratings, columns=['userId', 'movieId', 'rating', 'timestamp'])

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

def recov2(usu, rankSize, umbral):
    df = get_dataframe()
    p_recomendadas = obtenerPelis(usu)
    p_vistas = obtenerIdPelis(usu)
    numerador = 0
    denominador = 0
    predicciones = []

    #Comentar apartir de aqui para prueba
    for p_reco in p_recomendadas:
        for p_vis in p_vistas:
            cos = float(similitud_coseno(df,int(p_reco[0]),p_vis))
            if cos >= umbral:
                rateUsu = obtenerRatings(usu, p_vis)
                aux = cos * rateUsu
                numerador += aux
                denominador += cos
        if numerador != 0 and denominador !=0:
            prediccion = numerador/denominador
        else:
            prediccion = -5
        predicciones.append((p_reco,prediccion))
        print(p_reco, prediccion)

    # Prueba con numero de datos limitados para monstrar funcionabilidad
    '''counter = 0
    for p_reco in p_recomendadas:
        for p_vis in p_vistas:
            cos = float(similitud_coseno(df,int(p_reco[0]),p_vis))
            if cos >= umbral:
                rateUsu = obtenerRatings(usu, p_vis)
                aux = cos * rateUsu
                numerador += aux
                denominador += cos
        if numerador != 0 and denominador !=0:
            prediccion = numerador/denominador
        else:
            prediccion = -5
        predicciones.append((p_reco,prediccion))
        print(p_reco, prediccion)
        counter = counter + 1
        if (counter >= 10):
            break
    '''
    predicciones.sort(reverse=True, key=lambda x: x[1])
    print('Yo recomiendo') #print stupido
    return predicciones
    

######################################################## Funciones no funcional (prototipos) #######################################################
def recomendacion(usu, rankSize, umbral):
    p_recomendadas = obtenerPelis(usu)
    p_vistas = obtenerIdPelis(usu)
    df = get_dataframe()
    post_pred = []
    #predicciones de las peliculas no vistas
    for pelii in p_recomendadas:
        predichas = pred_reco(int(pelii[0]), usu, df, umbral)
        print("ID: " + str(pelii[0]) + " Nota: " + str(predichas))
        post_pred.append([int(pelii[0]), predichas])
    
    #mostramos en orden de mayor prediccion de mayor a menos filtrado en el paso anterior
    print(post_pred[:rankSize])
    print('Yo recomiendo')

def pred_reco(pelii, usuario, df, umbral):
    #calcular la similitud
    movieids = obtenerIdPelis(usuario)
    numerador = 0 #sumatorio
    denominador = 0 #sumatorio
    for rmovie in movieids: #hacer algo para evitar el NaN
        coseno = similitud_coseno(df, rmovie, pelii)
        umbralbis = umbral * -1
        if (coseno <= umbralbis or coseno >= umbral):
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

