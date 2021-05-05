import sqlite3
import pandas as pd
import numpy as np

# GET movies
con = sqlite3.connect('Movies.db')
cursorObj = con.cursor()
cursorObj.execute("SELECT * FROM ratings")
ratings = cursorObj.fetchall()
con.close()

df_rate = pd.DataFrame(ratings, columns=['userId', 'movieId', 'rating', 'timestamp'])
print(df_rate)

n_users = df_rate.userId.unique().shape[0]
n_movies = df_rate.movieId.unique().shape[0]