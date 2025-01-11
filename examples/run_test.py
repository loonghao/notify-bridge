"""Test script for notify-bridge."""

# Import built-in modules
import os

# Import third-party modules
from dotenv import load_dotenv
from run_github import run_github
from run_feishu import run_feishu
from run_wecom import run_wecom
from run_notify import run_notify

def main():
    """Run all test scripts."""
    # Try to load environment variables from .env file
    load_dotenv(".env")
    load_dotenv(".env.example")

    # Set default values if environment variables are not set
    if "WECOM_WEBHOOK_URL" not in os.environ:
        os.environ["WECOM_WEBHOOK_URL"] = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
    if "FEISHU_WEBHOOK_URL" not in os.environ:
        os.environ["FEISHU_WEBHOOK_URL"] = "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_KEY"

    if "NOTIFY_BASE_URL" not in os.environ:
        os.environ["NOTIFY_BASE_URL"] = "https://notify-demo.deno.dev"
    run_wecom()
    run_feishu()
    run_notify()
    # run_github()


if __name__ == "__main__":
    main()
