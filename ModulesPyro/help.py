from Panda import CMD_LIST, XTRA_CMD_LIST, pyrotgbot as bot
from Panda._func.decorators import Config, Panda_cmd as ilhammansiz_on_cmd
from Panda._func._helpers import edit_or_reply, get_text
from . import HELP


HELP(
    "help",
)


@ilhammansiz_on_cmd(
    ["helpme", "helper"],
    cmd_help={
        "help": "Gets Help Menu",
        "example": "{ch}helpme",
    },
)
async def help(client, message):
    f_ = await edit_or_reply(message, "`Please Wait!`")
    if bot:
        starkbot = bot.me
        bot_username = starkbot.username
        try:
            nice = await client.get_inline_bot_results(bot=bot_username, query="help")
            await client.send_inline_bot_result(
                message.chat.id, nice.query_id, nice.results[0].id, hide_via=True
            )
        except BaseException as e:
            return await f_.edit(f"`Unable To Open Help Menu Here.` \n**ERROR :** `{e}`")
        await f_.delete()
    else:
        cmd_ = get_text(message)
        if not cmd_:
            help_t = prepare_cmd_list()            
            await f_.edit(help_t)
        else:
            help_s = get_help_str(cmd_)
            if not help_s:
                await f_.edit("<code>404: Plugin Not Found!</code>")
                return
            await f_.edit(help_s)


@ilhammansiz_on_cmd(
    ["help", "ahelper"],
    cmd_help={
        "help": "Gets Help List & Info",
        "example": "{ch}ahelp (cmd_name)",
    },
)
async def help_(client, message):
    f_ = await edit_or_reply(message, "`Please Wait.`")
    cmd_ = get_text(message)
    if not cmd_:
        help_t = f"`{HELP}`"   
        await f_.edit(help_t)
    else:
        help_s = get_help_str(cmd_)
        if not help_s:
            await f_.edit("<code>404: Plugin Not Found!</code>")
            return
        await f_.edit(help_s)

        
def get_help_str(string):
    if string not in CMD_LIST.keys():
        if string not in XTRA_CMD_LIST.keys():
            return None
        return XTRA_CMD_LIST[string]
    return CMD_LIST[string]
    
def prepare_cmd_list():
    main_l = f"<b><u> __PandaUserbot CommandList__ </b></u> \n\n<b> __Number CommandList__ ({len(HELP)}) :</b> \n\n"
    for i in HELP:
        if i:
            main_l += f"<code>{i}</code>    "
    main_l += f"\n\nUse <code>{Config.COMMAND_HANDLER}help afk</code> To Know More About A Plugin."
    return main_l 


