#!/usr/bin/env python3
"""
简化 Clash 配置文件，只保留 Domestic, GLOBAL, PROXY 三个主要分类
并更新 rules 以使用新的代理组

动态从配置中提取所有节点名称，确保订阅源在前
"""

import re
import yaml

# 读取原始配置
with open('/opt/clash/config.yaml', 'r', encoding='utf-8') as f:
    content = f.read()

# 解析 YAML 配置
try:
    config = yaml.safe_load(content)
except Exception as e:
    print(f"⚠️ YAML 解析失败：{e}")
    print("   尝试使用正则提取...")
    config = None

# 提取所有节点名称
proxy_names = []
subscription_nodes = []  # 订阅源节点
other_nodes = []  # 其他节点

if config and 'proxies' in config:
    # 从解析的 YAML 中提取
    for proxy in config.get('proxies', []):
        name = proxy.get('name', '')
        if name:
            if '防失联' in name or '售前/售后' in name or 'haita.link' in name:
                subscription_nodes.append(name)
            else:
                other_nodes.append(name)
else:
    # 使用正则提取
    proxy_matches = re.findall(r'^\s+-\s+name:\s*["\']?([^"\'"\n]+)["\']?\s*$', content, re.MULTILINE)
    for name in proxy_matches:
        name = name.strip()
        if '防失联' in name or '售前/售后' in name or 'haita.link' in name:
            subscription_nodes.append(name)
        else:
            other_nodes.append(name)

# 确保订阅源在前
proxy_names = subscription_nodes + other_nodes

print(f"📋 找到 {len(proxy_names)} 个节点")
print(f"   - 订阅源节点：{len(subscription_nodes)} 个")
print(f"   - 其他节点：{len(other_nodes)} 个")

if len(proxy_names) == 0:
    print("❌ 错误：没有找到任何节点！")
    exit(1)

# 创建新的代理组配置
NEW_PROXY_GROUPS = """proxy-groups:
  - name: PROXY
    type: select
    proxies:
""" + '\n'.join([f'      - "{p}"' for p in proxy_names]) + """

  - name: Domestic
    type: select
    proxies:
      - DIRECT
      - PROXY

  - name: GLOBAL
    type: select
    proxies:
      - PROXY
      - DIRECT

  - name: 🎯 Direct
    type: select
    proxies:
      - DIRECT
      - PROXY

  - name: 🛑 Guard
    type: select
    proxies:
      - REJECT
      - PROXY
      - DIRECT

  - name: ✈️ Final
    type: select
    proxies:
      - PROXY
      - DIRECT
"""

# 找到 proxies 部分的结束位置（proxy-groups 开始之前）
proxies_end = content.find('\nproxy-groups:')
if proxies_end == -1:
    print("❌ 错误：找不到 proxy-groups")
    exit(1)

# 找到 rules 部分的开始位置
rules_start = content.find('\nrules:')
if rules_start == -1:
    print("❌ 错误：找不到 rules")
    exit(1)

# 提取头部（包括 proxies）
header = content[:proxies_end]

# 提取 rules 部分
rules = content[rules_start:]

# 更新 rules，替换旧的代理组引用
rules_updated = rules

# 旧代理组列表
old_groups = [
    'AI', 'Apple', 'CNMedia', 'Crypto', 'Game', 'GitHub', 'Google', 
    'Microsoft', 'Netflix', 'TikTok', 'YouTube', 'GMedia', 'NetEaseMusic', 
    'Telegram', 'Proxies'
]

for old in old_groups:
    # 替换规则中的代理组引用
    rules_updated = rules_updated.replace(f',{old},no-resolve', ',PROXY,no-resolve')
    rules_updated = rules_updated.replace(f',{old}\n', ',PROXY\n')
    rules_updated = rules_updated.replace(f',{old}\r\n', ',PROXY\r\n')

# 组合新配置
new_config = header + '\n' + NEW_PROXY_GROUPS + rules_updated

# 写入新配置
with open('/opt/clash/config.yaml', 'w', encoding='utf-8') as f:
    f.write(new_config)

print("✅ 配置更新完成！")
print("📋 新的代理组:")
print("   - PROXY (所有节点，订阅源在前)")
print("   - Domestic (直连)")
print("   - GLOBAL (全局代理)")
print("   - 🎯 Direct")
print("   - 🛑 Guard")
print("   - ✈️ Final")
