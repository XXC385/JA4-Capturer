# -*- coding: utf-8 -*-
from flask import Flask, render_template
import os
import subprocess
import time

app = Flask(__name__)

# 定义pcap文件所在的路径
pcap_dir = '/usr/ja4/tls_capturer_linux/tuils/pcap'

@app.route('/')
def index():
    results = []

    # 步骤1: 生成新的pcap文件
    try:
        # 假设collect.py生成的pcap文件保存在pcap_dir目录下，文件名为captured.pcap
        collect_script = ['python3', '/usr/ja4/tls_capturer_linux/tuils/collect.py']
        subprocess.run(collect_script, check=True)

        # 等待一会儿，确保文件生成完毕
        time.sleep(8)
    except subprocess.CalledProcessError as e:
        return f"Error during pcap collection: {e}"

    # 步骤2: 遍历pcap文件夹中的每个pcap文件
    for filename in os.listdir(pcap_dir):
        if filename.endswith('.pcap'):
            file = os.path.join(pcap_dir, filename)
            # 将pcap文件传递给ja4.py进行处理
            ja4 = ['python3', '/usr/ja4/tls_capturer_linux/tuils/ja4.py', file]
            result = subprocess.run(ja4, capture_output=True, text=True)

            # 异常抛出
            print(f"Processing file: {file}")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")

            ja4_result = result.stdout.strip()

            # 将处理结果保存到results列表中
            results.append({
                'filename': filename,
                'ja4_result': ja4_result
            })

    # 渲染index.html模板，并传递results变量给前端页面
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, debug=True, ssl_context=('ssl_key/server.crt', 'ssl_key/private.key'))