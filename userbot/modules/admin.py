# Copyright (C) 2018 Raphielscape LLC.
#
# Licensed under the Raphielscape Public License, Version 1.0 (the "License");
# you may not use this file except in compliance with the License.

from time import sleep

from telethon.errors import BadRequestError
from telethon.errors.rpcerrorlist import UserIdInvalidError
from telethon.tl.functions.channels import EditAdminRequest, EditBannedRequest

from telethon.tl.types import ChatAdminRights, ChatBannedRights

from userbot import (LOGGER, LOGGER_GROUP)
from userbot.events import register


@register(outgoing=True, pattern="^.promote$")
async def promote(promt):
    """ For .promote command, do promote targeted person """
    if not promt.text[0].isalpha() \
            and promt.text[0] not in ("/", "#", "@", "!"):
        chats = await promt.get_chat()
        admin = chats.admin_rights
        creator = chats.creator
        new_rights = ChatAdminRights(
            add_admins=True,
            invite_users=True,
            change_info=True,
            ban_users=True,
            delete_messages=True,
            pin_messages=True
        )

        # Self explanatory
        if not await promt.get_reply_message():
            await promt.edit("`Give a reply message`")
        elif not admin and creator:
            rights = new_rights
        elif not admin and not creator:
            rights = None
        await promt.edit("`Promoting...`")

        # Try to promote if current user is admin or creator
        try:
            await promt.client(
                EditAdminRequest(promt.chat_id,
                                 (await promt.get_reply_message()).sender_id,
                                 new_rights, "admin")
            )
            await promt.edit(f"**Promoted Successfully in {promt.chat.title}!**")

        # If Telethon spit BadRequestError, assume
        # we don't have Promote permission
        except BadRequestError:
            await promt.edit(
                "`You Don't have sufficient permissions to promote`"
                )
            return


@register(outgoing=True, pattern="^.demote$")
async def demote(dmod):
    """ For .demote command, do demote targeted person """
    if not dmod.text[0].isalpha() and dmod.text[0] not in ("/", "#", "@", "!"):
        # Get targeted chat
        chat = await dmod.get_chat()
        # Grab admin status or creator in a chat
        admin = chat.admin_rights
        creator = chat.creator

        # If there's no reply, return
        if not await dmod.get_reply_message():
            await dmod.edit("`Give a reply message`")
            return
        # If not admin and not creator, also return
        if not admin and not creator:
            await dmod.edit("`You aren't an admin!`")
            return

        # If passing, declare that we're going to demote
        await dmod.edit("`Demoting...`")

        # New rights after demotion
        newrights = ChatAdminRights(
            add_admins=None,
            invite_users=None,
            change_info=None,
            ban_users=None,
            delete_messages=None,
            pin_messages=None
        )
        # Edit Admin Permission
        try:
            await dmod.client(
                EditAdminRequest(dmod.chat_id,
                                 (await dmod.get_reply_message()).sender_id,
                                 newrights, "admin")
            )

        # If we catch BadRequestError from Telethon
        # Assume we don't have permission to demote
        except BadRequestError:
            await dmod.edit(
                "`You Don't have sufficient permissions to demote`"
                )
            return
        await dmod.edit("**Demoted Successfully! in {dmod.chat.title}**")


@register(outgoing=True, pattern="^.ban$")
async def thanos(bon):
    """ For .ban command, do "thanos" at targeted person """
    if not bon.text[0].isalpha() and bon.text[0] not in ("/", "#", "@", "!"):
        banned_rights = ChatBannedRights(
            until_date=None,
            view_messages=True,
            send_messages=True,
            send_media=True,
            send_stickers=True,
            send_gifs=True,
            send_games=True,
            send_inline=True,
            embed_links=True,
        )

        # Here laying the sanity check
        chat = await bon.get_chat()
        admin = chat.admin_rights
        creator = chat.creator

        # For dealing with reply-at-ban
        sender = await bon.get_reply_message()

        # Well
        if not admin and not creator:
            await bon.edit("`You aren't an admin!`")
            return

        # Announce that we're going to whacking the pest
        await bon.edit("`Whacking the pest!`")
        await bon.client(
            EditBannedRequest(
                bon.chat_id,
                sender.sender_id,
                banned_rights
            )
        )

        # Delete message and then tell that the command
        # is done gracefully
        await bon.edit("`Banned!`")

        # Announce to the logging group if we done a banning
        if LOGGER:
            await bon.client.send_message(
                LOGGER_GROUP,
                str((await bon.get_reply_message()).sender_id)
                + " was banned.",
            )


