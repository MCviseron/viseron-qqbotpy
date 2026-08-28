from viseron_qqbotpy import Intents, Permission


def test_intent_bits():
    assert Intents.guilds.flag == 1 << 0
    assert Intents.guild_members.flag == 1 << 1
    assert Intents.guild_messages.flag == 1 << 9
    assert Intents.public_guild_messages.flag == 1 << 30


def test_intents_all_and_default():
    all_intents = Intents.all()
    assert all_intents.guild_messages is True
    assert all_intents.forums is True

    default_intents = Intents.default()
    assert default_intents.public_guild_messages is True
    assert default_intents.guild_messages is False
    assert default_intents.forums is False


def test_permission_flags():
    perm = Permission(view_permission=True, speak_permission=True)
    assert perm.view_permission is True
    assert perm.manager_permission is False
    assert perm.value == (1 << 0) | (1 << 2)
