from osgeo import gdal, gdalconst, gdal_array
import cv2
import numpy as np


# メイン関数
def main():
    infile_path = "../../src03/AtamiDosya_Difference_Building.tif" # 入力画像パス
    outfile_path = "../../src03/result.tif" # 出力画像パス
    img = read_geotiff(infile_path)  # tiff画像読み込み
    write_geotiff(infile_path, outfile_path)


# tiff画像読み込み関数
def read_geotiff(path):
    # 入力画像読み込み（GeotiffでOK）
    img = cv2.imread(path, cv2.IMREAD_COLOR)

    return img

# tiff画像書き込み関数
def write_geotiff(infile_path, outfile_path):
    src = gdal.Open(infile_path)
    # X,Yのサイズとバンド数を求める
    xsize = src.RasterXSize
    ysize = src.RasterYSize
    band = src.RasterCount

    # 第1バンド
    b1 = src.GetRasterBand(1).ReadAsArray() # 第１バンド numpy array

    # データタイプ番号
    dtid = src.GetRasterBand(1).DataType
    gdal_array.GDALTypeCodeToNumericTypeCode(dtid) # 型番号 -> 型名 変換

    # 出力画像
    output = gdal.GetDriverByName('GTiff').Create(outfile_path, xsize, ysize, band, dtid)

    # 座標系指定
    output.SetGeoTransform(src.GetGeoTransform())

    # 空間情報を結合
    output.SetProjection(src.GetProjection())
    output.GetRasterBand(1).WriteArray(b1)
    # output.GetRasterBand(2).WriteArray(b2)
    # output.GetRasterBand(3).WriteArray(b3)
    # output.GetRasterBand(4).WriteArray(b4)
    # output.FlushCache()


if __name__ == '__main__':
        main()
