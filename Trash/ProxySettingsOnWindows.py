import winreg
import struct
from tkinter import *


def start_sys_proxy(ipaddr, port):
    try:
        KEY = r'Software\Microsoft\Windows\CurrentVersion\Internet Settings\Connections'
        SUBKEY = 'DefaultConnectionSettings'
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY, 0, winreg.KEY_ALL_ACCESS)
        value, regtype = winreg.QueryValueEx(key, SUBKEY)
        server = f'{ipaddr}:{port}'.encode()
        bypass = '<local>'.encode()
        counter = int.from_bytes(value[4:8], 'little') + 1
        value = value[:4] + struct.pack('<III', counter, 3, len(server)) + server + struct.pack('<I', len(
            bypass)) + bypass + b'\x00' * 36
        winreg.SetValueEx(key, SUBKEY, None, regtype, value)
        winreg.CloseKey(key)
        return 'OK'
    except:
        return 'Error'


def close_sys_proxy():
    try:
        KEY = r'Software\Microsoft\Windows\CurrentVersion\Internet Settings\Connections'
        SUBKEY = 'DefaultConnectionSettings'
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY, 0, winreg.KEY_ALL_ACCESS)
        value, regtype = winreg.QueryValueEx(key, SUBKEY)
        counter = int.from_bytes(value[4:8], 'little') + 1
        value = value[:4] + struct.pack('<II', counter, 1) + b'\x00' * 44
        winreg.SetValueEx(key, SUBKEY, None, regtype, value)
        winreg.CloseKey(key)
        root.destroy()
        exit()
        return 'OK'
    except:
        return 'Error'


if __name__ == '__main__':
    start_sys_proxy('ncu190919.com', '8118')
    root = Tk()
    root.wm_attributes('-topmost', 1)
    root.title('树莓派科学上网连接工具(寝室专用)')
    root.geometry("400x120")
    tips_label = Label(root,
                       text='打开本软件即连接上树莓派网络!\n\n如无法正常上网,请关闭本软件,并在数据中心远程代理界面重启翻墙进程!\n\n关闭软件自动停止代理!\n\n启动本软件将会导致无法访问数据中心,若要访问数据中心,请关闭本软件!')
    tips_label.pack()
    root.protocol("WM_DELETE_WINDOW", close_sys_proxy)
    root.mainloop()
