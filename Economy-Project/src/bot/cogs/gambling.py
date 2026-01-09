"""
Comandos de casino y gambling - Sistema de apuestas y juegos de azar con mensajes divertidos
"""

from discord.ext import commands
import discord
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.database import db

class Gambling(commands.Cog):
    """Comandos relacionados con el juego de azar"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="coinflip", aliases=["cf", "moneda"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def coinflip(self, ctx, amount: int, choice: str):
        """
        Lanza una moneda y apuesta
        
        Elige cara o cruz y duplica tu dinero si aciertas.
        
        Uso: .coinflip <cantidad> <cara/cruz>
        Ejemplo: .coinflip 100 cara
        """
        choice = choice.lower()
        if choice not in ["cara", "cruz", "heads", "tails"]:
            await ctx.send("❌ Elige 'cara' o 'cruz'")
            return
        
        if amount <= 0:
            await ctx.send("❌ La cantidad debe ser mayor que 0")
            return
        
        user_data = db.get_user(str(ctx.author.id))
        if user_data.get('wallet', 0) < amount:
            await ctx.send(f"❌ No tienes suficiente dinero. Tu wallet: ${user_data.get('wallet', 0):,}")
            return
        
        # Lanzar moneda
        result = random.choice(["cara", "cruz"])
        won = (choice in ["cara", "heads"] and result == "cara") or (choice in ["cruz", "tails"] and result == "cruz")
        
        if won:
            winnings = amount
            db.add_money(str(ctx.author.id), winnings, "wallet")
            
            embed = discord.Embed(
                title="🪙 Coinflip - ¡GANASTE!",
                description=f"La moneda cayó en **{result}**!",
                color=discord.Color.green()
            )
            embed.add_field(name="💰 Apuesta", value=f"${amount:,}", inline=True)
            embed.add_field(name="✅ Ganancia", value=f"${winnings:,}", inline=True)
            embed.add_field(name="💵 Nuevo Balance", value=f"${user_data.get('wallet', 0) + winnings:,}", inline=True)
        else:
            db.remove_money(str(ctx.author.id), amount, "wallet")
            
            embed = discord.Embed(
                title="🪙 Coinflip - Perdiste...",
                description=f"La moneda cayó en **{result}**",
                color=discord.Color.red()
            )
            embed.add_field(name="💸 Perdiste", value=f"${amount:,}", inline=True)
            embed.add_field(name="💵 Nuevo Balance", value=f"${user_data.get('wallet', 0) - amount:,}", inline=True)
        
        embed.set_footer(text=f"{ctx.author.name} eligió {choice}")
        await ctx.send(embed=embed)

    @commands.command(name="dice", aliases=["dados"])
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def dice(self, ctx, amount: int):
        """
        Lanza los dados
        
        Gana hasta 6x tu apuesta si sacas doble 6!
        
        Multiplicadores:
        - Suma >= 10: 2x
        - Suma >= 11: 3x
        - Doble 6: 6x
        """
        if amount <= 0:
            await ctx.send("❌ La cantidad debe ser mayor que 0")
            return
        
        user_data = db.get_user(str(ctx.author.id))
        if user_data.get('wallet', 0) < amount:
            await ctx.send(f"❌ No tienes suficiente dinero. Tu wallet: ${user_data.get('wallet', 0):,}")
            return
        
        # Lanzar dados
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        total = dice1 + dice2
        
        # Calcular multiplicador
        multiplier = 0
        if dice1 == 6 and dice2 == 6:
            multiplier = 6
        elif total >= 11:
            multiplier = 3
        elif total >= 10:
            multiplier = 2
        
        if multiplier > 0:
            winnings = amount * multiplier
            db.add_money(str(ctx.author.id), winnings - amount, "wallet")
            
            embed = discord.Embed(
                title="🎲 Dados - ¡GANASTE!",
                description=f"🎲 Dados: **{dice1}** y **{dice2}** (Total: {total})",
                color=discord.Color.green()
            )
            embed.add_field(name="💰 Apuesta", value=f"${amount:,}", inline=True)
            embed.add_field(name="📊 Multiplicador", value=f"{multiplier}x", inline=True)
            embed.add_field(name="✅ Ganancia", value=f"${winnings:,}", inline=True)
        else:
            db.remove_money(str(ctx.author.id), amount, "wallet")
            
            embed = discord.Embed(
                title="🎲 Dados - Perdiste",
                description=f"🎲 Dados: **{dice1}** y **{dice2}** (Total: {total})",
                color=discord.Color.red()
            )
            embed.add_field(name="💸 Perdiste", value=f"${amount:,}", inline=True)
        
        embed.set_footer(text="Necesitas 10+ para ganar")
        await ctx.send(embed=embed)

    @commands.command(name="slots", aliases=["tragamonedas"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def slots(self, ctx, amount: int):
        """
        Máquina tragamonedas
        
        Gira la máquina y gana hasta 10x tu apuesta!
        
        Multiplicadores:
        - 3 iguales: 10x
        - 2 iguales: 3x
        - Ninguno igual: pierdes
        """
        if amount <= 0:
            await ctx.send("❌ La cantidad debe ser mayor que 0")
            return
        
        user_data = db.get_user(str(ctx.author.id))
        if user_data.get('wallet', 0) < amount:
            await ctx.send(f"❌ No tienes suficiente dinero. Tu wallet: ${user_data.get('wallet', 0):,}")
            return
        
        # Símbolos de slots
        symbols = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣"]
        
        # Girar slots
        slot1 = random.choice(symbols)
        slot2 = random.choice(symbols)
        slot3 = random.choice(symbols)
        
        # Calcular resultado
        multiplier = 0
        if slot1 == slot2 == slot3:
            multiplier = 10 if slot1 == "💎" else 7
        elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
            multiplier = 3
        
        embed = discord.Embed(
            title="🎰 Slots",
            description=f"╔═══════════╗\n║  {slot1}  {slot2}  {slot3}  ║\n╚═══════════╝",
            color=discord.Color.gold()
        )
        
        if multiplier > 0:
            winnings = amount * multiplier
            db.add_money(str(ctx.author.id), winnings - amount, "wallet")
            
            embed.color = discord.Color.green()
            embed.add_field(name="💰 Apuesta", value=f"${amount:,}", inline=True)
            embed.add_field(name="📊 Multiplicador", value=f"{multiplier}x", inline=True)
            embed.add_field(name="✅ Ganancia", value=f"${winnings:,}", inline=True)
            embed.set_footer(text="¡Felicidades! 🎉")
        else:
            db.remove_money(str(ctx.author.id), amount, "wallet")
            
            embed.color = discord.Color.red()
            embed.add_field(name="💸 Perdiste", value=f"${amount:,}", inline=False)
            embed.set_footer(text="Mejor suerte la próxima vez...")
        
        await ctx.send(embed=embed)

    @commands.command(name="blackjack", aliases=["bj", "21"])
    @commands.cooldown(1, 90, commands.BucketType.user)
    async def blackjack(self, ctx, amount: int):
        """
        Juego de Blackjack simplificado
        
        Trata de acercarte a 21 sin pasarte.
        Blackjack natural (21 con 2 cartas): 2.5x
        Ganar: 2x
        Empate: devuelve tu apuesta
        """
        if amount <= 0:
            await ctx.send("❌ La cantidad debe ser mayor que 0")
            return
        
        user_data = db.get_user(str(ctx.author.id))
        if user_data.get('wallet', 0) < amount:
            await ctx.send(f"❌ No tienes suficiente dinero. Tu wallet: ${user_data.get('wallet', 0):,}")
            return
        
        # Cartas simplificadas
        def draw_cards(n):
            cards = []
            for _ in range(n):
                card = random.randint(1, 11)
                if card > 10:
                    card = 10  # J, Q, K = 10
                cards.append(card)
            return cards
        
        # Repartir cartas
        player_cards = draw_cards(2)
        dealer_cards = draw_cards(2)
        
        player_total = sum(player_cards)
        dealer_total = sum(dealer_cards)
        
        # Determinar ganador
        player_blackjack = player_total == 21
        dealer_blackjack = dealer_total == 21
        
        embed = discord.Embed(title="🃏 Blackjack", color=discord.Color.blue())
        embed.add_field(name="Tus Cartas", value=f"{player_cards} = **{player_total}**", inline=False)
        embed.add_field(name="Cartas del Dealer", value=f"{dealer_cards} = **{dealer_total}**", inline=False)
        
        if player_blackjack and not dealer_blackjack:
            winnings = int(amount * 2.5)
            db.add_money(str(ctx.author.id), winnings - amount, "wallet")
            embed.color = discord.Color.gold()
            embed.add_field(name="🎉 ¡BLACKJACK!", value=f"Ganaste ${winnings:,}", inline=False)
        elif player_total > 21:
            db.remove_money(str(ctx.author.id), amount, "wallet")
            embed.color = discord.Color.red()
            embed.add_field(name="💥 Te pasaste!", value=f"Perdiste ${amount:,}", inline=False)
        elif dealer_total > 21 or player_total > dealer_total:
            winnings = amount * 2
            db.add_money(str(ctx.author.id), winnings - amount, "wallet")
            embed.color = discord.Color.green()
            embed.add_field(name="✅ ¡Ganaste!", value=f"Ganaste ${winnings:,}", inline=False)
        elif player_total == dealer_total:
            embed.color = discord.Color.blue()
            embed.add_field(name="🤝 Empate", value=f"Recuperas ${amount:,}", inline=False)
        else:
            db.remove_money(str(ctx.author.id), amount, "wallet")
            embed.color = discord.Color.red()
            embed.add_field(name="❌ Perdiste", value=f"Perdiste ${amount:,}", inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Gambling(bot))