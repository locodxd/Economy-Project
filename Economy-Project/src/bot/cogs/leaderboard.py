from discord.ext import commands
import discord
from core.database import db

class Leaderboard(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="leaderboard", aliases=["lb"])
    async def leaderboard(self, ctx):
        # obtener todos los usuarers
        all_users = db.get_all_users()
        
        if not all_users:
            await ctx.send("❌ No hay usuarios registrados todavía")
            return
        
        user_wealth = []
        for user_id, user_data in all_users.items():
            try:
                member = await ctx.guild.fetch_member(int(user_id))
                username = member.display_name
            except:
                username = f"Usuario #{user_id[:4]}"
            
            wallet = user_data.get('wallet', 0)
            bank = user_data.get('bank', 0)
            total = wallet + bank
            
            user_wealth.append({
                'username': username,
                'wealth': total,
                'user_id': user_id
            })
        
        # ordenar por riqueza descendente
        user_wealth.sort(key=lambda x: x['wealth'], reverse=True)
        
        # top 10
        top_users = user_wealth[:10]
        
        embed = discord.Embed(title="🏆 Leaderboard", color=discord.Color.gold())
        
        for index, user in enumerate(top_users, start=1):
            medal = ""
            if index == 1:
                medal = "🥇"
            elif index == 2:
                medal = "🥈"
            elif index == 3:
                medal = "🥉"
            
            # resaltar al usuario que pidió el comando
            highlight = " ⭐" if user['user_id'] == str(ctx.author.id) else ""
            
            embed.add_field(
                name=f"{medal} {index}. {user['username']}{highlight}",
                value=f"💰 ${user['wealth']:,}",
                inline=False
            )
        
        # mostrar posicion del usuario si no está en top 10
        user_pos = next((i+1 for i, u in enumerate(user_wealth) if u['user_id'] == str(ctx.author.id)), None)
        if user_pos and user_pos > 10:
            user_data = next(u for u in user_wealth if u['user_id'] == str(ctx.author.id))
            embed.set_footer(text=f"Tu posición: #{user_pos} | ${user_data['wealth']:,}")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))