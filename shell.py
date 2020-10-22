import os
import sys
import shlex
import getpass
import socket
import signal
import subprocess
import platform
from func import *

# 定义一张字典表，用于存储命令与函数的映射
built_in_cmds = {}

def register_command(name, func):
    """
    注册命令，使命令与相应的处理函数建立映射关系
    @param name： 命令名
    @param func： 函数名
    """
    built_in_cmds[name] = func

def init():
    """
    注册所有命令
    """
    register_command("cd", cd)
    register_command("exit", exit)
    register_command("getenv", getenv)
    register_command("history", history)

def shell_loop():
    status = SHELL_STATUS_RUN

    while status == SHELL_STATUS_RUN:
        # 打印命令提示符，形如`[<user>@<hostname> <base_dir>]$`
        display_cmd_prompt()

        # 忽略Ctrl-Z 或者 Ctrl-C 信号
        ignore_signals()

        try:
            # 读取命令
            cmd = sys.stdin.readline()

            # 解析命令
            # 将命令进行分拆，返回一个列表
            cmd_tokens = tokenize(cmd)

            # 预处理函数
            cmd_tokens = preprocess(cmd_tokens)

            # 执行命令，并返回 shell 的状态
            status = execute(cmd_tokens)
        except:
            _, err, _ = sys.exc_info()
            print(err)

def display_cmd_prompt():
    # 获取当前用户名
    user = getpass.getuser()

    # 获取当前运行 python 程序的机器的主机名
    hostname = socket.gethostname()

    # 获取当前工作路径
    cwd = os.getcwd()

    # 获取路径cwd 的最低一级目录
    base_dir = os.path.basename(cwd)

    # 如果用户当前位于用户的根目录下，使用‘~’ 代替目录名
    home_dir = os.path.expanduser('~')
    if cwd == home_dir:
        base_dir = '~'

    # 输出命令提示符
    if platform.system() != 'windows':
        sys.stdout.write("[\033[1;33m%s\033[0;0m@%s \033[1;36m%s\033[0;0m] $" %
                (user, hostname, base_dir))
    else:
        sys.stdout.write("[%s@%s %s]$ " % (user, hostname, base_dir))
    sys.stdout.flush()

def ignore_signals():
    if platform.system() != 'Windows':
        signal.signal(signal.SIGTSTP, signal.SIG_IGN)
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def tokenize(string):
    # 将string 按shell 的语法规则进行分割
    return shlex.split(string)

def preprocess(tokens):
    processed_token = []
    for token in tokens:
        if token.startswith('$'):
            processed_token.append(os.getenv(token[1:]))
        else:
            processed_token.append(token)
    return processed_token

def handler_kill(signum, frame):
    raise OSError("Killed!")

def execute(cmd_tokens):
    with open(HISTORY_PATH, 'a') as history_file:
        history_file.write(' '.join(cmd_tokens) + os.linesep)

    if cmd_tokens:
        cmd_name = cmd_tokens[0]
        cmd_args = cmd_tokens[1:]

        if cmd_name in built_in_cmds:
            return built_in_cmds[cmd_name](cmd_args)

        signal.signal(signal.SIGINT, handler_kill)

        if platform.system() != 'Windows':
            p = subprocess.Popen(cmd_tokens)
            p.communicate()
        else:
            command = ""
            command = ' '.join(cmd_tokens)
            os.system(command)
    return SHELL_STATUS_RUN

def main():
    init()
    shell_loop()

if __name__ == "__main__":
    main()
