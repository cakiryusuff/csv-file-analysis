from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.cluster import KMeans
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, mean_squared_error
import pandas as pd

class ModelTrainer:
    def __init__(self, data, target_column, model_name, test_size, params):
        self.data = data
        self.target_column = target_column
        self.model_name = model_name
        self.test_size = test_size
        self.params = params
        self.model = None
        self.results = {}

    def preprocess_data(self):
        """Veriyi işleyip eğitim ve test setlerini ayırır."""
        X = self.data.drop(columns=[self.target_column]).select_dtypes(include=["number"])
        y = self.data[self.target_column]
        return train_test_split(X, y, test_size=self.test_size, random_state=42)

    def select_model(self):
        """Modeli seçer ve parametreleri uygular."""
        # Classification modelleri
        if self.model_name == "Logistic Regression Classifier":
            self.model = LogisticRegression(max_iter=int(self.params.get("custom_param", 100)))
        elif self.model_name == "Decision Tree Classifier":
            self.model = DecisionTreeClassifier(criterion=self.params.get("custom_param", "gini"))
        elif self.model_name == "Random Forest Classifier":
            self.model = RandomForestClassifier(n_estimators=int(self.params.get("custom_param", 100)))
        elif self.model_name == "Support Vector Machine Classifier":
            self.model = SVC(kernel=self.params.get("custom_param", "linear"))
        elif self.model_name == "K-Nearest Neighbors Classifier":
            self.model = KNeighborsClassifier(n_neighbors=int(self.params.get("custom_param", 5)))
        elif self.model_name == "Gaussian Naive Bayes Classifier":
            self.model = GaussianNB()
        
        # Regression modelleri
        elif self.model_name == "Linear Regression":
            self.model = LinearRegression()
        elif self.model_name == "Random Forest Regression":
            self.model = RandomForestRegressor(n_estimators=int(self.params.get("custom_param", 100)))
        
        # Clustering modelleri
        elif self.model_name == "K-Means Clustering":
            self.model = KMeans(n_clusters=int(self.params.get("custom_param", 2)))
        else:
            raise ValueError("Geçersiz model seçimi")

    def train_and_evaluate(self):
        """Modeli eğitir ve performansını değerlendirir."""
        # Classification ve Regression için
        if self.model_name in [
            "Logistic Regression Classifier", "Decision Tree Classifier", 
            "Random Forest Classifier", "Support Vector Machine Classifier", 
            "K-Nearest Neighbors Classifier", "Gaussian Naive Bayes Classifier",
            "Linear Regression", "Random Forest Regression"
        ]:
            X_train, X_test, y_train, y_test = self.preprocess_data()
            self.select_model()
            self.model.fit(X_train, y_train)
            y_pred = self.model.predict(X_test)

            if "Classifier" in self.model_name:
                # Classification sonuçları
                self.results = {
                    "accuracy": f"{accuracy_score(y_test, y_pred):.2f}",
                    "model": self.model_name,
                    "params": self.params,
                    "train_size": len(y_train),
                    "test_size": len(y_test),
                    "predictions": list(zip(y_test.tolist(), y_pred.tolist()))
                }
            elif "Regression" in self.model_name:
                # Regression sonuçları
                mse = mean_squared_error(y_test, y_pred)
                self.results = {
                    "mse": f"{mse:.2f}",
                    "model": self.model_name,
                    "params": self.params,
                    "train_size": len(y_train),
                    "test_size": len(y_test),
                    "predictions": list(zip(y_test.tolist(), y_pred.tolist()))
                }

        # Clustering için
        elif self.model_name in ["K-Means Clustering"]:
            X = self.data.select_dtypes(include=["number"])
            self.select_model()
            labels = self.model.fit_predict(X)
            self.results = {
                "model": self.model_name,
                "params": self.params,
                "clusters": labels.tolist()
            }

        return self.results