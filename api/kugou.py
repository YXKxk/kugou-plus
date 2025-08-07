#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: 潘高
LastEditors: 潘高
Date: 2025-01-27 10:00:00
LastEditTime: 2025-01-27 10:00:00
Description: 酷狗音乐下载API
usage: 在Javascript中调用window.pywebview.api.<methodname>(<parameters>)
'''

import hashlib
import os
import re
import time
import requests
from lxml import etree


class KugouAPI:
    '''酷狗音乐下载API'''

    def __init__(self):
        self.timestamp = str(time.time() * 1000)[:13]
        self.headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'i',
            'range': 'bytes=0-',
            'referer': 'https://www.kugou.com/',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'audio',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            'cookie': 'kg_mid=459098cc19fce2550dc5e1e00a19f9fa; kg_dfid=0jL2CE333LKk105xaB29Q5CL; kg_dfid_collect=d41d8cd98f00b204e9800998ecf8427e; Hm_lvt_aedee6983d4cfc62f509129360d6bb3d=1754165072; HMACCOUNT=6B6773E14E32BE16; KuGoo=KugooID=768747371&KugooPwd=9873E06548E1D33CB913E315F9E5E08E&NickName=%u751f%u6d3b%u7684%u6ecb%u5473&Pic=http://imge.kugou.com/kugouicon/165/20191116/20191116095027988954.jpg&RegState=1&RegFrom=&t=344d6c367ba05daa0358de184e6adaeb25e0cabe9df8cba1f5c49ce8779b079d&a_id=1014&ct=1754165170&UserName=%u006b%u0067%u006f%u0070%u0065%u006e%u0037%u0036%u0038%u0037%u0034%u0037%u0033%u0037%u0031&t1=; KugooID=768747371; t=344d6c367ba05daa0358de184e6adaeb25e0cabe9df8cba1f5c49ce8779b079d; a_id=1014; UserName=kgopen768747371; mid=459098cc19fce2550dc5e1e00a19f9fa; dfid=0jL2CE333LKk105xaB29Q5CL; kg_mid_temp=459098cc19fce2550dc5e1e00a19f9fa; Hm_lpvt_aedee6983d4cfc62f509129360d6bb3d=1754175122',
        }

    def MD5(self, signature_str):
        '''MD5加密'''
        return hashlib.md5(signature_str.encode('utf-8')).hexdigest()

    def kugou_download_rank_songs(self, rank_url=None):
        '''下载排行榜歌曲'''
        try:
            # 如果没有提供URL，使用默认的排行榜页面
            if not rank_url:
                rank_url = 'https://www.kugou.com/yy/html/rank.html'

            print(f"开始下载排行榜歌曲，URL: {rank_url}")

            # 获取排行榜页面
            response = requests.get(rank_url, headers=self.headers).text
            tree = etree.HTML(response)

            # 获取排行榜链接
            top_url = tree.xpath("/html/body/div[3]/div/div[1]/div[1]/ul/li/a/@href")

            download_results = []

            for index, url in enumerate(top_url):
                try:
                    print(f"正在处理排行榜 {index + 1}: {url}")

                    # 获取排行榜详情页面
                    res = requests.get(url, headers=self.headers).text
                    tree = etree.HTML(res)

                    # 获取排行榜标题
                    top_title = tree.xpath("/html/body/div[3]/div/div[1]/div[1]/ul/li/a/@title")
                    if top_title:
                        rank_name = top_title[0]
                    else:
                        rank_name = f"排行榜_{index + 1}"

                    # 获取歌曲ID列表
                    data_eid = tree.xpath('//*[@id="rankWrap"]/div[2]/ul/li/@data-eid')

                    rank_results = {
                        'rank_name': rank_name,
                        'songs': []
                    }

                    for song_index, id_ in enumerate(data_eid):
                        try:
                            # signature=MD5('NVPh5oo715z5DIWAeQlhMDsWXXQV4hwtappid=1014bitrate=0callback=callback123clienttime='+timestamp+'clientver=1000dfid=3x7fD93RtFKs0C9yg30SZhjLfilter=10inputtype=0iscorrection=1isfuzzy=0keyword='+song+'mid=aa67be01ec4f35db52689b116d8b8775page=1pagesize=30platform=WebFilterprivilege_filter=0srcappid=2919token=userid=0uuid=aa67be01ec4f35db52689b116d8b8775NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt')
                            # 生成签名
                            signature_str = 'NVPh5oo715z5DIWAeQlhMDsWXXQV4hwtappid=1014clienttime=' + self.timestamp + 'clientver=20000dfid=0jL2CE333LKk105xaB29Q5CLencode_album_audio_id=' + id_ + 'mid=459098cc19fce2550dc5e1e00a19f9faplatid=4srcappid=2919token=344d6c367ba05daa0358de184e6adaeb25e0cabe9df8cba1f5c49ce8779b079duserid=768747371uuid=459098cc19fce2550dc5e1e00a19f9faNVPh5oo715z5DIWAeQlhMDsWXXQV4hwt'
                            signature = self.MD5(signature_str)

                            # 获取歌曲信息
                            res = requests.get('https://wwwapi.kugou.com/play/songinfo',
                                            headers=self.headers,
                                            params={
                                                'srcappid': '2919',
                                                'clientver': '20000',
                                                'clienttime': self.timestamp,
                                                'mid': '459098cc19fce2550dc5e1e00a19f9fa',
                                                'uuid': '459098cc19fce2550dc5e1e00a19f9fa',
                                                'dfid': '0jL2CE333LKk105xaB29Q5CL',
                                                'appid': '1014',
                                                'platid': '4',
                                                'encode_album_audio_id': id_,
                                                'token': '344d6c367ba05daa0358de184e6adaeb25e0cabe9df8cba1f5c49ce8779b079d',
                                                'userid': '768747371',
                                                'signature': signature,
                                            })

                            song_data = res.json()
                            if 'data' in song_data:
                                song_name = re.sub(r'[/*?"|:<>\\]', '', song_data['data']['audio_name'])
                                song_url = song_data['data']['play_url']

                                # 创建下载目录
                                download_dir = os.path.join(os.getcwd(), 'downloads', rank_name)
                                os.makedirs(download_dir, exist_ok=True)

                                # 下载歌曲
                                try:
                                    res1 = requests.get(song_url, headers=self.headers)
                                    if res1.status_code == 200:
                                        file_path = os.path.join(download_dir, f"{song_name}.mp3")
                                        with open(file_path, 'wb') as f:
                                            f.write(res1.content)

                                        rank_results['songs'].append({
                                            'name': song_name,
                                            'status': 'success',
                                            'file_path': file_path
                                        })
                                        print(f"✓ {song_name} 下载完成")
                                    else:
                                        rank_results['songs'].append({
                                            'name': song_name,
                                            'status': 'failed',
                                            'error': f"HTTP {res1.status_code}"
                                        })
                                        print(f"✗ {song_name} 下载失败: HTTP {res1.status_code}")
                                except Exception as e:
                                    rank_results['songs'].append({
                                        'name': song_name,
                                        'status': 'failed',
                                        'error': str(e)
                                    })
                                    print(f"✗ {song_name} 下载失败: {str(e)}")
                            else:
                                print(f"✗ 获取歌曲信息失败: {song_data}")

                        except Exception as e:
                            print(f"✗ 处理歌曲失败: {str(e)}")
                            continue

                    download_results.append(rank_results)

                except Exception as e:
                    print(f"✗ 处理排行榜失败: {str(e)}")
                    continue

            return {
                'status': 'success',
                'message': '下载完成',
                'results': download_results
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'下载失败: {str(e)}',
                'results': []
            }

    def kugou_search_and_download(self, keyword):
        '''搜索并下载歌曲'''
        try:
            # 搜索歌曲
            signature_str = f'NVPh5oo715z5DIWAeQlhMDsWXXQV4hwtappid=1014bitrate=0clienttime={self.timestamp}clientver=1000dfid=0jL2CE333LKk105xaB29Q5CLfilter=10inputtype=0iscorrection=1isfuzzy=0keyword={ keyword}mid=459098cc19fce2550dc5e1e00a19f9fapage=1pagesize=30platform=WebFilterprivilege_filter=0srcappid=2919token=344d6c367ba05daa0358de184e6adaeb098b50913aea5d155a90562c2760974duserid=768747371uuid=459098cc19fce2550dc5e1e00a19f9faNVPh5oo715z5DIWAeQlhMDsWXXQV4hwt'
            signature = self.MD5(signature_str)

            search_url = 'https://complexsearch.kugou.com/v2/search/song'
            search_params = {
                "srcappid": "2919",
                "clientver": "1000",
                "clienttime": self.timestamp,
                "mid": "459098cc19fce2550dc5e1e00a19f9fa",
                "uuid": "459098cc19fce2550dc5e1e00a19f9fa",
                "dfid": "0jL2CE333LKk105xaB29Q5CL",
                "keyword": keyword,
                "page": "1",
                "pagesize": "30",
                "bitrate": "0",
                "isfuzzy": "0",
                "inputtype": "0",
                "platform": "WebFilter",
                "userid": "768747371",
                "iscorrection": "1",
                "privilege_filter": "0",
                "filter": "10",
                "token": "344d6c367ba05daa0358de184e6adaeb098b50913aea5d155a90562c2760974d",
                "appid": "1014",
                "signature": signature
            }
            # params={
            #     'srcappid': '2919',
            #     'clientver': '20000',
            #     'clienttime': self.timestamp,
            #     'mid': '459098cc19fce2550dc5e1e00a19f9fa',
            #     'uuid': '459098cc19fce2550dc5e1e00a19f9fa',
            #     'dfid': '0jL2CE333LKk105xaB29Q5CL',
            #     'appid': '1014',
            #     'platid': '4',
            #     'encode_album_audio_id': id_,
            #     'token': '344d6c367ba05daa0358de184e6adaeb25e0cabe9df8cba1f5c49ce8779b079d',
            #     'userid': '768747371',
            #     'signature': signature,
            # })

            search_response = requests.get(search_url, headers=self.headers, params=search_params)
            song_ids = re.findall(r'"EMixSongID":"(.*?)"', search_response.text, re.S)
            lists = search_response.json()['data']['lists']
            # print(lists)
            # print(search_response)
            keyword = re.sub(r'[\s\u3000\u00A0]+', ' ', keyword).strip()
            print(lists[0]['FileName'])
            if not song_ids:
                return {
                    'status': 'error',
                    'message': '未找到相关歌曲',
                    'results': []
                }

            download_results = []
            for index,song_id in enumerate(song_ids):
                try:
                    # print(lists[index]['FileName'])
                    if lists[index]['FileName'] != keyword:
                        # print(index)
                        continue
                    # 获取歌曲信息
                    signature_str = 'NVPh5oo715z5DIWAeQlhMDsWXXQV4hwtappid=1014clienttime=' + self.timestamp + 'clientver=20000dfid=0jL2CE333LKk105xaB29Q5CLencode_album_audio_id=' + song_id + 'mid=459098cc19fce2550dc5e1e00a19f9faplatid=4srcappid=2919token=344d6c367ba05daa0358de184e6adaeb25e0cabe9df8cba1f5c49ce8779b079duserid=768747371uuid=459098cc19fce2550dc5e1e00a19f9faNVPh5oo715z5DIWAeQlhMDsWXXQV4hwt'
                    signature = self.MD5(signature_str)

                    res = requests.get('https://wwwapi.kugou.com/play/songinfo',
                                    headers=self.headers,
                                    params={
                                        'srcappid': '2919',
                                        'clientver': '20000',
                                        'clienttime': self.timestamp,
                                        'mid': '459098cc19fce2550dc5e1e00a19f9fa',
                                        'uuid': '459098cc19fce2550dc5e1e00a19f9fa',
                                        'dfid': '0jL2CE333LKk105xaB29Q5CL',
                                        'appid': '1014',
                                        'platid': '4',
                                        'encode_album_audio_id': song_id,
                                        'token': '344d6c367ba05daa0358de184e6adaeb25e0cabe9df8cba1f5c49ce8779b079d',
                                        'userid': '768747371',
                                        'signature': signature,
                                    })

                    song_data = res.json()
                    # print(song_data)
                    if 'data' in song_data:
                        song_name = re.sub(r'[/*?"|:<>\\]', '', song_data['data']['audio_name'])
                        song_url = song_data['data']['play_url']

                        # 创建下载目录
                        download_dir = os.path.join(os.getcwd(), 'downloads', '搜索结果')
                        os.makedirs(download_dir, exist_ok=True)

                        # 下载歌曲
                        try:
                            res1 = requests.get(song_url, headers=self.headers)

                            file_path = os.path.join(download_dir, f"{song_name}.mp3")
                            with open(file_path, 'wb') as f:
                                f.write(res1.content)

                            download_results.append({
                                'name': song_name,
                                'status': 'success',
                                'file_path': file_path
                            })
                            print(f"✓ {song_name} 下载完成")
                            break


                        except Exception as e:
                            download_results.append({
                                'name': song_name,
                                'status': 'failed',
                                'error': str(e)
                            })
                            print(f"✗ {song_name} 下载失败: {str(e)}")
                    else:
                        print(f"✗ 获取歌曲信息失败: {song_data}")

                except Exception as e:
                    print(f"✗ 处理歌曲失败: {str(e)}")
                    continue

            return {
                'status': 'success',
                'message': '搜索下载完成',
                'results': download_results
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'搜索下载失败: {str(e)}',
                'results': []
            }

    def kugou_download_single_song(self, song_id, song_name):
        '''下载单首歌曲'''
        try:
            print(f"正在下载歌曲: {song_name},id:{song_id}")
            # 生成签名
            signature_str = 'NVPh5oo715z5DIWAeQlhMDsWXXQV4hwtappid=1014clienttime=' + self.timestamp + 'clientver=20000dfid=0jL2CE333LKk105xaB29Q5CLencode_album_audio_id=' + song_id + 'mid=459098cc19fce2550dc5e1e00a19f9faplatid=4srcappid=2919token=344d6c367ba05daa0358de184e6adaeb25e0cabe9df8cba1f5c49ce8779b079duserid=768747371uuid=459098cc19fce2550dc5e1e00a19f9faNVPh5oo715z5DIWAeQlhMDsWXXQV4hwt'
            signature = self.MD5(signature_str)

            # 获取歌曲信息
            res = requests.get('https://wwwapi.kugou.com/play/songinfo',
                            headers=self.headers,
                            params={
                                'srcappid': '2919',
                                'clientver': '20000',
                                'clienttime': self.timestamp,
                                'mid': '459098cc19fce2550dc5e1e00a19f9fa',
                                'uuid': '459098cc19fce2550dc5e1e00a19f9fa',
                                'dfid': '0jL2CE333LKk105xaB29Q5CL',
                                'appid': '1014',
                                'platid': '4',
                                'encode_album_audio_id': song_id,
                                'token': '344d6c367ba05daa0358de184e6adaeb25e0cabe9df8cba1f5c49ce8779b079d',
                                'userid': '768747371',
                                'signature': signature,
                            })
            print("下载歌曲："+song_name)
            song_data = res.json()
            if 'data' in song_data:
                song_name = re.sub(r'[/*?"|:<>\\]', '', song_data['data']['audio_name'])
                song_url = song_data['data']['play_url']
                # print("song_url:"+song_url)
                # 创建下载目录
                download_dir = os.path.join(os.getcwd(), 'downloads', '单曲下载')
                os.makedirs(download_dir, exist_ok=True)

                # 下载歌曲
                try:
                    res1 = requests.get(song_url, headers=self.headers)
                    print("下载歌曲"+song_name)

                    file_path = os.path.join(download_dir, f"{song_name}.mp3")
                    with open(file_path, 'wb') as f:
                        f.write(res1.content)
                    print("下载成功"+song_name)
                    return {
                        'status': 'success',
                        'message': '下载成功',
                        'file_path': file_path,
                        'song_name': song_name
                    }

                except Exception as e:
                    return {
                        'status': 'error',
                        'message': str(e),
                        'song_name': song_name
                    }
            else:
                return {
                    'status': 'error',
                    'message': '获取歌曲信息失败',
                    'song_name': song_name
                }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'下载失败: {str(e)}',
                'song_name': song_name
            }

    def kugou_download_single_song_to_rank(self, song_id, song_name, rank_name):
        '''下载单首歌曲到指定榜单文件夹'''
        try:
            print(f"正在下载歌曲: {song_name}, id:{song_id} 到榜单: {rank_name}")
            # 生成签名
            signature_str = 'NVPh5oo715z5DIWAeQlhMDsWXXQV4hwtappid=1014clienttime=' + self.timestamp + 'clientver=20000dfid=0jL2CE333LKk105xaB29Q5CLencode_album_audio_id=' + song_id + 'mid=459098cc19fce2550dc5e1e00a19f9faplatid=4srcappid=2919token=344d6c367ba05daa0358de184e6adaeb25e0cabe9df8cba1f5c49ce8779b079duserid=768747371uuid=459098cc19fce2550dc5e1e00a19f9faNVPh5oo715z5DIWAeQlhMDsWXXQV4hwt'
            signature = self.MD5(signature_str)

            # 获取歌曲信息
            res = requests.get('https://wwwapi.kugou.com/play/songinfo',
                            headers=self.headers,
                            params={
                                'srcappid': '2919',
                                'clientver': '20000',
                                'clienttime': self.timestamp,
                                'mid': '459098cc19fce2550dc5e1e00a19f9fa',
                                'uuid': '459098cc19fce2550dc5e1e00a19f9fa',
                                'dfid': '0jL2CE333LKk105xaB29Q5CL',
                                'appid': '1014',
                                'platid': '4',
                                'encode_album_audio_id': song_id,
                                'token': '344d6c367ba05daa0358de184e6adaeb25e0cabe9df8cba1f5c49ce8779b079d',
                                'userid': '768747371',
                                'signature': signature,
                            })
            print("下载歌曲："+rank_name)
            song_data = res.json()
            if 'data' in song_data:
                song_name = re.sub(r'[/*?"|:<>\\]', '', song_data['data']['audio_name'])
                song_url = song_data['data']['play_url']
                # print("song_url:"+song_url)

                # 创建下载目录 - 使用榜单名称
                download_dir = os.path.join(os.getcwd(), 'downloads', rank_name)
                os.makedirs(download_dir, exist_ok=True)

                # 下载歌曲
                try:
                    res1 = requests.get(song_url, headers=self.headers)
                    # print("res1"+res1.text)

                    file_path = os.path.join(download_dir, f"{song_name}.mp3")
                    with open(file_path, 'wb') as f:
                        f.write(res1.content)
                    print("下载成功")
                    return {
                        'status': 'success',
                        'message': '下载成功',
                        'file_path': file_path,
                        'song_name': song_name,
                        'rank_name': rank_name
                    }
                except Exception as e:
                    return {
                        'status': 'error',
                        'message': str(e),
                        'song_name': song_name,
                        'rank_name': rank_name
                    }
            else:
                return {
                    'status': 'error',
                    'message': '获取歌曲信息失败',
                    'song_name': song_name,
                    'rank_name': rank_name
                }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'下载失败: {str(e)}',
                'song_name': song_name,
                'rank_name': rank_name
            }