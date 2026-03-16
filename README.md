# Clash Dashboard - Mihomo 代理管理面板

一个简洁高效的 Mihomo/Clash 代理管理面板，支持多订阅合并、节点管理、流量监控等功能。

## ✨ 功能特性

- 🚀 **节点管理** - 实时查看和切换代理节点
- 📊 **模式切换** - 支持规则模式、全局模式、直连模式
- 📋 **订阅管理** - 显示当前配置的订阅地址列表
- 🔄 **多订阅合并** - 支持多个订阅源合并，自动去重
- 📈 **流量监控** - 实时流量统计
- 🎨 **响应式设计** - 适配桌面和移动端

## 📁 项目结构

```
clash-dashboard/
├── frontend/           # 前端文件
│   └── index.html     # Dashboard 主界面
├── backend/           # 后端服务
│   ├── api_server.py  # API 服务器
│   └── server.py      # 主服务器
├── scripts/           # 工具脚本
│   ├── merge-subscriptions.py  # 多订阅合并脚本
│   ├── simplify_config.py      # 配置简化脚本
│   └── get-subscription.sh     # 订阅获取脚本
├── Dockerfile         # Docker 构建文件
└── README.md          # 项目说明
```

## 🚀 快速开始

### 方式一：Docker 部署（推荐）

```bash
# 构建镜像
docker build -t clash-dashboard .

# 运行容器
docker run -d \
  -p 9093:80 \
  -p 9090:9090 \
  -v /opt/clash:/opt/clash \
  --name clash-dashboard \
  clash-dashboard
```

### 方式二：手动部署

```bash
# 1. 安装依赖
pip3 install flask requests pyyaml

# 2. 启动后端服务
cd backend
python3 api_server.py

# 3. 访问 Dashboard
# 浏览器打开 http://localhost:9093
```

## 📋 订阅管理

### 添加新订阅

编辑脚本 `/opt/clash/merge-subscriptions.py`：

```python
SUB_URLS = [
    "https://subscription1.com/...",
    "https://subscription2.com/...",  # 添加新的在这里
]
```

运行更新脚本：

```bash
/opt/clash/merge-subscriptions.py
```

### 订阅合并逻辑

1. 下载所有订阅 URL
2. 提取每个订阅的节点列表
3. 合并所有节点（不去重）
4. 订阅源节点始终显示在最前面
5. 自动应用简化的代理组配置

## 🛠️ 配置说明

### 代理组分类

系统自动简化为以下 6 个代理组：

- **PROXY** - 所有代理节点（订阅源在前）
- **Domestic** - 国内直连
- **GLOBAL** - 全局代理
- **🎯 Direct** - 直连
- **🛑 Guard** - 广告拦截
- **✈️ Final** - 最终代理

### 节点顺序

```
1. 订阅源节点（防失联网址、售前/售后）← 始终在前
2. 旧订阅的所有节点
3. 新订阅的节点 ← 追加到后面
```

## 📊 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/proxies` | GET | 获取代理列表 |
| `/api/configs` | GET/PUT | 获取/更新配置 |
| `/api/traffic` | GET | 获取流量统计 |
| `/api/providers` | GET | 获取订阅列表 |

## 🔧 脚本说明

### merge-subscriptions.py

多订阅合并脚本，功能：
- 支持多个订阅 URL
- 自动下载并解析订阅
- 合并所有节点
- 备份当前配置
- 自动重启 Clash 服务

### simplify_config.py

配置简化脚本，功能：
- 动态提取节点名称
- 简化代理组分类
- 更新 rules 引用
- 确保订阅源在前

## 📝 更新日志

### v1.0.0 (2026-03-16)
- ✅ 初始版本发布
- ✅ 多订阅合并功能
- ✅ 订阅列表显示
- ✅ 代理组简化
- ✅ 响应式界面设计

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👤 作者

整理自 Mihomo Dashboard 项目

## 🙏 致谢

- [Mihomo](https://github.com/MetaCubeX/mihomo)
- [Vue.js](https://vuejs.org/)
- [Axios](https://axios-http.com/)
