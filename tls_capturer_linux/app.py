# -*- coding: utf-8 -*-
import json
from flask import Flask, render_template, request
from concurrent.futures import ThreadPoolExecutor
import os
import subprocess
import threading

app = Flask(__name__)

# 定义pcap文件所在的路径
pcap_dir = '/usr/ja4/tls_capturer_linux/utils/pcap'

# 创建一个线程池
executor = ThreadPoolExecutor(max_workers=5)  # 可以根据需要调整线程池大小


def run_collect_script(ip_address):
    """运行 collect.py 脚本的后台任务"""
    try:
        # 指定 collect.py 的绝对路径和IP地址
        collect_script = ['python3', '/usr/ja4/tls_capturer_linux/utils/collect.py', ip_address]
        subprocess.run(collect_script, check=True)
        print(f"pcap collection for IP {ip_address} completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during pcap collection for IP {ip_address}: {e}")


@app.route('/')
def index():
    # 获取客户端的IP地址
    client_ip = request.remote_addr
    print(f"Received request from IP: {client_ip}")

    # 渲染 index.html 页面
    response = render_template('index.html', client_ip=client_ip)

    # 返回渲染的页面，同时附加一个在返回响应后启动后台任务的钩子
    def run_after_response():
        print("Response sent, running the background task.")
        executor.submit(run_collect_script, client_ip)

    # 使用一个线程来运行后台任务，以确保它在响应之后执行
    threading.Thread(target=run_after_response).start()

    return response


@app.route('/ja4_results')
def ja4_results():
    results = []

    # 遍历pcap文件夹中的每个pcap文件
    for filename in os.listdir(pcap_dir):
        if filename.endswith('.pcap'):
            file = os.path.join(pcap_dir, filename)
            # 将pcap文件传递给ja4.py进行处理
            ja4 = ['python3', '/usr/ja4/tls_capturer_linux/utils/ja4.py', "-J", file]
            result = subprocess.run(ja4, capture_output=True, text=True)

            ja4_result = result.stdout.strip()

            # 将字符串按独立的 JSON 对象分割
            json_strings = ja4_result.strip().split('\n}\n{')
            json_strings = [s if s.startswith('{') else '{' + s for s in json_strings]
            json_strings = [s if s.endswith('}') else s + '}' for s in json_strings]

            # 解析并过滤数据
            filtered_data = []
            for json_str in json_strings:
                try:
                    entry = json.loads(json_str)
                    if 'JA4' in entry and 'src' in entry:
                        filtered_entry = {"JA4": entry["JA4"], "src": entry["src"]}
                        filtered_data.append(filtered_entry)
                    else:
                        print(f"Missing expected keys in entry: {entry}")
                except json.JSONDecodeError as e:
                    print(f"JSONDecodeError: {e}")

            # 将过滤后的数据转换为 JSON 字符串
            filtered_data_str = json.dumps(filtered_data, indent=4)

            results.append({
                'filename': filename,
                'ja4_result': filtered_data_str
            })

    return render_template('ja4_results.html', results=results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, debug=True, ssl_context=('ssl_key/server.crt', 'ssl_key/private.key'))