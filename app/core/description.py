from datetime import datetime
import pytz
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

TARGET_TIME_FORMAT = "%Y-%m-%dT%H:%M+0000"    

def get_api_description():
    """Generate the API description with current timestamps."""
    return """

### 🎯  Last Update@UTC 🌐 {}

| Module | Description | Status |
|--------|-------------|--------|
| 📚 Knowledge Sharing (CN) | Share knowledge about filler products | ✅  [https://fillerwiki.info](https://fillerwiki.info) |
| 🔑 Auth | Manage user authentication and authorization | ✅ Available |
| 🏢 Brand | Find popular filler product brands and manufacturers | ✅ Available |
| 📦 Merchant | Find the merchant information | 🚧 On the way |

| Developer | Email | Other |
|-----------|-------|-------|
| 👨‍💻 **Zeliang YAO** | 📧 [zeliang.yao_filler@2925.com](mailto:zeliang.yao_filler@2925.com) | [My Github](https://github.com/yaozeliang) |

### 💰 Support
I appreciate you using the API! If it has been helpful to you, your support will motivate me to enhance it even further, 感谢您的使用，您的鼓励会激励我做得更好

   <div style="text-align: center;">
     <img src="/static/wechat_pay.jpg" alt="..." width="100" height="auto" style="border-radius: 10px;">
     <p style="font-size: 4px; color: #666; margin-top: 5px;">WeChat Pay</p>
   </div>

""".format(
    datetime.now(pytz.UTC).strftime(TARGET_TIME_FORMAT),
)