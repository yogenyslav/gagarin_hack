import abc

import numpy as np
import pandas as pd
import scipy.stats as stats
from scipy.signal import medfilt


class DataProcess(abc.ABC):
    @abc.abstractmethod
    def prepare_data(self, raw_data: np.ndarray) -> pd.DataFrame:
        pass

    @abc.abstractmethod
    def prepare_from_bin(self, bin_path: str) -> pd.DataFrame:
        pass


class SignalProcess(DataProcess):
    def __init__(
        self,
        denoize: bool = False,
        median_filter: bool = False,
    ) -> None:
        self._denoize = denoize
        self._median_filter = median_filter

    # Time and frequency domains
    @staticmethod
    def rms(y: np.ndarray):
        return np.sqrt(np.mean(y**2))

    @staticmethod
    def power(y: np.ndarray):
        return np.mean(y**2)

    @staticmethod
    def peak(y: np.ndarray):
        return np.max(np.abs(y))

    @staticmethod
    def p2p(y: np.ndarray):
        return np.ptp(y)

    @staticmethod
    def crest_factor(y: np.ndarray):
        return np.max(np.abs(y)) / np.sqrt(np.mean(y**2))

    @staticmethod
    def skew(y: np.ndarray):
        return stats.skew(y, nan_policy="omit")

    @staticmethod
    def kurtosis(y: np.ndarray):
        return stats.kurtosis(y)

    @staticmethod
    def form_factor(y: np.ndarray):
        return np.sqrt(np.mean(y**2)) / np.mean(y)

    @staticmethod
    def pulse_indicator(y: np.ndarray):
        return np.max(np.abs(y)) / np.mean(y)

    @staticmethod
    def denoize(dataset: np.ndarray, threshold: float = 0.05) -> np.ndarray:
        cleaned_dataset = dataset.copy()
        for i in range(len(dataset)):
            max_val = np.max(np.abs(dataset[i, 0]))
            silence_mask = np.abs(dataset[i, 0]) > threshold * max_val
            cleaned_dataset[i, 0] = dataset[i, 0][silence_mask]
        return cleaned_dataset

    @staticmethod
    def median_filter(dataset: np.ndarray) -> np.ndarray:
        cleaned_dataset = dataset.copy()
        for i in range(len(dataset)):
            cleaned_dataset[i, 0] = medfilt(dataset[i, 0], kernel_size=35)
        return cleaned_dataset

    def prepare_from_bin(self, bin_path: str) -> pd.DataFrame:
        data = pd.Series(np.fromfile(bin_path, dtype="uint8"))
        raw_data = data.value_counts().sort_index().values[None]

        return self.prepare_data(raw_data)

    def prepare_data(self, raw_data: np.ndarray) -> pd.DataFrame:
        assert raw_data.ndim == 2

        if self._median_filter:
            raw_data = self.median_filter(raw_data)

        if self._denoize:
            raw_data = self.denoize(raw_data)

        df = pd.DataFrame()
        df["min_t"] = [np.min(y) for y in raw_data[:]]
        df["max_t"] = [np.max(y) for y in raw_data[:]]
        df["mean_t"] = [np.mean(y) for y in raw_data[:]]
        df["rms_t"] = [SignalProcess.rms(y) for y in raw_data[:]]
        df["var_t"] = [np.var(y) for y in raw_data[:]]
        df["std_t"] = [np.std(y) for y in raw_data[:]]
        df["power_t"] = [SignalProcess.power(y) for y in raw_data[:]]
        df["peak_t"] = [SignalProcess.peak(y) for y in raw_data[:]]
        df["p2p_t"] = [SignalProcess.p2p(y) for y in raw_data[:]]
        df["crest_factor_t"] = [SignalProcess.crest_factor(y) for y in raw_data[:]]
        df["skew_t"] = [SignalProcess.skew(y) for y in raw_data[:]]
        df["kurtosis_t"] = [SignalProcess.kurtosis(y) for y in raw_data[:]]
        df["form_factor_t"] = [SignalProcess.form_factor(y) for y in raw_data[:]]
        df["pulse_indicator_t"] = [
            SignalProcess.pulse_indicator(y) for y in raw_data[:]
        ]

        # fft_data = [fft(y) for y in raw_data[:, 0]]
        # fft_data = [np.abs(y ** 2) / len(y) for y in raw_data[:, 0]]

        # df["max_f"] = [np.max(y) for y in fft_data]
        # df["sum_f"] = [np.sum(y) for y in fft_data]
        # df["mean_f"] = [np.mean(y) for y in fft_data]
        # df["var_f"] = [np.var(y) for y in fft_data]
        # df["peak_f"] = [SignalProcess.peak(y) for y in fft_data]
        # df["skew_f"] = [SignalProcess.skew(y) for y in fft_data]
        # df["kurtosis_f"] = [SignalProcess.kurtosis(y) for y in fft_data]

        # df["target"] = raw_data[:, 1]

        return df
