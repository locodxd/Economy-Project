from discord.ext import commands
import random

class Missions(commands.Cog):
    """Comandos para completar misiones y obtener recompensas"""

    def __init__(self, bot):
        self.bot = bot
        self.missions = {
            "collect_100_coins": {
                "description": "Recoge 100 monedas.",
                "reward": 100,
                "completed": False
            },
            "defeat_5_monsters": {
                "description": "Derrota a 5 monstruos.",
                "reward": 250,
                "completed": False
            },
            "find_hidden_treasure": {
                "description": "Encuentra un tesoro escondido.",
                "reward": 500,
                "completed": False
            },
            "help_10_users": {
                "description": "Ayuda a 10 usuarios.",
                "reward": 150,
                "completed": False
            },
            "complete_daily_tasks": {
                "description": "Completa 3 tareas diarias.",
                "reward": 200,
                "completed": False
            },
        }

    @commands.command(name="missions")
    async def list_missions(self, ctx):
        """Lista las misiones disponibles"""
        mission_list = "\n".join(
            [f"{name}: {details['description']} (Recompensa: {details['reward']} monedas)" 
             for name, details in self.missions.items() if not details['completed']]
        )
        await ctx.send(f"Misiones disponibles:\n{mission_list}")

    @commands.command(name="complete_mission")
    async def complete_mission(self, ctx, mission_name: str):
        """Completa una misión específica"""
        if mission_name in self.missions:
            mission = self.missions[mission_name]
            if mission['completed']:
                await ctx.send("Esta misión ya ha sido completada.")
                return
            
            # Simular la finalización de la misión
            if random.random() < 0.8:  # 80% de probabilidad de éxito
                mission['completed'] = True
                await ctx.send(f"Misión completada: {mission['description']}! Has ganado {mission['reward']} monedas.")
            else:
                await ctx.send("No has logrado completar la misión. Inténtalo de nuevo.")
        else:
            await ctx.send("Misión no encontrada. Usa `!missions` para ver las misiones disponibles.")

async def setup(bot):
    await bot.add_cog(Missions(bot))