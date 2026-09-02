from viseron_qqbotpy.panel import Panel, PanelItem


def test_panel_item_to_dict():
    item = PanelItem(type="command", name="签到", desc="每日签到", only_admin=False)
    assert item.to_dict() == {
        "type": "command",
        "name": "签到",
        "desc": "每日签到",
        "only_admin": False,
    }


def test_panel_add_command_and_link():
    panel = Panel(api=None)

    panel.add_command("签到", desc="每日签到")
    panel.add_link("官网", desc="打开官网", url="https://example.com")

    assert panel.items == [
        {
            "type": "command",
            "name": "签到",
            "desc": "每日签到",
            "only_admin": False,
        },
        {
            "type": "link",
            "name": "官网",
            "desc": "打开官网",
            "url": "https://example.com",
            "only_admin": False,
        },
    ]
