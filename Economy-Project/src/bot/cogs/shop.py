from discord.ext import commands
import json

class Shop(commands.Cog):
    """Shop commands for buying and selling items."""

    def __init__(self, bot):
        self.bot = bot
        self.shop_items = self.load_shop_items()

    def load_shop_items(self):
        with open('src/data/shop_items.json', 'r') as file:
            return json.load(file)

    @commands.command(name='shop', aliases=['tienda'])
    async def show_shop(self, ctx):
        """🛒 Muestra los artículos disponibles en la tienda."""
        embed = discord.Embed(title="Tienda", description="Artículos disponibles para comprar:")
        for item, details in self.shop_items.items():
            embed.add_field(name=item, value=f"Precio: ${details['price']}\nDescripción: {details['description']}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='buy', aliases=['comprar'])
    async def buy_item(self, ctx, item_name: str, quantity: int = 1):
        """💰 Compra un artículo de la tienda."""
        item_name = item_name.lower()
        if item_name not in self.shop_items:
            await ctx.send("Artículo no encontrado en la tienda.")
            return

        item = self.shop_items[item_name]
        total_price = item['price'] * quantity

        # Aquí deberías agregar la lógica para verificar el saldo del usuario y realizar la compra.
        # Esto es solo un ejemplo de respuesta.
        await ctx.send(f"Has comprado {quantity}x {item_name} por un total de ${total_price}.")

    @commands.command(name='sell', aliases=['vender'])
    async def sell_item(self, ctx, item_name: str, quantity: int = 1):
        """💸 Vende un artículo a la tienda."""
        item_name = item_name.lower()
        if item_name not in self.shop_items:
            await ctx.send("Artículo no encontrado en la tienda.")
            return

        item = self.shop_items[item_name]
        total_price = item['price'] * quantity * 0.5  # Vender a la mitad del precio

        # Aquí deberías agregar la lógica para verificar que el usuario tenga el artículo y realizar la venta.
        # Esto es solo un ejemplo de respuesta.
        await ctx.send(f"Has vendido {quantity}x {item_name} por un total de ${total_price}.")

async def setup(bot):
    await bot.add_cog(Shop(bot))