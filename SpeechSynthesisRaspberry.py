from aip import AipSpeech
import playsound
import subprocess
import platform
import os

""" 你的 APPID AK SK """
APP_ID = '11977145'
API_KEY = 'zX2sRK4h19hGLAWBa61tDfR5'
SECRET_KEY = 'ENxeIfU61t6OGB0my39Nc1IiVF07Tunz'

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)


def saveaudio(data):
    global times
    with open("speech.mp3", mode="wb") as file:
        file.write(data)


def generate(content, sex='女'):
    if sex == '女':
        voice = 0
    elif sex == '男':
        voice = 1
    else:
        voice = 0
    result = client.synthesis(content, "zh", 1, {"per": voice, })
    return result


def speech(content):
    if platform.system() == 'Windows':
        saveaudio(generate(content))
        playsound.playsound("speech.mp3", True)
    elif platform.system() == 'Linux':
        saveaudio(generate(content))
        os.system('sudo kill -9 $(pidof {})'.format('mplayer'))
        subprocess.Popen(['setsid', 'sudo', 'mplayer', 'speech.mp3', '<', '/dev/null', '>', '/dev/null', '2>1&'])


if __name__ == '__main__':
    speech('黄方军,欢迎回家!')
