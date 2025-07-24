import numpy as np
import pandas as pd


class Count5GHzFilter:
    def __init__(self, ap, rssi):
        self.ap = ap
        self.rssi = rssi

    def get_weight_and_coords(self, floor, p, l):
        """
        カウント + 5GHzフィルタ
        
        args:
            floor: 階数
            p: Location index P
            l: アンカーノードの個数 L
        
        return:
            weight: 重み
            coordinate: 座標 (x, y)
        """
        
        # 1. 指定階数で計測したデータを抽出
        rssi_floor_data = self.rssi[str(floor)]
        
        # 2. 5GHzフィルタを適用（5000MHz以上）
        if "Center Freq(MHz)" not in rssi_floor_data.columns:
            print(f"警告: Floor {floor} に 'Center Freq(MHz)' カラムがありません。")
            return [], []
        
        rssi_5ghz = rssi_floor_data[rssi_floor_data["Center Freq(MHz)"] >= 5000].copy()
        print(f"5GHzフィルタ適用: {len(rssi_floor_data)} -> {len(rssi_5ghz)} レコード")
        
        # 3. 指定階数のAPを抽出
        check_str = str(floor) + "F"
        rssi_floor_only = rssi_5ghz[rssi_5ghz["AP_name"].str.contains(check_str)]
        print(f"{floor}階のAP（5GHz）\n{rssi_floor_only}\n")
        
        # 4. 位置PのRSSIデータを抽出
        rssi_p = rssi_floor_only[rssi_floor_only["Location index P"] == p]
        print(f"位置PのRSSIデータ（5GHz）\n{rssi_p}\n")
        
        # データが空の場合
        if rssi_p.empty:
            print(f"位置P={p}: 5GHzフィルタ後にデータが見つかりませんでした")
            return [], []
        
        # 5. カウントベース + MED値でソート
        rssi_sorted = rssi_p.sort_values(by=["Counts (/100)", "MED (dBm)"], ascending=[False, False])
        print(f"カウント + MED値でソート済み\n{rssi_sorted}\n")
        
        # 6. 上位L個を取得（重複を許す）
        rssi_med = rssi_sorted[0:l]
        print(f"上位{l}個のRSSI値（カウント優先、重複許可）\n{rssi_med}\n")
        
        # データが不足している場合
        if len(rssi_med) == 0:
            print(f"位置P={p}: データが見つかりませんでした")
            return [], []
        
        # 7. 重みを計算
        weight = []
        min_rssi = float(rssi_med["MED (dBm)"].min())  # 最小の中央値を取得
        for rssi in rssi_med["MED (dBm)"]:
            rssi = float(rssi)
            if rssi == min_rssi:
                weight.append(1.0)  # 最小の中央値の重みを1に設定
            else:
                weight.append(float(10 ** ((rssi - min_rssi) / 10)))   # 最小中央値との差を基に計算
        print(f"重み\n{weight}\n")
        
        # 8. 座標を取得
        coordinate = []
        for rssi_name in rssi_med["AP_name"]:
            coordinate.append(
                (
                    float(self.ap[self.ap["AP_name"] == rssi_name]["x"].iloc[0]),
                    float(self.ap[self.ap["AP_name"] == rssi_name]["y"].iloc[0]),
                )
            )
        print(f"座標\n{coordinate}\n")
        
        return weight, coordinate