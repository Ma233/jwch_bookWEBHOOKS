#!/usr/bin/env python
# coding=utf-8
from flask import Flask, request, abort
import os, subprocess, time

app = Flask(__name__)

'''网站根目录的路径，最好使用绝对路径'''
ROOT_PATH = '/home/group/jwch_bookWEBHOOKS/jwch-book/'

@app.route('/', methods=['GET','POST'])
def web_hooks():
    ip = request.remote_addr.split('.')
    if ip[0] != 192 or ip[1] != 30 or ip[2]<252:
        abort(403)
    if request.method == 'GET':
        return 'hello'
    if request.method == 'POST':
        '''获取pusher信息'''
        pusher = request.form['pusher']

        '''打开记录文件'''
        if(os.path.exists(ROOT_PATH+'_build/html/record.txt')!=True):
           os.system('touch _build/html/record.txt')
        wFILE=open(ROOT_PATH+'_build/html/record.txt', 'w+')
        wFILE.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())+'\t'+pusher["name"]+'\t')
        
        '''更新本地仓库'''
        os.system('cd '+ROOT_PATH+' && git pull')

        '''尝试重启服务'''
        p = subprocess.Popen('cd '+ROOT_PATH+' && make html', shell=True, stdout=subprocess.PIPE, stderr=-1)
        if p.stderr.read() != '':
            os.system('cd '+ROOT_PATH+' && git reset --HARD')
            wFILE.write('MakeHtmlFailed\n')
            wFILE.close()
            return
        p = subprocess.Popen('cd '+ROOT_PATH+' && make rsync', shell=True, stdout=subprocess.PIPE, stderr=-1)
        if p.stdeer.read() != '':
            os.system('cd '+ROOT_PATH+' && git reset --HARD')
            wFILE.write('MakeRsyncFailed\n')
            wFILE.close()
            return

        '''重启成功'''
        wFILE.write('Success!\n')
        wFILE.close()
        return

if __name__=='__main__':
    app.run()
