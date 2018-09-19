#!/usr/bin/env python3

import os
import sys
import ast
import paramiko
import requests
import json
from threading import Thread

#ip地址已脱敏
hosts = {
    'aws-nginx': '52.14.179.83',
    'tir-nginx-b-aws': '18.19.223.245',
    'tir-nginx-a-aws': '52.194.17.83',
    'walianwang-app-aws': '52.98.19.25',
    'walianwang-db-aws': '18.12.28.0',
    'hbase-master-aws': '18.179.4.199',
    'redis-aws': '13.231.250.40',
    'node-server-a-aws': '18.12.21.48',
    'hbase-slave1-aws': '18.19.50.02',
    'node-server-b-aws': '13.30.39.20',
    'rabbitmq-aws': '18.179.62.31',
    'tir-mq-aws': '13.230.35.13',
    'hbase-slave2-aws': '18.12.20.11',
    'crawler-test-aws': '18.182.5.28'
}

script_src_path = '/home/op/crontab-script/aws-sys-data.py'
script_rmt_path = '/tmp/aws-sys-data.py'
pkey_path = '/home/op/.ssh/id_rsa'


def dingding_robot(msg):

    url = 'https://oapi.dingtalk.com/robot/send?access_token=d1a90fbd767646e6a36c9f99b917db744567aebe80a1c7933b8c96d41a782842'
    data_info = {
        "msgtype": "text",
        "text": {
            "content": msg
        }
    }
    header_info = {"Content-Type": "application/json"}

    requests.post(url, data=json.dumps(data_info), headers=header_info)


def check_cpu_usage(hostname, ssh_client):

    cpu_used_percent = []
    for i in range(5):
        stdin, stdout, stderr = ssh_client.exec_command('python /tmp/aws-sys-data.py cpu')
        cpu_used_percent.append(0.0)
        cpu_used_percent.append(float(stdout.readlines()[0]))

    average_percent = sum(cpu_used_percent) / len(cpu_used_percent)
    if average_percent >= 90:
        msg = 'aws: ' + hostname + '  =>  cpu使用率大于90%'
        dingding_robot(msg)


def check_mem_usage(hostname, ssh_client):

    stdin, stdout, stderr = ssh_client.exec_command('python /tmp/aws-sys-data.py mem')
    mem_used_percent = float(stdout.readlines()[0])

    if mem_used_percent >= 90:
        msg = 'aws: ' + hostname + '  =>  memory使用率大于90%'
        dingding_robot(msg)


def check_disk_usage(hostname, ssh_client):

    stdin, stdout, stderr = ssh_client.exec_command('python /tmp/aws-sys-data.py disk')
    disk_used_percent = ast.literal_eval(stdout.readlines()[0])

    disk_used_abnormal = {k: v for k, v in disk_used_percent.items() if v >= 90}
    for k in disk_used_abnormal.keys():
        msg = 'aws: ' + hostname + '  =>  ' + k + ' 分区使用率大于90%'
        dingding_robot(msg)


def thread_job(hostname, hostip, private_key):

    try:
        t = paramiko.Transport((hostip, 22))
    except SSHException:
        dingding_robot('aws: ' + hostname + '  =>  ' + 'ssh连接失败!')

    try:
        t.connect(username='op', pkey=private_key)
    except AuthenticationException:
        dingding_robot('aws: ' + hostname + '  =>  ' + 'ssh认证失败!')
    else:
        sftp_client = paramiko.SFTPClient.from_transport(t)
        sftp_client.put(script_src_path, script_rmt_path)
        t.close()

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=hostip, port=22, username='op', pkey=private_key)
        check_cpu_usage(hostname, ssh_client)
        check_mem_usage(hostname, ssh_client)
        check_disk_usage(hostname, ssh_client)
        ssh_client.close()


def main():

    if not os.path.isfile(script_src_path):
        dingding_robot('/home/op/crontab-script/aws-sys-data.py脚本不存在！')
        sys.exit()

    if not os.path.isfile(pkey_path):
        dingding_robot('/home/op/.ssh/id_rsa私钥不存在！')
        sys.exit()
    else:
        private_key = paramiko.RSAKey.from_private_key_file('/home/op/.ssh/id_rsa')

    for hostname, hostip in hosts.items():
        thread = Thread(target=thread_job, args=(hostname, hostip, private_key))
        thread.start()


if __name__ == '__main__':
    main()
