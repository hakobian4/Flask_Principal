import pandas as pd
from scipy import stats
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn import metrics


class Crdata():
    def __init__(self):

        self.data = pd.read_csv('data.csv')

        self.data = self.data.drop(columns = "Unnamed: 0")
        self.data = self.data.drop(columns = "url")
        self.data = self.data.drop(columns = "num_bathrooms")

        self.data['area'] = self.data['area'].fillna(value = self.data['area'].mean())
        self.data['price'] = self.data['price'].fillna(value = self.data['price'].mean())
        self.data['condition'] = self.data['condition'].fillna(value = stats.mode(self.data['condition'])[0][0])
        self.data['building_type'] = self.data['building_type'].fillna(value = stats.mode(self.data['building_type'])[0][0])

        self.X = self.data
        self.X = pd.get_dummies(self.X, drop_first = True)
        self.Y = self.X[['price', 'area']]
        self.Y = self.Y.drop('area', axis = 1)
        self.X = self.X.drop('price', axis = 1)
        

        self.data['conditions'] = self.data['condition']
        self.data['districts'] = self.data['district']
        self.data['streets'] = self.data['street']
        self.data['regions'] = self.data['region']
        self.data['building_types'] = self.data['building_type']

    def home_param(self, district, street, max_floor, building_type, area, condition, floor, num_rooms, ceiling_height):

        X = self.X.loc[0 : 1]
        
        X = X.drop(1, axis = 0)
        cols = X.columns
        for col in cols:
            X[col] = 0

        for j in cols:
            if 'district_' + district == j:
                X[j] = 1
                break

        for j in cols:
            if 'street_' + street == j:
                X[j] = 1
                break

        for j in cols:
            if 'building_type_' + building_type == j:
                X[j] = 1
                break

        for j in cols:
            if 'condition_' + condition == j:
                X[j] = 1
                break

        X['max_floor'] = max_floor
        X['area'] = area
        X['floor'] = floor
        X['num_rooms'] = num_rooms
        X['ceiling_height'] = ceiling_height

        return X

    def columns_name(self, col):
        
        return np.unique(np.array(self.data[col]))


    def evaluation(self, district, street, max_floor, building_type, area, condition, floor, num_rooms, ceiling_height):

        X = self.X.values
        Y = self.Y.values
        
        XX = self.home_param(district, street, max_floor, building_type, area, condition, floor, num_rooms, ceiling_height).values.reshape(1,379)

        LinReg = LinearRegression()
        betta = LinReg.fit(X, Y)

        polynom = PolynomialFeatures(degree =1) 
        X_polynom = polynom.fit_transform(X)

        PolyReg = LinearRegression() 
        PolyReg.fit(X_polynom, Y)


        Y_predict_pr = PolyReg.predict(polynom.fit_transform(XX))
        return int(Y_predict_pr)