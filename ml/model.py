import abc
import pickle
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MinMaxScaler
from catboost import CatBoostClassifier


class Model(abc.ABC):
    @abc.abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        pass

    @abc.abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        pass

    @abc.abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        pass

    @abc.abstractmethod
    def save(self, dir: str) -> None:
        pass

    @abc.abstractmethod
    def load(self, dir: str) -> None:
        pass

    @property
    @abc.abstractmethod
    def classes(self) -> np.ndarray:
        pass

    def decode_label(self, label: int) -> str:
        return self.classes[label]


class LogReg(Model):
    def __init__(self, **kwargs) -> None:
        self._model = LogisticRegression(**kwargs)
        self._scaler = MinMaxScaler()

    @property
    def model(self):
        return self._model

    @property
    def scaler(self):
        return self._scaler

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        X = self.scaler.fit_transform(X)
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = self._scaler.transform(X)
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        X = self._scaler.transform(X)
        return self.model.predict_proba(X)

    def save(self, dir: str) -> None:
        dir = Path(dir)
        with open(dir / "model.pkl", "wb") as f:
            pickle.dump(self.model, f)

        with open(dir / "scaler.pkl", "wb") as f:
            pickle.dump(self.scaler, f)

    def load(self, dir: str) -> None:
        dir = Path(dir)
        with open(dir / "model.pkl", "rb") as f:
            self._model = pickle.load(f)

        with open(dir / "scaler.pkl", "rb") as f:
            self._scaler = pickle.load(f)

    @property
    def classes(self):
        return ["not_anomaly", "blur"]


class CatBoost(Model):
    def __init__(self, **kwargs) -> None:
        self._model = CatBoostClassifier(**kwargs)
        self._scaler = MinMaxScaler()

    @property
    def model(self):
        return self._model

    @property
    def scaler(self):
        return self._scaler

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        X = self.scaler.fit_transform(X)
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = self._scaler.transform(X)
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        X = self._scaler.transform(X)
        return self.model.predict_proba(X)

    def save(self, dir: str) -> None:
        dir = Path(dir)
        with open(dir / "model.pkl", "wb") as f:
            pickle.dump(self.model, f)

        with open(dir / "scaler.pkl", "wb") as f:
            pickle.dump(self.scaler, f)

    def load(self, dir: str) -> None:
        dir = Path(dir)
        with open(dir / "cb_model.pkl", "rb") as f:
            self._model = pickle.load(f)

        with open(dir / "scaler.pkl", "rb") as f:
            self._scaler = pickle.load(f)

    def decode_label(self, label: str) -> str:
        return label

    @property
    def classes(self):
        return self._model._classes
