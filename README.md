# 163 Email and Twitter Account Manager

安全合规的 163 邮箱和 Twitter 账户管理工具

## 功能特性

- **163 邮箱管理**
  - 自动读取和分类邮件
  - 定时发送邮件
  - 邮件备份和导出
  - 标记已读/未读

- **Twitter 管理**
  - 定时发布推文
  - 读取和分类推文
  - 数据备份

## 安全设计

- 使用官方 SMTP/IMAP 协议和 OAuth 2.0 认证
- 遵守 API 速率限制
- 本地存储凭证（加密）
- 人工审核机制
- 符合平台使用条款

## 快速开始

1. 安装依赖：`pip install -r requirements.txt`
2. 配置凭证：复制 `.env.example` 到 `.env` 并填入你的信息
3. 配置设置：复制 `config.example.json` 到 `config.json`
4. 运行演示：`python demo.py`
5. 运行真实服务：`python main.py`

## 163 邮箱配置

1. 登录 163 邮箱
2. 进入"设置" -> "POP3/SMTP/IMAP"
3. 开启 IMAP/SMTP 服务
4. 获取授权码（不是登录密码）
5. 在 `.env` 文件中填入邮箱地址和授权码

详见 `docs/setup.md`
