import requests
import json
from flask import Flask, request, url_for, redirect, send_file
from doordriver import send_cmd_withback
import os
import time
from urllib.parse import quote, unquote
import threading
import platform
from functools import wraps
import MusicSpider
import SpeechSynthesisRaspberry

app = Flask(__name__, static_folder='./UploadFiles')

UPLOAD_FOLDER = './UploadFiles'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# bg_executor = ThreadPoolExecutor(max_workers=4)
time_last_request = 0
ip_table = {
    '192.168.1.199': '巢义虎',
    '192.168.1.224': '舒伟童',
    '192.168.1.165': '余廖祎',
    '192.168.1.185': '巢义虎',
    '192.168.1.218': '黄方军',
    '192.168.1.130': '余廖祎',
    '192.168.1.219': '黄方军',
    '192.168.1.152': '舒伟童',
    '192.168.1.140': '余廖祎',
    '127.0.0.1': '管理员'
}


def passport(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global ip_table
        ip = request.remote_addr
        if ip in ip_table.keys():
            return func(*args, **kwargs)
        else:
            return '''
                <body>
                <div style="text-align:center">
                <font></font><br/><font></font><br/><font></font><br/>
                <font face="宋体" size="+5" color="#000000">本机未授权!</font><br/>
                </div>
                '''

    return wrapper


def get_user_name(ip):
    global ip_table
    if ip in ip_table.keys():
        return ip_table[ip]
    elif ip == 'filedownload':
        return '远程下载任务'
    else:
        return '游客'


def get_time():
    time_now = time.localtime(time.time())[:6]
    time_now = "{}-{}-{} {:02d}:{:02d}:{:02d}".format(time_now[0], time_now[1], time_now[2], time_now[3], time_now[4],
                                                      time_now[5])
    return time_now


def get_modify_time(path):
    filetime_int = int(os.stat(path).st_mtime)
    filetime = time.localtime(filetime_int)[:6]
    filetime = "{}-{}-{} {:02d}:{:02d}:{:02d}".format(filetime[0], filetime[1], filetime[2], filetime[3], filetime[4],
                                                      filetime[5])
    return (filetime, filetime_int)


def filename_filter(filename):
    filename = filename.replace('/', '')
    filename = filename.replace('\\', '')
    filename = filename.replace(' ', '_')
    while filename[0] in ['.', '+', '-']:
        filename = filename[1:]
    while len(filename) > 255:
        filename = filename[1:]
    return filename


def get_disk_info():
    if platform.system() == 'Linux':
        import re
        disk_message = os.popen("df").readlines()[1]
        disk_message = disk_message.replace(" ", "*")
        print(disk_message)
        disk_message = re.findall('\d+', disk_message)
        all_space = int(disk_message[0]) * 1024
        used_space = int(disk_message[1]) * 1024
        free_space = int(disk_message[2]) * 1024
        used_percent = int(disk_message[3]) / 100
        return (all_space, used_space, free_space, used_percent)
    else:
        return (65535, 65535, 65535, 0.99)


def write_log(ip, content):
    if os.path.exists('datacenter.log'):
        with open('datacenter.log', mode='a', encoding='utf-8') as log:
            log.write('{} {} {}\n'.format(get_time(), get_user_name(ip), content))
    else:
        with open('datacenter.log', mode='w', encoding='utf-8') as log:
            log.write('{} {} {}\n'.format(get_time(), get_user_name(ip), content))


@app.route('/')
def index():
    global ip_table
    ip = request.remote_addr
    write_log(ip, '进入首页')
    if ip in ip_table.keys():
        welcome = '欢迎您,' + ip_table[ip] +'同志'
    else:
        welcome = '游客访问'
    return '''
    <!DOCTYPE html>
    <html lang="cn">
    
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" type="text/css" href="css/datacenter.css" />
    <title>Document</title>
    </head>
    <body style="background-image: url(http://www.pptbz.com/d/file/p/201708/a1d07b6201af8f574b6539cb724bbc16.png);background-repeat:no-repeat;background-size:100% 100%;-moz-background-size:100% 100%;">
    <div style="text-align:center;">
        <p style="color:dimgrey; font-family:Arial,Times New Roman,KaiTi;margin-top: 2%;margin-bottom: 2%;font-size: 48px;">南昌大学190919数据中心</p>
        <div style="font-size: 36px;font-family:Arial,Times New Roman,KaiTi;">
            <p style="color:firebrick">{}</p>
            
            <div style="font-size: 24px;">
                <span>
                      <script type="text/javascript">
                        var date = new Date();
                        var day= 202-date.getDate();
                        document.write("今天是：" + date.getFullYear() + "年" + (date.getMonth() + 1) + "月" + date.getDate() + "日" + " 星期" + "日一二三四五六".charAt(date.getDay()));
                        document.write(" 距考研还有"+day+"天");
                      </script>
                </span>
            </div>

            <p><a href='/opendoor'  style="color: dimgrey">一键开门</a></p>
            <p><a href='/playmusic'  style="color: dimgrey">来点小曲</a></p>
            <p><a href='/uploadpage'  style="color: dimgrey">上传文件</a></p>
            <p><a href='/downloadpage'  style="color: dimgrey">浏览文件</a></p>
            <p><a href='/remotedownload'  style="color: dimgrey">远程下载</a> </p>
            <p><a href='/printermanager'  style="color: dimgrey">CUPS打印机管理</a></p>
            <p><a href='/serverconfig'  style="color: dimgrey">服务器系统设置</a></p>
            <p><a href='/readlog'  style="color: dimgrey">日志查询</a></p>
        </div>
    </div>
    '''.format(welcome)


@app.route('/printermanager')
@passport
def printermanager():
    write_log(request.remote_addr, '进入打印机管理页面')
    return redirect('http://ncu190919.com:631/', code=302)


#废弃
@app.route('/opendoorpage')
@passport
def opendoorpage():
    write_log(request.remote_addr, '进入一键开门页面')
    return '''
    <body>
    <div style="text-align:center">
    <font></font><br/><font></font><br/><font></font><br/>
    <font face="宋体" size="+5" color="#000000">按下按钮以开门</font><br/>
    <font></font><br/>
    <font></font><br/>
    <form action ='/opendoor' method='post'>
        <button type="submit" class="opendoor"
        style="height:70px;width:200px;font-size: 40px;">一键开门</button> 
    </form>
    </div>
    '''

#废弃
@app.route('/elec')
@passport
def elec():
    write_log(request.remote_addr, '进入电费查询页面')
    return '''
        <body>
        <div style="text-align:center">
        <font></font><br/><font></font><br/><font></font><br/>
        <font face="宋体" size="+5" color="#000000">南昌大学寝室电量查询</font><br/>
        <font face="宋体" size="+3" color="#000000">支持批量查询,用/隔开</font><br/>
        <font face="宋体" size="+3" color="#000000">示例:190919或190919/200825</font><br/>
        <font></font><br/>
        <font></font><br/>
        <form action ='/search' method='post'>
            <input type="txt"  rows="2" cols="10" placeholder="请输入寝室号"  
            name='dormitory' style="height:40px;width:200px;">  
            <button type="submit" class="dormitory-submit"
            style="height:38px;width:60px;">查询</button> 
        </form>
        </div>
        '''


@app.route('/search', methods=['POST'])
@passport
def search():
    dormitories = request.form['dormitory'].split('/')
    info = []
    ncuos = requests.Session()
    return_string = ''
    try:
        for dormitory in dormitories:
            response = ncuos.post('https://spider.ncuos.com/spider/electricity', data={'dormitory': dormitory})
            info_dict = dict(json.loads(response.text))
            info_dict['dormitory'] = dormitory
            info.append(info_dict)
        for i in info:
            elec = i['remaining_elec']
            money = i['remaining_money']
            dormitory = i['dormitory']
            return_string += '<h1>寝室号:{},剩余电量:{}度,剩余金额:{}元</h1>'.format(dormitory, elec, money)
        write_log(request.remote_addr, '查询了寝室号为{}的电费,查询成功'.format(dormitories))
        return return_string
        # return '<h1>寝室号:{},剩余电量:{}度,剩余金额:{}元</h1>'.format(dormitory, elec, money)
    except:
        write_log(request.remote_addr, '查询了寝室号为{}的电费,查询失败'.format(dormitories))
        return '<h1>查询数据出错,请输入正确的寝室号!</h1>'


@app.route('/opendoor', methods=['POST', 'GET'])
@passport
def opendoor():
    global time_last_request
    global ip_table
    ip = request.remote_addr
    if ip in ip_table.keys():
        welcome = ip_table[ip] 
    else:
        welcome = '游客访问'
    if time.time() - time_last_request >= 20:
        try:
            status = send_cmd_withback('192.168.1.145', 8080, b'190919111111')
            if status == 'OK':
                time_last_request = time.time()
                # SpeechSynthesisRaspberry.speech('{},欢迎回家!'.format(ip_table[request.remote_addr]))
                write_log(request.remote_addr, '使用了一键开门,开门成功')
                return '''
                <body style="background-image: url(http://www.pptbz.com/d/file/p/201708/a1d07b6201af8f574b6539cb724bbc16.png);background-repeat:no-repeat;background-size:100% 100%;-moz-background-size:100% 100%;">
                    <div style="text-align:center;">
                        <p style="color:dimgrey; font-family:Arial,Times New Roman,KaiTi;margin-top: 2%;margin-bottom: 2%;font-size: 48px;">南昌大学190919数据中心提醒您</p>
                        <div style="font-size: 36px;font-family:Arial,Times New Roman,KaiTi;">
                            <h2 style="color:firebrick">欢迎回家，{}!</h2>
                            <h2 style="color:firebrick">门已为您开启!</h2>
                            <iframe src="https://cloud.mokeyjay.com/pixiv" frameborder="0"  style="width:240px; height:380px;"></iframe> 
                        </div>
                    </div>
                '''.format(welcome)
            elif status == 'Er':
                write_log(request.remote_addr, '使用了一键开门,但由于开门密钥不正确,开门失败!')
                return '<h1>由于开门密钥不正确,开门失败!请管理员检查代码!</h1>'
            elif status == 'Timeout':
                write_log(request.remote_addr, '使用了一键开门,但由于与门锁的连接超时,开门失败!')
                return '''
                <body style="background-image: url(http://www.pptbz.com/d/file/p/201708/a1d07b6201af8f574b6539cb724bbc16.png);background-repeat:no-repeat;background-size:100% 100%;-moz-background-size:100% 100%;">
                    <div style="text-align:center;">
                        <p style="color:dimgrey; font-family:Arial,Times New Roman,KaiTi;margin-top: 2%;margin-bottom: 2%;font-size: 48px;">南昌大学190919数据中心提醒您</p>
                        <div style="font-size: 36px;font-family:Arial,Times New Roman,KaiTi;">
                            <h2 style="color:firebrick">发生错误！</h2>
                            <h2 style="color:firebrick">门锁的连接超时,开门失败!</h2>
                        </div>
                    </div>
                '''
        except:
            write_log(request.remote_addr, '使用了一键开门,但由于与门锁的连接超时,开门失败!')
            return '''
            <body style="background-image: url(http://www.pptbz.com/d/file/p/201708/a1d07b6201af8f574b6539cb724bbc16.png);background-repeat:no-repeat;background-size:100% 100%;-moz-background-size:100% 100%;">
                <div style="text-align:center;">
                    <p style="color:dimgrey; font-family:Arial,Times New Roman,KaiTi;margin-top: 2%;margin-bottom: 2%;font-size: 48px;">南昌大学190919数据中心提醒您</p>
                    <div style="font-size: 36px;font-family:Arial,Times New Roman,KaiTi;">
                        <h2 style="color:firebrick">发生错误！</h2>
                        <h2 style="color:firebrick">门锁的连接超时,开门失败!</h2>
                    </div>
                </div>
            '''
    else:
        write_log(request.remote_addr, '使用了一键开门,由于请求过于频繁,开门失败')
        return '''
            <body style="background-image: url(http://www.pptbz.com/d/file/p/201708/a1d07b6201af8f574b6539cb724bbc16.png);background-repeat:no-repeat;background-size:100% 100%;-moz-background-size:100% 100%;">
                <div style="text-align:center;">
                    <p style="color:dimgrey; font-family:Arial,Times New Roman,KaiTi;margin-top: 2%;margin-bottom: 2%;font-size: 48px;">南昌大学190919数据中心提醒您</p>
                    <div style="font-size: 36px;font-family:Arial,Times New Roman,KaiTi;">
                        <h2 style="color:firebrick">门锁正在复位,请{}秒后再试!</h2>
                    </div>
                </div>      
        '''.format(20 - int((time.time() - time_last_request)))

@app.route('/downloadpage')
def downloadpage():
    write_log(request.remote_addr, '进入文件浏览页面')
    url_dict = {}
    printed_extensions = ['doc', 'ocx', 'xls', 'lsx', 'ppt', 'ptx', 'pdf', 'jpg', 'png', 'bmp']
    display_html = ''
    if not os.path.exists('./UploadFiles'):
        os.mkdir('./UplaodFiles')
    files = os.listdir('UploadFiles')
    for file in files:
        url_dict[file] = [os.path.abspath('./UploadFiles/{}'.format(file)),
                          '{:.4f}MB'.format(os.path.getsize('./UploadFiles/{}'.format(file)) / 1024 / 1024),
                          get_modify_time('./UploadFiles/{}'.format(file))]
    url_dict_sorted = sorted(url_dict.items(), key=lambda x: x[1][2][1], reverse=True)
    for i in range(len(url_dict_sorted)):
        display_html += '<tr><td class="link"><a style="font-size: 25px;" href="{}" title="{}">{}</a></td><td style="font-size: 25px;" class="size">{}</td><td class="link"><a style="font-size: 25px;" href="{}" title="打印">打印</a></td><td><a style="font-size: 25px;" href="{}" title="删除">删除</a></td><td style="font-size: 25px;" class="size">{}</td></tr>'.format(
            "/download?url=" + quote(url_dict_sorted[i][1][0]) + '&filename=' + quote(url_dict_sorted[i][0]),
            url_dict_sorted[i][0], url_dict_sorted[i][0], url_dict_sorted[i][1][1],
            "/print?filename=" + quote(url_dict_sorted[i][0]) if url_dict_sorted[i][0][
                                                                 -3:].lower() in printed_extensions else "",
            "/delete?filename=" + quote(url_dict_sorted[i][0]),
            url_dict_sorted[i][1][2][0])
    disk_info = get_disk_info()
    return '''
    <body style="background-image: url(http://www.pptbz.com/d/file/p/201708/a1d07b6201af8f574b6539cb724bbc16.png);background-repeat:no-repeat;background-size:100% 100%;-moz-background-size:100% 100%;font-family:Arial,Times New Roman,KaiTi;text-align:center;color: dimgrey;">
        <div>
            <p style="font-size: 18px;">总存储空间:{:.2f}GB 已用存储空间:{:.2f}GB 可用存储空间:{:.2f}GB 已占用比例:{:.1f}%</p>
            <p style="font-size: 18px;">当前远程打印仅支持doc docx xls xlsx ppt pptx pdf jpg png bmp格式,且office格式需要等待转换!</p>
            <h1 style="color:firebrick">文件管理</h1>
            <table style="text-align: center;">
                <thead>
                    <tr>
                        <th style="width:50%"></th>
                        <th style="width:15%"></th>
                        <th style="width:5%"></th>
                        <th style="width:5%"></th>
                        <th style="width:25%"></th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="link"><a style="font-size: 24px;" title="文件名">文件名</a></td>
                        <td style="font-size: 24px;" class="size">文件大小</td>
                        <td class="print"><a style="font-size: 24px;" title="打印"></a></td>
                        <td><a style="font-size: 24px;" title="删除文件"></a></td>
                        <td><a style="font-size: 24px;" title="上传日期">上传日期</a></td>
                    </tr>{}
                </tbody>
            </table>
        </div>
    </body>
    '''.format(disk_info[0] / 1024 / 1024 / 1024, disk_info[1] / 1024 / 1024 / 1024,
               disk_info[2] / 1024 / 1024 / 1024, disk_info[3] * 100, display_html)


@app.route('/download', methods=['GET'])
def download():
    if request.method == 'GET':
        url = unquote(str(request.args.get('url')))
        filename = unquote(str(request.args.get('filename')))
        # return send_file(url, conditional=True, attachment_filename=filename, as_attachment=True)
        write_log(request.remote_addr, '尝试打开/下载文件{}'.format(filename))
        return redirect(url_for('static', filename=filename))


@app.route('/uploadpage', methods=['GET', 'POST'])
@passport
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # ''.join(lazy_pinyin(file.filename))
            # filename = secure_filename(file.filename)
            filename = filename_filter(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            write_log(request.remote_addr, '上传了名为{}的文件'.format(filename))
            return '''
                <body style="background-image: url(http://www.pptbz.com/d/file/p/201708/a1d07b6201af8f574b6539cb724bbc16.png);background-repeat:no-repeat;background-size:100% 100%;-moz-background-size:100% 100%;">
                    <div style="text-align:center;">
                        <p style="color:dimgrey; font-family:Arial,Times New Roman,KaiTi;margin-top: 2%;margin-bottom: 2%;font-size: 48px;">南昌大学190919数据中心提醒您</p>
                        <div style="font-size: 36px;font-family:Arial,Times New Roman,KaiTi;">
                            <h2 style="color:firebrick">{}上传成功!</h2>
                            <h2 style="color:firebrick">奖励一个吻</h2>
                        </div>
                    </div>
            '''.format(filename)
    else:
        write_log(request.remote_addr, '进入文件上传页面')
        disk_info = get_disk_info()  # return (all_space, used_space, free_space, used_percent)
        return '''
        <body style="background-image: url(http://www.pptbz.com/d/file/p/201708/a1d07b6201af8f574b6539cb724bbc16.png);background-repeat:no-repeat;background-size:100% 100%;-moz-background-size:100% 100%;font-family:Arial,Times New Roman,KaiTi;text-align:center;color: dimgrey;">
            <div>
                <p style="font-size: 18px;">总存储空间:{:.2f}GB 已用存储空间:{:.2f}GB 可用存储空间:{:.2f}GB 已占用比例:{:.1f}%</p>
                <p style="font-size: 32px;color:firebrick;">当前只能上传单个文件!</p>
                <form action="" method=post enctype=multipart/form-data>
                    <p><input type=file name=file>
                        <input type=submit value=点击上传>
                </form>
            </div>
        </body>
        '''.format(disk_info[0] / 1024 / 1024 / 1024, disk_info[1] / 1024 / 1024 / 1024,
                   disk_info[2] / 1024 / 1024 / 1024, disk_info[3] * 100)


def kill_process(key):
    os.system('sudo kill -9 $(pidof {})'.format(key))


@app.route('/playmusic', methods=['GET', 'POST'])
@passport
def play_music():
    if request.method == 'GET':
        write_log(request.remote_addr, '进入点歌页面')
        return '''
        <body style="background-image: url(http://www.pptbz.com/d/file/p/201708/a1d07b6201af8f574b6539cb724bbc16.png);background-repeat:no-repeat;background-size:100% 100%;-moz-background-size:100% 100%;text-align:center;">
            <div sytle="position: absolute;top: 0;bottom: 0;left: 0;right: 0;margin: auto;height: 240px;width: 70%;">
                <h1>请输入歌曲名</h1>
                <div style="color:dimgrey; font-size: 24px;font-family:Arial,Times New Roman,KaiTi;">
                    <form action="" method=post enctype=multipart/form-data>
                        <p><input name=MusicName></p>
                        <p>音源选择:
                            <select name=Source>
                                <option value="网易云音乐搜索">网易云音乐</option>
                                <option value="QQ音乐搜索">QQ音乐</option>
                                <option value="酷狗音乐搜索">酷狗音乐</option>
                                <option value="酷我音乐搜索">酷我音乐</option>
                                <option value="虾米音乐搜索">虾米音乐</option>
                                <option value="喜马拉雅搜索">喜马拉雅</option>
                                <option value="百度音乐搜索">百度音乐</option>
                                <option value="咪咕音乐搜索">咪咕音乐</option>
                            </select></p>
                        <p><input type=submit name=button value=搜索><input type=submit name=button value=停止播放></p>
                    </form>
                </div>
            </div>
        </body>
        '''
    elif request.method == 'POST':
        source_dict = {'网易云音乐搜索': 'netease', '咪咕音乐搜索': 'migu', '虾米音乐搜索': 'xiami', 'QQ音乐搜索': 'qq', '百度音乐搜索': 'baidu',
                       '酷狗音乐搜索': 'kugou', '酷我音乐搜索': 'kuwo', '喜马拉雅搜索': 'ximalaya'}
        musicname = request.form['MusicName']
        source = request.form['Source']
        if request.form['button'] == '停止播放':
            os.system('sudo kill -9 $(pidof {})'.format('mplayer'))
            return '<h1>已停止音乐播放!</h1>'
        return MusicSpider.show_html_list(musicname, source=source_dict[source])


@app.route('/playsoundbyurl')
@passport
def playsound_url():
    if platform.system() == 'Linux':
        os.system('sudo kill -9 $(pidof {})'.format('mplayer'))
    url = request.args.get('playurl')
    MusicSpider.download_music_by_url(url)
    MusicSpider.playmusic_downloaded('temp.mp3')
    write_log(request.remote_addr, '点歌')
    return '''
    <body style="background-image: url(http://www.pptbz.com/d/file/p/201708/a1d07b6201af8f574b6539cb724bbc16.png);background-repeat:no-repeat;background-size:100% 100%;-moz-background-size:100% 100%;">
        <div style="text-align:center;">
            <p style="color:dimgrey; font-family:Arial,Times New Roman,KaiTi;margin-top: 2%;margin-bottom: 2%;font-size: 48px;">南昌大学190919数据中心提醒您</p>
            <div style="font-size: 36px;font-family:Arial,Times New Roman,KaiTi;">
                <h2 style="color:firebrick">当前曲目播放完毕！</h2>
            </div>
        </div>
    '''

@app.route('/delete')
@passport
def deletefile():
    filename = unquote(str(request.args.get('filename')))
    os.remove('./UploadFiles/{}'.format(filename))
    write_log(request.remote_addr, '删除了名为{}的文件'.format(filename))
    return redirect(url_for("downloadpage"))


@app.route('/print', methods=['GET'])
@passport
def printfile():
    if request.method == 'GET':
        special_format = ['doc', 'ocx', 'xls', 'lsx', 'ppt', 'ptx']
        filename = unquote(str(request.args.get('filename')))
        write_log(request.remote_addr, '提交了名为{}的文件到打印队列'.format(filename))
        if filename[-3:] not in special_format:
            os.system('lpoptions -d p2055d')
            os.system('lp /home/pi/RaspberryNetFramework/UploadFiles/{}'.format(filename))
            return "<h1>文件{}已发送至打印队列,若打印机未打开,请打开!</h1>".format(filename)
        else:
            os.system(
                'soffice --headless --invisible --convert-to pdf {} --outdir /home/pi/RaspberryNetFramework/convert'.format(
                    '/home/pi/RaspberryNetFramework/UploadFiles/' + filename))
            split_filename = filename.split('.')[:-1]
            pdffilename = '.'.join(split_filename) + '.pdf'
            while not os.path.exists('/home/pi/RaspberryNetFramework/convert/{}'.format(pdffilename)):
                continue
            os.system('lpoptions -d p2055d')
            os.system('lp /home/pi/RaspberryNetFramework/convert/{}'.format(pdffilename))
            os.system('sudo rm -r /home/pi/RaspberryNetFramework/convert/')
            return "<h1>文件{}格式转换完成,将会发送至打印队列并开始打印,若打印机未打开,请打开!</h1>".format(filename)


def aria2c_submit(url: str, store_filename=None):
    bt_flag = False
    if 'magnet' in url or 'torrent' in url:
        bt_flag = True
    if bt_flag:
        command_with_filename = 'aria2c -x10 -s16 {} -d /home/pi/RaspberryNetFramework/UploadFiles -o {} --seed-time=0'.format(
            url,
            store_filename)
        command = 'aria2c -x10 -s16 {} -d /home/pi/RaspberryNetFramework/UploadFiles --seed-time=0'.format(url)
    else:
        command_with_filename = 'aria2c -x10 -s16 {} -d /home/pi/RaspberryNetFramework/UploadFiles -o {}'.format(
            url,
            store_filename)
        command = 'aria2c -x10 -s16 {} -d /home/pi/RaspberryNetFramework/UploadFiles'.format(url)
    if platform.system() == 'Linux':
        if store_filename:
            if 'complete' in os.popen(command_with_filename).read():
                write_log('filedownload', '{}下载完成'.format(url))
            else:
                write_log('filedownload', '{}下载失败'.format(url))
        else:
            if 'complete' in os.popen(command).read():
                write_log('filedownload', '{}下载完成'.format(url))
            else:
                write_log('filedownload', '{}下载失败'.format(url))
    elif platform.system() == 'Windows':
        if store_filename:
            os.popen('aria2c {} -d ./UploadFiles -o {}'.format(url, store_filename))
        else:
            os.popen('aria2c {} -d ./UploadFiles'.format(url))


@app.route('/remotedownload', methods=['GET', 'POST'])
@passport
def remodedownload():
    if request.method == 'GET':
        disk_info = get_disk_info()  # return (all_space, used_space, free_space, used_percent)
        write_log(request.remote_addr, '进入了远程下载页面')
        return '''
       <body style="background-image: url(http://www.pptbz.com/d/file/p/201708/a1d07b6201af8f574b6539cb724bbc16.png);background-repeat:no-repeat;background-size:100% 100%;-moz-background-size:100% 100%;font-family:Arial,Times New Roman,KaiTi;text-align:center;color: dimgrey;">
            <div>
                <p style="font-size: 18px;">总存储空间:{:.2f}GB 已用存储空间:{:.2f}GB 可用存储空间:{:.2f}GB 已占用比例:{:.1f}%</p>
                <h1 style="color:firebrick">远程下载</h1>
                <form action="" method=post enctype=multipart/form-data>
                <p><input style="width:500px;" type=url name=url placeholder=可填写HTTP_FTP_Magnet_BT下载地址></p>
                <p><input style="width:500px;" type=filename name=filename placeholder=输入您想要保存的文件名,必须加上后缀,若此栏为空,默认使用下载文件作为文件名></p>
                    <input type=submit value=加入下载队列>
                </form>
            </div>
        </body>'''.format(disk_info[0] / 1024 / 1024 / 1024, disk_info[1] / 1024 / 1024 / 1024,
                          disk_info[2] / 1024 / 1024 / 1024, disk_info[3] * 100)
    elif request.method == 'POST':
        url = request.form.get('url')
        store_filename = request.form.get('filename')
        if url[:6] == 'magnet':
            url = '\'{}\''.format(url)
        if url:
            if '.' in store_filename:
                remote_download_thread = threading.Thread(target=aria2c_submit, args=(url, store_filename))
            else:
                remote_download_thread = threading.Thread(target=aria2c_submit, args=(url,))
            remote_download_thread.start()
            write_log(request.remote_addr, '提交了远程下载任务,任务URL为:{}'.format(url))
            return '<h1>已将下载任务加入到下载队列,请耐心等待!若您的请求不规范,将不会正常下载!</h1>'
        else:
            write_log(request.remote_addr, '提交了不符合规范的远程下载任务')
            return '<h1>请填写符合规范的URL!</h1>'


@app.route('/readlog')
@passport
def read_log():
    
    with open('datacenter.log', mode='r', encoding='utf-8') as log:
        info = log.read().split('\n')
    return_string = ''
    for i in info:
        return_string = i + "</br>" + return_string
    return return_string


@app.route('/serverconfig', methods=['GET', 'POST'])
@passport
def server_config():
    if request.method == 'GET':
        return '''
        <body style="background-image: url(http://www.pptbz.com/d/file/p/201708/a1d07b6201af8f574b6539cb724bbc16.png);background-repeat:no-repeat;background-size:100% 100%;-moz-background-size:100% 100%;text-align:center;">
            <div sytle="position: absolute;top: 0;bottom: 0;left: 0;right: 0;margin: auto;height: 240px;width: 70%;">
                <h1>服务器系统设置</h1>
                <form action="/volumnset" method=post enctype=multipart/form-data>
                <p><input style="width:140px" type=text name=vol placeholder=输入音量大小(0-100)>
                    <input type=submit value=调节音量></p>
                    </form>
                <form action="/startvncserver" method=post enctype=multipart/form-data>
                <p><input type=submit value=启动TightVNCServer></p>
                    </form>
            </div>
        </body>
        '''


@app.route('/volumnset', methods=['POST'])
@passport
def set_volumn():
    if request.method == 'POST':
        vol = request.form.get('vol')
        os.system("sudo amixer set Master {}%".format(vol))
        write_log(request.remote_addr, '调节系统音量到{}%'.format(vol))
        return '''
        <body style="background-image: url(http://www.pptbz.com/d/file/p/201708/a1d07b6201af8f574b6539cb724bbc16.png);background-repeat:no-repeat;background-size:100% 100%;-moz-background-size:100% 100%;">
            <div style="text-align:center;">
                <p style="color:dimgrey; font-family:Arial,Times New Roman,KaiTi;margin-top: 2%;margin-bottom: 2%;font-size: 48px;">南昌大学190919数据中心提醒您</p>
                <div style="font-size: 36px;font-family:Arial,Times New Roman,KaiTi;">
                    <h2 style="color:firebrick">系统音量已调至{}%!</h2>
                </div>
            </div>
        '''.format(vol)


@app.route('/startvncserver', methods=['POST'])
@passport
def start_vncserver():
    if request.method == 'POST':
        os.system("tightvncserver")
        write_log(request.remote_addr, '启动了TightVNCServer服务!')
        return "<h1>TightVNCServer已启动!</h1>"


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9999)
