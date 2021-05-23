#librería de manipulación de dataframes
import pandas as pd
#Funciones matemáticas, necesitaremos sólo importar la función sqrt
from math import sqrt
import numpy as np
import matplotlib.pyplot as plt


#GUIA SEGUIDA: https://www.statdeveloper.com/recomendaciones-basado-en-filtrado-colaborativo-en-python/

movies_df = pd.read_csv('ml-latest-small/movies.csv')
ratings_df = pd.read_csv('ml-latest-small/ratings.csv')

movies_df.head()

#Utilizar expresiones regulares para encontrar un año guardado entre paréntesis
#Especificamos los paréntesis de forma tal de que no haya problemas con las películas que tiene el año en sus títulos
movies_df['year'] = movies_df.title.str.extract('(<img loading="lazy" alt="\d\d\d\d" title="Rendered by QuickLaTeX.com" height="2" width="3" style="vertical-align: -4px;" data-src="https://www.statdeveloper.com/wp-content/ql-cache/quicklatex.com-6bed55770ce78fa33f73530474cdaed1_l3.png" class="ql-img-inline-formula quicklatex-auto-format lazyload" src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="><noscript><img loading="lazy"   alt="\d\d\d\d" title="Rendered by QuickLaTeX.com" height="2" width="3" style="vertical-align: -4px;" data-src="https://www.statdeveloper.com/wp-content/ql-cache/quicklatex.com-6bed55770ce78fa33f73530474cdaed1_l3.png" class="ql-img-inline-formula quicklatex-auto-format lazyload" src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==" /><noscript><img loading="lazy" src="https://www.statdeveloper.com/wp-content/ql-cache/quicklatex.com-6bed55770ce78fa33f73530474cdaed1_l3.png" class="ql-img-inline-formula quicklatex-auto-format" alt="\d\d\d\d" title="Rendered by QuickLaTeX.com" height="2" width="3" style="vertical-align: -4px;"/></noscript>)',expand=False)
#Sacando los paréntesis
movies_df['year'] = movies_df.year.str.extract('(\d\d\d\d)',expand=False)
#Sacando los años de la columna 'title'
movies_df['title'] = movies_df.title.str.replace('(<img loading="lazy" alt="\d\d\d\d" title="Rendered by QuickLaTeX.com" height="2" width="3" style="vertical-align: -4px;" data-src="https://www.statdeveloper.com/wp-content/ql-cache/quicklatex.com-6bed55770ce78fa33f73530474cdaed1_l3.png" class="ql-img-inline-formula quicklatex-auto-format lazyload" src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="><noscript><img loading="lazy"   alt="\d\d\d\d" title="Rendered by QuickLaTeX.com" height="2" width="3" style="vertical-align: -4px;" data-src="https://www.statdeveloper.com/wp-content/ql-cache/quicklatex.com-6bed55770ce78fa33f73530474cdaed1_l3.png" class="ql-img-inline-formula quicklatex-auto-format lazyload" src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==" /><noscript><img loading="lazy" src="https://www.statdeveloper.com/wp-content/ql-cache/quicklatex.com-6bed55770ce78fa33f73530474cdaed1_l3.png" class="ql-img-inline-formula quicklatex-auto-format" alt="\d\d\d\d" title="Rendered by QuickLaTeX.com" height="2" width="3" style="vertical-align: -4px;"/></noscript>)', '')
#Aplicando la función strip para sacar los espacios finales que pudiera haber
movies_df['title'] = movies_df['title'].apply(lambda x: x.strip())

#Eliminando la columna géneros
movies_df = movies_df.drop('genres', 1)

movies_df.head()
ratings_df.head()

#Drop elimina una fila en particular o columna dentro de un dataframe
ratings_df = ratings_df.drop('timestamp', 1)

#inicio de filtrado

userInput = [
            {'title':'Breakfast Club, The', 'rating':5},
            {'title':'Toy Story', 'rating':3.5},
            {'title':'Jumanji', 'rating':2},
            {'title':"Pulp Fiction", 'rating':5},
            {'title':'Akira', 'rating':4.5}
         ] 
inputMovies = pd.DataFrame(userInput)

