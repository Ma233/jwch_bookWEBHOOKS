#!/usr/bin/env python
# coding=utf-8
from flask import Flask, request, abort
import os, subprocess, time, logging, json

app = Flask(__name__)

'''网站根目录的路径，推荐使用绝对路径'''
ROOT_PATH = '/home/group/jwch_bookWEBHOOKS/jwch-book/'

def ipIdent(ip):
    '''用于限定ip地址'''
    ip = ip.split('.')
    if ip[0] != '192' or ip[1] != '30' or int(ip[2])<252:
        logging.warning("The "+ip[0]+"."+ip[1]+"."+ip[2]+"."+ip[3]+".")
        abort(403)
    logging.warning("ipAddr is OK")

def cmdProcess(cmd):
    '''执行接受的命令，返回布尔值,并在输出流中留下记录'''
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=-1)
    wrongInfo = p.stderr.read()
    if wrongInfo == '':                          
        logging.warning(cmd+" Done!")
        return None
    else:
        logging.error(cmd+" ERROR!")
        logging.error(wrongInfo)
        return wrongInfo
    
def JudgeAndRecord():
    pass




@app.route('/', methods=['GET','POST'])
def web_hooks():

    #ipIdent(request.remote_addr)

    if request.method == 'GET':
        return 'jwch_book自动更新系统，具体用法：保密……'

    if request.method == 'POST':
        logging.warning("in POST")
        pusher = json.loads(request.form['payload'])['pusher']
        logging.warning("pusher is "+pusher["name"])

        '''打开记录文件'''
        if(os.path.exists(ROOT_PATH+'_build/html/record.txt')!=True):
           os.system('touch _build/html/record.txt')
        wFILE=open(ROOT_PATH+'_build/html/record.txt', 'a')
        wFILE.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())+'\t'+pusher["name"]+'\tdebug:\n')
        logging.warning("write time and pusher")

        '''更新本地仓库'''
        os.system('cd '+ROOT_PATH+' && git pull')

        '''重启服务并记录错误'''
        logging.warning("Realoading jwch_book...")

        wrongInfo = cmdProcess('cd '+ROOT_PATH+' && make html')
        if wrongInfo:
            wFILE.write('Make Html Error\n')
            wFILE.write(wrongInfo)

        wrongInfo = cmdProcess('cd '+ROOT_PATH+' && make rsync')
        if wrongInfo:
            wFILE.write('Make Rsync Error\n')
            wFILE.write(wrongInfo)

        if wrongInfo == None:
            wFILE.write('Success!\n')

        os.system('cd '+ROOT_PATH+' && make rsync')
        wFILE.close()
        logging.warning("Done! ^_^  ")
        return 'http://jwch.sdut.edu.cn/book/record.txt'

#if __name__=='__main__':
#    app.run()
