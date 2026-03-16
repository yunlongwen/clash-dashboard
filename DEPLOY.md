# GitHub 部署指南

## 方式一：使用 GitHub CLI（推荐）

```bash
# 1. 安装 GitHub CLI
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update && sudo apt install gh -y

# 2. 认证
gh auth login

# 3. 创建仓库
cd /root/.openclaw/workspace/clash-dashboard
gh repo create clash-dashboard --public --source=. --remote=origin --push
```

## 方式二：使用 Git + HTTPS

```bash
# 1. 在 GitHub 上创建新仓库（命名为 clash-dashboard）

# 2. 添加远程仓库
cd /root/.openclaw/workspace/clash-dashboard
git remote add origin https://github.com/YOUR_USERNAME/clash-dashboard.git

# 3. 推送代码
git branch -M main
git push -u origin main
```

## 方式三：使用 Git + SSH

```bash
# 1. 生成 SSH 密钥（如果没有）
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. 将公钥添加到 GitHub
cat ~/.ssh/id_ed25519.pub
# 复制输出内容，在 GitHub Settings -> SSH and GPG keys 中添加

# 3. 添加远程仓库并推送
cd /root/.openclaw/workspace/clash-dashboard
git remote add origin git@github.com:YOUR_USERNAME/clash-dashboard.git
git branch -M main
git push -u origin main
```

## 部署后访问

推送成功后，代码将位于：
```
https://github.com/YOUR_USERNAME/clash-dashboard
```

## 启用 GitHub Actions（可选）

创建 `.github/workflows/deploy.yml` 实现自动部署。

## 更新代码

```bash
cd /root/.openclaw/workspace/clash-dashboard
git add .
git commit -m "Update: 更新说明"
git push origin main
```
