## SpiProtocolaParserCLi

### 介绍

> SpiProtocolaParserCLi：是基于Python 3.7 开发的一个嵌入式CLi应用


### 说明
```
usage: python SpiProtocolaParserCLi.py [-h] [--offset] [--verb] [--info] [--debug]
                       [-p {spi,rda}] [-f F] [-d D] [-v]

欢迎使用本打包工具

optional arguments:
  -h, --help    show this help message and exit
  --offset      使用偏移位置进行拼接
  --verb        打开VERB信息
  --info        打开info信息
  --debug       打开调试信息
  -p {spi,rda}  协议形式: spi 或者 rda
  -f F          逻辑分析仪协议导出数据[*.csv]
  -d D          待拼接图片文件夹 (注意：图片文件夹中文件名请以 `{数字}`.jpg 命名，并且按需从左到右拼接的图片，数字从小到大命名。) (拼接图片保存在 `out/stitching_images` 中。)
  -v            show program's version number and exit
```

