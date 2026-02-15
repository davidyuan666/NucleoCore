# NucleoCore

蛋白质晶体管 - Social Account Manager

安全合规的 163 邮箱和 Twitter 账户管理工具，通过 Telegram Bot 远程控制

## 功能特性

- **163 邮箱管理**
  - 自动读取和分类邮件
  - 发送邮件到指定地址
  - 邮件备份和导出
  - 通过 Telegram 控制

- **Twitter 管理**
  - 发布推文（自动添加签名）
  - 查看推文列表
  - 查看账户信息
  - 通过 RapidAPI 查看任意用户信息

- **Telegram Bot 控制**
  - 远程发送推文
  - 远程查看邮件
  - 查看系统状态
  - 交互式确认机制

## 安全设计

- 使用官方 SMTP/IMAP 协议和 OAuth 2.0 认证
- 遵守 API 速率限制
- 本地存储凭证（加密）
- 人工审核机制
- 符合平台使用条款

## 快速开始

1. 安装依赖：`pip install -r requirements.txt`
2. 配置凭证：复制 `.env.example` 到 `.env` 并填入你的信息
3. 启动 Telegram Bot：`python telegram_bot_start.py`

## 163 邮箱配置

1. 登录 163 邮箱
2. 进入"设置" -> "POP3/SMTP/IMAP"
3. 开启 IMAP/SMTP 服务
4. 获取授权码（不是登录密码）
5. 在 `.env` 文件中填入邮箱地址和授权码

详见 `docs/setup.md`

## Telegram Bot 命令

- `/start` - 开始使用
- `/help` - 帮助信息
- `/tweet` - 发送推文
- `/mytweets` - 查看我的推文
- `/twitterinfo` - Twitter 账户信息
- `/userinfo` - 查看任意用户信息（RapidAPI）
- `/checkemail` - 检查邮件
- `/status` - 系统状态

直接发送文字消息将作为推文发布（需确认）
