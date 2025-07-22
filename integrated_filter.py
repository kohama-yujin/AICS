"""
2.4GHz + カウント + 重複除外の統合フィルタ
"""

import numpy as np
import pandas as pd


class IntegratedFilter:
    def __init__(self, ap, rssi):
        self.ap = ap
        self.rssi = rssi

    def get_weight_and_coords(self, floor, p, l):
        """
        統合フィルタ：2.4GHz + カウント + 重複除外
        
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
        
        # 2. 2.4GHzフィルタを適用（3000MHz以下）
        if "Center Freq(MHz)" not in rssi_floor_data.columns:
            print(f"警告: Floor {floor} に 'Center Freq(MHz)' カラムがありません。")
            return [], []
        
        rssi_24ghz = rssi_floor_data[rssi_floor_data["Center Freq(MHz)"] <= 3000].copy()
        print(f"2.4GHzフィルタ適用: {len(rssi_floor_data)} -> {len(rssi_24ghz)} レコード")
        
        # 3. 指定階数のAPを抽出
        check_str = str(floor) + "F"
        rssi_floor_only = rssi_24ghz[rssi_24ghz["AP_name"].str.contains(check_str)]
        print(f"{floor}階のAP（2.4GHz）\n{rssi_floor_only}\n")
        
        # 4. 位置PのRSSIデータを抽出
        rssi_p = rssi_floor_only[rssi_floor_only["Location index P"] == p]
        print(f"位置PのRSSIデータ（2.4GHz）\n{rssi_p}\n")
        
        # データが空の場合
        if rssi_p.empty:
            print(f"位置P={p}: 2.4GHzフィルタ後にデータが見つかりませんでした")
            return [], []
        
        # 5. カウントベース + MED値でソート
        rssi_sorted = rssi_p.sort_values(by=["Counts (/100)", "MED (dBm)"], ascending=[False, False])
        print(f"カウント + MED値でソート済み\n{rssi_sorted}\n")
        
        # 6. 重複除外（AP_nameが重複しないようにする）
        rssi_med = []
        seen_ap_names = set()  # 重複チェック用のセット
        
        for _, row in rssi_sorted.iterrows():
            ap_name = row["AP_name"]
            if ap_name not in seen_ap_names:  # AP_nameがまだ選ばれていない場合
                rssi_med.append(row)  # 重複していない場合のみ追加
                seen_ap_names.add(ap_name)  # AP_nameを記録
            if len(rssi_med) == l:  # 上位L個を選び終えたら終了
                break
        
        # DataFrameに変換
        if not rssi_med:
            print(f"位置P={p}: 重複除外後にデータが見つかりませんでした")
            return [], []
            
        rssi_med = pd.DataFrame(rssi_med)
        print(f"上位{l}個のRSSI値（重複なし、カウント優先）\n{rssi_med}\n")
        
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