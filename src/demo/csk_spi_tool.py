#!/Users/abc/workshop/abc/project/utils/anaconda3/envs/py37/bin/python
# -*- coding:utf-8 -*-
#*************************************************************************
#	> File Name: LSFactoryPacker.py
#	> Author: ThierryCao
#	> Mail: sycao@listenai.com
#	> Created Time: Thu 13 Mar 2021 12:54:08 PM CST
# ************************************************************************

import os, sys, hashlib, signal, shutil
sys.path.append("..") 
from plugins import utils as utils
from plugins import logger as logger


global_big_end = 'little'

global_frame_count = 0
global_frame_head_len = 16

GLOMAL_SPI_NORMAL = False

g_stitich_image_using_offset = False
g_local_logger_debug = False

global_output_directory = {
    'cut_out_images': {
        'dir': 'out/cut_out_images'
    },

    'stitching_images': {
                            'dir':'out/stitching_images',
                            'file': 'out/stitching_images/final.bmp'
    },
    'binary_images': {
        'dir': 'out/binary_images'
    }
    
}

if os.name == 'posix':
    from plugins import console_posix as console
else:
    from plugins import console as console

def exit_app(_signum=0, _frame=0):
    import traceback
    try:
        # 等一等子线程销毁
        # time.sleep(0.5)
        sys.exit(1)
    except:
        traceback.print_exc()
        os._exit(0)

def init():
    signal.signal(signal.SIGINT, exit_app)
    signal.signal(signal.SIGTERM, exit_app)


def is_little_endian():
    global global_big_end
    return True if global_big_end == 'little' else False

def get_spi_frame_mosi_data(data):
    if data[2] == '':
        return 0
    else:
        return int(data[2], 16)

def get_spi_frame_tag(index, frame_list):
    if is_little_endian():
        return ( get_spi_frame_mosi_data(frame_list[index+0]) + get_spi_frame_mosi_data(frame_list[index+1]) * (2**8) )
    else:
        return ( get_spi_frame_mosi_data(frame_list[index+1]) + get_spi_frame_mosi_data(frame_list[index+0]) * (2**8) )

def get_spi_frame_version(index, frame_list):
    return get_spi_frame_mosi_data(frame_list[index+2])

def get_spi_frame_fuid(index, frame_list):
    if is_little_endian():
        return ( get_spi_frame_mosi_data(frame_list[index+3]) + get_spi_frame_mosi_data(frame_list[index+4]) * (2**8) )
    else:
        return ( get_spi_frame_mosi_data(frame_list[index+4]) + get_spi_frame_mosi_data(frame_list[index+3]) * (2**8) )

def get_spi_frame_type(index, frame_list):
    return get_spi_frame_mosi_data(frame_list[index+5])

def get_spi_frame_fmt(index, frame_list):
    return get_spi_frame_mosi_data(frame_list[index+6])


def get_spi_frame_xset(index, frame_list):
    if get_spi_frame_mosi_data(frame_list[index+7]) > 128:
        return (get_spi_frame_mosi_data(frame_list[index+7])  - 0x100 )
    else:
        return get_spi_frame_mosi_data(frame_list[index+7])

def get_spi_frame_yset(index, frame_list):
    if get_spi_frame_mosi_data(frame_list[index+8]) > 128:
        return (get_spi_frame_mosi_data(frame_list[index+8]) - 0x100)
    else:
        return get_spi_frame_mosi_data(frame_list[index+8])

def get_spi_frame_width(index, frame_list):
    if is_little_endian():
        return ( get_spi_frame_mosi_data(frame_list[index+9]) + get_spi_frame_mosi_data(frame_list[index+10]) * (2**8) )
    else:
        return ( get_spi_frame_mosi_data(frame_list[index+10]) + get_spi_frame_mosi_data(frame_list[index+9]) * (2**8) )

def get_spi_frame_heigh(index, frame_list):
    if is_little_endian():
        return ( get_spi_frame_mosi_data(frame_list[index+11]) + get_spi_frame_mosi_data(frame_list[index+12]) * (2**8) )
    else:
        return ( get_spi_frame_mosi_data(frame_list[index+12]) + get_spi_frame_mosi_data(frame_list[index+11]) * (2**8) )

