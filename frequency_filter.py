import pandas as pd

class FrequencyFilter:
    def __init__(self, data, threshold_mhz=5000):
        self.data = data
        self.threshold = threshold_mhz

    def filter_5ghz(self):
        """
        5GHz帯（例：5000MHz以上）のデータのみ残す
        data: dict型（各階のシートがDataFrame）
        """
        filtered = {}
        for floor, df in self.data.items():
            if "Center Freq(MHz)" not in df.columns:
                print(f"Floor {floor} has no 'Center Freq(MHz)' column.")
                continue
            filtered[floor] = df[df["Center Freq(MHz)"] >= self.threshold]
        return filtered



# # 5GHzフィルタをかける
#     freq_filter = FrequencyFilter(rssi.data)
#     rssi.data = freq_filter.filter_5ghz()