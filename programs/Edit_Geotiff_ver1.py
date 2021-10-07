from osgeo import gdal, gdalconst, gdal_array
from PIL import Image
import numpy as np
import cv2

def main():
    infile_path = "../../src03/AtamiDosya_Difference_Building.tif" # 入力画像パス
    outfile_path = "../../src03/result.tif" # 出力画像パス

    # tiff読み込み
    img = read_geotiff(infile_path)

    # 1バンドをNumpyに格納
    img_b1_origin = img.GetRasterBand(1).ReadAsArray()
    # 二値化
    img_b1_binarized = binarization(img_b1_origin)
    # Numpy -> Pillow の変換
    img_b1_binarized_PIL = Image.fromarray(img_b1_binarized)
    # Pillow -> OpenCV の変換
    img_b1_binarized_CV = pil2cv(img_b1_binarized_PIL)
    # OpenCV -> Pillow の変換
    img_b1_PIL = cv2pil(img_b1_binarized_CV)
    # Pillow -> Numpy の変換
    img_b1_treated = np.array(img_b1_PIL)
    # tiff書き込み
    write_geotiff(outfile_path, img, img_b1_treated)


# 1つのバンドを二値化する関数
def binarization(src_b1):
    threshold = 3 # 閾値
    img_bin = (src_b1> threshold) * 255

    return img_bin


# Pillow -> OpenCV の変換を行う関数
def pil2cv(image):
    new_image = np.array(image, dtype=np.uint8)
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
    return new_image


# OpenCV -> Pillow の変換を行う関数
def cv2pil(image):
    new_image = image.copy()
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGRA2RGBA)
    new_image = Image.fromarray(new_image)
    return new_image


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