def get_spi_frame_depth(index, frame_list):
    return get_spi_frame_mosi_data(frame_list[index+13])
 
def get_spi_frame_checksum(index, frame_list):
    if is_little_endian():
        return ( get_spi_frame_mosi_data(frame_list[index+14]) + get_spi_frame_mosi_data(frame_list[index+15]) * (2**8) )
    else:
        return ( get_spi_frame_mosi_data(frame_list[index+15]) + get_spi_frame_mosi_data(frame_list[index+14]) * (2**8) )   

def print_spi_frame_head(index, frame_list):
    logger.LOGV('TAG: {}'.format( get_spi_frame_tag(index, frame_list) ), \
            'version: {}'.format( get_spi_frame_version(index, frame_list) ), \
            'fuid: {}'.format( get_spi_frame_fuid(index, frame_list) ), \
            'type: {}'.format( get_spi_frame_type(index, frame_list) ), \
            'fmt: {}'.format( get_spi_frame_fmt(index, frame_list) ), \
            'xset: {}'.format( get_spi_frame_xset(index, frame_list) ), \
            'yset: {}'.format( get_spi_frame_yset(index, frame_list) ), \
            'width: {}'.format( get_spi_frame_width(index, frame_list) ), \
            'heigh: {}'.format( get_spi_frame_heigh(index, frame_list) ), \
            'depth: {}'.format( get_spi_frame_depth(index, frame_list) ), \
            'checksum: {}'.format( get_spi_frame_checksum(index, frame_list) )
        )

def get_spi_rda_line_start_data(index, frame_list):
    line_start = [ 0xff, 0xff, 0xff, 0x2, 0x0, 0x28 ]
    data_start = [ 0xff, 0xff, 0xff, 0x40, 0x0, 0x80 ]
    line_start_data = line_start + data_start
    if is_little_endian():
        return frame_list[index:index + 12] == line_start_data 
    else:
        return frame_list[index:index + 12] == line_start_data 

def get_spi_rda_data_index(index, frame_list):
    return get_spi_rda_line_start_data(index, frame_list) 


def get_spi_frame_data(index, frame_list):
    local_width = get_spi_frame_width(index, frame_list)
    local_heigh = get_spi_frame_heigh(index, frame_list)
    local_checksum = get_spi_frame_checksum(index, frame_list)

    if GLOMAL_SPI_NORMAL:
        return [ get_spi_frame_mosi_data(i) for i in frame_list[index + global_frame_head_len : index + global_frame_head_len + local_width * local_heigh] ]

    frames = int( (global_frame_head_len + local_heigh * local_width) / 128 )
    frames_remainder = int( (global_frame_head_len + local_heigh * local_width) % 128 )
    if frames_remainder > 0:
        frames += 1

    jump_count = 0
    line_count = 0
    frame_data = []
    raw_data = [ get_spi_frame_mosi_data(i) for i in frame_list[index + global_frame_head_len : (index + global_frame_head_len + (frames -1 )*12 + local_width * local_heigh) ] ]
    # print('raw_data:', raw_data)
    #logger.LOGV('raw_data', 'frames:',frames, 'len:', len(raw_data))
    if g_local_logger_debug:
        logger.print_hex(raw_data)

    for i, value in enumerate(raw_data):
        if i > len(raw_data) - 12:
            frame_data.extend(raw_data[i:])
            break

        if jump_count > 0:
            jump_count += -1
            continue
        is_rda_line_start = get_spi_rda_data_index(i, raw_data)
        if is_rda_line_start:
            jump_count = 11
            is_rda_line_start = False
            line_count += 1
            
            continue
        frame_data.append(value)
    #logger.LOGV('frame_data', 'len:', len(frame_data), 'line_count:', line_count) 
    
    
    local_cal_checksum = calc_list_sum(frame_data) & 0xFFFF

    if local_checksum != local_cal_checksum:
        logger.LOGE('SPI checksum fails')
        logger.LOGE(f'spi_checksum:{local_checksum}, calc_checksum:{local_cal_checksum}')
        #return []
        #exit_app()

    return frame_data

