# API 文档

## 基础信息

- **Base URL:** `http://localhost:8000`
- **认证方式:** JWT Bearer Token
- **数据格式:** JSON

---

## 认证接口

### 1. 用户注册

**POST** `/api/auth/register`

**请求体:**
```json
{
  "name": "张三",
  "email": "user@example.com",
  "password": "password123",
  "role": "bidder",
  "company": "某某公司"
}
```

**响应:**
```json
{
  "id": 1,
  "name": "张三",
  "email": "user@example.com",
  "role": "bidder",
  "company": "某某公司"
}
```

---

### 2. 用户登录

**POST** `/api/auth/login`

**请求体:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "张三",
    "email": "user@example.com",
    "role": "bidder",
    "company": "某某公司"
  }
}
```

---

## 项目接口

### 3. 创建项目

**POST** `/api/projects`

**权限:** 仅招标方 (tenderer)

**请求体:**
```json
{
  "title": "办公用品采购项目",
  "description": "采购一批办公用品",
  "params": {
    "规格": "A4",
    "数量": 1000,
    "材质": "80g 双胶纸"
  },
  "deadline": "2026-03-15T18:00:00"
}
```

**响应:**
```json
{
  "id": 1,
  "title": "办公用品采购项目",
  "description": "采购一批办公用品",
  "params": {
    "规格": "A4",
    "数量": 1000,
    "材质": "80g 双胶纸"
  },
  "deadline": "2026-03-15T18:00:00",
  "status": "active",
  "creator_id": 1,
  "created_at": "2026-03-05T10:00:00",
  "bid_count": 0
}
```

---

### 4. 获取项目列表

**GET** `/api/projects?status=active`

**查询参数:**
- `status` (可选): `draft` | `active` | `closed` | `opened`

**响应:**
```json
[
  {
    "id": 1,
    "title": "办公用品采购项目",
    "bid_count": 3,
    "status": "active",
    "deadline": "2026-03-15T18:00:00"
  }
]
```

---

### 5. 获取项目详情

**GET** `/api/projects/{project_id}`

**响应:** 同创建项目响应

---

### 6. 提交投标

**POST** `/api/projects/{project_id}/bids`

**权限:** 仅投标方 (bidder)

**请求体:**
```json
{
  "price": 15000.00,
  "params": {
    "交货期": "7 天",
    "质保": "1 年",
    "付款方式": "货到付款"
  }
}
```

**说明:** 
- 报价会在前端使用 AES-256 加密后传输
- 每个投标方对每个项目只能投标一次

**响应:**
```json
{
  "message": "投标提交成功",
  "bid_id": 1
}
```

---

### 7. 查看投标列表

**GET** `/api/projects/{project_id}/bids`

**权限:**
- 招标方：查看所有投标 (不含价格)
- 投标方：仅查看自己的投标

**响应:**
```json
[
  {
    "id": 1,
    "bidder_name": "李四",
    "bidder_company": "供应商 A 公司",
    "params": {
      "交货期": "7 天",
      "质保": "1 年"
    },
    "created_at": "2026-03-05T12:00:00"
  }
]
```

---

### 8. 开标

**POST** `/api/projects/{project_id}/open`

**权限:** 仅招标方 (tenderer)，且必须是项目创建者

**条件:** 当前时间 >= 截止时间

**响应:**
```json
{
  "message": "开标成功",
  "status": "opened"
}
```

---

### 9. 查看投标详情 (含报价)

**GET** `/api/projects/{project_id}/bids/detail`

**权限:** 仅招标方 (tenderer)

**条件:** 项目状态为 `opened`

**响应:**
```json
[
  {
    "id": 1,
    "bidder_name": "李四",
    "bidder_company": "供应商 A 公司",
    "price": 15000.00,
    "params": {
      "交货期": "7 天",
      "质保": "1 年"
    },
    "created_at": "2026-03-05T12:00:00"
  },
  {
    "id": 2,
    "bidder_name": "王五",
    "bidder_company": "供应商 B 公司",
    "price": 16500.00,
    "params": {
      "交货期": "5 天",
      "质保": "2 年"
    },
    "created_at": "2026-03-05T14:00:00"
  }
]
```

**说明:** 结果按价格升序排序

---

## 错误响应

**400 Bad Request**
```json
{
  "detail": "投标已截止"
}
```

**401 Unauthorized**
```json
{
  "detail": "邮箱或密码错误"
}
```

**403 Forbidden**
```json
{
  "detail": "只有招标方可以创建项目"
}
```

**404 Not Found**
```json
{
  "detail": "项目不存在"
}
```

---

## 测试账号

| 角色 | 邮箱 | 密码 |
|------|------|------|
| 招标方 | tenderer@example.com | password123 |
| 投标方 | bidder1@example.com | password123 |
| 投标方 | bidder2@example.com | password123 |

---

## 安全说明

1. **报价加密:** 使用 AES-256-GCM 算法
2. **传输加密:** 建议使用 HTTPS
3. **密码存储:** 使用 bcrypt 哈希
4. **审计日志:** 所有关键操作记录在案