#Filtrar las películas por título
inputId = movies_df[movies_df['title'].isin(inputMovies['title'].tolist())]
#Luego juntarlas para obtener el movieId. Implícitamente, lo está uniendo por título.
inputMovies = pd.merge(inputId, inputMovies)
#Eliminando información que no utilizaremos del dataframe de entrada
inputMovies = inputMovies.drop('year', 1)
#Dataframe de entrada final
#Si una película que se agregó no se encuentra, entonces podría no estar en el dataframe 
#original o podría estar escrito de otra forma, por favor revisar mayúscula o minúscula.


#Filtrando los usuarios que han visto las películas y guardándolas
userSubset = ratings_df[ratings_df['movieId'].isin(inputMovies['movieId'].tolist())]
userSubset.head()

#Groupby crea varios dataframes donde todos tienen el mismo valor para la columna especificada como parámetro
userSubsetGroup = userSubset.groupby(['userId'])

#userSubsetGroup.get_group(1130)

#Ordenamiento de forma tal de que los usuarios con más películas en común tengan prioridad
userSubsetGroup = sorted(userSubsetGroup,  key=lambda x: len(x[1]), reverse=True)

#USUARIO X USUARIO

userSubsetGroup = userSubsetGroup[0:100]

#Guardar la Correlación Pearson en un diccionario, donde la clave es el Id del usuario y el valor es el coeficiente
pearsonCorrelationDict = {}

#Para cada grupo de usuarios en nuestro subconjunto 
for name, group in userSubsetGroup:
    #Comencemos ordenando el usuario actual y el ingresado de forma tal que los valores no se mezclen luego
    group = group.sort_values(by='movieId')
    inputMovies = inputMovies.sort_values(by='movieId')
    #Obtener el N para la fórmula
    nRatings = len(group)
    #Obtener los puntajes de revisión para las películas en común
    temp_df = inputMovies[inputMovies['movieId'].isin(group['movieId'].tolist())]
    #Guardarlas en una variable temporal con formato de lista para facilitar cálculos futuros
    tempRatingList = temp_df['rating'].tolist()
    #Pongamos también las revisiones de grupos de usuarios en una lista
    tempGroupList = group['rating'].tolist()
    #Calculemos la Correlación Pearson entre dos usuarios, x e y
    Sxx = sum([i**2 for i in tempRatingList]) - pow(sum(tempRatingList),2)/float(nRatings)
    Syy = sum([i**2 for i in tempGroupList]) - pow(sum(tempGroupList),2)/float(nRatings)
    Sxy = sum( i*j for i, j in zip(tempRatingList, tempGroupList)) - sum(tempRatingList)*sum(tempGroupList)/float(nRatings)

    #Si el denominador es diferente a cero, entonces dividir, sino, la correlación es 0.
    if Sxx != 0 and Syy != 0:
        pearsonCorrelationDict[name] = Sxy/sqrt(Sxx*Syy)
    else:
        pearsonCorrelationDict[name] = 0

pearsonCorrelationDict.items()

pearsonDF = pd.DataFrame.from_dict(pearsonCorrelationDict, orient='index')
pearsonDF.columns = ['similarityIndex']
pearsonDF['userId'] = pearsonDF.index
pearsonDF.index = range(len(pearsonDF))
pearsonDF.head()

topUsers=pearsonDF.sort_values(by='similarityIndex', ascending=False)[0:50]
topUsers.head()

topUsersRating=topUsers.merge(ratings_df, left_on='userId', right_on='userId', how='inner')
topUsersRating.head()

#Se multiplica la similitud de los puntajes de los usuarios
topUsersRating['weightedRating'] = topUsersRating['similarityIndex']*topUsersRating['rating']
topUsersRating.head()

#Se aplica una suma a los topUsers luego de agruparlos por userId
tempTopUsersRating = topUsersRating.groupby('movieId').sum()[['similarityIndex','weightedRating']]
tempTopUsersRating.columns = ['sum_similarityIndex','sum_weightedRating']
tempTopUsersRating.head()

#Se crea un dataframe vacío
recommendation_df = pd.DataFrame()
#Ahora se toma el promedio ponderado
recommendation_df['weighted average recommendation score'] = tempTopUsersRating['sum_weightedRating']/tempTopUsersRating['sum_similarityIndex']
recommendation_df['movieId'] = tempTopUsersRating.index
recommendation_df.head()

recommendation_df = recommendation_df.sort_values(by='weighted average recommendation score', ascending=False)
recommendation_df.head(10)

movies_df.loc[movies_df['movieId'].isin(recommendation_df.head(10)['movieId'].tolist())]

