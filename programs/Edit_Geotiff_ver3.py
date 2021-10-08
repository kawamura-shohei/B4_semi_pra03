from osgeo import gdal, gdalconst, gdal_array
from PIL import Image
import numpy as np

def main():
    infile_path = "../../src03/AtamiDosyaMap_Difference.tif" # 入力画像パス
    outfile_path = "../../src03/result_Numpy.tif" # 出力画像パス
    max_num = 26.8717193604 # 最大の画素値
    min_num = -25.7181396484    # 最小の画素値

    # tiff読み込み
    img = read_geotiff(infile_path)
    # 1バンドをNumpyに格納
    img_b1_origin = img.GetRasterBand(1).ReadAsArray()

    # コントラスト強調
    img_b1_contrast = enhance_contrast(img_b1_origin, max_num, min_num)

    # tiff書き込み
    write_geotiff(outfile_path, img, img_b1_contrast)


# コントラスト強調を行う関数
def enhance_contrast(src_b1, max, min):
    src_b1 = (src_b1 - min)*255 / (max - min)

    return src_b1


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
    # gdal_array.GDALTypeCodeToNumericTypeCode(dtype) # 型番号 -> 型名 変換

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
