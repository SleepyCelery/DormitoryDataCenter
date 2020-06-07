from ShadowsocksConfigSpider import ShadowsocksConfig
import time
import os
import multiprocessing
import logging
import traceback


def kill_process(key):
    os.system('sudo kill -9 $(pidof {})'.format(key))


def BuildServer():
    print('正在获取配置信息...')
    ss = ShadowsocksConfig(selenium_mode=False)
    print('已获取到配置信息!正在测速...')
    config = ss.get_config_random()
    print('已检测到最快节点!正在连接...')
    ss.dump_single_json(config)
    print('连接成功!')
    os.system('sslocal -c ssconfig.json')


if __name__ == '__main__':
    logging.basicConfig(filename='ShadowsocksServer_log.txt', level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logging.debug(traceback.format_exc())
    ss_processing = multiprocessing.Process(target=BuildServer, args=())
    run_flag = False
    while True:
        if run_flag:
            print('Shadowsocks进程已中断!')
            kill_process('sslocal')
            ss_processing.terminate()
            run_flag = False
        print('开始建立Shadowsocks连接!')
        kill_process('sslocal')
        ss_processing.start()
        run_flag = True
        time.sleep(1800)
