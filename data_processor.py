from sklearn.preprocessing import MinMaxScaler, StandardScaler, LabelEncoder
import pandas as pd
import numpy as np

class DataProcessor:
    def __init__(self, data):
        self.data = data

    def handle_missing_values(self, method):
        if method:
            for column in self.data.columns:
                if self.data[column].isnull().any():
                    if method == "mean":
                        self.data[column].fillna(self.data[column].mean(), inplace=True)
                    elif method == "median":
                        self.data[column].fillna(self.data[column].median(), inplace=True)
                    elif method == "mode":
                        self.data[column].fillna(self.data[column].mode()[0], inplace=True)

    def normalize(self, method):
        if method:
            numeric_columns = self.data.select_dtypes(include=["number"])
            if method == "minmax":
                scaler = MinMaxScaler()
            elif method == "zscore":
                scaler = StandardScaler()
            self.data[numeric_columns.columns] = scaler.fit_transform(numeric_columns)

    def encode_categorical(self, method):
        if method:
            categorical_columns = self.data.select_dtypes(include=["object", "category"]).columns
            if method == "label":
                label_enc = LabelEncoder()
                for col in categorical_columns:
                    self.data[col] = label_enc.fit_transform(self.data[col])
            elif method == "onehot":
                self.data = pd.get_dummies(self.data, columns=categorical_columns)

    def drop_column(self, column_name):
        if column_name and column_name in self.data.columns:
            self.data.drop(columns=[column_name], inplace=True)

    def drop_row(self, row_index):
        if row_index is not None:
            try:
                row_index = int(row_index)
                if 0 <= row_index < len(self.data):
                    self.data.drop(index=row_index-1, inplace=True)
                    self.data.reset_index(drop=True, inplace=True)
            except ValueError:
                pass
