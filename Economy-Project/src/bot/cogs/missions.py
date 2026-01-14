from discord.ext import commands
import random

class Mission(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.mission_data = {
            "collect_100_coins": {
                "description": "Recoge 100 monedas.",
                "reward": 100
            },
            "defeat_5_monsters": {
                "description": "Derrota a 5 monstruos.",
                "reward": 250
            },
            "find_hidden_treasure": {
                "description": "Encuentra un tesoro escondido.",
                "reward": 500
            },
            "help_10_users": {
                "description": "Ayuda a 10 usuarios.",
                "reward": 150
            },
            "complete_daily_tasks": {
                "description": "Completa 3 tareas diarias.",
                "reward": 200
            },
        }

        self.user_missions = {}

    def get_user_mission(self, user_id):
        if user_id not in self.user_missions:
            self.user_missions[user_id] = {
                key: False for key in self.mission_data.keys()
            }
        return self.user_missions[user_id]
    
    @commands.command(name='mission', aliases=['mision'])
    async def list_missions(self, ctx):
        user_id = str(ctx.author.id)
        missions = self.get_user_mission(user_id)

        text = []

        for key, data in self.mission_data.items():
            if not missions[key]:
                text.append(
                    f"**{key}** — {data['description']} "
                    f"(Recompensa: {data['reward']} monedas)"
                )
            
        if not text:
            await ctx.send("Has completado todas las misiones disponibles, ya era hora!")
            return
        
        await ctx.send(
            "Misiones disponibles:\n" + "\n".join(text)
        )
    @commands.command(name='complete_mission', aliases=['completar_mision'])
    async def complete_mission(self, ctx, mission_xd: str):
        user_id = str(ctx.author.id)
        missions = self.get_user_mission(user_id)

        if mission_xd not in self.mission_data:
            await ctx.send("Esa misión no existe bro, usa .mission")
            return
        if missions[mission_xd]:
            await ctx.send("Ya completaste esa misión bro")
            return
        
        if random.random() < 0.8:
            missions[mission_xd] = True
            reward = self.mission_data[mission_xd]['reward']

            await ctx.send(
                f"¡Misión completada! Has ganado {reward} monedas."
            )
        else:
            await ctx.send(
                "No lograste completar la misión, nefasto"
            )
async def setup(bot):
    await bot.add_cog(Mission(bot))