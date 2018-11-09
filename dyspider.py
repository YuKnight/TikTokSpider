#!/usr/bin/python
# -*- coding: utf-8 -*-

''' 一只抖音小爬虫 '''

#############################
#
#  Author: huang ke
#  Email: huangkwell@163.com
#
#############################


# 导入标准库
import os
import re
import sys
from argparse import ArgumentParser
from time import sleep

# 导入第三方库
import requests

# 导入自定义变量
from head import download_headers, video_headers, Web_UA

# 全局变量
VIDEO_URLS, PAGE = [], 1


def get_all_video_urls(user_id, max_cursor, dytk):
    '''
    获取用户所有视频的源地址url

    :param user_id:     用户抖音id
    :param max_cursor:  下一页地址游标
    :param dytk:        抖音token

    :return:            video urls
    '''
    url = "https://www.amemv.com/aweme/v1/aweme/post/?"
    params = {'user_id': user_id,
              'count': 21,
              'max_cursor': max_cursor,
              'dytk': dytk}
    try:
        response = requests.request(
            "GET", url, params=params, headers=video_headers)
        if response.status_code == 200:
            data = response.json()
            for li in data['aweme_list']:
                name = li.get('share_info').get('share_desc')
                url = li.get('video').get('play_addr').get('url_list')[0]
                VIDEO_URLS.append([name, url])

            # 下拉获取更多视频
            if data['has_more'] == 1 and data.get('max_cursor') != 0:
                sleep(1)
                global PAGE
                print('正在收集第%s页视频地址' % (PAGE))
                PAGE += 1
                return get_all_video_urls(
                    user_id, data.get('max_cursor'), dytk)
            else:
                return VIDEO_URLS
        else:
            print(response.status_code)
            return
    except Exception as e:
        print('failed,', e)
        return


def download_video(index, username, name, url, retry=3):
    '''
    下载视频,显示进度

    :param index:       视频序号
    :param username:    用户名
    :param name:        视频名
    :param url:         视频地址
    :param retry:       重试次数

    :return:            None
    '''
    print("\r正在下载第%s个视频: %s" % (index, name))
    try:
        response = requests.get(
            url,
            stream=True,
            headers=download_headers,
            timeout=15,
            allow_redirects=False)
        video_url = response.headers['Location']
        video_response = requests.get(
            video_url, headers=download_headers, timeout=15)

        # 保存视频，显示下载进度
        if video_response.status_code == 200:
            video_size = int(video_response.headers['Content-Length'])
            with open('%s/%s.mp4' % (username, name), 'wb') as f:
                data_length = 0
                for data in video_response.iter_content(chunk_size=1024):
                    data_length += len(data)
                    f.write(data)
                    done = int(50 * data_length / video_size)
                    sys.stdout.write("\r下载进度: [%s%s]" % (
                        '█' * done, ' ' * (50 - done)))
                    sys.stdout.flush()

        # 失败重试3次，超过放弃
        elif video_response.status_code != 200 and retry:
            retry -= 1
            download_video(index, username, name, url, retry)
        else:
            return
    except Exception as e:
        print('download failed,', name, e)
        return None


def get_name_and_dytk(num):
    '''
    获取用户名和dytk

    :param num:     用户抖音id
    :returns:       username，dytk
    '''
    url = "https://www.amemv.com/share/user/%s" % num
    headers = {'user-agent': Web_UA}
    try:
        response = requests.request("GET", url, headers=headers)
        name = re.findall('<p class="nickname">(.*?)</p>', response.text)[0]
        dytk = re.findall("dytk: '(.*?)'", response.text)[0]
        return name, dytk
    except (TypeError, IndexError):
        sys.stdout.write("提示： 请确认输入的是用户ID，而不是抖音号或单个视频的id\n")
        return None, None
    except requests.exceptions:
        sys.stdout.write("连接错误，未能获取正确数据\n")
        return None, None


def makedir(name):
    '''
    建立用户名文件夹

    :param name:    username
    :return:        None
    '''
    if not os.path.isdir(name):
        os.mkdir(name)
    else:
        pass


def parse_args(args):
    '''
    解析命令行参数

    :param args:    命令行参数
    :return:        新的parse_args函数
    '''
    parser = ArgumentParser()
    parser.add_argument('--uid', dest='user_id', type=int, help='用户的抖音id')
    return parser.parse_args(args)


def get_douyin_id():
    '''
    获取抖音用户id

    :return:    user_id
    '''
    _id1 = get_id_from_cmd(sys.argv[1:])
    if _id1:
        return _id1

    _id2 = get_id_from_input()
    return _id2 if _id2 else None


def get_id_from_cmd(cmd_args):
    '''
    从命令行获取user_id

    :param cmd_args:    命令行参数
    :return:            user_id
    '''
    args = parse_args(cmd_args)
    if not args:
        return

    if args.user_id:
        _id = args.user_id
        return _id
    return None


def get_id_from_input():
    '''
    从用户输入获取user_id

    :return:    user_id
    '''
    _id = input('请输入你要爬取的抖音用户id: ')
    return int(_id)


def is_valid_id(_id):
    '''
    检查用户输入的抖音id是否合法

    :param _id:  user_id
    :return:     bool
    '''
    if not _id:
        return False
    if not re.match('^\\d+$', str(_id).strip()):
        sys.stdout.write("请输入正确格式的抖音id\n")
        return False
    return True


def main():
    '''
    主函数, 下载视频

    :return: None
    '''
    _id = get_douyin_id()
    if not is_valid_id(_id):
        return

    username, dytk = get_name_and_dytk(_id)
    if not (username and dytk):
        return

    makedir(username)
    VIDEO_URLS = get_all_video_urls(_id, 0, dytk)
    for index, item in enumerate(VIDEO_URLS, 1):
        name = item[0]
        if name == '抖音-原创音乐短视频社区':
            name = name + str(index)
        url = item[1]
        download_video(index, username, name, url)
        sleep(1)


if __name__ == '__main__':
    main()
