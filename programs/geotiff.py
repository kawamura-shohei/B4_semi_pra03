# from os import write
from osgeo import gdal,osr
import cv2,os


def write_tiffile(res,path):
  src = gdal.Open(path)

  xsize = src.RasterXSize
  ysize = src.RasterYSize
  band = src.RasterCount

  # height,width = res.shape[0],res.shape[1]
  # res = cv2.resize(res, (int(width*2), int(height*2)))

  # 第1-4バンド
  b3,b2,b1 = cv2.split(res)
  b4 = src.GetRasterBand(4).ReadAsArray()

  # データタイプ番号
  dtid = src.GetRasterBand(1).DataType

  # 出力画像
  output = gdal.GetDriverByName('GTiff').Create('result.tif', xsize, ysize, band, dtid)

  # 座標系指定
  output.SetGeoTransform(src.GetGeoTransform())

  # 空間情報を結合
  output.SetProjection(src.GetProjection())
  output.GetRasterBand(1).WriteArray(b1)
  output.GetRasterBand(2).WriteArray(b2)
  output.GetRasterBand(3).WriteArray(b3)
  output.GetRasterBand(4).WriteArray(b4)
  output.FlushCache()


# 画像パス
path = "./geo.tif"

# 入力画像読み込み（GeotiffでOK）
img = cv2.imread(path, cv2.IMREAD_COLOR)

# ここでimgに対して画像処理を行う

# GEOTIFF画像入出力
write_tiffile(img, path)
