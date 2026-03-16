#!/usr/bin/env python3
"""
多订阅合并脚本 - Python 版本
支持多个订阅合并，新订阅节点追加到后面
"""

import yaml
import requests
import base64
import sys
from datetime import datetime

# 订阅 URL 列表（按顺序下载，新订阅追加到后面）
SUB_URLS = [
    "https://su.anywayfosec.xyz/api/v1/client/subscribe?token=bdc2904c4caa84f2e41fb73be508725c",
    "https://sub3.smallstrawberry.com/api/v1/client/subscribe?token=0a0f66805e2c4a66a2533279d872982d",
]

CONFIG_FILE = "/opt/clash/config.yaml"
BACKUP_DIR = "/opt/clash/backups/"

def download_subscription(url):
    """下载订阅（带重试）"""
    print(f"  下载：{url}")
    
    # 尝试通过代理下载
    try:
        response = requests.get(url, proxies={'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}, 
                               timeout=30, headers={'User-Agent': 'ClashForWindows/0.20.39'})
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"    代理下载失败：{e}")
    
    # 直接下载
    try:
        response = requests.get(url, timeout=30, headers={'User-Agent': 'ClashForWindows/0.20.39'}, verify=False)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"    直接下载失败：{e}")
    
    return None

def parse_subscription(content):
    """解析订阅内容，返回 proxies 列表"""
    # 尝试 base64 解码
    try:
        decoded = base64.b64decode(content).decode('utf-8')
        if 'proxies:' in decoded:
            content = decoded
    except:
        pass
    
    # 解析 YAML
    try:
        data = yaml.safe_load(content)
        if data and 'proxies' in data:
            return data['proxies']
    except Exception as e:
        print(f"    YAML 解析失败：{e}")
    
    return []

def main():
    print("=== 多订阅合并脚本 (Python) ===")
    print(f"订阅数量：{len(SUB_URLS)}\n")
    
    # 备份当前配置
    import shutil
    backup_file = f"{BACKUP_DIR}config.{datetime.now().strftime('%Y%m%d%H%M')}.yaml"
    try:
        shutil.copy(CONFIG_FILE, backup_file)
        print(f"✓ 已备份配置：{backup_file}\n")
    except Exception as e:
        print(f"⚠ 备份失败：{e}\n")
    
    # 读取当前配置
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取当前所有节点
    current_config = yaml.safe_load(content)
    current_proxies = current_config.get('proxies', [])
    print(f"当前配置节点数：{len(current_proxies)}")
    
    # 识别订阅源节点（放在最前面）
    subscription_nodes = []
    other_nodes = []
    
    for proxy in current_proxies:
        name = proxy.get('name', '')
        if '防失联' in name or '售前/售后' in name or 'haita.link' in name:
            subscription_nodes.append(proxy)
        else:
            other_nodes.append(proxy)
    
    print(f"  - 订阅源节点：{len(subscription_nodes)}")
    print(f"  - 其他节点：{len(other_nodes)}\n")
    
    # 下载并合并新订阅
    all_new_proxies = []
    for i, url in enumerate(SUB_URLS):
        print(f"[{i+1}/{len(SUB_URLS)}] 下载订阅 {i+1}...")
        content = download_subscription(url)
        
        if content:
            proxies = parse_subscription(content)
            if proxies:
                print(f"  ✓ 成功，找到 {len(proxies)} 个节点")
                all_new_proxies.extend(proxies)
            else:
                print(f"  ✗ 未找到节点")
        else:
            print(f"  ✗ 下载失败")
        print()
    
    # 合并所有节点（订阅源在前 + 旧节点 + 新节点）
    final_proxies = subscription_nodes + other_nodes + all_new_proxies
    
    print(f"合并后总节点数：{len(final_proxies)}")
    print(f"  - 订阅源：{len(subscription_nodes)}")
    print(f"  - 旧节点：{len(other_nodes)}")
    print(f"  - 新节点：{len(all_new_proxies)}\n")
    
    if len(final_proxies) == 0:
        print("❌ 错误：没有可用节点！")
        sys.exit(1)
    
    # 更新配置
    current_config['proxies'] = final_proxies
    
    # 写入配置
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(current_config, f, allow_unicode=True, default_flow_style=False)
    
    print("✓ 配置已更新")
    
    # 应用简化的代理组
    print("\n正在应用简化的代理组配置...")
    import subprocess
    result = subprocess.run(['python3', '/opt/clash/simplify_config.py'], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    print("\n✅ 完成！")
    print("\n📋 提示：")
    print("   - 新订阅的节点已追加到列表末尾")
    print("   - 订阅源始终显示在最前面")
    print("   - 代理组分类：PROXY, Domestic, GLOBAL, 🎯 Direct, 🛑 Guard, ✈️ Final")

if __name__ == '__main__':
    main()
