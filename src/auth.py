from discord import Member
from discord.ext.commands import Context, check

import config

async def is_admin(context: Context):
    if not isinstance(context.author, Member): return False
    if context.author.guild.owner == context.author: return True
    for role in context.author.roles:
        if role.id in config.ADMIN_ROLES:
            return True
    else:
        return False

check_admin = check(is_admin)
