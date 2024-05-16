import discord
from discord import Activity, ActivityType
from discord.ext.commands import Bot, Cog, Context, command, Command, CommandRegistrationError
from discord.embeds import Embed
import os, logging, random
from datetime import datetime, UTC

import config, save, auth

LOGGING_LEVEL = logging.DEBUG

# Move old log and timestamp
if not os.path.exists(config.LOG_FOLDER): os.mkdir(f"./{config.LOG_FOLDER}")
if os.path.exists(config.LOG_PATH): os.rename(config.LOG_PATH, f"{config.LOG_FOLDER}/{datetime.now(UTC).strftime('%Y-%m-%d_%H-%M-%S_hornet.log')}")
# Setup logging
filehandler = logging.FileHandler(filename=config.LOG_PATH, encoding="utf-8", mode="w")
filehandler.setFormatter(logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', '%Y-%m-%d %H:%M:%S', style='{'))
logging.getLogger().addHandler(filehandler)  # file log

discord.utils.setup_logging(level=LOGGING_LEVEL)  # add stream to stderr & set for discord.py

class EmbedContext(Context):
    @staticmethod
    def get_embed(message=None, title=None, fields=None):
        embed = Embed(description=message[:4096] if message is not None else None,
                      title=title[:256] if title is not None else None,
                      colour=config.EMBED_COLOUR)
        if fields:
            for i, f in zip(range(25), fields):  # 25 fields is the maximum
                inline = f[2] if len(f) == 3 else False
                embed.add_field(name=f[0][:256], value=f[1][:1024], inline=inline)
        return embed
    
    async def embed_reply(self, message=None, title=None, fields=None):
        await self.reply(embed=self.get_embed(message, title, fields), mention_author=False)
    
    async def embed_message(self, message=None, title=None, fields=None):
        await self.send(embed=self.get_embed(message, title, fields))

class ZoteBot(Bot):
    def __init__(self, **args) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.presences = True
        intents.members = True
        super().__init__(case_insensitive=True, command_prefix="~", intents=intents, **args)
    
    async def get_context(self, message, *, cls: type[Context] = EmbedContext):
        return await super().get_context(message, cls=cls)
    
    async def on_ready(self):
        await self.add_cog(BaseCog(self))

class BaseCog(Cog):
    """Base commands for ZoteBot."""
    def __init__(self, bot: ZoteBot) -> None:
        self.bot = bot
        for name, content in save.PASTAS.items():
            try:
                cmd = self.get_plain_command(name, content)
                self.bot.add_command(cmd)
            except CommandRegistrationError as e:
                logging.error(f"Command {e.name} was already registered!")
        super().__init__()
    
    def get_plain_command(self, name: str, content: str):
        async def plain_cmd(context: Context):
            await context.send(content)
        return Command(plain_cmd, name=name, cog=self)
    
    @command()
    async def list(self, context: EmbedContext):
        """I'll tell you all of the pastas I have been told in my travels."""
        await context.send(", ".join(save.PASTAS.keys()))
    
    @command()
    async def precept(self, context: EmbedContext, index: int | None = None):
        """I'll recite one of my 57 legendary precepts."""
        index = random.randint(0, 56) if index is None else (index - 1) % 56
        precept = config.precepts[index]
        await context.send(precept)
    
    @command()
    @auth.check_admin
    async def create(self, context: EmbedContext, name: str, *, content: str):
        if name in self.bot.all_commands:
            await context.reply(f"Pasta {name} is already registered!", mention_author=False)
            return
        self.bot.add_command(self.get_plain_command(name, content))
        save.PASTAS[name] = content
        save.save()
        await context.reply(f"Added {name}!", mention_author=False)
    
    @command()
    @auth.check_admin
    async def remove(self, context: EmbedContext, name: str):
        if name not in save.PASTAS:
            await context.reply(f"Pasta {name} not found!", mention_author=False)
            return
        self.bot.remove_command(name)
        await context.reply(f"Removed {name}!", mention_author=False)


bot = ZoteBot(activity=Activity(name="The Eternal Ordeal", type=ActivityType.competing))

bot.run(config.TOKEN)
