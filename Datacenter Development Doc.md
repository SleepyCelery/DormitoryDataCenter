# 南昌大学190919数据中心开发文档

[TOC]

------

## 概述

南昌大学190919数据中心是190919寝室的中心数据交互平台:happy:,暂支持功能如下:

* 电费查询

* 一键开门

* 文件管理(包括上传,下载和删除)

* 浏览文件

* 文件打印

* 远程下载

* 获取日志

  以上所有功能皆采用标准RESTful API实现

---

## 请求公共部分

请求URL:<http://ncu190919.com/>

请求返回内容均为json,结构如下所示:

| 返回字段 | 返回值                                                       |
| -------- | ------------------------------------------------------------ |
| status   | 表示服务器对请求的处理状态,1为请求正常,0为由于服务器内部原因导致请求失败,-1为请求用户无权限访问该API |
| name     | 根据请求的IP地址,返回请求终端所有者的姓名,具体值见下面表格   |
| data     | 包含请求的具体API的返回值或服务器处理状态,**若用户无权限访问,则没有该字段** |

IP地址与姓名的对应关系如下所示(IP与设备MAC绑定):

| 对应姓名 | IP地址        |
| -------- | ------------- |
| 巢义虎   | 192.168.1.199 |
| 巢义虎   | 192.168.1.185 |
| 舒伟童   | 192.168.1.224 |
| 舒伟童   | 192.168.1.152 |
| 余廖祎   | 192.168.1.165 |
| 余廖祎   | 192.168.1.130 |
| 黄方军   | 192.168.1.218 |
| 黄方军   | 192.168.1.219 |
| 管理员   | 127.0.0.1     |
| 游客     | 其余IP地址    |

------

## 各API单独请求部分

### 电费查询

**本API支持全校寝室电费查询​,​向​游客开放:grin:**

请求URL:<http://ncu190919.com/elec>

请求方法:POST

需要POST的表单数据:

| 表单字段  | 对应值 |
| --------- | ------ |
| dormitory | 寝室号 |

请求成功后返回json数据的data字段:

| 字段名    | 值                    |
| --------- | --------------------- |
| dormitory | 请求的寝室号          |
| elec      | 剩余电量(单位:千瓦时) |
| money     | 剩余金额(单位:元)     |

Python请求示例:

>import requests
>
>response = requests.post(url="http://ncu190919.com/elec",data={"dormitory":"190919"})
>
>print(response.json())

请求成功示例:

> {
>
> ​		"status": "1",
>
> ​		"name": "管理员",
>
> ​		"data":{
>
> ​						"dormitory": "190919",
>
> ​						"elec": "62.99",
>
> ​						"money": "39.05"
>
> ​						}
>
> }

请求失败示例:

> {
>
> ​		"status": "0",
>
> ​		"name": "管理员"
>
> }

### 一键开门

**本API游客无权访问:disappointed:**

请求URL:<http://ncu190919.com/opendoor>

请求方法:GET

请求携带参数:无

请求成功后返回json数据的data字段:

| 字段名  | 值                                                           |
| ------- | ------------------------------------------------------------ |
| message | 开门状态,success表示开门成功,若返回数字,则表示请求过于频繁,开门失败,数字代表允许下一次请求的间隔时间,单位:秒 |

Python请求示例:

> import requests
>
> response = requests.get(url="http://ncu190919.com/opendoor")
>
> print(response.json())

请求成功示例:

> {
>
> ​		"status": "1",
>
> ​		"name": "管理员",
>
> ​		"data":{
>
> ​						"message": "success"
>
> ​						}
>
> }

请求失败示例:

> {
>
> ​		"status": "1",
>
> ​		"name": "管理员",
>
> ​		"data":{
>
> ​						"message": "13"
>
> ​						}
>
> }

### 文件上传

**本API游客无权访问:disappointed:**

请求URL:<http://ncu190919.com/uploadfile>

请求方法:POST

