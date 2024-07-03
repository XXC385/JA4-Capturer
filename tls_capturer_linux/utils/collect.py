# -*- coding: utf-8 -*-
import subprocess
import time
import os
import signal
from scapy.all import rdpcap, wrpcap
from datetime import datetime
import sys

# 定义全局变量
output_dir = "/usr/ja4/tls_capturer_linux/utils/pcap"
duration = 5  # 捕获持续时间

# 确保输出目录存在
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


def save_pcap_from_tcpdump(output_file):
    """处理从tcpdump生成的pcap文件"""
    packets = rdpcap(output_file)
    if packets:
        print("Saved {} packets to {}".format(len(packets), output_file))
    else:
        print("No packets captured.")


def start_tcpdump(duration, output_file, ip_address):
    """启动tcpdump进程，运行指定的时间并保存到输出文件"""
    # 根据IP地址启动tcpdump进程
    process = subprocess.Popen(["tcpdump", "-i", "any", f"host {ip_address}", "-w", output_file],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        print(f"tcpdump started for IP {ip_address}. Capturing for {duration} seconds...")
        # 等待指定的持续时间
        time.sleep(duration)

        # 发送SIGINT信号以模拟Ctrl+C
        process.send_signal(signal.SIGINT)

        # 等待tcpdump进程结束
        process.communicate()
        print(f"tcpdump stopped for IP {ip_address}.")
    except Exception as e:
        print("An error occurred: {}".format(e))
    finally:
        if process.poll() is None:
            process.terminate()


if __name__ == "__main__":
    # 获取传入的IP地址参数
    if len(sys.argv) < 2:
        print("Usage: python collect.py <IP_ADDRESS>")
        sys.exit(1)

    ip_address = sys.argv[1]

    # 使用带时间戳和IP地址的文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pcap_output_file = f"{output_dir}/tcpdump_capture_{ip_address}_{timestamp}.pcap"

    print(f"Starting tcpdump for IP {ip_address} for {duration} seconds...")
    start_tcpdump(duration, pcap_output_file, ip_address)

    print("Processing captured packets...")
    save_pcap_from_tcpdump(pcap_output_file)

    print("Capture and processing completed.")