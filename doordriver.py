import socket


def send_cmd_withback(ip, port: int, content):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.connect((ip, port))
        server.send(bytes(content))
        recv = server.recv(2)
        print('命令发送成功,接收到返回值为{}'.format(recv.decode()))
        return recv.decode()
    except TimeoutError:
        print('连接超时!')
        return 'Timeout'
    finally:
        server.close()


def send_cmd(ip, port: int, content):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.connect((ip, port))
        server.send(bytes(content))
        print('命令发送成功')
        server.close()
        return 'Success'
    except TimeoutError:
        print('连接超时!')
        server.close()
        return 'Timeout'


if __name__ == '__main__':
    send_cmd_withback('192.168.1.145', 8080, b'190919111111')
