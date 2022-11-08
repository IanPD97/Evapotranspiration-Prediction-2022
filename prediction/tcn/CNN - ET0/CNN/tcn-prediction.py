from tcn import TCN
import numpy as np
import keras


def saveModels(savename,trained_models):
   """
   Guardar los modelos entrenados
   parametro savename: string con la ruta y el nombre a guardar
   parametro num: cantidad de modelos entrenados en el ensemble
   """
   for i in range(len(trained_models)):
     trained_models[i].save(savename+str(i)+'.h5') # GUARDAR MODELOS ENTRENADOS ex: model_1.h5,model_2.h5...etc

def loadModels(savename,num):
  """
  Cargar los modelos entrenados
  parametro savename: string con la ruta y el nombre que se utilizó en saveModels
  parametro num: cantidad de modelos entrenados y guardados en el ensemble
  """
  models = []
  for i in range(num):
    models.append(keras.models.load_model(savename+str(i)+'.h5',custom_objects={'TCN': TCN}))
  return models

def getMindata(models):
  final = []
  for i in range(len(models)):
    nbfilters = models[i].get_config()['layers'][1]['config']['nb_filters']
    dilations = models[i].get_config()['layers'][1]['config']['dilations']
    lags = models[i].get_config()['layers'][0]['config']['batch_input_shape'][1]
    total = lags+nbfilters+sum(dilations) 
    final.append(total)
  datos = max(final) # Cantidad mínima de datos para predicción = lags + nb_filters + sum(dilations)
  return datos

def getMaxlag(models):
  """
  Obtener la cantidad de datos necesarios hacia atrás para generar la predicción
  retorna un valor de tipo entero que indica lo anterior
  """
  lags = []
  for i in range(len(models)):
    lags.append(models[i].input_shape[1])
  return np.array(lags).max()

def getTest(data, max_lag, i,models):
    """
    Pre-processing of data
    :parameter train: training database
    :parameter test: test database
    """
    test = data[max_lag-models[i].input_shape[1]:]
    return test

# GridSearchCV
def grid(x):
    """
    GridSearch for choosing the bandwidth (h) of the KDE method
    :parametro data: data
    :return: bandwidth(h)
    """
    from sklearn.neighbors import KernelDensity
    from sklearn.model_selection import GridSearchCV
    bandwidths = np.linspace(0, 1, 10)
    gd = GridSearchCV(KernelDensity(kernel='gaussian'),{'bandwidth': bandwidths}, cv=len(x))
    x = np.array(x)
    gd.fit(x.reshape(-1, 1))
    return np.round(gd.best_params_['bandwidth'],2)

# SlideWindow modificado para incluir el último día
def slideWindow(data, n_lags):
    """
    Separates input and output data
    parameter data: data
    parameter n_lags: number of lags used by the model
    """
    X = []
    y = []
    for i in range(n_lags, len(data)):
        X.append(data[(i-n_lags)+1:i+1])
        y.append(data[i])
    X, y = np.array(X), np.array(y)
    X = np.reshape(X,(X.shape[0],X.shape[1],1))
    return X, y

# Point Forecast para tiempo real...
def pointForecast(test,models):
  """
  Forecast para el día siguiente
  parámetro test: datos de test
  """
  max_lag = getMaxlag(models)
  dta = getTest(test.values,max_lag,0,models)
  tst = []
  windows = []
  X = []
  y_pred = []
  for i in range(len(models)):
    tst.append(getTest(dta,max_lag,i,models))
    window,y_test = slideWindow(tst[i],models[i].input_shape[1])
    windows.append(window)
    X.append(windows[i][windows[i].shape[0]-1,:,0].reshape((1,windows[i].shape[1],windows[i].shape[2])))
    y_pred.append(models[i].predict(X[i], verbose=0))
  return y_pred


# Forecast probabilístico para el cálculo del Ensemble
def probabilisticForecast(test,models):
    from sklearn.neighbors import KernelDensity
    """
    Gera distribuição de probabilidade das previsões dos modelos que compõem o ensemble
    :parametro yhats: valores previstos
    :return: distribuição de probabilidade
    """
    yhats = pointForecast(test,models)
    y, ys, yss, kde_l, kde_list = [], [], [], [], []
    for z in range(yhats[0].shape[1]):
        for j in range(yhats[0].shape[0]):
            for i in range(len(yhats)):
                y.append(yhats[i][j,z])
            yy = np.array(y)
            y = []
            ys.append(yy)
        yss.append(ys)
        ys = []

    for i in range(len(yss)):
        for j in range(len(yss[0])):
            band = grid(yss[i][j])
            kde = KernelDensity(kernel='gaussian', bandwidth=band).fit(yss[i][j].reshape(-1, 1))
            kde_l.append(kde)
        kde_list.append(kde_l)
        kde_l = []

    return kde_list