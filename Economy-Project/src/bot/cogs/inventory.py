from discord.ext import commands
import json

class Inventory(commands.Cog):
    """Cog for managing user inventory commands."""

    def __init__(self, bot):
        self.bot = bot
        self.items_data = self.load_items()

    def load_items(self):
        with open('src/data/items.json', 'r') as f:
            return json.load(f)

    @commands.command(name='inventory', aliases=['inv'])
    async def inventory(self, ctx):
        """📦 View your inventory."""
        user_id = ctx.author.id
        user_inventory = await self.get_user_inventory(user_id)

        if not user_inventory:
            await ctx.send("Tu inventario está vacío.")
            return

        inventory_list = "\n".join(f"{item['name']} x{item['quantity']}" for item in user_inventory)
        await ctx.send(f"**Tu inventario:**\n{inventory_list}")

    async def get_user_inventory(self, user_id):
        # Placeholder for fetching user inventory from the database
        return []

    @commands.command(name='additem', aliases=['add'])
    async def add_item(self, ctx, item_name: str, quantity: int):
        """➕ Add an item to your inventory."""
        user_id = ctx.author.id
        item = next((item for item in self.items_data if item['name'].lower() == item_name.lower()), None)

        if not item:
            await ctx.send("Ese ítem no existe.")
            return

        if quantity <= 0:
            await ctx.send("La cantidad debe ser mayor que cero.")
            return

        # Placeholder for adding item to the user's inventory in the database
        await ctx.send(f"Has añadido {quantity} x {item_name} a tu inventario.")

    @commands.command(name='removeitem', aliases=['remove'])
    async def remove_item(self, ctx, item_name: str, quantity: int):
        """➖ Remove an item from your inventory."""
        user_id = ctx.author.id
        item = next((item for item in self.items_data if item['name'].lower() == item_name.lower()), None)

        if not item:
            await ctx.send("Ese ítem no existe.")
            return

        if quantity <= 0:
            await ctx.send("La cantidad debe ser mayor que cero.")
            return

        # Placeholder for removing item from the user's inventory in the database
        await ctx.send(f"Has eliminado {quantity} x {item_name} de tu inventario.")

async def setup(bot):
    await bot.add_cog(Inventory(bot))