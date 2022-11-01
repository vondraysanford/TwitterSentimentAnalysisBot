import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Literal

class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
 
    @commands.Cog.listener()
    async def on_ready(self):
        print('Admin Cog Loaded')
        print('------')

    @commands.command(name='sync')
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()
            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return
        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1
        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")
    
    # To make an argument optional, you can either give it a supported default argument
    # or you can mark it as Optional from the typing standard library. This example does both.
    @app_commands.checks.has_role("Admin")
    @app_commands.describe(member='The member you want to get the joined date from; defaults to the user who uses the command')
    @app_commands.command(name="expose")
    async def expose(self, interaction: discord.Interaction, member: Optional[discord.Member] = None) -> None:
        """Says when a member joined."""
        # If no member is explicitly provided then we use the command user here
        member = member or interaction.user

        # The format_dt function formats the date time into a human readable representation in the official client
        await interaction.response.send_message(f'{member} joined {discord.utils.format_dt(member.joined_at)}')

    @expose.error
    async def userinfo_error(self, interaction: discord.Interaction, error: commands.CommandError):
        # if the conversion above fails for any reason, it will raise `commands.BadArgument`
        # so we handle this in this error handler:
        if isinstance(error, commands.BadArgument):
            return await interaction.response.send_message('Couldn\'t find that user.')
     
async def setup(bot):
    await bot.add_cog(Admin(bot))