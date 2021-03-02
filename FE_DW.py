
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.preprocessing import OrdinalEncoder
from sklearn.feature_selection import mutual_info_classif
from sklearn.feature_selection import f_regression
from sklearn.feature_selection import f_classif
from itertools import combinations

def val_couts_cols (Dataframe,cols):
  for x in cols:
    print('coluna: {0}, categorias: {1}'.format(x,len(Dataframe[x].value_counts())))
  print('Total Samples :' + str(len(Dataframe)))

def to_type(DataFrame, columns, type):
  DataFrame_aux = DataFrame.copy()
  for col in columns:
      DataFrame_aux[col]=DataFrame_aux[col].astype(type)
  return DataFrame_aux

def remove_incoherence(DataFrame,expression, replace_val, columns=[]):
  if len(columns)==0:
    columns = DataFrame.columns
  
  DataFrame_aux=DataFrame.copy()
  
  if str(replace_val) == str(np.nan):
    DataFrame_aux=DataFrame.replace(expression, replace_val, regex=True) # não usar str.replace pois não aceita np.nan
    return DataFrame_aux
  else: 
    for col in columns:
      while (True): # quando trabalhamos com grupos no regex, ele não é capaz de substituir todos os grupos, então é necessario iterar a cada nova substituição
        DataFrame_aux[col]=DataFrame[col].str.replace(expression, replace_val, regex=True)
        #warnings.filterwarnings('ignore','UserWarning') # para evitar warning quando str.contains chamar expressions contendo groups que não serão utilizados
        num_matchs = len(DataFrame_aux[DataFrame_aux[col].str.contains(expression, na=False)])#  verifica se regex funcionou, caso sim retorna 0, senão retorna o numero de matchs
        DataFrame = DataFrame_aux
        if num_matchs == 0:
            break
    return DataFrame_aux
 
def remove_cat_low_freq(DataFrame, col_name, threshold=0.25):
  cat_freq = (DataFrame[col_name].value_counts())
  cut_low_freq = DataFrame[DataFrame[col_name].isin(cat_freq[cat_freq >= threshold*cat_freq.max()].index)]
  return cut_low_freq

def feature_selection(Dataset, feature, target ,in_out, method='na'): 
  fs_score =[]
  oe = OrdinalEncoder()

  X = (np.array(Dataset[feature])).reshape(-1,1)
  oe.fit(X)
  X_enc = oe.transform(X)

  y = np.array(Dataset[target]).reshape(-1,1)
  oe.fit(y)
  y_enc = oe.transform(y)
  
  if in_out == 'cat_cat': 
    if method == 'chi2':
      fs = SelectKBest(score_func=chi2, k='all') 
    else:
      fs = SelectKBest(score_func=mutual_info_classif, k='all')
    fs.fit(X_enc, y_enc)
    fs_score = fs.scores_
  elif in_out == 'num_num':
    fs = SelectKBest(score_func=f_regression, k='all')
    fs.fit(X, y.ravel())
    fs_score = fs.scores_
  elif in_out == 'num_cat':
    fs = SelectKBest(score_func=f_classif, k='all')
    fs.fit(X, y_enc)
    fs_score = fs.scores_
  elif in_out == 'cat_num':
    fs = SelectKBest(score_func=f_classif, k='all')
    fs.fit(X_enc, y.ravel())
    fs_score = fs.scores_
  else:
    fs_score=[]

  return fs_score

def exclui_outliers(DataFrame, col_name):
  Q1 = DataFrame[col_name].quantile(.25)
  Q3 = DataFrame[col_name].quantile(.75)
  IIQ =Q3 -Q1
  limite_inf = Q1 -1.5*IIQ
  limite_sup = Q3 +1.5*IIQ
  
  return DataFrame[(DataFrame[col_name]>=limite_inf) & (DataFrame[col_name]<=limite_sup)]

def subplot_strip(Dataset,features,target):
  perm_features = list(combinations(features, 2))
  fig, axes = plt.subplots(len(perm_features),1,figsize=(10,len(perm_features)*10))
  
  for i, perm in enumerate(perm_features):
        sns.stripplot(ax=axes[i],data=Dataset,x=perm[0],y=perm[1], hue=target)
  plt.show()