需要POST的表单数据:

| 表单字段    | 对应值                                                       |
| ----------- | ------------------------------------------------------------ |
| filename    | 上传文件的文件名,该文件将以该名称保存到服务器,应确保文件名符合Linux文件命名规范 |
| filecontent | 上传文件的二进制数据,数据大小应该在1TB内                     |

请求成功后返回json数据的data字段:

| 字段名   | 值                                                           |
| -------- | ------------------------------------------------------------ |
| filename | 最终保存在服务器上的文件名,经过了命名规则的过滤              |
| message  | 数据保存状态,success表示保存成功,out of range表示上传的文件大小超过限制 |

Python请求示例:

> import requests
>
> with open("abc.jpg",mode="rb") as file:
>
> ​		file_binary_code = file.read()
>
> response = requests.post(url="http://ncu190919.com/uploadfile", data={filename="abc.jpg",filecontent=file_binary_code})
>
> print(response.json())

请求成功示例:

> {
>
> ​		"status": "1",
>
> ​		"name": "管理员",
>
> ​		"data":{
>
> ​						"filename": "abc.jpg",
>
> ​						"message": "success"
>
> ​						}
>
> }

请求失败示例:

> {
>
> ​		"status": "1",
>
> ​		"name": "管理员",
>
> ​		"data":{
>
> ​						"filename": "abc.jpg",
>
> ​						"message": "out of range"
>
> ​						}
>
> }

### 文件下载

**本API向游客开放:happy:**

请求URL:<http://ncu190919.com/downloadfile>

请求方法:GET

请求携带参数:

| 参数名   | 值                             |
| -------- | ------------------------------ |
| filename | 要下载的文件名(该文件必须存在) |

该请求在请求成功后,直接重定向到文件路径.若请求失败,则返回json数据

请求成功后返回json数据的data字段:

| 字段名   | 值                                             |
| -------- | ---------------------------------------------- |
| filename | 请求下载的文件名                               |
| message  | 数据下载状态,not found表示未在服务器上找到文件 |

Python请求示例:

> import requests
>
> response = requests.get(url="http://ncu190919.com/downloadfile", params={"filename":"abc.jpg"})
>
> print(response.json())

请求成功,直接重定向至文件路径

请求失败示例:

> {
>
> ​		"status": "1",
>
> ​		"name": "管理员",
>
> ​		"data":{
>
> ​						"filename": "abc.jpg",
>
> ​						"message": "not found"
>
> ​						}
>
> }

### 文件删除

**本API游客无权访问:disappointed:**

请求URL:<http://ncu190919.com/deletefile>

请求方法:GET

请求携带参数:

| 参数名   | 对应值                           |
| -------- | -------------------------------- |
| filename | 请求删除的文件名(该文件必须存在) |

请求成功后返回json数据的data字段:

| 字段名   | 值                                                           |
| -------- | ------------------------------------------------------------ |
| filename | 请求删除的文件名                                             |
| message  | 文件删除状态,success表示文件删除成功,not found表示未找到要删除的文件 |

Python请求示例:

> import requests
>
> response = requests.get(url="http://ncu190919.com/deletefile", params={"filename":"abc.jpg"})
>
> print(response.json())

请求成功示例:

> {
>
> ​		"status": "1",
>
> ​		"name": "管理员",
>
> ​		"data":{
>
> ​						"filename": "abc.jpg",
>
> ​						"message": "success"
>
> ​						}
>
> }

请求失败示例:

> {
>
> ​		"status": "1",
>
> ​		"name": "管理员",
>
> ​		"data":{
>
> ​						"filename": "abc.jpg",
>
> ​						"message": "not found"
>
> ​						}
>
> }

### 浏览文件

**本API向游客开放:happy:**

请求URL:<http://ncu190919.com/getfileinfo>

请求方法:GET

请求携带参数:

