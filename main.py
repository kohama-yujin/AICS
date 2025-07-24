from aics_excel_loader import AicsExcelLoader
from sample_wcl import SampleWCL
from wcl import WCL
from overlap_ap import Overlapap
import csv
from frequency_filter import FrequencyFilter


def main():
    data_folda = "./dataset"  # フォルダ名

    # インスタンス化
    ap = AicsExcelLoader(data_folda + "/AP_coordinate.xlsx")
    location = AicsExcelLoader(data_folda + "/location_coordinate.xlsx")
    rssi = AicsExcelLoader(data_folda + "/measured_RSSI.xlsx")

    # データの確認
    # print(ap.data)  # シートが1枚の時：データフレーム型
    # print(location.data["3"])  # シートが複数枚の時：辞書型（keyはシート名）
    # print(location.data["4"])  # 処理しやすいよう、シート名を階数に変更している
    # print(rssi.data["3"])  # key指定したdata["3"]等は、データフレーム型
    # print(rssi.data["4"])

    # カラムの確認
    # print(location.data["3"].columns)  # .columnsでカラム名を確認できる
    # print(location.data["3"]["x"])

    # === 5GHzフィルタを適用 ===
    # freq_filter = FrequencyFilter(rssi.data)
    # filtered_rssi_data = freq_filter.filter_5ghz() 

    # # === 2.4GHzフィルタを適用 ===
    freq_filter = FrequencyFilter(rssi.data)
    filtered_rssi_data = freq_filter.filter_24ghz() 



    
    # 授業資料中のWCLを実装（位置P=1から59まで）
    # sampleWcl = SampleWCL(ap.data, rssi.data)
    sampleWcl = SampleWCL(ap.data, filtered_rssi_data) # 5GHzフィルタを適用したRSSIデータを使用


    # デバッグ: RSSIデータの構造を確認
    # print("RSSI data keys:", rssi.data.keys() if hasattr(rssi.data, 'keys') else type(rssi.data))
    # if hasattr(rssi.data, 'keys'):
    #     print("RSSI data['3'] columns:", rssi.data['3'].columns.tolist())
    #     print("RSSI data['3'] 位置Pの値:", rssi.data['3']['Location index P'].unique())

    
    # 結果を格納するリスト
    sample_results = []
    
    for p in range(1, 60):  # 位置P=1から59まで
        try:
            weight, coordinate = sampleWcl.get_weight_and_coords(3, p, 3)
            print(f"位置P={p}の重み: {weight}, 座標: {coordinate}")

            # 重みや座標が空でないかチェック
            if not weight or not coordinate:
                print(f"位置P={p}: アクセスポイントが見つかりませんでした（5GHzフィルタ後）")
                continue
            
            # 推定位置座標 T を計算
            wcl = WCL(weight, coordinate)
            T = wcl.calculate_coordinate()
            print(f"位置P={p}の推定座標(T): {T}")
            
            sample_results.append({
                'position': p,
                'estimated_coordinate': T,
                'weights': weight,
                'anchor_coordinates': coordinate
            })
            
        except Exception as e:
            print(f"SampleWCL 位置P={p}: エラーが発生しました - {e}")
            continue
    
    print(f"\nSampleWCL処理完了: {len(sample_results)}個の位置で推定が成功しました")
    
    # 推定座標をまとめて出力
    # print("\n=== 推定位置座標一覧 ===")
    # for result in sample_results:
    #     print(f"位置P={result['position']}: {result['estimated_coordinate']}")
    
    # CSVファイルに結果を出力（検出できなかった位置は除外）
    csv_filename = "estimation_results_5GHzfilter.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # ヘッダーを書き込み
        writer.writerow(['Position', 'X_Coordinate', 'Y_Coordinate'])
        
        # データを書き込み（検出できた位置のみ）
        for result in sample_results:
            position = result['position']  # これは実際の位置P番号
            x_coord = result['estimated_coordinate'][0]
            y_coord = result['estimated_coordinate'][1]
            writer.writerow([position, x_coord, y_coord])

    print(f"\n結果をCSVファイル '{csv_filename}' に保存しました")
    print(f"検出できた位置: {len(sample_results)}個")
     
    '''
    # アクセスポイントの被りなし（位置P=1から59まで）
    overlapWcl = Overlapap(ap.data, rssi.data)
    
    # 結果を格納するリスト
    overlap_results = []
    
    for p in range(1, 60):  # 位置P=1から59まで
        try:
            weight, coordinate = overlapWcl.get_weight_and_coords(4, p, 3)
            
            # 推定位置座標 T を計算
            wcl = WCL(weight, coordinate)
            T = wcl.calculate_coordinate()
            
            overlap_results.append({
                'position': p,
                'estimated_coordinate': T,
                'weights': weight,
                'anchor_coordinates': coordinate
            })
            
        except Exception as e:
            print(f"Overlapap 位置P={p}: エラーが発生しました - {e}")
            continue
    
    print(f"\nOverlapap処理完了: {len(overlap_results)}個の位置で推定が成功しました")
    
    # 推定座標をまとめて出力
    print("\n=== Overlapap推定位置座標一覧 ===")
    for result in overlap_results:
        print(f"位置P={result['position']}: {result['estimated_coordinate']}")
    
    # CSVファイルに結果を出力
    overlap_csv_filename = "overlap_estimation_results.csv"
    with open(overlap_csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # ヘッダーを書き込み
        writer.writerow(['Position', 'X_Coordinate', 'Y_Coordinate'])
        
        # データを書き込み
        for result in overlap_results:
            position = result['position']
            x_coord = result['estimated_coordinate'][0]
            y_coord = result['estimated_coordinate'][1]
            writer.writerow([position, x_coord, y_coord])
    
    print(f"\nOverlapap結果をCSVファイル '{overlap_csv_filename}' に保存しました")
    '''

