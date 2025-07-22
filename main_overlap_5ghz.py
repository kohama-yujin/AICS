from aics_excel_loader import AicsExcelLoader
from wcl import WCL
import csv
from overlap_5ghz_filter import Overlap5GHzFilter


def main():
    # パスを確認・修正
    data_folda = "./AICS/dataset"  # 必要に応じてパスを修正してください
    
    # インスタンス化
    ap = AicsExcelLoader(data_folda + "/AP_coordinate.xlsx")
    location = AicsExcelLoader(data_folda + "/location_coordinate.xlsx")
    rssi = AicsExcelLoader(data_folda + "/measured_RSSI.xlsx")

    print("=== 重複除外 + 5GHzフィルタ実行 ===")
    print("適用フィルタ: 5GHz + MED値優先 + 重複除外")
    
    # 重複除外 + 5GHzフィルタのインスタンス化
    overlap_5ghz_filter = Overlap5GHzFilter(ap.data, rssi.data)
    
    # 結果を格納するリスト
    results = []
    
    for p in range(1, 60):  # 位置P=1から59まで
        try:
            weight, coordinate = overlap_5ghz_filter.get_weight_and_coords(4, p, 3)
            print(f"重複除外 + 5GHzフィルタ結果 位置P={p}の重み: {weight}, 座標: {coordinate}")
            
            # 重みや座標が空でないかチェック
            if not weight or not coordinate:
                print(f"位置P={p}: アクセスポイントが見つかりませんでした（重複除外 + 5GHzフィルタ後）")
                continue
            
            # 推定位置座標 T を計算
            wcl = WCL(weight, coordinate)
            T = wcl.calculate_coordinate()
            
            results.append({
                'position': p,
                'estimated_coordinate': T,
                'weights': weight,
                'anchor_coordinates': coordinate
            })
            
        except Exception as e:
            print(f"重複除外 + 5GHzフィルタ 位置P={p}: エラーが発生しました - {e}")
            continue
    
    print(f"\n重複除外 + 5GHzフィルタ処理完了: {len(results)}個の位置で推定が成功しました")
    
    # 推定座標をまとめて出力
    print("\n=== 重複除外 + 5GHzフィルタ推定位置座標一覧 ===")
    for result in results:
        print(f"位置P={result['position']}: {result['estimated_coordinate']}")
    
    # CSVファイルに結果を出力
    csv_filename = "estimation_results_overlap_5ghz_filter.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # ヘッダーを書き込み
        writer.writerow(['Position', 'X_Coordinate', 'Y_Coordinate'])
        
        # データを書き込み（検出できた位置のみ）
        for result in results:
            position = result['position']  # 実際の位置P番号
            x_coord = result['estimated_coordinate'][0]
            y_coord = result['estimated_coordinate'][1]
            writer.writerow([position, x_coord, y_coord])
    
    print(f"\n結果をCSVファイル '{csv_filename}' に保存しました")
    print(f"検出できた位置: {len(results)}個")
    print(f"検出できなかった位置: {60 - 1 - len(results)}個")


if __name__ == "__main__":
    main()