| 参数名   | 对应值                                                       |
| -------- | ------------------------------------------------------------ |
| filename | 查询文件的文件名(该文件必须存在),特殊的,如果该参数的值为#all_files#,则会返回所有文件的信息列表 |

请求成功后返回json数据的data字段:

| 字段名   | 值                                                           |
| -------- | ------------------------------------------------------------ |
| filename | 请求查询的文件名                                             |
| message  | 查询状态,success表示查询成功,not found表示未找到要查询的文件,如果返回not found,则没有info字段 |
| info     | 一个列表,包含查询的文件的信息,包含文件名,文件大小,上传日期,其中文件大小的单位为字节 |

Python请求示例:

> import requests
>
> response = requests.get(url="http://ncu190919.com/getfileinfo", params={"filename":"abc.jpg"})
>
> print(response.json())

请求成功示例:

> {
>
> ​		"status": "1",
>
> ​		"name": "管理员",
>
> ​		"data":{
>
> ​						"filename": "abc.jpg",
>
> ​						"message": "success",
>
> ​						"info":[
>
> ​										{
>
> ​											"filename": "abc.jpg",
>
> ​											"filesize": "1876283",
>
> ​											"uploadtime": "2019-9-27 22:04:45"
>
> ​										}
>
> ​								]
>
> ​						}
>
> }

请求失败示例:

> {
>
> ​		"status": "1",
>
> ​		"name": "管理员",
>
> ​		"data":{
>
> ​						"filename": "abc.jpg",
>
> ​						"message": "not found"
>
> ​						}
>
> }

### 文件打印

文件打印只能打印已上传的文档,且仅支持以下格式:

* doc
* docx
* xls
* xlsx
* ppt
* pptx
* pdf
* jpg
* png
* bmp

其中,与office相关的格式,会调用本地的soffice组件强制转换为pdf打印,可能会导致打印出来的文件排版不正常.建议先在本地使用Microsoft Office组件转换成pdf后再上传到服务器调用打印服务

**本API游客无权访问:disappointed:**

请求URL:<http://ncu190919.com/printfile>

请求方法:GET

请求携带参数:

| 参数名   | 对应值                                   |
| -------- | ---------------------------------------- |
| filename | 请求加入打印队列的文件名(该文件必须存在) |

请求成功后返回json数据的data字段:

| 字段名   | 值                                                           |
| -------- | ------------------------------------------------------------ |
| filename | 请求加入打印队列的文件名                                     |
| message  | 加入打印队列状态,success表示成功,not found表示未找到要打印的文件,format not allowed表示文件格式不受支持 |

Python请求示例:

> import requests
>
> response = requests.get(url="http://ncu190919.com/printfile", params={"filename":"abc.jpg"})
>
> print(response.json())

请求成功示例:

> {
>
> ​		"status": "1",
>
> ​		"name": "管理员",
>
> ​		"data":{
>
> ​						"filename": "abc.jpg",
>
> ​						"message": "success"
>
> ​						}
>
> }

请求失败示例:

> {
>
> ​		"status": "1",
>
> ​		"name": "管理员",
>
> ​		"data":{
>
> ​						"filename": "abc.jpg",
>
> ​						"message": "not found"
>
> ​						}
>
> }

### 远程下载

开辟一个新线程,并调用服务器的Aria2服务进行下载,最终下载成功的文件可通过浏览文件功能查看,并支持局域网内高速下载.目前支持的URL类型为:

* HTTP
* HTTPS
* FTP
* BitTorrent
* Magnet

BT下载有大概率出现问题,并不推荐使用.HTTP和HTTPS经测试,可以稳定下载

可搭配获取百度网盘文件的aria2下载链接插件进行下载 fuck baidupan :)

本API仅返回加入下载队列状态,并不返回即时下载情况,如要查看下载情况,请查看日志!

**本API游客无权访问:disappointed:**

请求URL:<http://ncu190919.com/remotedownload>

请求方法:GET

请求携带参数:

