from pandas import read_csv
from pandas import datetime
from matplotlib import pyplot
from statsmodels.tsa.arima.model import ARIMA
import pandas
from statsmodels.tsa.stattools import adfuller
import numpy as np

def parser(x):
    return datetime.strptime(x, '%Y/%m/%d')


series = read_csv('files/bcgold.csv', header=0, parse_dates=[0], squeeze = False, index_col=0, date_parser=parser)
print(series.head())
predict_set = read_csv('files/Date.csv', header=0, parse_dates=[0], index_col=0, date_parser=parser)
pl = []
for item in predict_set:
    pl.append(item)
print(pl)

series.plot()
pyplot.show()
series.index = series.index.to_period('M')
# fit model
model = ARIMA(series['gold'], order=(0,1,0))
model_fit = model.fit()
# summary of fit model
print(model_fit.summary())
# line plot of residuals
residuals = pandas.DataFrame(model_fit.resid)
residuals.plot()
pyplot.show()
# density plot of residuals
residuals.plot(kind='kde')
pyplot.show()
# summary stats of residuals
print(residuals.describe())

model2 = ARIMA(series['bitcoin'], order=(0,1,2))
model_fit2 = model2.fit()
# summary of fit model
print(model_fit2.summary())
# line plot of residuals
residuals2 = pandas.DataFrame(model_fit2.resid)
residuals2.plot()
pyplot.show()
# density plot of residuals
residuals2.plot(kind='kde')
pyplot.show()
# summary stats of residuals
print(residuals2.describe())


print(predict_set[0])
model_fit.predict(predict_set[0])
model_fit2.predict(predict_set[0])