#!/bin/bash
# 订阅获取脚本 - 调用多订阅合并脚本
# 要添加新订阅，请编辑 /opt/clash/merge-subscriptions.sh 中的 SUB_URLS 数组

echo "🔄 调用多订阅合并脚本..."
exec /opt/clash/merge-subscriptions.sh
