from osgeo import gdal, gdalconst, gdal_array
from PIL import Image
import numpy as np
import cv2

def main():
    infile_path = "../../src03/result_Numpy.tif" # 入力画像パス
    outfile_path = "../../src03/result_Binarized.tif" # 出力画像パス

    # tiff読み込み
    img = read_geotiff(infile_path)

    # 1バンドをNumpyに格納
    img_b1_origin = img.GetRasterBand(1).ReadAsArray()
    # Numpy -> Pillow の変換
    img_b1_PIL_origin = Image.fromarray(img_b1_origin)
    # Pillow -> OpenCV の変換
    img_b1_CV_origin = pil2cv(img_b1_PIL_origin)

    # コントラスト強調
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    img_clahe = clahe.apply(img_b1_CV_origin)
    
    # 二値化
    ret, img_b1_Bin = cv2.threshold(img_clahe, 170, 255, cv2.THRESH_BINARY)
    # ret, img_b1_Bin = cv2.threshold(img_clahe, 0, 255, cv2.THRESH_OTSU)
    # print("ret: {}".format(ret))

    # 画像の確認
    cv2.imshow("sample", img_b1_Bin)
    cv2.waitKey()
    cv2.destroyAllWindows()

    # OpenCV -> Pillow の変換
    img_b1_PIL_treated = cv2pil(img_b1_Bin)
    # Pillow -> Numpy の変換
    img_b1_treated = np.array(img_b1_PIL_treated)
    # tiff書き込み
    write_geotiff(outfile_path, img, img_b1_treated)


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
