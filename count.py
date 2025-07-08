# カウント回数の多いアクセスポイント選択（重複を許す）
import numpy as np
import pandas as pd 


class Count:
    def __init__(self, ap, rssi):
        self.ap = ap
        self.rssi = rssi

    def get_weight_and_coords(self, floor, p, l):
        rssi_floor_data = self.rssi[str(floor)]

        check_str = str(floor) + "F"
        rssi_floor_only = rssi_floor_data[rssi_floor_data["AP_name"].str.contains(check_str)]
        print(f"{floor}階のAP\n{rssi_floor_only}\n")  # デバッグ用

        rssi_p = rssi_floor_only[rssi_floor_only["Location index P"] == p]
        print(f"位置PのRSSIデータ\n{rssi_p}\n")  # デバッグ用

        # 1. 各APの出現回数を集計
        ap_counts = rssi_p["AP_name"].value_counts().to_dict()

        # 2. RSSIデータにカウント列を追加
        rssi_p["count"] = rssi_p["AP_name"].map(ap_counts)

        # 3. MED (dBm) の値が高く、かつ count が多い順にソート
        rssi_sorted = rssi_p.sort_values(by=["MED (dBm)", "count"], ascending=[False, False])

        # 4. 上位L個をそのまま取得（重複を許す）
        rssi_med = rssi_sorted.head(l)
        print(f"上位{l}個のRSSI値\n{rssi_med}\n")  # デバッグ用

        # 5. 重みを計算
        weight = []
        min_rssi = float(rssi_med["MED (dBm)"].min())
        for rssi in rssi_med["MED (dBm)"]:
            rssi = float(rssi)
            if rssi == min_rssi:
                weight.append(1.0)
            else:
                weight.append(float(10 ** ((rssi - min_rssi) / 10)))
        print(f"重み\n{weight}\n")  # デバッグ用

        # 6. 座標を取得
        coordinate = []
        for rssi_name in rssi_med["AP_name"]:
            ap_info = self.ap[self.ap["AP_name"] == rssi_name]
            if not ap_info.empty:
                coordinate.append(
                    (
                        float(ap_info["x"].iloc[0]),
                        float(ap_info["y"].iloc[0]),
                    )
                )
            else:
                coordinate.append((0.0, 0.0))  # AP名が見つからないときの処理（任意）
        print(f"座標\n{coordinate}\n")  # デバッグ用

        return weight, coordinate
