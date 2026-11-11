# gzlTEcollection — 基于 Flask + MySQL 的博客应用

一个使用 Flask 框架及常用扩展搭建的多用户博客系统，参考《Flask Web Development》（Miguel Grinberg）的经典 Flasky 结构实现。

## 功能特性

- **用户认证**：注册、邮箱确认、登录/登出、密码保护（散列存储）、密码重置、邮箱变更
- **角色与权限**：普通用户 / 协管员 / 管理员三级角色，权限位校验
- **博客核心**：文章发布与编辑、Markdown 渲染、评论管理、评论审核
- **社交功能**：关注/取关其他用户、关注者列表、关注与被关注文章流
- **REST API**：`/api/v1.0` 提供基于令牌认证的文章、评论、用户 JSON 接口
- **数据库迁移**：基于 Flask-Migrate（Alembic）的版本化迁移
- **单元测试**：模型与应用基础行为测试，支持覆盖率统计

## 技术栈

| 类别 | 组件 |
|------|------|
| Web 框架 | Flask 1.1 + Flask-Bootstrap（蓝图组织） |
| 数据库 | MySQL（PyMySQL 驱动）+ Flask-SQLAlchemy |
| 认证 | Flask-Login + itsdangerous 签名令牌 |
| 表单 | Flask-WTF（CSRF 保护） |
| 其他扩展 | Flask-Mail、Flask-Moment、Flask-PageDown、Flask-Migrate |

## 目录结构

```
gzlTEcollection/
├── app/                        # 应用主包
│   ├── __init__.py             # create_app 工厂，注册扩展与蓝图
│   ├── models.py               # ORM 模型：User/Role/Post/Comment/Follow/Permission
│   ├── decorators.py           # 权限装饰器（permission_required 等）
│   ├── email.py                # 异步邮件发送
│   ├── exceptions.py           # 业务异常（ValidationError）
│   ├── main/                   # 主蓝图：文章流、用户资料、评论审核等页面
│   ├── auth/                   # 认证蓝图：注册/登录/确认/重置（/auth 前缀）
│   ├── api_1_0/                # REST API 蓝图（/api/v1.0 前缀）
│   ├── static/                 # 静态资源（样式、图标）
│   └── templates/              # Jinja2 模板（含 auth 子目录与邮件模板）
├── migrations/                 # 数据库迁移脚本（Alembic）
├── tests/                      # 单元测试
├── config.py                   # 分环境配置（development/testing/production）
├── manage.py                   # 管理入口：启动、测试、shell、数据库迁移命令
├── requirements.txt            # 依赖清单（固定为 Python 3.6 兼容版本）
└── README.md
```

## 快速开始

### 1. 环境准备

```bash
# Python 3.6+（遗留代码，依赖版本固定）
pip install -r requirements.txt
```

### 2. 环境变量

```bash
export FLASK_CONFIG=development          # development / testing / production
export SECRET_KEY=<你的密钥>
export DEV_DATABASE_URL='mysql+pymysql://user:password@localhost:3306/lxbdemo?charset=utf8mb4'
export MAIL_USERNAME=<邮箱账号>           # 邮件功能需要
export MAIL_PASSWORD=<邮箱密码或授权码>
export FLASKY_ADMIN=<管理员邮箱>
```

> 未设置 `DEV_DATABASE_URL` 时，默认连接 `mysql+pymysql://root:password@localhost:3306/lxbdemo`，请按需修改 `config.py`。

### 3. 初始化数据库并启动

```bash
python manage.py db init        # 首次运行（已有 migrations/ 可跳过）
python manage.py db migrate -m "init"
python manage.py db upgrade
python manage.py runserver      # 默认 http://127.0.0.1:5000
```

### 4. 运行测试

```bash
python manage.py test                          # 单元测试
python manage.py test --coverage               # 带覆盖率
```

或使用 shell 交互：

```bash
python manage.py shell
>>> User.insert_roles()   # 初始化角色数据
```

## API 概览（/api/v1.0，HTTP Basic 认证，支持令牌）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1.0/posts/` | 文章列表（分页） |
| POST | `/api/v1.0/posts/` | 发布新文章 |
| GET/PUT | `/api/v1.0/posts/<id>` | 查看 / 编辑文章 |
| GET | `/api/v1.0/comments/` | 评论列表（协管权限） |
| GET | `/api/v1.0/posts/<id>/comments/` | 文章评论列表 |
| POST | `/api/v1.0/posts/<id>/comments/` | 发表评论 |
| GET | `/api/v1.0/users/<id>` | 用户信息 |
| GET | `/api/v1.0/users/<id>/posts/` | 用户文章 |
| GET | `/api/v1.0/users/<id>/followed-posts/` | 用户关注流 |
| POST | `/api/v1.0/tokens` | 换取 API 令牌 |

## 项目说明

- 邮件主题前缀、分页大小等参数位于 `config.py`。
- 原始代码基于 Python 3.6 时代编写，部分依赖（如 `itsdangerous.TimedJSONWebSignatureSerializer`、`flask_script`/`MigrateCommand`）在新版本中已移除，故 `requirements.txt` 固定了兼容版本。
- 首次部署后请通过 shell 执行 `Role.insert_roles()` 并将管理员邮箱设置为 `FLASKY_ADMIN`。
