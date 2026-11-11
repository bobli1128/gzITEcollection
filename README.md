# BossBao（gzITEcollection）— 基于 Flask 3 + MySQL 的多用户博客

一个使用 Flask 框架及常用扩展搭建的多用户博客系统，参考《Flask Web Development》（Miguel Grinberg）的 Flasky 结构实现。

**当前技术栈（2026-11 现代化迁移后）：Python 3.13 · Flask 3.x · SQLAlchemy 2.x · Bootstrap 5（Bootstrap-Flask）**

## 功能特性

- **用户认证**：注册、邮箱确认、登录/登出、密码散列保护、密码重置、邮箱变更
- **角色与权限**：普通用户 / 协管员 / 管理员三级角色，权限位校验
- **博客核心**：文章发布与编辑、Markdown 渲染、评论管理、评论审核
- **社交功能**：关注/取关、关注者列表、关注与被关注文章流
- **REST API**：`/api/v1.0` 提供基于 Basic/令牌认证的文章、评论、用户 JSON 接口
- **数据库迁移**：Flask-Migrate（Alembic）版本化迁移，完整建表链
- **单元测试**：SQLite 内存库跑模型/应用测试，支持覆盖率统计

## 技术栈

| 类别 | 组件 |
|------|------|
| 运行环境 | Python 3.13 |
| Web 框架 | Flask 3.1（蓝图组织）+ Bootstrap-Flask 2.6（Bootstrap 5） |
| 数据库 | MySQL（PyMySQL）/ SQLite（测试与本地开发默认） |
| ORM | Flask-SQLAlchemy 3.1（SQLAlchemy 2.x） |
| 认证 | Flask-Login + itsdangerous `URLSafeTimedSerializer` 签名令牌 |
| 表单 | Flask-WTF（CSRF 保护）+ email-validator |
| 其他扩展 | Flask-Migrate、Flask-Mail、Flask-Moment、Flask-PageDown、Flask-HTTPAuth |

## 目录结构

```
gzITEcollection/
├── app/                        # 应用主包
│   ├── __init__.py             # create_app 工厂，注册扩展、Migrate 与蓝图
│   ├── models.py               # ORM 模型：User/Role/Post/Comment/Follow/Permission
│   ├── decorators.py           # 权限装饰器（permission_required 等）
│   ├── email.py                # 异步邮件发送
│   ├── exceptions.py           # 业务异常（ValidationError）
│   ├── main/                   # 主蓝图：文章流、用户资料、评论审核等页面
│   ├── auth/                   # 认证蓝图：注册/登录/确认/重置（/auth 前缀）
│   ├── api_1_0/                # REST API 蓝图（/api/v1.0 前缀）
│   ├── static/                 # 静态资源（样式、图标）
│   └── templates/              # Jinja2 模板（Bootstrap 5 布局与邮件模板）
├── migrations/                 # 数据库迁移（Alembic，含完整初始建表脚本）
├── tests/                      # 单元测试（SQLite 内存库，无需 MySQL）
├── config.py                   # 分环境配置，全部通过环境变量注入
├── manage.py                   # Flask CLI 入口（run/test/shell）
├── requirements.txt            # 依赖清单（Python 3.13 兼容版本）
├── .flaskenv                   # FLASK_APP / FLASK_CONFIG（可提交）
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
py -3.13 -m venv .venv
.venv/Scripts/pip install -r requirements.txt      # Windows
# source .venv/bin/activate && pip install -r requirements.txt  # Linux/macOS
```

### 2. 环境变量（`.flaskenv` 提供默认值，敏感信息放 `.env`，不要提交）

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `FLASK_CONFIG` | development / testing / production | development |
| `SECRET_KEY` | 签名密钥 | 开发用占位值，生产必须设置 |
| `DEV_DATABASE_URL` | 开发库连接串 | `sqlite:///data-dev.sqlite` |
| `DATABASE_URL` | 生产库连接串 | `sqlite:///data-prod.sqlite` |
| `TEST_DATABASE_URL` | 测试库连接串 | SQLite 内存库 |
| `FLASKY_ADMIN` | 管理员邮箱（该邮箱注册即 Administrator） | 无 |
| `MAIL_USERNAME` / `MAIL_PASSWORD` | SMTP 账号（邮件功能需要） | 无 |
| `MAIL_DEFAULT_SENDER` | 发件人 | BossBao <noreply@example.com> |

连接 MySQL 示例：

```bash
set DEV_DATABASE_URL=mysql+pymysql://user:password@localhost:3306/bossbao?charset=utf8mb4
```

### 3. 初始化数据库并启动

```bash
flask db init        # 仅全新项目首次需要（本仓库已含 migrations/）
flask db upgrade     # 建表
flask run --debug    # http://127.0.0.1:5000
```

初始化角色数据：

```bash
flask shell
>>> Role.insert_roles()
>>> exit
```

### 4. 运行测试

```bash
flask test                       # 单元测试（SQLite 内存库，无需 MySQL）
flask coverage-test --coverage   # 带覆盖率
```

## API 概览（/api/v1.0，HTTP Basic 认证，支持令牌）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1.0/posts/` | 文章列表（分页） |
| POST | `/api/v1.0/posts/` | 发布新文章 |
| GET/PUT | `/api/v1.0/posts/<id>` | 查看 / 编辑文章 |
| GET | `/api/v1.0/comments/` | 评论列表 |
| GET/POST | `/api/v1.0/posts/<id>/comments/` | 文章评论列表 / 发表评论 |
| GET | `/api/v1.0/users/<id>` | 用户信息 |
| GET | `/api/v1.0/users/<id>/posts/` | 用户文章 |
| GET | `/api/v1.0/users/<id>/timeline/` | 用户关注流 |
| POST | `/api/v1.0/tokens` | 换取 API 令牌（令牌有效期 3600 秒） |

## 2026-11 现代化迁移记录

- Python 3.6 → **3.13**；Flask 1.1 → **3.1**；SQLAlchemy 1.4 → **2.1**
- Flask-Bootstrap（Bootstrap 3）→ **Bootstrap-Flask 2.6（Bootstrap 5）**：自建 base 布局 + `bootstrap.load_css()/load_js()`，表单宏 `bootstrap5/form.html::render_form`，闪烁消息 `bootstrap5/utils.html::render_messages`，全站 BS5 标记（navbar/card/badge/分页）
- Flask-Script（已停维护）→ Flask 3 官方 CLI + Click（`flask run/test/shell/db`）
- 已移除的 `itsdangerous.TimedJSONWebSignatureSerializer` → `URLSafeTimedSerializer`（载荷内嵌 expiration，`return_timestamp` 校验有效期）
- 移除已废弃的 `SQLALCHEMY_COMMIT_ON_TEARDOWN`，改为显式 `db.session.commit()`
- `paginate()` 改为关键字参数；`Query.get()/get_or_404()` → `db.session.get()` / `db.get_or_404()`
- 假数据生成 `forgery_py`（已从 PyPI 下架）→ **Faker**
- 测试配置改用 **SQLite 内存库**，无需 MySQL 即可 `flask test`
- 修复历史 bug：初始迁移缺 users/roles/posts 表、管理员角色判断 `filter_by(permissions=...)`、`change_email` 令牌解析崩溃、密码重置邮件模板 Jinja 语法错误、评论页码浮点除法、API 用户 JSON 指向错误端点、`change_email` 路由缺前导斜杠
