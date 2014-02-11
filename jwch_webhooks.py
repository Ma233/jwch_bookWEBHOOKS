#!/usr/bin/env python
# coding=utf-8
from flask import Flask, request, abort
import os, subprocess, time, logging

app = Flask(__name__)

'''网站根目录的路径，最好使用绝对路径'''
ROOT_PATH = '/home/group/jwch_bookWEBHOOKS/jwch-book/'


@app.route('/', methods=['GET','POST'])
def web_hooks():

    '''ip地址限定'''
    ip = request.remote_addr.split('.')
    if ip[0] != 192 or ip[1] != 30 or ip[2]<252:
        abort(403)
    logging.warning("ipAddr is OK")

    if request.method == 'POST':
        '''获取pusher信息'''
        pusher = request.form['pusher']
        logging.warning("pusher is "+pusher["name"])

        '''打开记录文件'''
        if(os.path.exists(ROOT_PATH+'_build/html/record.txt')!=True):
           os.system('touch _build/html/record.txt')
        wFILE=open(ROOT_PATH+'_build/html/record.txt', 'w+')
        wFILE.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())+'\t'+pusher["name"]+'\t')
        logging.warning("write time and pusher")

        '''更新本地仓库'''
        os.system('cd '+ROOT_PATH+' && git pull')
        logging.warning("git pull success, realoading...")

        '''尝试重启服务'''
        p = subprocess.Popen('cd '+ROOT_PATH+' && make html', shell=True, stdout=subprocess.PIPE, stderr=-1)
        if p.stderr.read() != '':
            os.system('cd '+ROOT_PATH+' && git reset --HARD')
            wFILE.write('MakeHtmlFailed\n')
            wFILE.close()
            logging.error("make html failed")
            return
        p = subprocess.Popen('cd '+ROOT_PATH+' && make rsync', shell=True, stdout=subprocess.PIPE, stderr=-1)
        if p.stdeer.read() != '':
            os.system('cd '+ROOT_PATH+' && git reset --HARD')
            wFILE.write('MakeRsyncFailed\n')
            wFILE.close()
            logging.error("make rsync failed")
            return

        '''重启成功'''
        wFILE.write('Success!\n')
        wFILE.close()
        logging.warning("Done! ^_^  ")
        return

#if __name__=='__main__':
#    app.run()
