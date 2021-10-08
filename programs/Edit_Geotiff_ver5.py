from osgeo import gdal, gdalconst, gdal_array
from PIL import Image
import numpy as np
import cv2


def main():
    infile_path = "../../src03/AtamiDosyaMap_Difference.tif" # 入力画像パス
    outfile_path01 = "../../src03/result_Nrmalized.tif" # 正規化された出力画像パス
    outfile_path02 = "../../src03/result_Enhanced.tif" # コントラスト強調された出力画像パス
    outfile_path03 = "../../src03/result_Binarized.tif" # 二値化された出力画像パス
    max_num = 26.8717193604 # 最大の画素値
    min_num = -25.7181396484    # 最小の画素値

    ## tiffを正規化して保存 ##
    img01 = read_geotiff(infile_path)
    img01_b1_origin = img01.GetRasterBand(1).ReadAsArray()  # 1バンドをNumpyに格納
    img01_b1_normalized = normalized(img01_b1_origin, max_num, min_num) # 正規化
    write_geotiff(outfile_path01, img01, img01_b1_normalized)

    ## 正規化されたtiffをコントラスト強調して保存 ##
    img02 = read_geotiff(outfile_path01)
    img02_b1_origin = img02.GetRasterBand(1).ReadAsArray()  # 1バンドをNumpyに格納
    img02_b1_PIL_origin = Image.fromarray(img02_b1_origin)  # Numpy -> Pillow の変換
    img02_b1_CV_origin = pil2cv( img02_b1_PIL_origin)    # Pillow -> OpenCV の変換
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))  # コントラスト強調
    img02_clahe = clahe.apply(img02_b1_CV_origin)
    img02_b1_PIL_treated = cv2pil(img02_clahe) # OpenCV -> Pillow の変換
    img02_b1_treated = np.array(img02_b1_PIL_treated)   # Pillow -> Numpy の変換
    write_geotiff(outfile_path02, img02, img02_b1_treated)

    ## コントラスト強調されたtiffを二値化して保存 ##
    img03 = read_geotiff(outfile_path02)
    img03_b1_origin = img03.GetRasterBand(1).ReadAsArray()  # 1バンドをNumpyに格納
    img03_b1_PIL_origin = Image.fromarray(img03_b1_origin)  # Numpy -> Pillow の変換
    img03_b1_CV_origin = pil2cv( img03_b1_PIL_origin)    # Pillow -> OpenCV の変換
    ret, img03_b1_Bin = cv2.threshold(img03_b1_CV_origin, 170, 255, cv2.THRESH_BINARY)  # 閾値170で二値化
    print("ret: {}".format(ret))
    img03_b1_PIL_treated = cv2pil(img03_b1_Bin) # OpenCV -> Pillow の変換
    img03_b1_treated = np.array(img03_b1_PIL_treated)   # Pillow -> Numpy の変換
    write_geotiff(outfile_path03, img03, img03_b1_treated)


# tiffの正規化を行う関数
def normalized(src_b1, max, min):
    src_b1 = (src_b1 - min)*255 / (max - min)

    return src_b1


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


# OpenCVの画像表示確認
def show_CV(src):
    # 画像の確認
    cv2.imshow("sample", src)
    cv2.waitKey()
    cv2.destroyAllWindows()


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
