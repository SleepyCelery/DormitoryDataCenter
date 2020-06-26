import requests
from UserAgentList import get_useragent
import os
import pygame
import platform
import subprocess


def add_html_row(row_list):
    html = '<tr>{}</tr>'
    tmp = ''
    for i in row_list:
        tmp += '<th>{}</th>'.format(i)

    return html.format(tmp)


def get_music_by_name(name, source='netease', page=1):
    # type可以是netease qq kugou kuwo xiami baidu migu ximalaya
    response = requests.post(url='https://music.liuzhijin.cn/',
                             data={'input': name, 'filter': 'name', 'type': source, 'page': str(page)},
                             headers={'origin': 'https://music.liuzhijin.cn', 'sec-fetch-site': 'same-origin',
                                      'sec-fetch-mode': 'cors',
                                      'x-requested-with': 'XMLHttpRequest', 'User-Agent': get_useragent()})
    data = response.json()['data']
    info_list = []
    for i in data:
        single_info = []
        single_info.append(i['title'])
        single_info.append(i['author'])
        single_info.append(i['url'])
        info_list.append(single_info)
    return info_list


def download_music_by_url(url: str):
    response = requests.get(url, headers={'User-Agent':get_useragent()})
    with open('temp.mp3', mode='wb') as music:
        music.write(response.content)




def playmusic_downloaded(name):
    if platform.system() == 'Windows':
        pygame.mixer.init()
        pygame.mixer.music.load('temp.mp3')
        pygame.mixer.music.play()
    elif platform.system() == 'Linux':
        subprocess.Popen('sudo kill -9 $(pidof {})'.format('mplayer'))
        subprocess.Popen('setsid sudo mplayer {} < /dev/null > /dev/null 2>1&'.format(name))
    return


def show_html_list(name, source='netease', page=1, debugmode=False):
    try:
        info_list = get_music_by_name(name, source, page)

        for index, info in enumerate(info_list):
            if 'http' in info[-1]:
                info_list[index][-1] = '''
                <body style="background-image: url(http://www.pptbz.com/d/file/p/201708/a1d07b6201af8f574b6539cb724bbc16.png);background-repeat:no-repeat;background-size:100% 100%;-moz-background-size:100% 100%;font-family:Arial,Times New Roman,KaiTi;font-size: 24px;text-align:center;color: dimgrey;">
                    <div>
                        <a href="{}">播放</a>
                    </div>
                </body>
                '''.format('/playsoundbyurl?playurl=' + info[-1])
        html = '<table border="1" style="text-align:center">{}</table>'
        tmp = ''
        tmp += add_html_row(['歌曲名', '歌手', '歌曲播放链接'])
        for i in info_list:
            tmp += add_html_row(i)
        if debugmode:
            with open('test.html', mode='w') as file:
                file.write(html.format(tmp))
            os.system('test.html')
        return html.format(tmp)
    except:
        return '<h1>获取数据出现错误!</h1>'


if __name__ == '__main__':
    playmusic_by_name('沙漠骆驼')
