from discord.ext import commands
import json 
from pathlib import Path

class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.items_data = self.load_items()


    def load_items(self):
        path = Path("src/data/items.json")

        if not path.exists():
            print("No se encontró el archivo de items.")
            return []

        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
        
    def find_item(self, item_name):
        return next((item for item in self.items_data if item['name'].lower() == item_name.lower()), None)
        
    async def get_user_inventory(self, user_id):
            # TODO : Implementar la lógica para obtener el inventario del usuario desde la base de datos de momento es ram

            return []
        
    @commands.command(name='inventory', aliases=['inventario', 'inv'])
    async def show_inventory(self, ctx):
        user_id = str(ctx.author.id)
        inventory = await self.get_user_inventory(user_id)

        if not inventory:
            await ctx.send("Tu inventario está vacío, pobre")
            return
        
        text = "\n".join(
            f"{item['name']} x{item['quantity']}"
            for item in inventory
        )

        await ctx.send(f" **Tu inventario:**\n{text}")

    @commands.command(name='additem', aliases=['add'])
    async def add_item(self, ctx, item_name: str, quantity: int = 1):
        if quantity <= 0:
            await ctx.send("La cantidad debe ser al menos 1, a menos que quieras aire")
            return
        item = self.find_item(item_name)
        if not item:
            await ctx.send("Ese item no existe bro")
            return
        
        await ctx.send(
            f" Has añadido **{quantity} x {item['name']}** a tu inventario."
        
        )

    @commands.command(name='removeitem', aliases=['remove', 'rm', 'removeritemporfa'])
    async def remove_item(self, ctx, item_name: str, quantity: int = 1):
        if quantity <= 0:
            await ctx.send("La cantidad debe ser al menos 1, a menos que quieras aire")
            return
        item = self.find_item(item_name)
        if not item:
            await ctx.send("Ese item no existe bro")
            return
        
        await ctx.send(
            f" Has removido **{quantity} x {item['name']}** de tu inventario."
        
        )

async def setup(bot):
    await bot.add_cog(Inventory(bot))