def calc_list_sum(list_data):
    from functools import reduce
    from operator import add
    return reduce(add, list_data)

def camera_spi_parse(frame, index, frame_list):
    global global_frame_count
    global_frame_count += 1
    #logger.LOGV(index, global_frame_count)
    print_spi_frame_head(index, frame_list)

    spi_frame_data = get_spi_frame_data(index, frame_list)

    #logger.LOGI('camera_spi_parse: ', len(spi_frame_data))
    # print(spi_frame_data)

    # 生成bin文件
    binary_images_save_path = os.path.join( global_output_directory.get('binary_images').get('dir'), f'{global_frame_count}_{get_spi_frame_width(index, frame_list)}_{get_spi_frame_heigh(index, frame_list)}.bin')
    generate_binary_images(spi_frame_data, output= binary_images_save_path)

    logger.LOGD('generate_binary_images done')
    # 生成裁剪图片
    cut_out_images_save_path = os.path.join(global_output_directory.get('cut_out_images').get('dir'), f'{global_frame_count}_{get_spi_frame_width(index, frame_list)}_{get_spi_frame_heigh(index, frame_list)}.bmp')
    generate_cut_out_images(spi_frame_data, width=get_spi_frame_width(index, frame_list), height=get_spi_frame_heigh(index, frame_list), output=cut_out_images_save_path)
    logger.LOGD('generate_cut_out_images done')
    
    return {'width':get_spi_frame_width(index, frame_list), \
            'heigh': get_spi_frame_heigh(index, frame_list), \
            'xset': get_spi_frame_xset(index, frame_list), \
            'yset': get_spi_frame_yset(index, frame_list), \
            'fuid': get_spi_frame_fuid(index, frame_list), \
            'file_path': cut_out_images_save_path }

def get_spi_frame_info(frame, index, frame_list):
    if is_little_endian():
        if frame[2] == '0x46' and frame_list[index+1][2] == '0x5A' and frame_list[index+2][2] == '0x00':
            return True
        else:
            return False

def get_spi_data(file_name):
    frame_info = list()
    
    spi_data_list = utils.read_list_from_csv(file_name, column_num=-1)
    if not spi_data_list:
        return
    # logger.LOGV(spi_data_list)
    for index, frame in enumerate(spi_data_list):
        if get_spi_frame_info(frame, index, spi_data_list):
            info = {}
            info = camera_spi_parse(frame, index, spi_data_list)
            frame_info.append(info)

    #print(frame_info)
    # 生成拼接图片
    generate_stitch_image(frame_info, global_output_directory.get('stitching_images').get('file') )

def generate_cut_out_images(frame_data, width, height, output):
    utils.write_bin_list_to_bmp(frame_data, width, height, output)

def generate_binary_images(frame_data, output):
    utils.write_bin_list_to_file(frame_data, output)

def generate_stitch_image(frame_info, output):
    global g_stitich_image_using_offset
    if g_stitich_image_using_offset:
        utils.connect_bmp(frame_info, output, using_offset=True)
    else:
        utils.connect_bmp(frame_info, output)


def get_file_full_path(file_dir): 
    L=[] 
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if os.path.splitext(file)[1] == '.jpg' or os.path.splitext(file)[1] == '.bmp':
                L.append(os.path.join(root, file))
    return L   

def stitch_image(pics_dir):

    images_list = get_file_full_path(pics_dir)
    images_list = sorted(images_list, key = lambda f: os.path.splitext(os.path.basename(f))[0] )

    # print(images_list)
    if images_list:
        utils.dirs(global_output_directory.get('stitching_images').get('dir'))
        utils.stitch_image_long_figure(images_list, global_output_directory.get('stitching_images').get('file'))

        print('拼接完成=> {} '.format(global_output_directory.get('stitching_images').get('file')))
    else:
        print(f'拼接失败 目标文件夹: {pics_dir}', images_list)

def set_log_level(level):
    logger.set_log_level(level)