| 参数名      | 对应值                                                       |
| ----------- | ------------------------------------------------------------ |
| downloadurl | 请求加入下载队列的文件URL                                    |
| filename    | 要保存的文件名,需要符合Linux文件命名规范,若留空,则自动以下载文件名保存 |

请求成功后返回json数据的data字段:

| 字段名   | 值                                                     |
| -------- | ------------------------------------------------------ |
| filename | 请求加入下载队列的最终文件名,经过Linux文件命名规范过滤 |
| message  | 加入下载队列状态,success表示成功,fail表示失败          |

Python请求示例:

> import requests
>
> response = requests.get(url="http://ncu190919.com/downloadfile", params={"downloadurl": "http://b.hiphotos.baidu.com/image/pic/item/908fa0ec08fa513db777cf78376d55fbb3fbd9b3.jpg","filename":"abc.jpg"})
>
> print(response.json())

请求成功示例:

> {
>
> ​		"status": "1",
>
> ​		"name": "管理员",
>
> ​		"data":{
>
> ​						"filename": "abc.jpg",
>
> ​						"message": "success"
>
> ​						}
>
> }

请求失败示例:

> {
>
> ​		"status": "1",
>
> ​		"name": "管理员",
>
> ​		"data":{
>
> ​						"filename": "abc.jpg",
>
> ​						"message": "fail"
>
> ​						}
>
> }

### 获取磁盘状态

**本API游客无权访问:disappointed:**​

请求URL:<http://ncu190919.com/diskstatus>

请求方法:GET

请求携带参数:无

请求成功后返回json数据的data字段:

| 字段名       | 值                                                           |
| ------------ | ------------------------------------------------------------ |
| all_space    | 磁盘总空间大小(单位:字节)                                    |
| used_space   | 已使用的空间大小(单位:字节)                                  |
| free_space   | 剩余未使用的空间大小(单位:字节)                              |
| used_percent | 已使用的空间大小占总空间大小的百分比(用小于等于1的浮点数表示) |

Python请求示例:

> import requests
>
> response = requests.get(url="http://ncu190919.com/diskstatus")
>
> print(response.json())

请求成功示例:

> {
>
> ​		"status": "1",
>
> ​		"name": "管理员",
>
> ​		"data":{
>
> ​						"all_space": "65535",
>
> ​						"used_space": "65535",
>
> ​						"free_space": "0",
>
> ​						"used_percent": "1.0" 
>
> ​						}
>
> }

请求失败示例:

> {
>
> ​		"status": "-1",
>
> ​		"name": "管理员",
>
> ​		"data":{}
>
> }



### 获取日志

每请求一次服务器API,就会写入一次日志(包括上述所有API)

**本API游客无权访问:disappointed:**

请求URL:<http://ncu190919.com/readlog>

请求方法:GET

请求携带参数:无

请求成功后返回json数据的data字段:

| 字段名 | 值                                                        |
| ------ | --------------------------------------------------------- |
| log    | 一个列表,包含了所有的日志信息,若无日志信息,则该字段为空值 |

Python请求示例:

> import requests
>
> response = requests.get(url="http://ncu190919.com/readlog")
>
> print(response.json())

请求成功示例:

> {
>
> ​		"status": "1",
>
> ​		"name": "管理员",
>
> ​		"data":{
>
> ​						"log": [
>
> ​										"2019-9-28 01:41:56 巢义虎 进入了远程下载页面",
>
> ​										"2019-9-28 01:29:29 巢义虎 进入文件浏览页面",
>
> ​										"2019-9-28 00:21:16 巢义虎 查询了寝室号为['190919']的电费,查询成功",
>
> ​										"2019-9-28 00:21:13 巢义虎 进入电费查询页面",
>
> ​										"2019-9-27 23:37:13 巢义虎 进入首页"
>
> ​								]
>
> ​						}
>
> }

请求失败示例:

> {
>
> ​		"status": "-1",
>
> ​		"name": "游客",
>
> }

