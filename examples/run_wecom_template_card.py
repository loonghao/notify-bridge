"""Example of using WeCom template card notifications.

This example demonstrates how to send template card messages using the WeCom notifier.
Template cards support two types:
1. text_notice - Text notification template card
2. news_notice - Image and text display template card
"""

# Import built-in modules
import os

# Import local modules
from notify_bridge import NotifyBridge


def send_text_notice_template_card():
    """Send a text notice template card."""
    print("\n" + "=" * 60)
    print("Sending text notice template card...")
    print("=" * 60)

    webhook_url = os.getenv("WECOM_WEBHOOK_URL")
    if not webhook_url:
        print("ERROR: WECOM_WEBHOOK_URL environment variable is not set!")
        print("Please set it using: export WECOM_WEBHOOK_URL='your_webhook_url'")
        return

    bridge = NotifyBridge()
    try:
        response = bridge.send(
            "wecom",
            webhook_url=webhook_url,
            msg_type="template_card",
            template_card_type="text_notice",
            template_card_source={
                "icon_url": "https://wework.qpic.cn/wwpic/252813_jOfDHtcISzuodLa_1629280209/0",
                "desc": "Enterprise WeChat",
                "desc_color": 0,
            },
            template_card_main_title={
                "title": "Welcome to Enterprise WeChat",
                "desc": "Your friend is inviting you to join Enterprise WeChat",
            },
            template_card_emphasis_content={
                "title": "100",
                "desc": "Data Meaning",
            },
            template_card_quote_area={
                "type": 1,
                "url": "https://work.weixin.qq.com/?from=openApi",
                "title": "Quote Title",
                "quote_text": "Jack: Enterprise WeChat is really good~\nBalian: Super good software!",
            },
            template_card_sub_title_text="Download Enterprise WeChat to grab red packets!",
            template_card_horizontal_content_list=[
                {
                    "keyname": "Inviter",
                    "value": "Zhang San",
                },
                {
                    "keyname": "Official Website",
                    "value": "Click to visit",
                    "type": 1,
                    "url": "https://work.weixin.qq.com/?from=openApi",
                },
            ],
            template_card_jump_list=[
                {
                    "type": 1,
                    "url": "https://work.weixin.qq.com/?from=openApi",
                    "title": "Enterprise WeChat Official Website",
                },
            ],
            template_card_card_action={
                "type": 1,
                "url": "https://work.weixin.qq.com/?from=openApi",
            },
        )
        print("✓ Text notice template card sent successfully!")
        print(f"Response: {response}")
    except Exception as e:
        print("✗ Failed to send text notice template card!")
        print(f"Error: {e}")


def send_news_notice_template_card():
    """Send a news notice template card."""
    print("\n" + "=" * 60)
    print("Sending news notice template card...")
    print("=" * 60)

    webhook_url = os.getenv("WECOM_WEBHOOK_URL")
    if not webhook_url:
        print("ERROR: WECOM_WEBHOOK_URL environment variable is not set!")
        print("Please set it using: export WECOM_WEBHOOK_URL='your_webhook_url'")
        return

    bridge = NotifyBridge()
    try:
        response = bridge.send(
            "wecom",
            webhook_url=webhook_url,
            msg_type="template_card",
            template_card_type="news_notice",
            template_card_source={
                "icon_url": "https://wework.qpic.cn/wwpic/252813_jOfDHtcISzuodLa_1629280209/0",
                "desc": "Enterprise WeChat",
                "desc_color": 0,
            },
            template_card_main_title={
                "title": "Welcome to Enterprise WeChat",
                "desc": "Your friend is inviting you to join Enterprise WeChat",
            },
            template_card_image={
                "url": "https://wework.qpic.cn/wwpic/354393_4zpkKXd7SrGMvfg_1629280616/0",
                "aspect_ratio": 2.25,
            },
            template_card_image_text_area={
                "type": 1,
                "url": "https://work.weixin.qq.com",
                "title": "Welcome to Enterprise WeChat",
                "desc": "Your friend is inviting you to join Enterprise WeChat",
                "image_url": "https://wework.qpic.cn/wwpic/354393_4zpkKXd7SrGMvfg_1629280616/0",
            },
            template_card_quote_area={
                "type": 1,
                "url": "https://work.weixin.qq.com/?from=openApi",
                "title": "Quote Title",
                "quote_text": "Jack: Enterprise WeChat is really good~\nBalian: Super good software!",
            },
            template_card_vertical_content_list=[
                {
                    "title": "Surprise red packets waiting for you",
                    "desc": "Download Enterprise WeChat to grab red packets!",
                },
            ],
            template_card_horizontal_content_list=[
                {
                    "keyname": "Inviter",
                    "value": "Zhang San",
                },
                {
                    "keyname": "Official Website",
                    "value": "Click to visit",
                    "type": 1,
                    "url": "https://work.weixin.qq.com/?from=openApi",
                },
            ],
            template_card_jump_list=[
                {
                    "type": 1,
                    "url": "https://work.weixin.qq.com/?from=openApi",
                    "title": "Enterprise WeChat Official Website",
                },
            ],
            template_card_card_action={
                "type": 1,
                "url": "https://work.weixin.qq.com/?from=openApi",
            },
        )
        print("✓ News notice template card sent successfully!")
        print(f"Response: {response}")
    except Exception as e:
        print("✗ Failed to send news notice template card!")
        print(f"Error: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("WeCom Template Card Notification Examples")
    print("=" * 60)
    print("\nMake sure to set WECOM_WEBHOOK_URL environment variable:")
    print("  export WECOM_WEBHOOK_URL='https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY'")
    print("\n")

    # Send text notice template card
    send_text_notice_template_card()

    # Send news notice template card
    send_news_notice_template_card()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
