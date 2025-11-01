# -*- coding: utf-8 -*-

# Google Drive 上传文件夹名称，可按需修改
drive_folder_name = "GDriveUploaderBot"

# Mega 下载账号（如不需要可留空或自行配置）
MEGA_EMAIL = "bearyan8@yandex.com"
MEGA_PASSWORD = "bearyan8@yandex.com"

START = (
    "你好，{}！我是你的谷歌云盘同步机器人 🤖。\n"
    "请发送 /auth 开始授权流程。\n\n"
    "更多帮助请使用 /help，查看更新请发送 /update。\n"
    "遇到问题可联系 @aryanvikash。"
)

HELP = (
    "📖 <b>使用指南</b>\n"
    "1. 回复 /auth 获取授权链接。\n"
    "2. 在浏览器完成 Google 授权并复制令牌。\n"
    "3. 将令牌粘贴发送给我即可完成绑定。\n\n"
    "<b>想切换账户？</b>\n"
    "使用 /revoke 撤销当前授权，再执行 /auth。\n\n"
    "<b>我能做什么？</b>\n"
    "• 将网络文件上传到你的 Google Drive。\n"
    "• 支持直链、Dropbox、Mega 等常见来源。\n\n"
    "如需帮助请联系 @aryanvikash。"
)

DP_DOWNLOAD = "📥 已接收到 Dropbox 链接，开始下载……"
OL_DOWNLOAD = "📥 已接收到 Openload 链接，正在下载（速度可能较慢）……"
PROCESSING = "⏳ 正在处理你的请求，请稍候……"
DOWN_TWO = True
DOWNLOAD = "📥 已开始下载文件，请耐心等待……"
DOWN_MEGA = "📥 正在下载 Mega 文件，可能会稍慢，请耐心等待……"
DOWN_COMPLETE = "✅ 下载完成！"
NOT_AUTH = "⚠️ 你尚未授权，请先发送 /auth 完成授权。"
REVOKE_FAIL = "⚠️ 未找到可撤销的授权，请先完成授权或重试。"
AUTH_SUCC = "✅ 授权成功！现在可以发送链接让我帮你上传到 Google Drive。"
ALREADY_AUTH = "ℹ️ 你已经授权，如需切换账号，请使用 /revoke。"
AUTH_URL = '<a href="{}">🔗 点击此处完成 Google Drive 授权</a>\n复制生成的令牌并发送给我。'
UPLOADING = "☁️ 下载完成，正在上传到 Google Drive……"
REVOKE_TOK = "🔒 授权已撤销，如需重新使用请发送 /auth 完成授权。"
# DOWN_PATH = "Downloads\\"  # Windows 路径
DOWN_PATH = "Downloads/"  # Linux 路径
DOWNLOAD_URL = (
    "✅ 文件上传成功！\n\n"
    "<b>文件名</b>：{}\n"
    "<b>大小</b>：{} MB\n"
    "<b>下载链接</b>：{}"
)
AUTH_ERROR = "❌ 授权失败，请发送有效的令牌或重新执行 /auth。"
OPENLOAD = True
DROPBOX = True
MEGA = True

UPDATE = (
    "🆕 <b>近期更新</b>\n"
    "• 新增 Mega 链接支持\n"
    "• 优化错误处理与日志输出\n"
    "• 持续完善下载源支持"
)
