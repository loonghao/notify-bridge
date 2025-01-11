"""Test script for notify-bridge."""

# Import built-in modules
import os

# Import third-party modules
from dotenv import load_dotenv
from run_feishu import run_feishu

# Import local modules
from run_wecom import run_wecom


def main():
    """Run all test scripts."""
    # Try to load environment variables from .env file
    load_dotenv('.env')
    load_dotenv('.env.example')

    # Set default values if environment variables are not set
    if "WECOM_URL" not in os.environ:
        os.environ["WECOM_URL"] = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
    if "FEISHU_URL" not in os.environ:
        os.environ["FEISHU_URL"] = "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_KEY"

    run_wecom()
    run_feishu()


if __name__ == "__main__":
    main()
