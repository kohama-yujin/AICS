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
    freq_filter = FrequencyFilter(rssi.data)
    filtered_rssi_data = freq_filter.filter_5ghz() 

    # # === 2.4GHzフィルタを適用 ===
    # freq_filter = FrequencyFilter(rssi.data)
    # filtered_rssi_data = freq_filter.filter_24ghz() 



    
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
            weight, coordinate = sampleWcl.get_weight_and_coords(4, p, 3)
            print(f"位置P={p}の重み: {weight}, 座標: {coordinate}")

            # 重みや座標が空でないかチェック
            if not weight or not coordinate:
                print(f"位置P={p}: アクセスポイントが見つかりませんでした（5GHzフィルタ後）")
                continue
            
            # 推定位置座標 T を計算
            wcl = WCL(weight, coordinate)
            T = wcl.calculate_coordinate()
            
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
