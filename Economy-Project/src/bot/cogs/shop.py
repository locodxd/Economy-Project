import discord
from discord.ext import commands
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.database import db

class Shop(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.shop_items = self.load_shop_items()

    def load_shop_items(self):
        with open('src/data/shop_items.json', 'r') as file:
            data = json.load(file)
            items_dict = {}
            for item in data['items']:
                items_dict[item['name'].lower()] = item
            return items_dict

    @commands.command(name='shop', aliases=['tienda'])
    async def show_shop(self, ctx):
        user_data = db.get_user(str(ctx.author.id))
        wallet = user_data.get('wallet', 0)
        
        embed = discord.Embed(
            title="Tienda del Pueblo",
            description=f"Tu dinero: ${wallet:,}",
            color=discord.Color.gold()
        )
        
        categories = {}
        for item_name, item in self.shop_items.items():
            cat = item['type']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)
        
        for cat, items in categories.items():
            items_text = "\n".join([f"**{it['name']}** - ${it['price']:,}\n{it['description']}" for it in items])
            embed.add_field(name=cat.upper(), value=items_text, inline=False)
        
        embed.set_footer(text="usa .comprar <nombre> para comprar")
        await ctx.send(embed=embed)

    @commands.command(name='comprar', aliases=['buy'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def buy_item(self, ctx, *, item_name: str):
        user_id = str(ctx.author.id)
        user_data = db.get_user(user_id)
        wallet = user_data.get('wallet', 0)
        
        item_name_lower = item_name.lower()
        
        if item_name_lower not in self.shop_items:
            ctx.command.reset_cooldown(ctx)
            await ctx.send("ese item no existe pa")
            return
        
        item = self.shop_items[item_name_lower]
        price = item['price']
        
        if wallet < price:
            ctx.command.reset_cooldown(ctx)
            await ctx.send(f"necesitas ${price:,}, tenes ${wallet:,}")
            return
        
        db.remove_money(user_id, price, "wallet")
        
        if 'inventory' not in user_data:
            user_data['inventory'] = {}
        
        if item['name'].lower() not in user_data['inventory']:
            user_data['inventory'][item['name'].lower()] = 0
        
        user_data['inventory'][item['name'].lower()] += 1
        db.update_user(user_id, user_data)
        
        bonus = int(price * 0.05)
        db.add_money(user_id, bonus, 'wallet')
        
        embed = discord.Embed(
            title=f"Compra Exitosa!",
            description=f"Compraste **{item['name']}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Precio", value=f"-${price:,}", inline=True)
        embed.add_field(name="Bonus Cashback", value=f"+${bonus:,} (5%)", inline=True)
        embed.add_field(name="Dinero Restante", value=f"${wallet - price + bonus:,}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='inventario')
    async def show_inventory(self, ctx):
        user_data = db.get_user(str(ctx.author.id))
        inventory = user_data.get('inventory', {})
        
        if not inventory:
            await ctx.send("tu inventario está vacío")
            return
        
        embed = discord.Embed(
            title=f"Inventario de {ctx.author.display_name}",
            color=discord.Color.blue()
        )
        
        for item_name, quantity in inventory.items():
            if quantity > 0:
                item = self.shop_items.get(item_name)
                if item:
                    embed.add_field(
                        name=f"{item['name']} x{quantity}",
                        value=f"Precio: ${item['price']:,}",
                        inline=False
                    )
        
        await ctx.send(embed=embed)

    @commands.command(name='vender', aliases=['sell'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def sell_item(self, ctx, *, item_name: str):
        user_id = str(ctx.author.id)
        user_data = db.get_user(user_id)
        inventory = user_data.get('inventory', {})
        
        item_name_lower = item_name.lower()
        
        if item_name_lower not in inventory or inventory[item_name_lower] == 0:
            ctx.command.reset_cooldown(ctx)
            await ctx.send("no tenes ese item pa")
            return
        
        if item_name_lower not in self.shop_items:
            ctx.command.reset_cooldown(ctx)
            await ctx.send("ese item no se puede vender")
            return
        
        item = self.shop_items[item_name_lower]
        sell_price = int(item['price'] * 0.6)
        
        db.add_money(user_id, sell_price, "wallet")
        inventory[item_name_lower] -= 1
        user_data['inventory'] = inventory
        db.update_user(user_id, user_data)
        
        await ctx.send(f"vendiste {item['name']} por ${sell_price:,}")

async def setup(bot):
    await bot.add_cog(Shop(bot))