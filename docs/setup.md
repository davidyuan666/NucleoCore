# 配置指南

## 1. 163 邮箱配置

### 1.1 开启 IMAP/SMTP 服务

1. 登录 163 邮箱网页版 (mail.163.com)
2. 点击右上角"设置" -> "POP3/SMTP/IMAP"
3. 找到"IMAP/SMTP服务"，点击"开启"
4. 按照提示发送短信验证
5. 获取授权码（16位字符，这不是你的登录密码）

### 1.2 配置环境变量

复制 `.env.example` 到 `.env`，填入你的信息：

```bash
EMAIL_ADDRESS=your_email@163.com
EMAIL_PASSWORD=your_16_digit_authorization_code
```

**重要提示：**
- EMAIL_PASSWORD 是授权码，不是登录密码
- 授权码格式类似：abcd efgh ijkl mnop（16位）
- 不要泄露授权码，它等同于你的邮箱密码

### 1.3 163 邮箱限制

- SMTP 发送限制：每天约 200 封（个人邮箱）
- IMAP 连接限制：建议不要频繁连接
- 建议间隔：每 30 分钟检查一次邮件

## 2. Twitter API 配置

### 2.1 申请开发者账号

1. 访问 [Twitter Developer Portal](https://developer.twitter.com/)
2. 申请开发者账号（需要说明使用目的）
3. 创建应用
4. 获取以下凭证：
   - API Key
   - API Secret
   - Access Token
   - Access Token Secret
   - Bearer Token

### 2.2 配置环境变量

在 `.env` 文件中填入你的凭证：

```bash
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
TWITTER_BEARER_TOKEN=your_bearer_token



App-Only Authentication:
beaer_token: AAAAAAAAAAAAAAAAAAAAAKV67gEAAAAASFho64QwFwPtR9T3UR8ZGaeJChs%3D65UuF5m6AUC56Gq8b0HIzRhoqvn4PLlB0k6HX7KYzFc9ld9kUT

OAuth 2.0 Keys:
client_secret_id: U1Z2Y2xIYUgzSklTSE9VUjJXdFM6MTpjaQ
client_secret: SM99KoQTQRbAFSoGOz9C4uTUh9TBtQeuVsjaEYAZ70oh6MMkkG

OAuth 1.0 Keys:
consumer_key: h5hcYeiEykk2QB2AOjmJtBRbv
access_token: 2886232572-MTVfak8NM6aYnbHOQ63BKnHw7b5915oyNIWSZmI
access_token_secret: Eoa0l2kynOAjgcfK2bh8258bKHIDgckib3VK8ycUUCw90
```

### 2.3 Twitter API 限制

- 免费版: 每月 1500 条推文
- Basic: 每月 3000 条推文
- 建议间隔：每条推文间隔至少 5 分钟

## 3. 安全建议

### 3.1 凭证保护

- 永远不要提交 `.env` 文件到 Git
- 不要在代码中硬编码密码
- 定期更换授权码

### 3.2 速率限制

本项目已内置速率限制器：
- 163 邮箱: 每天最多 200 封邮件
- Twitter: 每天最多 50 条推文，最小间隔 5 分钟

### 3.3 合规使用

- 遵守平台服务条款
- 不要发送垃圾邮件或垃圾推文
- 不要使用自动化工具进行欺诈行为
- 保持合理的请求频率

## 4. 首次运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 复制配置文件：
```bash
cp config.example.json config.json
cp .env.example .env
```

3. 编辑 `.env` 文件，填入你的邮箱和 Twitter 凭证

4. 运行演示模式：
```bash
python demo.py
```

5. 测试邮箱连接（演练模式）：
```bash
python main.py
```

6. 关闭演练模式：
   - 编辑 `config.json`
   - 设置 `"dry_run_mode": false`

## 5. 常见问题

### Q: 163 邮箱连接失败？
A:
1. 确认已开启 IMAP/SMTP 服务
2. 确认使用的是授权码，不是登录密码
3. 检查授权码是否正确（16位字符）

### Q: 发送邮件失败？
A:
1. 检查是否达到每日发送限制（200封）
2. 确认收件人地址正确
3. 检查网络连接

### Q: Twitter API 返回 429 错误？
A: 达到速率限制，等待一段时间后重试

### Q: 如何测试邮箱配置？
A: 运行 `python test_email.py` 进行测试

## 6. 服务器配置信息

### 163 邮箱服务器
- IMAP 服务器: imap.163.com
- IMAP 端口: 993 (SSL)
- SMTP 服务器: smtp.163.com
- SMTP 端口: 465 (SSL)

### 其他邮箱服务器（可选）
- QQ邮箱: imap.qq.com / smtp.qq.com
- 126邮箱: imap.126.com / smtp.126.com
- Outlook: outlook.office365.com
