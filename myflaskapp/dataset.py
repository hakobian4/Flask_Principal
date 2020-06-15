import pandas as pd
from scipy import stats
import numpy as np


class Data():

    def __init__(self):

        self.data = pd.read_csv('data.csv')

        self.data = self.data.drop(columns = "Unnamed: 0")
        self.data = self.data.drop(columns = "url")
        self.data = self.data.drop(columns = "num_bathrooms")

        self.data['area'] = self.data['area'].fillna(value = self.data['area'].mean())
        self.data['price'] = self.data['price'].fillna(value = self.data['price'].mean())
        self.data['condition'] = self.data['condition'].fillna(value = stats.mode(self.data['condition'])[0][0])
        self.data['building_type'] = self.data['building_type'].fillna(value = stats.mode(self.data['building_type'])[0][0])

        self.data['conditions'] = self.data['condition']
        self.data['districts'] = self.data['district']
        self.data['streets'] = self.data['street']
        self.data['regions'] = self.data['region']
        self.data['building_types'] = self.data['building_type']
        

    def columns_name(self, col):
        
        return np.unique(np.array(self.data[col]))

    def numerical(self):

        self.data = self.data.values
        index = [1, 2, 4, 6, 8]

        for ind in index:

            unique, counts = np.unique(self.data[ : , ind], return_counts=True)
            a = np.asarray((unique, counts))

            for i in range(6234):
                for j in range(len(a[0])):
                    if self.data[i,ind] == a[0][j]:
                        self.data[i, ind] = a[1][j] / 6234
                        break


# data = Data()
# print(data.data.columns)
# print(np.unique(data.data['street']))




# data = pd.read_csv("myflaskapp/data.csv")

# data = data.drop(columns = "Unnamed: 0")
# data = data.drop(columns = "url")
# data = data.drop(columns = "num_bathrooms")

# data['area'] = data['area'].fillna(value = data['area'].mean())
# data['price'] = data['price'].fillna(value = data['price'].mean())
# data['condition'] = data['condition'].fillna(value = stats.mode(data['condition'])[0][0])
# data['building_type'] = data['building_type'].fillna(value = stats.mode(data['building_type'])[0][0])

# data['conditions'] = data['condition']
# data['districts'] = data['district']
# data['streets'] = data['street']
# data['regions'] = data['region']
# data['building_types'] = data['building_type']
# print(data.columns)

# data = data.values
# index = [1, 2, 4, 6, 8]

# for ind in index:

#     unique, counts = np.unique(data[ : , ind], return_counts=True)
#     a = np.asarray((unique, counts))

#     for i in range(6234):
#         for j in range(len(a[0])):
#             if data[i,ind] == a[0][j]:
#                 data[i, ind] = a[1][j] / 6234
#                 break
# print(data.columns)               
# print(np.unique(data['districts']))