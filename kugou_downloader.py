#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Author: 潘高
LastEditors: 潘高
Date: 2025-01-27 10:00:00
LastEditTime: 2025-01-27 10:00:00
Description: 酷狗音乐下载器 - 桌面工具
usage: 运行前，请确保本机已经搭建Python3开发环境，且已经安装 pywebview 模块。
'''

import os
import webview
from api.kugou import KugouAPI


class KugouDownloaderAPI(KugouAPI):
    '''酷狗音乐下载器API'''

    def __init__(self):
        super().__init__()
        self._window = None

    def setWindow(self, window):
        '''获取窗口实例'''
        self._window = window

    def open_downloads_folder(self):
        '''打开下载文件夹'''
        import os
        import subprocess
        import platform

        try:
            # 获取当前工作目录下的downloads文件夹
            downloads_path = os.path.join(os.getcwd(), 'downloads')

            if not os.path.exists(downloads_path):
                return {'status': 'error', 'message': '下载文件夹不存在'}

            # 根据操作系统打开文件夹
            system = platform.system()
            if system == 'Windows':
                os.startfile(downloads_path)
            elif system == 'Darwin':  # macOS
                subprocess.call(['open', downloads_path])
            elif system == 'Linux':
                subprocess.call(['xdg-open', downloads_path])
            else:
                return {'status': 'error', 'message': f'不支持的操作系统: {system}'}

            return {'status': 'success', 'message': f'已打开下载文件夹: {downloads_path}'}
        except Exception as e:
            return {'status': 'error', 'message': f'打开文件夹失败: {str(e)}'}

    def inject_js_to_kugou(self):
        '''注入JS到酷狗网页'''
        js_code = '''
        // 为每首歌曲添加下载按钮
        function addDownloadButtonsToSongs() {
            console.log('开始为歌曲添加下载按钮...');

            // 1. 处理常规排行榜/歌单
            const songContainers = document.querySelectorAll('.pc_temp_songlist ul li, .rank_songlist ul li, .song_list ul li');
            if (songContainers.length > 0) {
                addButtonsToElements(songContainers);
            }

            // 2. 处理搜索结果 .list_content > li
            const searchSongLis = document.querySelectorAll('.list_content > li');
            if (searchSongLis.length > 0) {
                searchSongLis.forEach((element, index) => {
                    // 检查是否已经添加过按钮
                    if (element.querySelector('.ppx-download-song-btn')) {
                        return;
                    }
                    // 获取歌曲名
                    let songName = '';
                    // 尝试常见结构
                    const nameNode = element.querySelector('.song_name, .song-title, .name, a[title]');
                    if (nameNode) {
                        songName = nameNode.textContent.trim() || nameNode.getAttribute('title');
                    } else {
                        songName = element.textContent.trim();
                    }
                    if (!songName) {
                        console.log('搜索结果li未获取到歌曲名', element);
                        return;
                    }
                    // 创建下载按钮
                    const downloadBtn = document.createElement('button');
                    downloadBtn.className = 'ppx-download-song-btn';
                    downloadBtn.textContent = '下载';
                    downloadBtn.style.cssText = `
                        background: #2d8cf0;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 12px;
                        cursor: pointer;
                        margin-left: 8px;
                        transition: background 0.3s;
                    `;
                    downloadBtn.onmouseover = () => downloadBtn.style.background = '#1e6fd9';
                    downloadBtn.onmouseout = () => downloadBtn.style.background = '#2d8cf0';
                    downloadBtn.onclick = function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        downloadSearchSong(songName);
                    };
                    // 添加到a.song_name节点旁边
                    const songNameLink = element.querySelector('a.song_name');
                    if (songNameLink) {
                        songNameLink.parentNode.insertBefore(downloadBtn, songNameLink.nextSibling);
                    } else {
                        // 如果找不到a.song_name，则添加到li末尾
                        element.appendChild(downloadBtn);
                    }
                });
            }
        }

        // 添加批量下载按钮
        function addBatchDownloadButton() {
            // 检查是否已经存在批量下载按钮和打开文件位置按钮
            if (document.getElementById('ppx-batch-download-btn') && document.getElementById('ppx-open-folder-btn')) {
                return;
            }

            console.log('开始查找批量下载按钮位置...');

            // 使用XPath查找全选按钮
            const xpath = '//*[@id="rankWrap"]/div[1]/span';
            const result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            const selectAllElement = result.singleNodeValue;

            let targetContainer = null;

            if (selectAllElement) {
                console.log('通过XPath找到全选元素:', selectAllElement);
                // 如果找到全选元素，在其父容器中添加按钮
                targetContainer = selectAllElement.parentElement;
                console.log('全选元素父容器:', targetContainer);
            }

            // 如果没找到排行榜页面的按钮位置，尝试搜索页面
            if (!targetContainer) {
                addSearchPageButtons();
                return;
            }

            // 创建批量下载按钮
            const batchBtn = document.createElement('button');
            batchBtn.id = 'ppx-batch-download-btn';
            batchBtn.textContent = '批量下载选中歌曲';
            batchBtn.style.cssText = `
                background: #19be6b;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
                cursor: pointer;
                margin-left: 15px;
                transition: all 0.3s;
                font-family: Arial, sans-serif;
                display: inline-block;
                vertical-align: middle;
                z-index: 99999;
            `;

            // 鼠标悬停效果
            batchBtn.onmouseover = () => {
                batchBtn.style.background = '#16a05a';
                batchBtn.style.transform = 'translateY(-1px)';
            };
            batchBtn.onmouseout = () => {
                batchBtn.style.background = '#19be6b';
                batchBtn.style.transform = 'translateY(0)';
            };

            // 点击批量下载
            batchBtn.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                batchDownloadCurrentRankSongs();
            };

            // 创建打开文件位置按钮
            const openFolderBtn = document.createElement('button');
            openFolderBtn.id = 'ppx-open-folder-btn';
            openFolderBtn.textContent = '打开文件位置';
            openFolderBtn.style.cssText = `
                background: #2d8cf0;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
                cursor: pointer;
                margin-left: 10px;
                transition: all 0.3s;
                font-family: Arial, sans-serif;
                display: inline-block;
                vertical-align: middle;
                z-index: 99999;
            `;

            // 鼠标悬停效果
            openFolderBtn.onmouseover = () => {
                openFolderBtn.style.background = '#1e6fd9';
                openFolderBtn.style.transform = 'translateY(-1px)';
            };
            openFolderBtn.onmouseout = () => {
                openFolderBtn.style.background = '#2d8cf0';
                openFolderBtn.style.transform = 'translateY(0)';
            };

            // 点击打开文件位置
            openFolderBtn.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                openDownloadsFolder();
            };

                                    // 创建状态显示区域
            const statusDiv = document.getElementById('ppx-status') || createStatusDiv();

            // 添加到目标容器
            targetContainer.appendChild(batchBtn);
            targetContainer.appendChild(openFolderBtn);
            targetContainer.appendChild(statusDiv);
            console.log('批量下载按钮、打开文件位置按钮和状态显示区域已添加到目标容器:', targetContainer);

            // 调整状态区域位置到目标元素旁边
            setTimeout(() => {
                adjustStatusPosition();
            }, 100);

                        // 如果按钮不可见，尝试调整位置
            setTimeout(() => {
                if (batchBtn.offsetParent === null || openFolderBtn.offsetParent === null) {
                    console.log('按钮不可见，尝试添加到body');
                    document.body.appendChild(batchBtn);
                    document.body.appendChild(openFolderBtn);
                    document.body.appendChild(statusDiv);
                    batchBtn.style.position = 'fixed';
                    batchBtn.style.top = '20px';
                    batchBtn.style.right = '120px';
                    batchBtn.style.zIndex = '99999';
                    openFolderBtn.style.position = 'fixed';
                    openFolderBtn.style.top = '20px';
                    openFolderBtn.style.right = '20px';
                    openFolderBtn.style.zIndex = '99999';
                    statusDiv.style.position = 'fixed';
                    statusDiv.style.top = '20px';
                    statusDiv.style.right = '-200px';
                    statusDiv.style.zIndex = '99999';
                }
            }, 1000);
        }

                // 批量下载当前榜单歌曲
        function batchDownloadCurrentRankSongs() {
            console.log('开始批量下载选中的歌曲...');

            // 显示下载状态
            const statusDiv = document.getElementById('ppx-status') || createStatusDiv();
            statusDiv.textContent = '正在批量下载选中的歌曲...';
            statusDiv.style.background = '#2d8cf0';
            statusDiv.style.color = 'white';

            // 获取选中的歌曲列表（排除全选按钮）
            const checkedButtons = document.querySelectorAll('.pc_temp_btn_check.pc_temp_btn_checked:not(.checkedAll)');

            if (checkedButtons.length === 0) {
                statusDiv.textContent = '请先选择要下载的歌曲';
                statusDiv.style.background = '#ed4014';
                statusDiv.style.color = 'white';
                return;
            }

            console.log(`找到 ${checkedButtons.length} 首选中的歌曲，开始批量下载`);

            // 收集选中歌曲的信息
            const songsToDownload = [];
            checkedButtons.forEach((button, index) => {
                // 找到按钮所在的li元素
                const liElement = button.closest('li');
                if (liElement) {
                    const songName = getSongName(liElement);
                    const songId = getSongId(liElement);

                    if (songName && songId) {
                        songsToDownload.push({
                            name: songName,
                            id: songId,
                            element: liElement
                        });
                    }
                }
            });

            if (songsToDownload.length === 0) {
                statusDiv.textContent = '无法获取选中歌曲信息';
                statusDiv.style.background = '#ed4014';
                statusDiv.style.color = 'white';
                return;
            }

            // 获取当前榜单名称
            const rankName = getCurrentRankName();
            console.log('当前榜单名称:', rankName);

            // 开始批量下载
            let completedCount = 0;
            let successCount = 0;
            let failCount = 0;

            statusDiv.textContent = `正在下载: 0/${songsToDownload.length}`;

            // 逐个下载歌曲
            songsToDownload.forEach((song, index) => {
                setTimeout(() => {
                    // 显示当前正在下载的歌曲
                    statusDiv.textContent = `正在下载: ${song.name} (${completedCount + 1}/${songsToDownload.length})`;
                    statusDiv.style.background = '#2d8cf0';
                    statusDiv.style.color = 'white';

                    downloadSingleSongForBatch(song.id, song.name, rankName, () => {
                        completedCount++;
                        if (song.status === 'success') {
                            successCount++;
                            // 显示成功状态
                            statusDiv.textContent = `✓ ${song.name} 下载成功 (${completedCount}/${songsToDownload.length})`;
                            statusDiv.style.background = '#19be6b';
                            statusDiv.style.color = 'white';
                        } else {
                            failCount++;
                            // 显示失败状态
                            statusDiv.textContent = `✗ ${song.name} 下载失败 (${completedCount}/${songsToDownload.length})`;
                            statusDiv.style.background = '#ed4014';
                            statusDiv.style.color = 'white';
                        }

                        // 所有歌曲下载完成
                        if (completedCount === songsToDownload.length) {
                            statusDiv.textContent = `批量下载完成！成功: ${successCount}, 失败: ${failCount}`;
                            statusDiv.style.background = successCount > 0 ? '#19be6b' : '#ed4014';
                            statusDiv.style.color = 'white';
                        }
                    }, song);
                },  500); // 每0.5秒下载一首，避免请求过于频繁
            });
        }

        // 为批量下载准备的单曲下载函数
        function downloadSingleSongForBatch(songId, songName, rankName, callback, songObj) {
            console.log(`批量下载歌曲: ${songName} (ID: ${songId}) 到榜单: ${rankName}`);

            window.pywebview.api.kugou_download_single_song_to_rank(songId, songName, rankName).then(result => {
                if (result.status === 'success') {
                    console.log(`歌曲 "${songName}" 下载成功`);
                    songObj.status = 'success';
                } else {
                    console.log(`歌曲 "${songName}" 下载失败: ${result.message}`);
                    songObj.status = 'failed';
                    songObj.error = result.message;
                }
                callback();
            }).catch(error => {
                console.log(`歌曲 "${songName}" 下载出错: ${error}`);
                songObj.status = 'failed';
                songObj.error = error;
                callback();
            });
        }

        // 获取当前榜单名称
        function getCurrentRankName() {



                const element = document.querySelector("div.pc_rank_sidebar > ul > li > a.current");
                if (element) {
                    return element.textContent.trim();
                }


            return '当前榜单';
        }

        // 原有排行榜/歌单下载按钮逻辑
        function addButtonsToElements(elements) {
            elements.forEach((element, index) => {
                if (element.querySelector('.ppx-download-song-btn')) {
                    return;
                }
                const songName = getSongName(element);
                const songId = getSongId(element);
                if (!songName || !songId) {
                    console.log(`跳过第 ${index + 1} 首歌曲，无法获取信息`);
                    return;
                }
                const downloadBtn = document.createElement('button');
                downloadBtn.className = 'ppx-download-song-btn';
                downloadBtn.textContent = '下载';
                downloadBtn.style.cssText = `
                    background: #2d8cf0;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 12px;
                    cursor: pointer;
                    margin-left: 8px;
                    transition: background 0.3s;
                `;
                downloadBtn.onmouseover = () => downloadBtn.style.background = '#1e6fd9';
                downloadBtn.onmouseout = () => downloadBtn.style.background = '#2d8cf0';
                downloadBtn.onclick = function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    downloadSingleSong(songId, songName);
                };
                const actionArea = element.querySelector('.pc_temp_songlist_operate, .song_operate, .rank_operate');
                if (actionArea) {
                    actionArea.appendChild(downloadBtn);
                } else {
                    element.appendChild(downloadBtn);
                }
            });
        }

        // 获取歌曲名称
        function getSongName(element) {
            const nameSelectors = [
                '.pc_temp_songname',
                '.song_name',
                '.rank_songname',
                'a[title]',
                '.song_title'
            ];
            for (let selector of nameSelectors) {
                const nameElement = element.querySelector(selector);
                if (nameElement) {
                    return nameElement.textContent.trim() || nameElement.getAttribute('title');
                }
            }
            const text = element.textContent.trim();
            const match = text.match(/^\\d+\\s+(.+?)\\s+-/);
            return match ? match[1].trim() : null;
        }
        // 获取歌曲ID
        function getSongId(element) {
            const dataEid = element.getAttribute('data-eid');
            console.log("获取歌曲id"+dataEid)
            if (dataEid) {
                return dataEid;
            }
            const link = element.querySelector('a[href*="hash="]');
            if (link) {
                const href = link.getAttribute('href');
                const hashMatch = href.match(/hash=([^&]+)/);
                if (hashMatch) {
                    return hashMatch[1];
                }
            }
            return null;
        }
        // 下载单首歌曲（排行榜/歌单）
        function downloadSingleSong(songId, songName) {
            console.log(`开始下载歌曲: ${songName} (ID: ${songId})`);
            const statusDiv = document.getElementById('ppx-status') || createStatusDiv();
            statusDiv.textContent = `正在下载: ${songName}...`;
            statusDiv.style.background = '#2d8cf0';
            statusDiv.style.color = 'white';
            window.pywebview.api.kugou_download_single_song(songId, songName).then(result => {
                if (result.status === 'success') {
                    statusDiv.textContent = `下载完成: ${songName}`;
                    statusDiv.style.background = '#19be6b';
                    statusDiv.style.color = 'white';
                    console.log(`歌曲 "${songName}" 下载成功`);
                } else {
                    statusDiv.textContent = `下载失败: ${songName} - ${result.message}`;
                    statusDiv.style.background = '#ed4014';
                    statusDiv.style.color = 'white';
                    console.log(`歌曲 "${songName}" 下载失败: ${result.message}`);
                }
            }).catch(error => {
                statusDiv.textContent = `下载出错: ${songName} - ${error}`;
                statusDiv.style.background = '#ed4014';
                statusDiv.style.color = 'white';
                console.log(`歌曲 "${songName}" 下载出错: ${error}`);
            });
        }
        // 下载搜索结果歌曲（只用名字）
        function downloadSearchSong(songName, callback) {
            console.log(`开始搜索并下载歌曲: ${songName}`);
            const statusDiv = document.getElementById('ppx-status') || createStatusDiv();

            // 如果不是批量下载模式，显示状态
            if (!callback) {
                statusDiv.textContent = `正在搜索并下载: ${songName}...`;
                statusDiv.style.background = '#2d8cf0';
                statusDiv.style.color = 'white';
            }

            window.pywebview.api.kugou_search_and_download(songName).then(result => {
                if (result.status === 'success') {
                    if (!callback) {
                        statusDiv.textContent = `下载完成: ${songName}`;
                        statusDiv.style.background = '#19be6b';
                        statusDiv.style.color = 'white';
                    }
                    console.log(`歌曲 "${songName}" 搜索下载成功`);

                    // 如果是批量下载模式，设置状态并调用回调
                    if (callback) {
                        songName.status = 'success';
                        callback();
                    }
                } else {
                    if (!callback) {
                        statusDiv.textContent = `下载失败: ${songName} - ${result.message}`;
                        statusDiv.style.background = '#ed4014';
                        statusDiv.style.color = 'white';
                    }
                    console.log(`歌曲 "${songName}" 搜索下载失败: ${result.message}`);

                    // 如果是批量下载模式，设置状态并调用回调
                    if (callback) {
                        songName.status = 'failed';
                        songName.error = result.message;
                        callback();
                    }
                }
            }).catch(error => {
                if (!callback) {
                    statusDiv.textContent = `下载出错: ${songName} - ${error}`;
                    statusDiv.style.background = '#ed4014';
                    statusDiv.style.color = 'white';
                }
                console.log(`歌曲 "${songName}" 搜索下载出错: ${error}`);

                // 如果是批量下载模式，设置状态并调用回调
                if (callback) {
                    songName.status = 'failed';
                    songName.error = error;
                    callback();
                }
            });
        }
                // 打开下载文件夹
        function openDownloadsFolder() {
            console.log('正在打开下载文件夹...');
            const statusDiv = document.getElementById('ppx-status') || createStatusDiv();
            statusDiv.textContent = '正在打开下载文件夹...';
            statusDiv.style.background = '#2d8cf0';
            statusDiv.style.color = 'white';

            window.pywebview.api.open_downloads_folder().then(result => {
                if (result.status === 'success') {
                    statusDiv.textContent = '已打开下载文件夹';
                    statusDiv.style.background = '#19be6b';
                    statusDiv.style.color = 'white';
                    console.log('下载文件夹打开成功:', result.message);
                } else {
                    statusDiv.textContent = `打开文件夹失败: ${result.message}`;
                    statusDiv.style.background = '#ed4014';
                    statusDiv.style.color = 'white';
                    console.log('打开文件夹失败:', result.message);
                }
            }).catch(error => {
                statusDiv.textContent = `打开文件夹出错: ${error}`;
                statusDiv.style.background = '#ed4014';
                statusDiv.style.color = 'white';
                console.log('打开文件夹出错:', error);
            });
        }

                                // 创建状态显示区域
        function createStatusDiv() {
            const statusDiv = document.createElement('div');
            statusDiv.id = 'ppx-status';
            statusDiv.style.cssText = `
                background: #2d8cf0;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
                font-family: Arial, sans-serif;
                display: inline-block;
                vertical-align: middle;
                z-index: 99999;
                min-width: 120px;
                text-align: center;
                transition: all 0.3s;
                margin-left: 10px;
                line-height: 1.2;
                height: 37px;
                box-sizing: border-box;
            `;
            statusDiv.textContent = '准备就绪';
            return statusDiv;
        }

                                        // 添加搜索页面按钮
        function addSearchPageButtons() {
            // 检查是否已经存在按钮
            if (document.getElementById('ppx-open-folder-btn')) {
                return;
            }

            console.log('开始查找搜索页面按钮位置...');

            // 查找搜索页面的目标容器
            const searchContainer = document.querySelector('.width_f_li.song_name_li');
            if (!searchContainer) {
                console.log('未找到搜索页面容器');
                return;
            }

            console.log('找到搜索页面容器:', searchContainer);

            // 修改搜索页面歌曲名称链接的宽度
            const songNameLinks = document.querySelectorAll('.search_content .search_song .width_f_li a.song_name');
            songNameLinks.forEach(link => {
                link.style.width = '300px';
            });

            // 创建打开文件位置按钮
            const openFolderBtn = document.createElement('button');
            openFolderBtn.id = 'ppx-open-folder-btn';
            openFolderBtn.textContent = '打开文件位置';
            openFolderBtn.style.cssText = `
                background: #2d8cf0;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
                cursor: pointer;
                margin-left: 10px;
                transition: all 0.3s;
                font-family: Arial, sans-serif;
                display: inline-block;
                vertical-align: middle;
                z-index: 99999;
            `;

            // 鼠标悬停效果
            openFolderBtn.onmouseover = () => {
                openFolderBtn.style.background = '#1e6fd9';
                openFolderBtn.style.transform = 'translateY(-1px)';
            };
            openFolderBtn.onmouseout = () => {
                openFolderBtn.style.background = '#2d8cf0';
                openFolderBtn.style.transform = 'translateY(0)';
            };

            // 点击打开文件位置
            openFolderBtn.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                openDownloadsFolder();
            };

            // 创建状态显示区域
            const statusDiv = document.getElementById('ppx-status') || createStatusDiv();

            // 添加到搜索页面容器
            searchContainer.appendChild(openFolderBtn);
            searchContainer.appendChild(statusDiv);
            console.log('搜索页面按钮和状态显示区域已添加到容器:', searchContainer);
        }

        // 批量下载搜索结果
        function batchDownloadSearchResults() {
            console.log('开始批量下载搜索结果...');

            // 显示下载状态
            const statusDiv = document.getElementById('ppx-status') || createStatusDiv();
            statusDiv.textContent = '正在批量下载搜索结果...';
            statusDiv.style.background = '#2d8cf0';
            statusDiv.style.color = 'white';

            // 获取搜索结果列表
            const searchResults = document.querySelectorAll('.list_content > li');

            if (searchResults.length === 0) {
                statusDiv.textContent = '未找到搜索结果';
                statusDiv.style.background = '#ed4014';
                statusDiv.style.color = 'white';
                return;
            }

            console.log(`找到 ${searchResults.length} 个搜索结果，开始批量下载`);

            // 收集搜索结果信息
            const songsToDownload = [];
            searchResults.forEach((element, index) => {
                const songName = getSongName(element);
                if (songName) {
                    songsToDownload.push({
                        name: songName,
                        element: element
                    });
                }
            });

            if (songsToDownload.length === 0) {
                statusDiv.textContent = '无法获取搜索结果信息';
                statusDiv.style.background = '#ed4014';
                statusDiv.style.color = 'white';
                return;
            }

            // 开始批量下载
            let completedCount = 0;
            let successCount = 0;
            let failCount = 0;

            statusDiv.textContent = `正在下载: 0/${songsToDownload.length}`;

            // 逐个下载歌曲
            songsToDownload.forEach((song, index) => {
                setTimeout(() => {
                    // 显示当前正在下载的歌曲
                    statusDiv.textContent = `正在下载: ${song.name} (${completedCount + 1}/${songsToDownload.length})`;
                    statusDiv.style.background = '#2d8cf0';
                    statusDiv.style.color = 'white';

                    downloadSearchSong(song.name, () => {
                        completedCount++;
                        if (song.status === 'success') {
                            successCount++;
                            // 显示成功状态
                            statusDiv.textContent = `✓ ${song.name} 下载成功 (${completedCount}/${songsToDownload.length})`;
                            statusDiv.style.background = '#19be6b';
                            statusDiv.style.color = 'white';
                        } else {
                            failCount++;
                            // 显示失败状态
                            statusDiv.textContent = `✗ ${song.name} 下载失败 (${completedCount}/${songsToDownload.length})`;
                            statusDiv.style.background = '#ed4014';
                            statusDiv.style.color = 'white';
                        }

                        // 所有歌曲下载完成
                        if (completedCount === songsToDownload.length) {
                            statusDiv.textContent = `批量下载完成！成功: ${successCount}, 失败: ${failCount}`;
                            statusDiv.style.background = successCount > 0 ? '#19be6b' : '#ed4014';
                            statusDiv.style.color = 'white';
                        }
                    });
                }, index * 500); // 每0.5秒下载一首
            });
        }

        // 调整状态区域位置到指定元素旁边
        function adjustStatusPosition() {
            const statusDiv = document.getElementById('ppx-status');

            if (statusDiv) {
                // 如果状态区域在body中（备用位置），则调整到目标元素旁边
                if (statusDiv.parentElement === document.body) {
                    // 使用XPath查找目标元素
                    const xpath = '//*[@id="rankWrap"]/div[1]/span';
                    const result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                    const targetElement = result.singleNodeValue;

                    if (targetElement) {
                        const elementRect = targetElement.getBoundingClientRect();
                        statusDiv.style.position = 'absolute';
                        statusDiv.style.top = (elementRect.top + window.scrollY) + 'px';
                        statusDiv.style.left = (elementRect.right + 10) + 'px';
                        statusDiv.style.right = 'auto';
                        statusDiv.style.zIndex = '99999';
                        statusDiv.style.transform = 'translateY(0)'; // 确保垂直对齐
                    } else {
                        // 如果找不到目标元素，使用默认位置
                        statusDiv.style.position = 'fixed';
                        statusDiv.style.top = '20px';
                        statusDiv.style.right = '20px';
                        statusDiv.style.left = 'auto';
                        statusDiv.style.zIndex = '99999';
                    }
                }
                // 如果状态区域在目标容器中，则不需要调整位置，会自动跟随按钮布局
            }
        }
        // 立即尝试添加按钮
        addDownloadButtonsToSongs();
        addBatchDownloadButton();
        addSearchPageButtons();
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                addDownloadButtonsToSongs();
                addBatchDownloadButton();
                addSearchPageButtons();
            });
        }
        window.addEventListener('load', () => {
            addDownloadButtonsToSongs();
            addBatchDownloadButton();
            addSearchPageButtons();
        });
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    setTimeout(() => {
                        addDownloadButtonsToSongs();
                        addBatchDownloadButton();
                        addSearchPageButtons();
                    }, 1000);
                }
            });
        });
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        setInterval(() => {
            addDownloadButtonsToSongs();
            addBatchDownloadButton();
            addSearchPageButtons();
        }, 3000);
        console.log('歌曲下载按钮和批量下载按钮注入完成');
        '''

        try:
            self._window.evaluate_js(js_code)
            return {'status': 'success', 'message': 'JS注入成功'}
        except Exception as e:
            return {'status': 'error', 'message': f'JS注入失败: {str(e)}'}


def on_shown():
    '''窗口显示事件'''
    print('酷狗音乐下载器启动')


def on_loaded():
    '''页面加载完成事件'''
    print('页面加载完成')
    # 延迟注入JS，确保页面完全加载
    import threading
    import time

    def inject_js_delayed():
        time.sleep(2)  # 等待2秒确保页面完全加载
        try:
            # 获取全局的api实例
            global api_instance
            result = api_instance.inject_js_to_kugou()
            print(f"JS注入结果: {result}")
        except Exception as e:
            print(f"JS注入失败: {e}")

    threading.Thread(target=inject_js_delayed, daemon=True).start()


def on_closing():
    '''窗口关闭事件'''
    print('酷狗音乐下载器关闭')


def create_kugou_downloader():
    '''创建酷狗音乐下载器窗口'''

    # 创建API实例
    global api_instance
    api_instance = KugouDownloaderAPI()

    # 创建窗口
    window = webview.create_window(
        title='酷狗音乐增强版（程序员小风）',
        url='https://www.kugou.com/yy/html/rank.html',
        js_api=api_instance,
        width=1200,
        height=800,
        min_size=(800, 600),
        resizable=True,
        text_select=True,
        confirm_close=False
    )

    # 设置窗口实例
    api_instance.setWindow(window)

    # 绑定事件
    window.events.shown += on_shown
    window.events.loaded += on_loaded
    window.events.closing += on_closing

    # 启动应用
    webview.start(debug=True, http_server=True)


if __name__ == "__main__":
    create_kugou_downloader()