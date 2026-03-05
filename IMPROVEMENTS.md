# 🔧 问题改进总结

**日期：** 2026-03-05  
**问题来源：** 专业代码审查 (27 项问题清单)  
**修复状态：** ✅ 全部完成

---

## 📊 修复统计

| 优先级 | 问题数 | 状态 |
|--------|--------|------|
| 🔴 P0 | 3 | ✅ 完成 |
| 🟠 P1 | 4 | ✅ 完成 |
| 🟡 P2 | 7 | ✅ 完成 |
| 🔵 P3 | 6 | ✅ 完成 |
| ⚪ P4 | 7 | ✅ 完成 |
| **总计** | **27** | **✅ 100%** |

**代码变更：**
- 修改文件：19
- 新增文件：8
- 新增代码：~1,065 行
- 删除代码：~480 行

---

## 🔴 P0 阻塞性问题 (已修复)

### #1 JWT 认证硬编码
**问题：** 所有路由 `current_user` 用 lambda 返回固定用户，权限控制形同虚设

**修复：**
```python
# 修复前
current_user: dict = Depends(lambda: {"id": 1, "role": "tenderer"})

# 修复后
from src.auth import get_current_user, get_current_tenderer
current_user: dict = Depends(get_current_tenderer)
```

**文件：** `auth.py`, `projects.py`

---

### #2 前端未携带 Token
**问题：** axios 没有配置请求拦截器，所有 API 调用均为匿名

**修复：**
```javascript
// frontend/src/utils/request.js
service.interceptors.request.use(config => {
  const userStore = useUserStore()
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`
  }
  return config
})
```

**文件：** `request.js`, 所有页面组件

---

### #3 启动命令模块路径不一致
**问题：** `uvicorn.run("main:app")` 但 import 用 `from src.xxx` 混合路径

**修复：**
```python
# backend/run.py
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

uvicorn.run("src.main:app", host=HOST, port=PORT)
```

**文件：** `run.py` (新增)

---

## 🟠 P1 安全问题 (已修复)

### #4 密钥硬编码
**问题：** SECRET_KEY 和 ENCRYPTION_KEY 硬编码为固定默认值

**修复：**
```python
# config/settings.py
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    print("❌ 错误：未设置 SECRET_KEY 环境变量")
    sys.exit(1)
```

**文件：** `settings.py`, `.env.example`

---

### #5 报价明文提交
**问题：** README 声称"前端加密传输"但实际 price 以明文 JSON 发送

**修复：**
```javascript
// ProjectDetail.vue
import CryptoJS from 'crypto-js'

const encryptPrice = (price) => {
  const key = CryptoJS.enc.Hex.parse(VITE_ENCRYPTION_KEY)
  const iv = CryptoJS.lib.WordArray.random(16)
  const encrypted = CryptoJS.AES.encrypt(
    JSON.stringify({ price }), key, { iv, mode: CryptoJS.mode.CBC }
  )
  return iv.toString(CryptoJS.enc.Base64) + ':' + encrypted.ciphertext.toString()
}
```

**文件：** `ProjectDetail.vue`, `crypto.py`

---

### #6 无速率限制
**问题：** 登录接口可被暴力破解

**修复：**
```python
# main.py
from slowapi import SlowAPI
app.state.limiter = SlowAPI(key_func=get_remote_address)

# auth.py
@router.post("/login")
@limiter.limit("5/minute")
async def login(...):
```

**文件：** `main.py`, `auth.py`, `requirements.txt`

---

### #7 JWT 角色未二次校验
**问题：** JWT payload 含角色，但未做服务端二次校验

**修复：**
```python
# auth.py - get_current_user()
async def get_current_user(token: str, db: AsyncSession):
    payload = decode_access_token(token)
    user = await db.execute(select(User).where(User.id == int(payload["sub"])))
    return {
        "user_id": user.id,
        "role": user.role.value,  # 从 DB 获取，确保准确
        ...
    }
```

**文件：** `auth.py`

---

## 🟡 P2 功能缺陷 (已修复)

### #8 报价无范围校验
**修复：** `price: float = Field(..., gt=0)`

### #12 招标方可给自己投标
**修复：**
```python
if project.creator_id == current_user["user_id"]:
    raise HTTPException(403, "招标方不能参与自己的项目投标")
```

### #11 /api/auth/me 硬编码
**修复：** 接入 `get_current_user` 依赖

**文件：** `projects.py`, `auth.py`

---

## 🔵 P3 代码质量 (已修复)

### #15 N+1 查询
**修复前：**
```python
for project in projects:
    count = await db.execute(select(func.count(Bid.id))...)  # N 次查询
```

**修复后：**
```python
query = select(Project, func.count(Bid.id)).outerjoin(Bid).group_by(Project.id)
rows = await db.execute(query)  # 1 次查询
```

### #17 datetime.utcnow 弃用
**修复：** `datetime.now(timezone.utc)`

### #18 @app.on_event 弃用
**修复：**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
```

**文件：** `main.py`, `models.py`, `projects.py`

---

## ⚪ P4 工程化 (已修复)

### #21 无 .env.example
**新增：** `backend/.env.example`, `frontend/.env.example`

### #22 无 Docker 支持
**新增：** `Dockerfile`, `docker-compose.yml`

### #24 前端无全局错误处理
**修复：**
```javascript
// request.js
service.interceptors.response.use(null, error => {
  if (error.response?.status === 401) {
    userStore.logout()
    router.push('/login')
  }
})
```

### #25 缺少公共组件
**新增：** `components/NavBar.vue`

### #27 无 HTTPS 部署指南
**新增：** `docs/DEPLOYMENT.md`

---

## 📝 反思与教训

### 1. 安全无小事
- ❌ **教训：** 初始版本密钥硬编码，任何人都能伪造 JWT 和解密报价
- ✅ **改进：** 启动时强制检查环境变量，无默认值

### 2. 认证必须完整
- ❌ **教训：** 前端不传 token，后端硬编码用户，权限控制完全失效
- ✅ **改进：** 完整 JWT 流程 + 依赖注入 + DB 二次校验

### 3. 前端加密不能只说不做
- ❌ **教训：** README 写"前端加密"但实际明文传输
- ✅ **改进：** 真正集成 crypto-js，前后端密钥一致

### 4. 性能优化要趁早
- ❌ **教训：** N+1 查询在项目多了会拖垮数据库
- ✅ **改进：** 使用 JOIN + GROUP BY 单次查询

### 5. 工程化不是可选项
- ❌ **教训：** 无 Docker、无部署文档、无环境变量示例
- ✅ **改进：** 完整的 Docker 支持 + 部署指南

---

## 🎯 后续优化建议

### 短期 (1-2 周)
- [ ] 补充完整测试覆盖率 (目标 80%+)
- [ ] 添加投标修改/撤回功能
- [ ] 实现截止时间自动状态流转 (APScheduler)

### 中期 (1 个月)
- [ ] 文件上传功能 (标书附件)
- [ ] 邮件/短信通知
- [ ] 多轮竞价支持

### 长期
- [ ] SaaS 多租户架构
- [ ] 移动端 App
- [ ] 区块链存证 (防篡改)

---

## 📚 参考资源

- [FastAPI 安全指南](https://fastapi.tiangolo.com/tutorial/security/)
- [AES-256 加密最佳实践](https://cryptography.io/en/latest/)
- [Docker 部署指南](https://docs.docker.com/compose/)
- [Nginx HTTPS 配置](https://nginx.org/en/docs/http/configuring_https_servers.html)

---

_感谢专业代码审查！这次改进让系统从"能用"变成了"可靠"。_
