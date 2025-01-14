# 
from pyrogram import filters

from Panda.database.notesdb import add_note, all_note, del_note, del_notes, note_info
from Panda import Config
from Panda._func.decorators import Panda_cmd as ilhammansiz_on_cmd, listen
from Panda._func._helpers import edit_or_reply, get_text

from . import HELP

HELP(
    "notes",
)



@ilhammansiz_on_cmd(
    ["savenote"],
    cmd_help={
        "help": "Save Notes In The Chat!",
        "example": "{ch}savenote (note name) (reply to Note message)",
    },
)
async def notes(client, message):
    note_ = await edit_or_reply(message, "`Processing..`")
    note_name = get_text(message)
    if not note_name:
        await note_.edit("`Give A Note Name!`")
        return
    if not message.reply_to_message:
        await note_.edit("Reply To Message To Save As Note!")
        return
    note_name = note_name.lower()
    msg = message.reply_to_message
    copied_msg = await msg.copy(int(Config.LOG_GRP))
    add_note(note_name, message.chat.id, copied_msg.message_id)
    await note_.edit(f"`Done! {note_name} Added To Notes List!`")


@listen(filters.incoming & filters.regex("\#(\S+)"))
async def lmao(client, message):
    if all_note(message.chat.id):
        pass
    else:
        return
    owo = message.matches[0].group(1)
    if owo is None:
        return
    if note_info(owo, message.chat.id):
        sed = note_info(owo, message.chat.id)
        await client.copy_message(
            from_chat_id=int(Config.LOG_GRP),
            chat_id=message.chat.id,
            message_id=sed["msg_id"],
            reply_to_message_id=message.message_id,
        )
    


@ilhammansiz_on_cmd(
    ["delnote"],
    cmd_help={"help": "Delete Note In The Chat!", "example": "{ch}delnote (Note Name)"},
)
async def notes(client, message):
    note_ = await edit_or_reply(message, "`Processing..`")
    note_name = get_text(message)
    if not note_name:
        await note_.edit("`Give A Note Name!`")
        return
    note_name = note_name.lower()
    if not note_info(note_name, message.chat.id):
        await note_.edit("`Note Not Found!`")
        return
    del_note(note_name, message.chat.id)
    await note_.edit(f"`Note {note_name} Deleted Successfully!`")


@ilhammansiz_on_cmd(
    ["delnotes"],
    cmd_help={"help": "Delete All The Notes In The Chat!", "example": "{ch}delnotes"},
)
async def noteses(client, message):
    pablo = await edit_or_reply(message, "`Processing..`")
    poppy = all_note(message.chat.id)
    if poppy is False:
        await pablo.edit("`No Notes Found In This Chat...`")
        return
    del_notes(message.chat.id)
    await pablo.edit("Deleted All The Notes Successfully!!")


@ilhammansiz_on_cmd(
    ["notes"],
    cmd_help={"help": "List All The Chat Notes!", "example": "{ch}notes"},
)
async def noteses(client, message):
    pablo = await edit_or_reply(message, "`Processing..`")
    poppy = all_note(message.chat.id)
    if poppy is False:
        await pablo.edit("`No Notes Found In This Chat...`")
        return
    kk = ""
    for Escobar in poppy:
        kk += f"""\n~ `{Escobar.get("keyword")}`"""
    X = await client.get_chat(message.chat.id)
    grp_nme = X.title
    mag = f""" List Of Notes In {grp_nme}:
{kk}

Get Notes With `#NoteName`"""
    await pablo.edit(mag)
