from osgeo import gdal, gdalconst, gdal_array
import numpy as np

def main():
    infile_path = "../../src03/AtamiDosya_Difference_Building.tif" # 入力画像パス
    outfile_path = "../../src03/result.tif" # 出力画像パス

    # tiff読み込み
    img = read_geotiff(infile_path)

    # なんらかの処理
    img_b1_binarized = binarization(img)    #二値化
    

    # tiff書き込み
    write_geotiff(outfile_path, img, img_b1_binarized)


# 1つのバンドを二値化をする関数
def binarization(src):
    threshold = 3 # 閾値
    img_gray = src.GetRasterBand(1).ReadAsArray()
    img_bin = (img_gray > threshold) * 255

    return img_bin


# tiff画像読み込み関数
def read_geotiff(path):
    # 入力画像読み込み
    src = gdal.Open(path)

    return src


# tiff画像書き込み関数
def write_geotiff(outfile_path, src, edit_b1):
    # X,Yのサイズとバンド数を求める
    xsize = src.RasterXSize
    ysize = src.RasterYSize
    band = src.RasterCount

    # バンドを格納(本実験では1つしかない)
    b1 = edit_b1
    #b1 = src.GetRasterBand(1).ReadAsArray() # 第１バンド numpy arrayに格納

    # データタイプ番号
    dtype = src.GetRasterBand(1).DataType # 型番号 (ex: 6 -> numpy.float32)
    gdal_array.GDALTypeCodeToNumericTypeCode(dtype) # 型番号 -> 型名 変換

    # 出力画像
    output = gdal.GetDriverByName('GTiff').Create(outfile_path, xsize, ysize, band, dtype)

    # 座標系指定
    output.SetGeoTransform(src.GetGeoTransform())

    # 空間情報を結合
    output.SetProjection(src.GetProjection())
    output.GetRasterBand(1).WriteArray(b1)
    output.FlushCache()


if __name__ == '__main__':
        main()