def app_main(file_name):
    if not os.path.isfile(file_name):
        logger.LOGE(f"can't found {file_name}")
        return

    for item in global_output_directory.keys():
        if 'dir' in global_output_directory.get(item).keys():
            utils.dirs(global_output_directory.get(item).get('dir'))

    get_spi_data(file_name)
    table_element_list = list()
    for item in global_output_directory.keys():
        if 'dir' in global_output_directory.get(item).keys():
            if 'file' in global_output_directory.get(item).keys():
                #logger.LOGV(item , '=>', os.path.join(global_output_directory.get(item).get('dir'), global_output_directory.get(item).get('file')))
                item_value = global_output_directory.get(item).get('file')
                table_element_list.append([item, item_value])
            else:
                #logger.LOGV(item , '=>', global_output_directory.get(item).get('dir'))
                item_value = global_output_directory.get(item).get('dir')
                table_element_list.append([item, item_value])
    # 生成结果
    logger.LOGB('\n生成结果')
    print(utils.table_prompt(table_element_list))


    # 显示拼接图
    ret = utils.run_shell('command -v imgcat')
    item = 'stitching_images'
    stitch_image_file_path = global_output_directory.get(item).get('file')

    if ret.returncode == 0 and os.path.isfile(os.path.join( stitch_image_file_path ) ):
        logger.LOGB('\nstitch结果')
        os.system('imgcat {}'.format( stitch_image_file_path ))

def version_print():
    import time
    description = [
['Version', 'v1.0' ],
['Time', time.ctime() ], 
['Author', 'theirrycao' ],
['RELEASE', '支持SPI协议和RDA协议解析，默认是SPI协议' ]
]
    description = utils.table_prompt(description)
    #description = logger.get_yellow_text(description)
    return description

def parse_user_choice():
    import argparse
    args = None
    try:
        parser = argparse.ArgumentParser(description='欢迎使用本打包工具')
        # parser.add_argument("-c", type=int, choices=[1,2], help="芯片类型[1:300x 2:4002][已废弃，使用默认资源，不支持修改]")
        parser.add_argument("--offset", dest="offset", action='store_true', help="使用偏移位置进行拼接")
        parser.add_argument("--verb", dest="verb", action='store_true', help="打开VERB信息")
        parser.add_argument("--info", dest="info", action='store_true', help="打开info信息")
        parser.add_argument("--debug", dest="debug", action='store_true', help="打开调试信息")
        parser.add_argument("-p", type=str, required = False, choices=['spi','rda'], help="协议形式: spi 或者 rda")
        parser.add_argument("-f", type=str, required = False, help="逻辑分析仪协议导出数据[*.csv]")
        parser.add_argument("-d", type=str, required = False, help="待拼接图片文件夹")
        parser.add_argument("-v", action="version", version=version_print())
        
        args = parser.parse_args()
        print('parse_user_choice', args)
        # args = parser.parse_args(choice.split())
    # args = parser.parse_args(['-main', './main.bin', '-cmd', './cmd.bin', '-bias', './bias.bin', '-mlp', './mlp.bin'])
    except Exception as e:
        eprint(e)

    finally:
        return args if args else None

def main():
    global GLOMAL_SPI_NORMAL
    global g_stitich_image_using_offset
    init()

    args = parse_user_choice()
    logger.LOGI(args)
    if not args:
        print('缺乏参数')
        return
    GLOMAL_SPI_NORMAL = True if args.p == 'spi' else False

    if args.offset:
        g_stitich_image_using_offset = True
    if args.debug:
        g_local_logger_debug = True
        set_log_level('dbg')
    if args.info:
        set_log_level('info')
    if args.verb:
        set_log_level('verb')
    if args.f and os.path.isfile(args.f):
        app_main(args.f)
    elif args.d and os.path.isdir(args.d):
        # print(stitch_image)
        stitch_image(args.d)
    elif args.d and not os.path.isdir(args.d):
        print(f'不存在: {args.d}这个文件夹')
    else:
        print(version_print())


if __name__ == '__main__':
    main()
