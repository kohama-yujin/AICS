from aics_excel_loader import AicsExcelLoader
from count import Count
from wcl import WCL


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

    # 授業資料中のWCLを実装
    sampleWcl = Count(ap.data, rssi.data)
    weight, coordinate = sampleWcl.get_weight_and_coords(3, 1, 3)

    # 推定位置座標 T を計算
    wcl = WCL(weight, coordinate)
    T = wcl.calculate_coordinate()

    print(f"推定位置座標 T: {T}")


if __name__ == "__main__":
    main()
