from datetime import datetime
import pytz

TARGET_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"    

def get_api_description():
    """Generate the API description with current timestamps."""
    return """

### 🎯 Features

| Module | Description | Status |
|--------|-------------|--------|
| 🔑 Auth | Manage user authentication and authorization | ✅ Available |
| 🏢 Brands | Manage filler product brands and manufacturers | ✅ Available |
| 📦 Products | Manage filler product details | 🚧 Coming Soon |



### ⏰ Last Update

| @UTC 🌐 | @Paris 🗼 | @Shanghai 🐼 |
|---------|-----------|--------------|
| {} | {} | {} |

### 📞 Support

For technical support, please contact:
* 👨‍💻 **Developer**: Zeliang YAO
* 📧 **Email**: [zeliang.yao_filler@2925.com](mailto:zeliang.yao_filler@2925.com)
* 🌐 **Website**: [hephaestus.fr](https://hephaestus.fr)

""".format(
    datetime.now(pytz.UTC).strftime(TARGET_TIME_FORMAT),
    datetime.now(pytz.timezone('Europe/Paris')).strftime(TARGET_TIME_FORMAT),
    datetime.now(pytz.timezone('Asia/Shanghai')).strftime(TARGET_TIME_FORMAT)
) 