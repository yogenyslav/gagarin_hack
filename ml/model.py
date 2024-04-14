import abc
import pickle
from pathlib import Path

import numpy as np
import torch
import torchvision.models as models
from catboost import CatBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from torch import nn


class Model(abc.ABC):
    @abc.abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
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


class ResNet(nn.Module):
    def __init__(self, n_class=2):
        super(ResNet, self).__init__()

        self.resnet = models.resnet18(pretrained=False)
        self.resnet.fc = torch.nn.Identity()

        self.fc = nn.Sequential(
            nn.Linear(
                512,
                256,
            ),
            nn.ReLU(),
            nn.Linear(256, n_class),
        )

    def forward(self, x):
        batch_size, seq_size = x.shape[:2]
        x = self.resnet(x.reshape(batch_size * seq_size, 3, 224, 224))
        x = x.reshape(batch_size, seq_size, 512)
        x = x.mean(1)
        x = self.fc(x)
        return x


class DLModel(Model):
    def __init__(
        self,
    ) -> None:
        self._model = ResNet(5).to("cpu")
        self._le = LabelEncoder()
        self.model.eval()

    @property
    def model(self):
        return self._model

    @property
    def le(self):
        return self._le

    @torch.no_grad
    def predict(self, X: torch.Tensor) -> np.ndarray:
        print(self.le.classes_)
        return self.le.inverse_transform(self.model(X).argmax(1))

    def save(self, dir: str) -> None:
        dir = Path(dir)

        with open(dir / "model.pt", "wb") as f:
            torch.save(self.model, f)

        with open(dir / "le.pkl", "wb") as f:
            pickle.dump(self.le, f)

    def load(self, dir: str) -> None:
        dir = Path(dir)
        with open(dir / "model.pt", "rb") as f:
            self.model.load_state_dict(torch.load(f, map_location=torch.device("cpu")))

        with open(dir / "le.pkl", "rb") as f:
            self._le = pickle.load(f)

    @property
    def classes(self):
        return self.le.classes_


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
        labels = self.model.predict(X).reshape(1, -1)[0]
        return np.array([self.decode_label(label) for label in labels])

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

    @property
    def classes(self):
        return ["blur", "crop", "highlight", "normal", "overlap"]
