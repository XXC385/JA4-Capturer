# -*- coding: utf-8 -*-
import subprocess
import time
import os
import signal
from scapy.all import rdpcap, wrpcap

# 定义全局变量
output_dir = "/usr/ja4/tls_capturer_linux/tuils/pcap"
duration = 30  # 捕获持续时间

# 确保输出目录存在
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def save_pcap_from_tcpdump(output_file):
    """从tcpdump生成的pcap文件中保存捕获的包"""
    packets = rdpcap(output_file)
    if packets:
        filename = "{}/tcpdump_capture.pcap".format(output_dir)  # 使用固定的文件名
        wrpcap(filename, packets)
        print("Saved {} packets to {}".format(len(packets), filename))
    else:
        print("No packets captured.")

def start_tcpdump(duration, output_file):
    """启动tcpdump进程，运行指定的时间并保存到输出文件"""
    process = subprocess.Popen(["tcpdump", "-i", "any", "-w", output_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        # 等待指定的持续时间
        time.sleep(duration)

        # 发送SIGINT信号以模拟Ctrl+C
        process.send_signal(signal.SIGINT)

        # 等待tcpdump进程结束
        process.communicate()
    except Exception as e:
        print("An error occurred: {}".format(e))
    finally:
        if process.poll() is None:
            process.terminate()

if __name__ == "__main__":
    pcap_output_file = "{}/tcpdump_capture.pcap".format(output_dir)  # 使用固定的文件名

    print("Starting tcpdump for {} seconds...".format(duration))
    start_tcpdump(duration, pcap_output_file)

    print("Processing captured packets...")
    save_pcap_from_tcpdump(pcap_output_file)

    print("Capture and processing completed.")