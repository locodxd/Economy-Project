"""
Comandos relacionados con el juego de azar, super facil de ampliar en el proximo commit
"""

from discord.ext import commands
import discord
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.database import db

class Gambling(commands.Cog):
    """Comandos del juego de azar"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="coinflip", aliases=["cf", "moneda"])
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
        
        bucket = self.coinflip._buckets.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            await ctx.send(f"⏳ Este comando está en cooldown. Intenta de nuevo en {retry_after:.1f}s")
            return
        
        if random.random() < 0.01:
            bonus = int(amount * 3)
            db.add_money(str(ctx.author.id), bonus, "wallet")
            await ctx.send(f"🪙 La moneda cayó de canto!! WTF. Ganaste ${bonus:,} por este evento imposible tenes un pedo increible!")
            return
        
        rigged_coin = random.random() < 0.03
        
        if rigged_coin:
            result = "cara" if choice in ["cara", "heads"] else "cruz"
        else:
            result = random.choice(["cara", "cruz"])
        
        won = (choice in ["cara", "heads"] and result == "cara") or (choice in ["cruz", "tails"] and result == "cruz")
        
        if won:
            winnings = amount
            
            perfect_bet = random.random() < 0.10
            if perfect_bet:
                bonus = int(amount * 0.5)
                winnings += bonus
            
            db.add_money(str(ctx.author.id), winnings, "wallet")
            
            embed = discord.Embed(
                title=" Coinflip - ¡GANASTE!",
                description=f"La moneda cayó en **{result}**!",
                color=discord.Color.green()
            )
            embed.add_field(name=" Apuesta", value=f"${amount:,}", inline=True)
            embed.add_field(name=" Ganancia", value=f"${winnings:,}", inline=True)
            embed.add_field(name=" Nuevo Balance", value=f"${user_data.get('wallet', 0) + winnings:,}", inline=True)
            
            if rigged_coin:
                embed.set_footer(text="Usaste una moneda trucada sin darte cuenta lol")
            elif perfect_bet:
                embed.set_footer(text=f"Apuesta perfecta! +${bonus:,} bonus")
        else:
            saved = random.random() < 0.05
            if saved:
                refund = int(amount * 0.6)
                db.remove_money(str(ctx.author.id), amount - refund, "wallet")
                await ctx.send(f" Perdiste pero alguien te dio ${refund:,} de vuelta. Solo perdiste ${amount - refund:,}")
                return
            
            db.remove_money(str(ctx.author.id), amount, "wallet")
            
            embed = discord.Embed(
                title=" Coinflip - Perdiste...",
                description=f"La moneda cayó en **{result}**",
                color=discord.Color.red()
            )
            embed.add_field(name=" Perdiste", value=f"${amount:,}", inline=True)
            embed.add_field(name=" Nuevo Balance", value=f"${user_data.get('wallet', 0) - amount:,}", inline=True)
        
        embed.set_footer(text=f"{ctx.author.name} eligió {choice}")
        await ctx.send(embed=embed)

    @commands.command(name="dice", aliases=["dados"])
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def dice(self, ctx, amount: int):
        """
        Lanza los dados
        
        Gana hasta 6x tu apuesta si sacas doble 6 con dados dorados!
        
        Multiplicadores:
        - Suma >= 10: 1.8x
        - Suma >= 11: 2.5x
        - Doble 6: 4x
        """
        if amount <= 0:
            await ctx.send("❌ La cantidad debe ser mayor que 0")
            return
        
        user_data = db.get_user(str(ctx.author.id))
        if user_data.get('wallet', 0) < amount:
            await ctx.send(f"❌ No tienes suficiente dinero. Tu wallet: ${user_data.get('wallet', 0):,}")
            return
        
        bucket = self.dice._buckets.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            await ctx.send(f"⏳ Este comando está en cooldown. Intenta de nuevo en {retry_after:.1f}s")
            return
        
        golden_dice = random.random() < 0.01
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        total = dice1 + dice2
        
        loaded_dice = random.random() < 0.04 and not golden_dice
        if loaded_dice:
            dice1 = 6
            total = dice1 + dice2
        
        # Calcular multiplicador
        multiplier = 0
        if dice1 == 6 and dice2 == 6:
            multiplier = 4  
            if golden_dice:
                multiplier = 6  
        elif total >= 11:
            multiplier = 2.5  
            if golden_dice:
                multiplier = 4  
        elif total >= 10:
            multiplier = 1.8  
            if golden_dice:
                multiplier = 3 
        
        if multiplier > 0:
            winnings = int(amount * multiplier)
            db.add_money(str(ctx.author.id), winnings - amount, "wallet")
            
            embed = discord.Embed(
                title=" Dados - ¡GANASTE!",
                description=f" Dados: **{dice1}** y **{dice2}** (Total: {total})",
                color=discord.Color.green()
            )
            embed.add_field(name=" Apuesta", value=f"${amount:,}", inline=True)
            embed.add_field(name=" Multiplicador", value=f"{multiplier}x", inline=True)
            embed.add_field(name=" Ganancia", value=f"${winnings:,}", inline=True)
            
            if golden_dice:
                embed.set_footer(text="Dados dorados! Multiplicador x2!")
            elif loaded_dice:
                embed.set_footer(text="Encontraste un dado cargado. Nice")
        else:

            pity_roll = random.random() < 0.08
            if pity_roll:
                refund = int(amount * 0.4)
                db.remove_money(str(ctx.author.id), amount - refund, "wallet")
                await ctx.send(f" Sacaste {dice1} y {dice2}. Que sad. Te devuelven ${refund:,} de consolación")
                return
            
            db.remove_money(str(ctx.author.id), amount, "wallet")
            
            embed = discord.Embed(
                title=" Dados - Perdiste",
                description=f" Dados: **{dice1}** y **{dice2}** (Total: {total})",
                color=discord.Color.red()
            )
            embed.add_field(name=" Perdiste", value=f"${amount:,}", inline=True)
    
        embed.set_footer(text="Necesitas 10+ para ganar")
        await ctx.send(embed=embed)

    @commands.command(name="slots", aliases=["tragamonedas"])
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
    
    
        bucket = self.slots._buckets.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            await ctx.send(f"⏳ Este comando está en cooldown. Intenta de nuevo en {retry_after:.1f}s")
            return
        
        # evento: maquina rota (2% chance)
        if random.random() < 0.02:
            refund = int(amount * 1.5)
            db.add_money(str(ctx.author.id), refund, "wallet")
            await ctx.send(f" La máquina se trabo y escupio ${refund:,}! Stonks")
            return
        
        # Símbolos de slots
        symbols = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣"]
        
        # jackpot secreto jejejej (0.5% chance)
        jackpot_event = random.random() < 0.005
        if jackpot_event:
            symbols.append("👑")
        
        slot1 = random.choice(symbols)
        slot2 = random.choice(symbols)
        slot3 = random.choice(symbols)
        
        multiplier = 0
        jackpot = False
        
        if slot1 == "👑" and slot2 == "👑" and slot3 == "👑":
            multiplier = 50
            jackpot = True
        elif slot1 == slot2 == slot3:
            multiplier = 10 if slot1 == "💎" else 7
        elif slot1 == slot2 or slot2 == slot3 or slot1 == slot3:
            multiplier = 3
        
        almost_won = multiplier == 0 and random.random() < 0.15
        
        embed = discord.Embed(
            title="🎰 Slots",
            description=f"╔═══════════╗\n║  {slot1}  {slot2}  {slot3}  ║\n╚═══════════╝",
            color=discord.Color.gold()
        )
        
        if jackpot:
            winnings = amount * multiplier
            db.add_money(str(ctx.author.id), winnings - amount, "wallet")
            embed.color = discord.Color.gold()
            embed.add_field(name=" JACKPOT SECRETO!! amigo tenes mucha suerte", value=f"WTF!! Ganaste ${winnings:,}", inline=False)
            embed.add_field(name=" Multiplicador", value=f"{multiplier}x", inline=True)
            embed.set_footer(text="Que suerte tienes loco")
        elif multiplier > 0:
            winnings = amount * multiplier
            
            extra_mult = random.random() < 0.1
            if extra_mult and multiplier >= 7:
                extra = int(winnings * 0.5)
                winnings += extra
                embed.set_footer(text=f"Bonus de racha! +${extra:,}")
            
            db.add_money(str(ctx.author.id), winnings - amount, "wallet")
            
            embed.color = discord.Color.green()
            embed.add_field(name=" Apuesta", value=f"${amount:,}", inline=True)
            embed.add_field(name=" Multiplicador", value=f"{multiplier}x", inline=True)
            embed.add_field(name=" Ganancia", value=f"${winnings:,}", inline=True)
            if not extra_mult:
                embed.set_footer(text="¡Felicidades! 🎉")
        else:
            if almost_won:
                refund = int(amount * 0.3)
                db.remove_money(str(ctx.author.id), amount - refund, "wallet")
                embed.color = discord.Color.orange()
                embed.add_field(name=" Casi!", value=f"Perdiste ${amount - refund:,} (consolación: ${refund:,})", inline=False)
                embed.set_footer(text="Estuviste cerca bro")
            else:
                db.remove_money(str(ctx.author.id), amount, "wallet")
                embed.color = discord.Color.red()
                embed.add_field(name=" Perdiste", value=f"${amount:,}", inline=False)
                embed.set_footer(text="Mejor suerte la próxima vez...")
        
        await ctx.send(embed=embed)

    @commands.command(name="blackjack", aliases=["bj", "21"])
    @commands.cooldown(1, 50, commands.BucketType.user)
    async def blackjack(self, ctx, bet: str):
        """
        Juego de Blackjack simplificado
        
        Trata de acercarte a 21 sin pasarte.
        Blackjack natural (21 con 2 cartas): 2.5x
        Ganar: 2x
        Empate: devuelve tu apuesta
        
        Uso: .bj <amount> o .bj all
        """
        user_data = db.get_user(str(ctx.author.id))
        wallet = user_data.get('wallet', 0)
        
        # manejar "all"
        if bet.lower() == "all":
            amount = wallet
        else:
            try:
                amount = int(bet)
            except ValueError:
                await ctx.send("❌ Argumento inválido. Usa .help blackjack para más información.")
                return
        
        if amount <= 0:
            await ctx.send("❌ La cantidad debe ser mayor que 0")
            return
        
        if wallet < amount:
            await ctx.send(f"❌ No tienes suficiente dinero, pobre. Tu wallet: ${wallet:,}")
            return
        
        # aplicar cooldown DESPUÉS de validar
        bucket = self.blackjack._buckets.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            await ctx.send(f"⏳ Este comando está en cooldown. Intenta de nuevo en {retry_after:.1f}s")
            return
        
        # evento random antes del juego (3% chance)
        pre_event_chance = random.random()
        if pre_event_chance < 0.015:
            # dealer se escapa con tu dinero
            db.remove_money(str(ctx.author.id), amount, "wallet")
            await ctx.send(f" El dealer agarro tu apuesta de ${amount:,} y salio corriendo!! No mames...")
            return
        elif pre_event_chance < 0.03:
            bonus = int(amount * 0.5)
            db.add_money(str(ctx.author.id), bonus, "wallet")
            await ctx.send(f" Descubriste que las cartas estaban marcadas! El casino te compenso con ${bonus:,} extras para que no lo delates. Apuesta devuelta.")
            return
        
        def draw_cards(n):
            cards = []
            for _ in range(n):
                card = random.randint(1, 11)
                if card > 10:
                    card = 10 
                cards.append(card)
            return cards
        
        player_cards = draw_cards(2)
        dealer_cards = draw_cards(2)
        
        player_total = sum(player_cards)
        dealer_total = sum(dealer_cards)
        
        dealer_drunk = random.random() < 0.05
        if dealer_drunk and dealer_total > 15:
            dealer_total = random.randint(22, 25) 
        
        player_blackjack = player_total == 21
        dealer_blackjack = dealer_total == 21 and not dealer_drunk
        
        embed = discord.Embed(title=" Blackjack", color=discord.Color.blue())
        embed.add_field(name="Tus Cartas", value=f"{player_cards} = **{player_total}**", inline=False)
        embed.add_field(name="Cartas del Dealer", value=f"{dealer_cards} = **{dealer_total}**", inline=False)
        
        if dealer_drunk:
            embed.set_footer(text="El dealer esta medio borracho lol")
        
        double_blackjack = player_blackjack and dealer_blackjack and random.random() < 0.01
        if double_blackjack:
            mega_win = amount * 5
            db.add_money(str(ctx.author.id), mega_win - amount, "wallet")
            embed.color = discord.Color.gold()
            embed.add_field(name="💎 DOBLE BLACKJACK!!", value=f"Esto casi nunca pasa! Ganaste ${mega_win:,}", inline=False)
        elif player_blackjack and not dealer_blackjack:
            tip_event = random.random() < 0.1
            winnings = int(amount * 2.5)
            if tip_event:
                tip = int(amount * 0.3)
                winnings += tip
                embed.set_footer(text=f"El dealer te dio ${tip:,} de propina por el blackjack!")
            
            db.add_money(str(ctx.author.id), winnings - amount, "wallet")
            embed.color = discord.Color.gold()
            embed.add_field(name="🎉 ¡BLACKJACK!", value=f"Ganaste ${winnings:,}", inline=False)
        elif player_total > 21:
            insurance = random.random() < 0.05
            if insurance:
                refund = int(amount * 0.5)
                db.remove_money(str(ctx.author.id), amount - refund, "wallet")
                embed.color = discord.Color.orange()
                embed.add_field(name=" Te pasaste!", value=f"Perdiste ${amount - refund:,} (seguro cubrió ${refund:,})", inline=False)
            else:
                db.remove_money(str(ctx.author.id), amount, "wallet")
                embed.color = discord.Color.red()
                embed.add_field(name=" Te pasaste bro!", value=f"Perdiste ${amount:,}", inline=False)
        elif dealer_total > 21 or player_total > dealer_total:
            winnings = amount * 2
            db.add_money(str(ctx.author.id), winnings - amount, "wallet")
            embed.color = discord.Color.green()
            embed.add_field(name=" ¡Ganaste!", value=f"Ganaste ${winnings:,}", inline=False)
        elif player_total == dealer_total:
            generous_dealer = random.random() < 0.8

            if generous_dealer:
                bonus = int(amount * 0.25)
                db.add_money(str(ctx.author.id), bonus, "wallet")
                embed.color = discord.Color.blue()
                embed.add_field(name="🤝 Empate", value=f"Recuperas ${amount:,} + ${bonus:,} de bonus por empate", inline=False)
            else:
                embed.color = discord.Color.blue()
                embed.add_field(name="🤝 Empate", value=f"Recuperas ${amount:,}", inline=False)
        else:
            db.remove_money(str(ctx.author.id), amount, "wallet")
            embed.color = discord.Color.red()
            embed.add_field(name="❌ Perdiste", value=f"Perdiste ${amount:,}", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name="roulette", aliases=["ruleta"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def roulette(self, ctx, amount: int, bet: str):
        """
        Ruleta europea
        
        Apuesta a rojo/negro, par/impar, o un número específico.
        
        Multiplicadores:
        - Rojo/Negro: 2x
        - Par/Impar: 2x
        - Número específico: 35x
        
        Uso: .roulette <cantidad> <rojo/negro/par/impar/0-36>
        """
        if amount <= 0:
            await ctx.send("❌ La cantidad debe ser mayor que 0")
            return
        
        user_data = db.get_user(str(ctx.author.id))
        if user_data.get('wallet', 0) < amount:
            await ctx.send(f"❌ No tienes suficiente dinero. Tu wallet: ${user_data.get('wallet', 0):,}")
            return
        
        bucket = self.roulette._buckets.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            await ctx.send(f"⏳ Este comando está en cooldown. Intenta de nuevo en {retry_after:.1f}s")
            return
        
        bet = bet.lower()
        
        rigged = random.random() < 0.02
        
        if rigged and bet.isdigit():
            number = int(bet)
        else:
            number = random.randint(0, 36)
        
        reds = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        color = "rojo" if number in reds else "negro" if number != 0 else "verde"
        is_even = number % 2 == 0 and number != 0
        
        won = False
        multiplier = 0
        
        if bet.isdigit():
            bet_num = int(bet)
            if 0 <= bet_num <= 36 and bet_num == number:
                won = True
                multiplier = 35
        elif bet in ["rojo", "red"] and color == "rojo":
            won = True
            multiplier = 2
        elif bet in ["negro", "black"] and color == "negro":
            won = True
            multiplier = 2
        elif bet in ["par", "even"] and is_even:
            won = True
            multiplier = 2
        elif bet in ["impar", "odd"] and not is_even and number != 0:
            won = True
            multiplier = 2
        
        embed = discord.Embed(title="🎡 Ruleta", color=discord.Color.gold())
        embed.add_field(name="Número", value=f"**{number}** ({color})", inline=False)
        embed.add_field(name="Tu apuesta", value=bet, inline=True)
        
        if won:
            winnings = amount * multiplier
            db.add_money(str(ctx.author.id), winnings - amount, "wallet")
            
            embed.color = discord.Color.green()
            embed.add_field(name="✅ Ganaste", value=f"${winnings:,}", inline=True)
            
            if rigged:
                embed.set_footer(text="La ruleta estaba trabada en tu número lol")
        else:
            db.remove_money(str(ctx.author.id), amount, "wallet")
            embed.color = discord.Color.red()
            embed.add_field(name="❌ Perdiste", value=f"${amount:,}", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name="scratch", aliases=["rasca"])
    async def scratch(self, ctx, amount: int):
        """
        Rasca y gana
        
        Compra un boleto y rasca para ver si ganaste.
        3 símbolos iguales = premio!
        
        Multiplicadores:
        - 3x 💎: 20x
        - 3x 7️⃣: 10x
        - 3x 🍀: 5x
        - 3x ⭐: 3x
        """
        if amount <= 0:
            await ctx.send("❌ La cantidad debe ser mayor que 0")
            return
        
        user_data = db.get_user(str(ctx.author.id))
        if user_data.get('wallet', 0) < amount:
            await ctx.send(f"❌ No tienes suficiente dinero. Tu wallet: ${user_data.get('wallet', 0):,}")
            return
        
        bucket = self.scratch._buckets.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            await ctx.send(f"⏳ Este comando está en cooldown. Intenta de nuevo en {retry_after:.1f}s")
            return
        
        symbols = ["💎", "7️⃣", "🍀", "⭐", "❌", "❌", "❌", "❌", "❌", "💔"]  # 60% de perder
        
        golden = random.random() < 0.01
        if golden:
            # garantiza premio
            prize_symbol = random.choice(["💎", "7️⃣", "🍀", "⭐"])
            s1 = s2 = s3 = prize_symbol
        else:
            s1 = random.choice(symbols)
            s2 = random.choice(symbols)
            s3 = random.choice(symbols)
        
        embed = discord.Embed(
            title="🎫 Rasca y Gana",
            description=f"║ {s1} ║ {s2} ║ {s3} ║",
            color=discord.Color.gold()
        )
        
        # Verificar premio
        multiplier = 0
        if s1 == s2 == s3:
            if s1 == "💎":
                multiplier = 20
            elif s1 == "7️⃣":
                multiplier = 10
            elif s1 == "🍀":
                multiplier = 5
            elif s1 == "⭐":
                multiplier = 3
        
        if multiplier > 0:
            winnings = amount * multiplier
            db.add_money(str(ctx.author.id), winnings - amount, "wallet")
            
            embed.color = discord.Color.green()
            embed.add_field(name="🎉 Premio", value=f"${winnings:,} ({multiplier}x)", inline=False)
            
            if golden:
                embed.set_footer(text="Boleto dorado! Que crack")
        else:
            db.remove_money(str(ctx.author.id), amount, "wallet")
            embed.color = discord.Color.red()
            embed.add_field(name="😢 Sin premio", value=f"Perdiste ${amount:,}", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name="crash")
    @commands.cooldown(1, 50, commands.BucketType.user)
    async def crash(self, ctx, amount: int, target: float):
        """
        Juego de crash
        
        Elige un multiplicador objetivo. Si el crash es mayor, ganas!
        Mayor riesgo = mayor recompensa
        
        Uso: .crash <cantidad> <multiplicador>
        Ejemplo: .crash 100 2.5
        """
        if amount <= 0:
            await ctx.send("❌ La cantidad debe ser mayor que 0")
            return
        
        if target < 1.1 or target > 10:
            await ctx.send("❌ El multiplicador debe estar entre 1.1x y 10x")
            return
        
        user_data = db.get_user(str(ctx.author.id))
        if user_data.get('wallet', 0) < amount:
            await ctx.send(f"❌ No tienes suficiente dinero. Tu wallet: ${user_data.get('wallet', 0):,}")
            return
        
        bucket = self.crash._buckets.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            await ctx.send(f"⏳ Este comando está en cooldown. Intenta de nuevo en {retry_after:.1f}s")
            return
        
        # evento: crash manipulado (3% chance) - siempre llegas
        manipulated = random.random() < 0.03
        
        # Generar crash point con distribución más realista
        if manipulated:
            crash_point = round(target + random.uniform(0.1, 1.0), 2)
        else:
            # la mayoría de crashes son bajos
            rand = random.random()
            if rand < 0.4:
                crash_point = round(random.uniform(1.0, 2.0), 2)
            elif rand < 0.7:
                crash_point = round(random.uniform(2.0, 4.0), 2)
            elif rand < 0.9:
                crash_point = round(random.uniform(4.0, 7.0), 2)
            else:
                crash_point = round(random.uniform(7.0, 15.0), 2)
        
        embed = discord.Embed(title="💥 Crash", color=discord.Color.orange())
        embed.add_field(name="Tu objetivo", value=f"{target}x", inline=True)
        embed.add_field(name="Crash en", value=f"{crash_point}x", inline=True)
        
        if crash_point >= target:
            winnings = int(amount * target)
            db.add_money(str(ctx.author.id), winnings - amount, "wallet")
            
            embed.color = discord.Color.green()
            embed.add_field(name="✅ Ganaste!", value=f"${winnings:,}", inline=False)
            
            if manipulated:
                embed.set_footer(text="El sistema te dio una ayudita")
        else:
            db.remove_money(str(ctx.author.id), amount, "wallet")
            embed.color = discord.Color.red()
            embed.add_field(name="💥 Crash!", value=f"Perdiste ${amount:,}", inline=False)
            embed.set_footer(text="F")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Gambling(bot))