if __name__ == "__main__":
    main()






# from aics_excel_loader import AicsExcelLoader
# from sample_wcl import SampleWCL
# from wcl import WCL
# import csv
# import pandas as pd

# def debug_specific_position(sampleWcl, position):
#     """特定位置での詳細デバッグ"""
#     print(f"\n=== 位置{position}の詳細デバッグ ===")
    
#     try:
#         # sample_wcl.pyの処理を段階的に確認
#         rssi_floor_data = sampleWcl.rssi["4"]
#         print(f"4階のRSSIデータ行数: {len(rssi_floor_data)}")
        
#         # 4階APの抽出
#         check_str = "4F"
#         rssi_floor_only = rssi_floor_data[rssi_floor_data["AP_name"].str.contains(check_str)]
#         print(f"4階APのみに絞った行数: {len(rssi_floor_only)}")
#         print(f"4階APの一覧: {rssi_floor_only['AP_name'].unique()}")
        
#         # 位置Pのデータ抽出
#         rssi_p = rssi_floor_only[rssi_floor_only["Location index P"] == position]
#         print(f"位置{position}のデータ行数: {len(rssi_p)}")
        
#         if len(rssi_p) > 0:
#             print(f"位置{position}のRSSI値:")
#             print(rssi_p[["AP_name", "MED (dBm)"]].sort_values(by="MED (dBm)", ascending=False))
            
#             # 上位3個の選択結果
#             rssi_sorted = rssi_p.sort_values(by="MED (dBm)", ascending=False)
#             top3 = rssi_sorted[0:3]
#             print(f"\n選択される上位3個:")
#             for idx, row in top3.iterrows():
#                 ap_coord = sampleWcl.ap[sampleWcl.ap["AP_name"] == row["AP_name"]]
#                 if len(ap_coord) > 0:
#                     print(f"  {row['AP_name']}: RSSI={row['MED (dBm)']} dBm, 座標=({ap_coord['x'].iloc[0]}, {ap_coord['y'].iloc[0]})")
#                 else:
#                     print(f"  {row['AP_name']}: RSSI={row['MED (dBm)']} dBm, 座標=見つからず")
        
#     except Exception as e:
#         print(f"デバッグ中にエラー: {e}")



# def main():
#     data_folda = "./dataset"  # データフォルダのパス
    
#     # Excelファイルの読み込み
#     ap = AicsExcelLoader(data_folda + "/AP_coordinate.xlsx")
#     location = AicsExcelLoader(data_folda + "/location_coordinate.xlsx")
#     rssi = AicsExcelLoader(data_folda + "/measured_RSSI.xlsx")
    
#     # SampleWCLをインスタンス化（RSSIフィルタなし）
#     sampleWcl = SampleWCL(ap.data, rssi.data)
    
#     # ★ デバッグを先に実行（位置26と31のみ）
#     print("=== 差異の大きい位置のデバッグ ===")
#     debug_specific_position(sampleWcl, 26)
#     debug_specific_position(sampleWcl, 31)
    
#     sample_results = []
    
#     for p in range(1, 60):  # 位置P=1～59
#         try:
#             # 第1引数: 階数, 第2引数: 位置P, 第3引数: 上位何個のAPを使うか
#             weight, coordinate = sampleWcl.get_weight_and_coords(4, p, 3)
            
#             if not weight or not coordinate:
#                 print(f"位置P={p}: アクセスポイントが見つかりませんでした")
#                 continue
            
#             wcl = WCL(weight, coordinate)
#             T = wcl.calculate_coordinate()
            
#             # 位置26と31の結果を特別に表示
#             if p in [26, 31]:
#                 print(f"★ 位置P={p}の推定結果: {T}")
#                 print(f"   重み: {weight}")
#                 print(f"   座標: {coordinate}")
            
#             sample_results.append({
#                 'position': p,
#                 'estimated_coordinate': T,
#                 'weights': weight,
#                 'anchor_coordinates': coordinate
#             })
            
#         except Exception as e:
#             print(f"SampleWCL 位置P={p}: エラーが発生しました - {e}")
#             continue
    
#     print(f"\nSampleWCL処理完了: {len(sample_results)}個の位置で推定が成功しました")
    
#     # 結果をCSVに保存
#     csv_filename = "results.csv"
#     with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(['Position', 'X_Coordinate', 'Y_Coordinate'])
#         for result in sample_results:
#             position = result['position']
#             x_coord = result['estimated_coordinate'][0]
#             y_coord = result['estimated_coordinate'][1]
#             writer.writerow([position, x_coord, y_coord])
    
#     print(f"\n結果をCSVファイル '{csv_filename}' に保存しました")
#     print(f"検出できた位置: {len(sample_results)}個")

# if __name__ == "__main__":
#     main()














    