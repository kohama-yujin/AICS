from aics_excel_loader import AicsExcelLoader
from sample_wcl import SampleWCL
from wcl import WCL
from overlap_ap import Overlapap
from count import Count
from frequency_filter import FrequencyFilter
import csv


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

    # 周波数フィルタ
    freq_filter = FrequencyFilter(rssi.data)
    filtered_5ghz_rssi_data = freq_filter.filter_5ghz()
    filtered_24ghz_rssi_data = freq_filter.filter_24ghz()

    # 授業資料中のWCLを実装
    sampleWcl = SampleWCL(ap.data, rssi.data)
    # 5GHzフィルタを適用して授業資料中のWCLを実装
    filtered_5ghz_sampleWcl = SampleWCL(ap.data, filtered_5ghz_rssi_data)
    # 2.4GHzフィルタを適用して授業資料中のWCLを実装
    filtered_24ghz_sampleWcl = SampleWCL(ap.data, filtered_24ghz_rssi_data)

    # 結果を格納するリスト
    all_results = []
    method_results = []
    floor_results = []
    # 手法リスト
    methods = ["SampleWCL", "5GHz", "24GHz"]
    # 階数リスト
    floors = [3, 4]

    for method in methods:
        method_results = []  # 初期化
        for floor in floors:
            floor_results = []  # 初期化
            for p in range(1, 60):
                try:
                    weight, coordinate = sampleWcl.get_weight_and_coords(floor, p, 3)
                    # 推定位置座標 T を計算
                    wcl = WCL(weight, coordinate)
                    T = wcl.calculate_coordinate()
                    # 推定結果を階数結果リストに追加
                    floor_results.append(
                        {
                            "position": p,
                            "estimated_coordinate": T,
                        }
                    )
                # 例外処理を追加
                except Exception as e:
                    print(
                        f"\033[33mSampleWCL 位置P={p}: エラーが発生しました - {e}\033[0m"
                    )
                    continue
            # 階数ごとの結果を手法結果リストに追加
            method_results.append(
                {
                    "floor": floor,
                    "results": floor_results,
                }
            )
            print(
                f"{floor}階での処理完了: {len(floor_results)}個の位置で推定が成功しました"
            )
        # 手法ごとの推定結果をすべての結果リストに追加
        all_results.append({"name": method, "results": method_results})
        print(f"\033[32m{method}の推定が終わりました\033[0m")

    for method in all_results:
        # CSVファイルに結果を出力
        csv_filename = f'results/{method["name"]}.csv'
        # ファイルオープン
        with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            # ヘッダーを作成
            header = []
            for floor in method["results"]:
                header.extend(
                    [
                        f"{floor['floor']}F-{method['name']}",
                        "X_Coordinate",
                        "Y_Coordinate",
                    ]
                )
            # ヘッダーを書き込み
            writer.writerow(header)
            # データを作成
            data = []
            for floor in method["results"]:
                for results in floor["results"]:
                    position = results["position"]
                    x_coord = results["estimated_coordinate"][0]
                    y_coord = results["estimated_coordinate"][1]
                    data.extend([position, x_coord, y_coord])
            # データを書き込み
            writer.writerow(data)
        print(f"\033[32m結果をCSVファイル '{csv_filename}' に保存しました\033[0m")


if __name__ == "__main__":
    main()
