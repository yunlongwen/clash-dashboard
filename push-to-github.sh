#!/bin/bash
# Clash Dashboard 推送到 GitHub 脚本

set -e

REPO_NAME="clash-dashboard"
GITHUB_USER=""  # 留空则自动检测

echo "🚀 Clash Dashboard GitHub 推送脚本"
echo "=================================="
echo ""

# 检测当前目录
if [ ! -f "README.md" ]; then
    echo "❌ 错误：请在 clash-dashboard 目录下运行此脚本"
    exit 1
fi

# 自动检测 GitHub 用户名
if [ -z "$GITHUB_USER" ]; then
    if command -v gh &> /dev/null; then
        GITHUB_USER=$(gh api user | jq -r .login 2>/dev/null || echo "")
    fi
    
    if [ -z "$GITHUB_USER" ]; then
        echo "💡 请输入你的 GitHub 用户名:"
        read -p "> " GITHUB_USER
    fi
fi

echo "👤 GitHub 用户名：$GITHUB_USER"
echo ""

# 检查远程仓库
REMOTE_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"
echo "📦 远程仓库：$REMOTE_URL"
echo ""

# 添加远程仓库
if ! git remote | grep -q "origin"; then
    echo "➕ 添加远程仓库..."
    git remote add origin "$REMOTE_URL"
else
    echo "✓ 远程仓库已存在"
    git remote set-url origin "$REMOTE_URL"
fi
echo ""

# 推送代码
echo "🚀 推送到 GitHub..."
echo "   如果提示认证，请使用 GitHub Token 或 SSH 密钥"
echo ""

git branch -M main
git push -u origin main

echo ""
echo "✅ 推送成功！"
echo ""
echo "📋 访问地址:"
echo "   https://github.com/${GITHUB_USER}/${REPO_NAME}"
echo ""
echo "🎉 完成！"
