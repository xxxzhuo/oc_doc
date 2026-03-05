# 🏆 暗标竞标系统

**安全、透明、公平的电子竞标平台**

---

## 📖 项目简介

本系统实现了一个完整的暗标竞标流程，确保：
- ✅ 投标方互相看不到其他投标人的报价
- ✅ 只能看到公开的产品参数
- ✅ 招标方可在开标后查看所有报价
- ✅ AES-256 加密保护敏感数据

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                      前端 (Vue 3)                        │
│  - 用户登录/注册                                         │
│  - 项目管理                                              │
│  - 投标界面 (前端加密)                                   │
│  - 开标结果展示                                          │
└─────────────────────────────────────────────────────────┘
                          ↓ HTTPS
┌─────────────────────────────────────────────────────────┐
│                   后端 (FastAPI)                         │
│  - RESTful API                                           │
│  - JWT 认证                                              │
│  - AES-256 加密/解密                                     │
│  - 权限控制                                              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  数据库 (SQLite/PostgreSQL)               │
│  - 用户表                                                │
│  - 项目表                                                │
│  - 投标表 (加密存储)                                     │
│  - 操作日志表                                            │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- SQLite (开发) / PostgreSQL (生产)

### 后端启动
```bash
cd backend
pip install -r requirements.txt
python src/main.py
# 服务运行在 http://localhost:8000
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
# 服务运行在 http://localhost:3000
```

---

## 📁 项目结构

```
bidding-system/
├── backend/
│   ├── src/
│   │   ├── main.py          # API 入口
│   │   ├── models.py        # 数据库模型
│   │   ├── crypto.py        # 加密模块
│   │   ├── auth.py          # 认证模块
│   │   └── routes/          # API 路由
│   ├── config/
│   │   └── settings.py      # 配置管理
│   ├── tests/               # 测试文件
│   └── requirements.txt     # Python 依赖
├── frontend/
│   ├── src/
│   │   ├── components/      # Vue 组件
│   │   ├── pages/           # 页面
│   │   ├── utils/           # 工具函数
│   │   └── styles/          # 样式文件
│   ├── public/              # 静态资源
│   └── package.json         # Node 依赖
├── docs/                    # 文档
└── scripts/                 # 部署脚本
```

---

## 🔐 安全机制

### 报价加密流程
1. 投标方填写报价 → 前端 AES 加密
2. 加密后的密文传输到后端
3. 后端存储密文 + 时间戳
4. 开标后，招标方使用密钥解密

### 权限控制
| 操作 | 招标方 | 投标方 | 未登录 |
|------|--------|--------|--------|
| 创建项目 | ✅ | ❌ | ❌ |
| 查看项目参数 | ✅ | ✅ | ✅ |
| 提交投标 | ❌ | ✅ | ❌ |
| 查看他人报价 | ✅ (开标后) | ❌ | ❌ |
| 开标操作 | ✅ | ❌ | ❌ |

---

## 📊 数据库设计

### 用户表 (users)
```sql
id INTEGER PRIMARY KEY
name TEXT NOT NULL
email TEXT UNIQUE NOT NULL
role TEXT NOT NULL  -- 'tenderer' or 'bidder'
company TEXT
password_hash TEXT NOT NULL
created_at TIMESTAMP
```

### 项目表 (projects)
```sql
id INTEGER PRIMARY KEY
title TEXT NOT NULL
description TEXT
params_json TEXT  -- 公开的产品参数
deadline TIMESTAMP NOT NULL
status TEXT       -- 'draft', 'active', 'closed', 'opened'
creator_id INTEGER REFERENCES users(id)
created_at TIMESTAMP
```

### 投标表 (bids)
```sql
id INTEGER PRIMARY KEY
project_id INTEGER REFERENCES projects(id)
bidder_id INTEGER REFERENCES users(id)
price_encrypted TEXT NOT NULL  -- AES-256 加密
params_json TEXT  -- 投标方填写的参数
created_at TIMESTAMP
UNIQUE(project_id, bidder_id)
```

---

## 🧪 测试

```bash
# 后端测试
cd backend
pytest tests/

# 前端测试
cd frontend
npm run test
```

---

## 📝 API 文档

详见 [docs/API.md](docs/API.md)

---

## 📄 许可证

MIT License

---

## 👥 开发团队

龙虾智能实验室 🦞
