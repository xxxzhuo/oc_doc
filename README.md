# 🏆 暗标竞标系统

**安全、透明、公平的电子竞标平台**

---

## 📖 项目简介

本系统实现了一个完整的暗标竞标流程，确保：
- ✅ 投标方互相看不到其他投标人的报价
- ✅ 只能看到公开的产品参数
- ✅ 招标方可在开标后查看所有报价
- ✅ **前端 AES-256 加密**保护敏感数据
- ✅ **JWT 认证** + **速率限制**保障安全

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                  前端 (Vue 3 + Vite)                     │
│  - Element Plus UI                                       │
│  - Axios 拦截器 (自动 Token + 错误处理)                  │
│  - Crypto-JS (前端报价加密)                              │
│  - Pinia 状态管理                                        │
└─────────────────────────────────────────────────────────┘
                          ↓ HTTPS + Bearer Token
┌─────────────────────────────────────────────────────────┐
│                后端 (FastAPI + SQLAlchemy)               │
│  - JWT 认证 (依赖注入解析)                               │
│  - AES-256-GCM 解密                                      │
│  - SlowAPI 速率限制 (登录 5 次/分钟)                       │
│  - 审计日志                                              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  数据库 (SQLite/PostgreSQL)               │
│  - 用户表 (加密密码)                                     │
│  - 项目表                                                │
│  - 投标表 (密文存储)                                     │
│  - 审计日志表                                            │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 方式一：Docker Compose (推荐)

```bash
# 1. 克隆仓库
git clone git@github.com:xxxzhuo/oc_doc.git
cd oc_doc/bidding-system

# 2. 配置环境变量
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 生成密钥
python -c "import secrets; print(secrets.token_hex(32))"

# 编辑 .env 文件，填入生成的密钥

# 3. 启动服务
docker-compose up -d

# 4. 访问
# 前端：http://localhost:3000
# 后端 API: http://localhost:8000
# API 文档：http://localhost:8000/docs
```

### 方式二：本地开发

**后端启动：**
```bash
cd backend

# 复制并配置环境变量
cp .env.example .env
# 编辑 .env 填入密钥

# 安装依赖
pip install -r requirements.txt

# 启动服务
python run.py
# 或：uvicorn src.main:app --reload
```

**前端启动：**
```bash
cd frontend

# 复制环境变量
cp .env.example .env

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

---

## 🔐 安全机制

### 1. 报价加密流程
```
投标方填写报价 → 前端 AES-256 加密 → HTTPS 传输 → 后端存储密文 → 
截止后招标方解密 → 显示明文报价
```

### 2. 认证与授权
| 机制 | 说明 |
|------|------|
| **JWT Token** | 7 天有效期，自动过期检查 |
| **角色分离** | 招标方/投标方权限隔离 |
| **速率限制** | 登录接口 5 次/分钟防暴力破解 |
| **密钥验证** | 启动时检查环境变量，无默认值 |

### 3. 权限控制
| 操作 | 招标方 | 投标方 | 未登录 |
|------|--------|--------|--------|
| 创建项目 | ✅ | ❌ | ❌ |
| 查看项目参数 | ✅ | ✅ | ✅ |
| 提交投标 | ❌ | ✅ | ❌ |
| 查看他人报价 | ✅ (开标后) | ❌ | ❌ |
| 开标操作 | ✅ | ❌ | ❌ |
| 给自己项目投标 | ❌ | ❌ | ❌ |

---

## 📁 项目结构

```
bidding-system/
├── backend/
│   ├── src/
│   │   ├── main.py              # API 入口 (lifespan)
│   │   ├── models.py            # 数据库模型
│   │   ├── crypto.py            # AES-256 加密模块
│   │   ├── auth.py              # JWT 认证 (依赖注入)
│   │   ├── database.py          # 数据库连接
│   │   └── routes/
│   │       ├── auth.py          # 认证路由 (限流)
│   │       └── projects.py      # 项目路由 (JOIN 优化)
│   ├── config/
│   │   └── settings.py          # 配置 (密钥验证)
│   ├── tests/
│   │   └── test_api.py          # API 测试
│   ├── run.py                   # 统一启动入口
│   ├── .env.example             # 环境变量示例
│   └── requirements.txt         # Python 依赖
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── NavBar.vue       # 导航栏组件
│   │   ├── pages/               # 页面组件
│   │   ├── router/
│   │   │   └── index.js         # 路由 (Token 过期检查)
│   │   ├── stores/
│   │   │   └── user.js          # 用户状态
│   │   ├── utils/
│   │   │   └── request.js       # Axios 封装 (拦截器)
│   │   └── styles/
│   │       └── main.scss        # 全局样式
│   ├── .env.example
│   └── package.json
├── docs/
│   ├── API.md                   # API 文档
│   └── DEPLOYMENT.md            # 部署指南
├── Dockerfile                   # 后端 Docker 镜像
├── docker-compose.yml           # 一键部署
├── README.md                    # 本文件
└── PROJECT_SUMMARY.md           # 项目总结
```

---

## 🧪 测试账号

| 角色 | 邮箱 | 密码 |
|------|------|------|
| 招标方 | tenderer@example.com | password123 |
| 投标方 1 | bidder1@example.com | password123 |
| 投标方 2 | bidder2@example.com | password123 |

---

## 📊 核心 API

| 接口 | 方法 | 权限 | 说明 |
|------|------|------|------|
| `/api/auth/register` | POST | 公开 | 用户注册 |
| `/api/auth/login` | POST | 公开 | 登录 (限流 5 次/分) |
| `/api/auth/me` | GET | 登录 | 获取当前用户 |
| `/api/projects` | GET | 登录 | 项目列表 (JOIN 优化) |
| `/api/projects` | POST | 招标方 | 创建项目 |
| `/api/projects/{id}/bids` | POST | 投标方 | 提交投标 (前端加密) |
| `/api/projects/{id}/bids/detail` | GET | 招标方 | 查看报价 (开标后) |

完整文档：[docs/API.md](docs/API.md)

---

## 🔧 改进记录 (2026-03-05)

### P0 阻塞性问题 - 已修复 ✅
- [x] JWT 认证硬编码 → 实现真正的依赖注入解析
- [x] 前端未携带 token → Axios 请求拦截器自动附加
- [x] 启动命令不一致 → 统一使用 `python run.py`

### P1 安全问题 - 已修复 ✅
- [x] 密钥硬编码 → 启动时验证环境变量
- [x] 报价明文传输 → 前端 Crypto-JS 加密
- [x] 无速率限制 → SlowAPI 登录限流
- [x] 角色未二次校验 → 从 DB 获取确认

### P2 功能缺陷 - 已修复 ✅
- [x] 报价无校验 → Pydantic Field 约束
- [x] 招标方可自投 → 添加 creator_id 校验
- [x] /api/auth/me 假数据 → 接入真实认证

### P3 代码质量 - 已修复 ✅
- [x] N+1 查询 → JOIN + GROUP BY 优化
- [x] datetime.utcnow → datetime.now(timezone.utc)
- [x] @app.on_event → lifespan 上下文
- [x] 多余依赖 → 移除未使用包

### P4 工程化 - 已修复 ✅
- [x] 无 .env.example → 创建示例文件
- [x] 无 Docker 支持 → Dockerfile + compose
- [x] 前端无组件 → 创建 NavBar.vue
- [x] 无部署指南 → docs/DEPLOYMENT.md

---

## 📄 许可证

MIT License

---

## 👥 开发团队

龙虾智能实验室 🦞  
**GitHub:** https://github.com/xxxzhuo/oc_doc