@register(outgoing=True, pattern="^.unban$")
async def nothanos(unbon):
    if not unbon.text[0].isalpha() and unbon.text[0] \
            not in ("/", "#", "@", "!"):
        rights = ChatBannedRights(
            until_date=None,
            send_messages=None,
            send_media=None,
            send_stickers=None,
            send_gifs=None,
            send_games=None,
            send_inline=None,
            embed_links=None,
            )
        replymsg = await unbon.get_reply_message()
        try:
            await unbon.client(EditBannedRequest(
                unbon.chat_id,
                replymsg.sender_id,
                rights
                ))
            await unbon.edit("```Unbanned Successfully```")

            if LOGGER:
                await unbon.client.send_message(
                    LOGGER_GROUP,
                    str((await unbon.get_reply_message()).sender_id)
                    + " was unbanned.",
                )
        except UserIdInvalidError:
            await unbon.edit("`Uh oh my unban logic broke!`")


@register(outgoing=True, pattern="^.mute$")
async def spider(spdr):
    """
    This function basically muting peeps
    """
    if not spdr.text[0].isalpha() and spdr.text[0] not in ("/", "#", "@", "!"):

        # Check if the function running under SQL mode
        try:
            from userbot.modules.sql_helper.spam_mute_sql import mute
        except Exception:
            await spdr.edit("`Running on Non-SQL mode!`")
            return

        # Get the targeted chat
        chat = await spdr.get_chat()
        # Check if current user is admin
        admin = chat.admin_rights
        # Check if current user is creator
        creator = chat.creator

        # If not admin and not creator, return
        if not admin and not creator:
            await spdr.edit("`You aren't an admin!`")
            return

        target = await spdr.get_reply_message()
        # Else, do announce and do the mute
        mute(spdr.chat_id, target.sender_id)
        await spdr.edit("`Gets a tape!`")

        # Announce that the function is done
        await spdr.edit("`Safely taped!`")

        # Announce to logging group
        if LOGGER:
            await spdr.client.send_message(
                LOGGER_GROUP,
                str((await spdr.get_reply_message()).sender_id)
                + " was muted.",
            )


@register(outgoing=True, pattern="^.unmute$")
async def unmoot(unmot):
    if not unmot.text[0].isalpha() and unmot.text[0] \
            not in ("/", "#", "@", "!"):
        rights = ChatBannedRights(
            until_date=None,
            send_messages=None,
            send_media=None,
            send_stickers=None,
            send_gifs=None,
            send_games=None,
            send_inline=None,
            embed_links=None,
            )
        replymsg = await unmot.get_reply_message()
        from userbot.modules.sql_helper.spam_mute_sql import unmute
        unmute(unmot.chat_id, replymsg.sender_id)
        try:
            await unmot.client(EditBannedRequest(
                unmot.chat_id,
                replymsg.sender_id,
                rights
                ))
            await unmot.edit("```Unmuted Successfully```")
        except UserIdInvalidError:
            await unmot.edit("`Uh oh my unmute logic broke!`")


@register(incoming=True)
async def muter(moot):
    try:
        from userbot.modules.sql_helper.spam_mute_sql import is_muted
        from userbot.modules.sql_helper.gmute_sql import is_gmuted
    except:
        return
    muted = is_muted(moot.chat_id)
    gmuted = is_gmuted(moot.sender_id)
    rights = ChatBannedRights(
                until_date=None,
                send_messages=True,
                send_media=True,
                send_stickers=True,
                send_gifs=True,
                send_games=True,
                send_inline=True,
                embed_links=True,
                )
    if muted:
        for i in muted:
            if str(i.sender) == str(moot.sender_id):
                await moot.delete()
                await moot.client(EditBannedRequest(
                    moot.chat_id,
                    moot.sender_id,
                    rights
                    ))
    for i in gmuted:
        if i.sender == str(moot.sender_id):
            await moot.delete()


@register(outgoing=True, pattern="^.ungmute$")
async def ungmoot(ungmoot):
    if not ungmoot.text[0].isalpha() and ungmoot.text[0] \
            not in ("/", "#", "@", "!"):
        try:
            from userbot.modules.sql_helper.gmute_sql import ungmute
        except:
            await ungmoot.edit('`Running on Non-SQL Mode!`')
        ungmute(str((await ungmoot.get_reply_message()).sender_id))
        await ungmoot.edit("```Ungmuted Successfully```")


@register(outgoing=True, pattern="^.gmute$")
async def gspider(gspdr):
    if not gspdr.text[0].isalpha() and gspdr.text[0] not in ("/", "#", "@", "!"):
        try:
            from userbot.modules.sql_helper.gmute_sql import gmute
        except Exception as err:
            print(err)
            await gspdr.edit("`Running on Non-SQL mode!`")
            return

        gmute(str((await gspdr.get_reply_message()).sender_id))
        await gspdr.edit("`Grabs a huge, sticky duct tape!`")
        sleep(5)
        await gspdr.delete()
        await gspdr.respond("`Taped!`")

        if LOGGER:
            await gspdr.send_message(
                LOGGER_GROUP,
                str((await gspdr.get_reply_message()).sender_id)
                + " was muted.",
            )
