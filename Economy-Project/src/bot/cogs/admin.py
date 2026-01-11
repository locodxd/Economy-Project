# admin.py no testeado aún - módulo para comandos administrativos del bot de Discord, implementación futura
from discord.ext import commands

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="kick", aliases=["expulsar"])
    @commands.has_permissions(kick_members=True)
    async def kick_user(self, ctx, member: commands.MemberConverter, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f"{member.display_name} ha sido expulsado. Razón: {reason}")

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_user(self, ctx, member: commands.MemberConverter, *, reason=None):
        """Ban a user from the server."""
        await member.ban(reason=reason)
        await ctx.send(f"{member.display_name} ha sido baneado. Razón: {reason}")

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban_user(self, ctx, *, member_name):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member_name.split('#')

        for ban_entry in banned_users:
            if ban_entry.user.name == member_name and ban_entry.user.discriminator == member_discriminator:
                await ctx.guild.unban(ban_entry.user)
                await ctx.send(f"{ban_entry.user.display_name} ha sido desbaneado.")
                return
        await ctx.send(f"No se encontró a {member_name} en la lista de baneados.")

    @commands.command(name="clear", aliases=["purge"])
    @commands.has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"{amount} mensajes han sido eliminados.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Admin(bot))