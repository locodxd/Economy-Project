"""
Comandos relacionados con el juego de azar, super facil de ampliar en los proximos devlogs
porfavor tratar de no tocar el sistema de tenor que es un quilombo, está corriendo
bien quien sabe como 
"""

from discord.ext import commands
import discord
from discord import ui
import random
import sys
from pathlib import Path
try:
    from core.database import db
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.exception("Error importing core.database, attempting sys.path fixup")
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from core.database import db
from utils.card_utils import create_deck, draw_card, hand_value, format_hand
from utils.event_system import maybe_trigger_event
from utils.tenor_core import get_tenor

class Gambling(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    # Helper functions porque copypastear codigo es de junior dev
    def _tiene_plata(self, user_id, cantidad):
        saldo = db.get_user(str(user_id)).get('wallet', 0)
        return saldo >= cantidad, saldo
    
    def _calcular_premio_slots(self, s1, s2, s3):
        if s1 == "👑" and s2 == "👑" and s3 == "👑":
            return 50, True  
        elif s1 == s2 == s3:
            multi = 10 if s1 == "💎" else 7
            return multi, False
        elif s1 == s2 or s2 == s3 or s1 == s3:
            return 3, False
        return 0, False
    
    async def _agregar_gif(self, embed, categoria):
        try:
            gif_url = await get_tenor().get_gif(categoria)
            if gif_url:
                embed.set_image(url=gif_url)
        except Exception as e:
            # Tenor se cae cada 2x3, mejor no romper el comando por eso
            print(f"[GIF FAIL] {categoria}: {e}")

    @commands.command(name="coinflip", aliases=["cf", "moneda"])
    async def coinflip(self, ctx, apuesta: int, eleccion: str):
        eleccion = eleccion.lower()
        if eleccion not in ["cara", "cruz", "heads", "tails"]:
            return await ctx.send("man elige cara o cruz, no es tan dificil")
        if apuesta <= 0:
            return await ctx.send("no podes apostar 0 pesos amigo")
        
        tiene_guita, saldo = self._tiene_plata(ctx.author.id, apuesta)
        if not tiene_guita:
            return await ctx.send(f"estas re pobre loco, tenes ${saldo:,} nomas")
        evento = await maybe_trigger_event(ctx, 0.08, ["Huir", "Pelear", "Llamar a la policia"])
        if evento:
            if evento == "Huir":
                if random.random() < 0.6:
                    await ctx.send("zafaste por suerte, sigue el juego")
                else:
                    perdida = int(apuesta * random.uniform(0.4, 0.9))
                    db.remove_money(str(ctx.author.id), perdida, "wallet")
                    return await ctx.send(f"te chorearon ${perdida:,} mientras corrias jaja")
            elif evento == "Pelear":
                if random.random() < 0.45:
                    extra = int(apuesta * 0.3)
                    db.add_money(str(ctx.author.id), extra, "wallet")
                    await ctx.send(f"re capo, ganaste la pelea y ${extra:,}")
                else:
                    perdida = int(apuesta * random.uniform(0.3, 0.8))
                    db.remove_money(str(ctx.author.id), perdida, "wallet")
                    return await ctx.send(f"te cagaron a palos y te robaron ${perdida:,} F")
            else:  # policia
                if random.random() < 0.7:
                    compensacion = int(apuesta * 0.2)
                    db.add_money(str(ctx.author.id), compensacion, "wallet")
                    return await ctx.send(f"la policia llego y te dieron ${compensacion:,} de compensacion")
                else:
                    perdida = int(apuesta * random.uniform(0.2, 0.6))
                    db.remove_money(str(ctx.author.id), perdida, "wallet")
                    return await ctx.send(f"la policia no llego (re argento) perdiste ${perdida:,}")
        
        if random.random() < 0.01:
            premio_loco = int(apuesta * 3)
            db.add_money(str(ctx.author.id), premio_loco, "wallet")
            return await ctx.send(f"🪙 LA MONEDA CAYO DE CANTO WTF!! +${premio_loco:,} no lo puedo creer")
        
        # a veces la moneda esta trucada sin que te des cuenta xd igual medio dificil trucar una moneda
        moneda_trucada = random.random() < 0.03
        resultado = "cara" if eleccion in ["cara", "heads"] else "cruz" if moneda_trucada else random.choice(["cara", "cruz"])
        
        ganaste = (eleccion in ["cara", "heads"] and resultado == "cara") or (eleccion in ["cruz", "tails"] and resultado == "cruz")
        
        if ganaste:
            plata = apuesta
            if random.random() < 0.10:
                extra = int(apuesta * 0.5)
                plata += extra
            
            db.add_money(str(ctx.author.id), plata, "wallet")
            
            embed = discord.Embed(title="💰 GANASTE LOCO", color=0x2ecc71)
            embed.description = f"salio **{resultado}**, apostaste ${apuesta:,} y ganaste ${plata:,}"
            
            if moneda_trucada:
                embed.set_footer(text="(la moneda estaba re trucada pero bueno)")
            elif plata > apuesta:
                embed.set_footer(text=f"te dieron ${plata - apuesta:,} de bonus")
        else:
            # a veces alguien te salva y te devuelve algo
            if random.random() < 0.05:
                devolucion = int(apuesta * 0.6)
                db.remove_money(str(ctx.author.id), apuesta - devolucion, "wallet")
                return await ctx.send(f"perdiste pero alguien te dio ${devolucion:,} de lastima")
            
            db.remove_money(str(ctx.author.id), apuesta, "wallet")
            embed = discord.Embed(title="💸 F", color=0xe74c3c)
            embed.description = f"salio **{resultado}**, perdiste ${apuesta:,}"
        
        embed.set_footer(text=f"{ctx.author.name} eligió {eleccion}")
        await self._agregar_gif(embed, 'win' if ganaste else 'lose')
        await ctx.send(embed=embed)
    @commands.command(name="dice", aliases=["dados"])
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def dice(self, ctx, plata: int):
        user_data = db.get_user(str(ctx.author.id))
        saldo_actual = user_data.get('wallet', 0)
        
        if saldo_actual < plata:
            return await ctx.send(f"no tenes plata wacho (${saldo_actual:,})")
        if plata <= 0:
            return await ctx.send("anda a apostar algo real")
        

        dados_dorados = random.random() < 0.01
        d1, d2 = random.randint(1, 6), random.randint(1, 6)
        if random.random() < 0.04 and not dados_dorados:
            d1 = 6
        
        suma = d1 + d2
        multi = 0
        
        # calculo de multiplicador (esto lo hice medio apurado)
        if d1 == 6 and d2 == 6:
            multi = 6 if dados_dorados else 4
        elif suma >= 11:
            multi = 4 if dados_dorados else 2.5
        elif suma >= 10:
            multi = 3 if dados_dorados else 1.8 
        
        if multi > 0:
            premio = int(plata * multi)
            db.add_money(str(ctx.author.id), premio - plata, "wallet")
            
            embed = discord.Embed(title="🎲 GANASTE PAA", color=0x2ecc71)
            embed.description = f"Sacaste **{d1}** y **{d2}** (total: {suma})\nGanaste ${premio:,} con {multi}x"
            
            if dados_dorados:
                embed.set_footer(text="DADOS DORADOS WTF")
            elif d1 == 6 and d2 != 6:
                embed.set_footer(text="encontraste un dado cargado jaja")
            
            await self._agregar_gif(embed, 'dice')
        else:
            if random.random() < 0.08:
                devuelto = int(plata * 0.4)
                db.remove_money(str(ctx.author.id), plata - devuelto, "wallet")
                return await ctx.send(f"sacaste {d1} y {d2}, re poco. te dan ${devuelto:,} de lastima")
            
            db.remove_money(str(ctx.author.id), plata, "wallet")
            embed = discord.Embed(title="🎲 perdiste bro", color=0xe74c3c)
            embed.description = f"Sacaste {d1} y {d2} (suma: {suma})\nPerdiste ${plata:,}"
            embed.set_footer(text="necesitas 10+ para ganar algo")
            await self._agregar_gif(embed, 'lose')
        
        await ctx.send(embed=embed)

    @commands.command(name="slots", aliases=["tragamonedas"])
    async def slots(self, ctx, apuesta: int):
        tiene_guita, balance = self._tiene_plata(ctx.author.id, apuesta)
        if apuesta <= 0:
            return await ctx.send("apostá algo real viejo")
        if not tiene_guita:
            return await ctx.send(f"no tenes ni un peso (saldo: ${balance:,})")
        evento = await maybe_trigger_event(ctx, 0.07, ["Huir", "Pelear", "Llamar a la policia"])
        if evento == "Huir":
            if random.random() > 0.6:
                perdida = int(apuesta * random.uniform(0.4, 0.9))
                db.remove_money(str(ctx.author.id), perdida, "wallet")
                return await ctx.send(f"te asaltaron en el casino y te robaron ${perdida:,}")
            await ctx.send("escapaste, sigue la tirada")
        elif evento == "Pelear":
            if random.random() < 0.45:
                db.add_money(str(ctx.author.id), int(apuesta * 0.25), "wallet")
                await ctx.send("ganaste la pelea, sigue la tirada")
            else:
                perdida = int(apuesta * random.uniform(0.3, 0.8))
                db.remove_money(str(ctx.author.id), perdida, "wallet")
                return await ctx.send(f"te re cagaron a palos, perdiste ${perdida:,}")
        elif evento:
            if random.random() < 0.7:
                bonus = int(apuesta * 0.5)
                db.add_money(str(ctx.author.id), bonus, "wallet")
                return await ctx.send(f"la policia te dio ${bonus:,} de compensacion")
            else:
                perdida = int(apuesta * random.uniform(0.2, 0.6))
                db.remove_money(str(ctx.author.id), perdida, "wallet")
                return await ctx.send(f"la policia no llego (re LATAM esto) -${perdida:,}")
        # maquina rota a veces escupe plata, ojala esto me pase a mi :V
        if random.random() < 0.02:
            regalo = int(apuesta * 1.5)
            db.add_money(str(ctx.author.id), regalo, "wallet")
            return await ctx.send(f"🎰 la maquina se trabo y te dio ${regalo:,} gratis JAJA")
        
        simbolos = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣"]
        
        if random.random() < 0.005:
            simbolos.append("👑")
        
        s1, s2, s3 = random.choice(simbolos), random.choice(simbolos), random.choice(simbolos)
        multi, es_jackpot = self._calcular_premio_slots(s1, s2, s3)
        
        embed = discord.Embed(color=0xf39c12)
        embed.description = f"════════\n {s1}  {s2}  {s3} \n════════"
        
        if es_jackpot:
            plata_ganada = apuesta * multi
            db.add_money(str(ctx.author.id), plata_ganada - apuesta, "wallet")
            embed.title = "👑 JACKPOT SECRETO WTF"
            embed.color = 0xffd700
            embed.add_field(name="Premio", value=f"${plata_ganada:,} ({multi}x)")
            embed.set_footer(text="no lo puedo creer amigo")
            await self._agregar_gif(embed, 'jackpot')
        elif multi > 0:
            plata_ganada = apuesta * multi
            # bonus random si tenes racha
            if random.random() < 0.1 and multi >= 7:
                extra = int(plata_ganada * 0.5)
                plata_ganada += extra
                embed.set_footer(text=f"RACHA +${extra:,}")
            
            db.add_money(str(ctx.author.id), plata_ganada - apuesta, "wallet")
            embed.title = "🎰 GANASTE"
            embed.color = 0x2ecc71
            embed.add_field(name="Ganancia", value=f"${plata_ganada:,} ({multi}x)")
            if not embed.footer:
                embed.set_footer(text="bien ahi")
            await self._agregar_gif(embed, 'win')
        else:
            # a veces te dan algo de vuelta si estuviste cerca
            casi = random.random() < 0.15
            if casi:
                devuelto = int(apuesta * 0.3)
                db.remove_money(str(ctx.author.id), apuesta - devuelto, "wallet")
                embed.title = "🎰 casi"
                embed.color = 0xe67e22
                embed.add_field(name="Perdida", value=f"${apuesta - devuelto:,}")
                embed.set_footer(text=f"estuviste cerca, te dan ${devuelto:,} de consolacion")
            else:
                db.remove_money(str(ctx.author.id), apuesta, "wallet")
                embed.title = "🎰 F en el chat"
                embed.color = 0xe74c3c
                embed.add_field(name="Perdiste", value=f"${apuesta:,}")
                embed.set_footer(text="mejor suerte la proxima bro")
        
        await ctx.send(embed=embed)

    @commands.command(name="blackjack", aliases=["bj", "21"])
    @commands.cooldown(1, 50, commands.BucketType.user)
    async def blackjack(self, ctx, apuesta_arg: str):
        """21 contra el dealer, no te pases"""
        # a veces el dealer hace trampa, arreglar eso
        
        saldo = db.get_user(str(ctx.author.id)).get('wallet', 0)
        
        apuesta = saldo if apuesta_arg.lower() == "all" else int(apuesta_arg) if apuesta_arg.isdigit() else 0
        
        if apuesta <= 0:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send("usa .bj <cantidad> o .bj all")
        if saldo < apuesta:
            ctx.command.reset_cooldown(ctx)
            return await ctx.send(f"no tenes ${apuesta:,}, solo tenes ${saldo:,}")
        
        # eventos raros pre-juego
        evento_random = random.random()
        if evento_random < 0.015:
            db.remove_money(str(ctx.author.id), apuesta, "wallet")
            return await ctx.send(f"el dealer se fugo con tu plata de ${apuesta:,} jajaja")
        elif evento_random < 0.03:
            compensacion = int(apuesta * 0.5)
            db.add_money(str(ctx.author.id), apuesta + compensacion, "wallet")
            return await ctx.send(f"habia cartas marcadas, te devuelven todo + ${compensacion:,}")

        class BlackjackView(ui.View):
            def __init__(self, ctx, mazo, cartas_player, cartas_dealer, plata):
                super().__init__(timeout=120)
                self.ctx = ctx
                self.deck = mazo
                self.player = cartas_player
                self.dealer = cartas_dealer
                self.bet = plata
                self.message = None

            async def end(self, interaction, embed):
                # desactivar botones cuando termina
                for item in self.children:
                    item.disabled = True
                await interaction.response.edit_message(embed=embed, view=self)

            @ui.button(label="Hit", style=discord.ButtonStyle.primary)
            async def hit(self, interaction: discord.Interaction, button: ui.Button):
                if interaction.user.id != self.ctx.author.id:
                    return await interaction.response.send_message("no es tu juego bro", ephemeral=True)

                # eventos raros mid-game
                if random.random() < 0.02:
                    db.remove_money(str(self.ctx.author.id), self.bet, "wallet")
                    embed = discord.Embed(title="♟️ mazo trucado", color=0xe74c3c)
                    embed.description = f"el mazo estaba marcado, perdiste ${self.bet:,} auto"
                    return await self.end(interaction, embed)
                elif random.random() < 0.05:
                    propina = int(self.bet * 0.2)
                    db.add_money(str(self.ctx.author.id), propina, "wallet")

                nueva_carta, self.deck = draw_card(self.deck, 1)
                self.player.extend(nueva_carta)
                valor_player = hand_value(self.player)

                embed = discord.Embed(
                    title="Blackjack en vivo",
                    description=f"Apuesta: ${self.bet:,}",
                    color=0x3498db
                )
                embed.add_field(
                    name="Tus cartas",
                    value=f"{format_hand(self.player)} = **{valor_player}**",
                    inline=False
                )
                embed.add_field(
                    name="Dealer",
                    value=f"{format_hand(self.dealer)} = **{hand_value(self.dealer)}**",
                    inline=False
                )

                if valor_player > 21:
                    db.remove_money(str(self.ctx.author.id), self.bet, "wallet")
                    embed.color = 0xe74c3c
                    embed.title = "Te pasaste papá"
                    embed.description = f"**Perdiste:** ${self.bet:,}\n\nTus cartas sumaban {valor_player}, te fuiste al carajo"
                    try:
                        gif = await get_tenor().get_gif('lose')
                        if gif:
                            embed.set_image(url=gif)
                    except Exception as e:
                        print(f"[GIF FAIL] lose: {e}")
                    return await self.end(interaction, embed)

                if valor_player == 21:
                    return await self.stand.callback(self, interaction, button)

                await interaction.response.edit_message(embed=embed, view=self)

            @ui.button(label="Stand", style=discord.ButtonStyle.secondary)
            async def stand(self, interaction: discord.Interaction, button: ui.Button):
                if interaction.user.id != self.ctx.author.id:
                    return await interaction.response.send_message("este no es tu juego", ephemeral=True)
                
                trampa = random.random()
                nota = None
                if trampa < 0.03:
                    self.dealer = ['K♠', 'A♠']
                    nota = "el casino te hizo trampa jaja"
                elif trampa < 0.06:
                    self.dealer = ['K♠', 'K♣', 'Q♣'] 
                    nota = "el dealer se confundio y se paso"

                if not nota:
                    while hand_value(self.dealer) < 17:
                        carta, self.deck = draw_card(self.deck, 1)
                        self.dealer.extend(carta)

                val_player = hand_value(self.player)
                val_dealer = hand_value(self.dealer)

                embed = discord.Embed(
                    title="Resultado Final",
                    color=0xf39c12
                )
                embed.add_field(
                    name="Tus cartas",
                    value=f"{format_hand(self.player)}\n**Total: {val_player}**",
                    inline=True
                )
                embed.add_field(
                    name="Dealer",
                    value=f"{format_hand(self.dealer)}\n**Total: {val_dealer}**",
                    inline=True
                )
                if nota:
                    embed.add_field(name="Nota", value=nota, inline=False)

                if val_dealer > 21 or val_player > val_dealer:
                    premio = self.bet * 2
                    db.add_money(str(self.ctx.author.id), premio - self.bet, "wallet")
                    embed.color = 0x2ecc71
                    embed.title = "GANASTE LOCOO"
                    embed.description = f"**Ganancia:** +${self.bet:,}\n**Total recibido:** ${premio:,}"
                    try:
                        gif = await get_tenor().get_gif('victory')
                        if gif:
                            embed.set_image(url=gif)
                    except Exception as e:
                        print(f"[GIF FAIL] victory: {e}")
                elif val_player == val_dealer:
                    if random.random() < 0.8:
                        extra = int(self.bet * 0.25)
                        db.add_money(str(self.ctx.author.id), extra, "wallet")
                        embed.color = 0x3498db
                        embed.title = "Empate (con bonus)"
                        embed.description = f"Recuperas tu apuesta + ${extra:,} de bonus porque si"
                    else:
                        embed.color = 0x3498db
                        embed.title = "Empate"
                        embed.description = f"Recuperas tu apuesta de ${self.bet:,}"
                else:
                    db.remove_money(str(self.ctx.author.id), self.bet, "wallet")
                    embed.color = 0xe74c3c
                    embed.title = "Perdiste amigo"
                    embed.description = f"**Perdiste:** ${self.bet:,}\n\nEl dealer te gano con {val_dealer} vs tu {val_player}"
                    try:
                        gif = await get_tenor().get_gif('lose')
                        if gif:
                            embed.set_image(url=gif)
                    except Exception as e:
                        print(f"[GIF FAIL] lose: {e}")

                await self.end(interaction, embed)

        mazo = create_deck()
        p1, mazo = draw_card(mazo, 1)
        p2, mazo = draw_card(mazo, 1)
        d1, mazo = draw_card(mazo, 1)
        d2, mazo = draw_card(mazo, 1)

        cartas_player = p1 + p2
        cartas_dealer = d1 + d2

        embed = discord.Embed(title="♟️ 21", color=0x3498db)
        embed.add_field(name="Tus cartas", value=f"{format_hand(cartas_player)} = {hand_value(cartas_player)}", inline=False)
        embed.add_field(name="Dealer", value=f"{format_hand([cartas_dealer[0], '??'])}", inline=False)
        embed.set_footer(text="Hit para pedir carta, Stand para plantarte")

        view = BlackjackView(ctx, mazo, cartas_player, cartas_dealer, apuesta)
        msg = await ctx.send(embed=embed, view=view)
        view.message = msg

    @commands.command(name="roulette", aliases=["ruleta"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def roulette(self, ctx, plata: int, apuesta: str):
        apuesta = apuesta.lower()
        
        saldo = db.get_user(str(ctx.author.id)).get('wallet', 0)
        if plata > saldo:
            return await ctx.send(f"no tenes ${plata:,}, solo ${saldo:,}")
        if plata <= 0:
            return await ctx.send("aposta algo real")
        
        trabada = random.random() < 0.02 and apuesta.isdigit()
        numero = int(apuesta) if trabada else random.randint(0, 36)
        
        rojos = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        color = "rojo" if numero in rojos else "negro" if numero != 0 else "verde"
        es_par = numero % 2 == 0 and numero != 0
        
        ganaste = False
        multi = 0
        
        if apuesta.isdigit() and 0 <= int(apuesta) <= 36 and int(apuesta) == numero:
            ganaste, multi = True, 35
        elif apuesta in ["rojo", "red"] and color == "rojo":
            ganaste, multi = True, 2
        elif apuesta in ["negro", "black"] and color == "negro":
            ganaste, multi = True, 2
        elif apuesta in ["par", "even"] and es_par:
            ganaste, multi = True, 2
        elif apuesta in ["impar", "odd"] and not es_par and numero != 0:
            ganaste, multi = True, 2
        
        embed = discord.Embed(color=0xf39c12)
        embed.description = f"salio el **{numero}** ({color})"
        
        if ganaste:
            premio = plata * multi
            db.add_money(str(ctx.author.id), premio - plata, "wallet")
            embed.title = "🎰 GANASTE"
            embed.add_field(name="Premio", value=f"${premio:,} ({multi}x)")
            embed.color = 0x2ecc71
            if trabada:
                embed.set_footer(text="la ruleta estaba trabada en tu numero lol")
        else:
            db.remove_money(str(ctx.author.id), plata, "wallet")
            embed.title = "🎰 F"
            embed.add_field(name="Perdiste", value=f"${plata:,}")
            embed.color = 0xe74c3c
        
        await self._agregar_gif(embed, 'slots' if ganaste else 'lose')
        await ctx.send(embed=embed)

    @commands.command(name="scratch", aliases=["rasca"])
    async def scratch(self, ctx, plata: int):
        """Rasca y gana, literal como los de la calle"""
        tiene_guita, saldo = self._tiene_plata(ctx.author.id, plata)
        if not tiene_guita:
            return await ctx.send(f"no tenes guita (${saldo:,})")
        if plata <= 0:
            return await ctx.send("compra un raspadita de verdad")
        
        simbolos = ["💎", "7️⃣", "🍀", "⭐", "❌", "❌", "❌", "❌", "❌", "💔"]
        
        dorado = random.random() < 0.01
        if dorado:
            simbolo_ganador = random.choice(["💎", "7️⃣", "🍀", "⭐"])
            s1 = s2 = s3 = simbolo_ganador
        else:
            s1, s2, s3 = random.choice(simbolos), random.choice(simbolos), random.choice(simbolos)
        
        embed = discord.Embed(color=0xf39c12)
        embed.description = f" {s1}  {s2}  {s3} "
        
        multi = 0
        if s1 == s2 == s3:
            if s1 == "💎": multi = 20
            elif s1 == "7️⃣": multi = 10
            elif s1 == "🍀": multi = 5
            elif s1 == "⭐": multi = 3
        
        if multi > 0:
            premio = plata * multi
            db.add_money(str(ctx.author.id), premio - plata, "wallet")
            embed.title = "🎫 GANASTE"
            embed.add_field(name="Premio", value=f"${premio:,} ({multi}x)")
            embed.color = 0x2ecc71
            if dorado:
                embed.set_footer(text="TICKET DORADO WTF")
        else:
            db.remove_money(str(ctx.author.id), plata, "wallet")
            embed.title = "🎫 sin premio"
            embed.add_field(name="F", value=f"perdiste ${plata:,}")
            embed.color = 0xe74c3c
        
        await ctx.send(embed=embed)

    @commands.command(name="crash")
    @commands.cooldown(1, 50, commands.BucketType.user)
    async def crash(self, ctx, plata: int, objetivo: float):
        
        if objetivo < 1.1 or objetivo > 10:
            return await ctx.send("el multi debe estar entre 1.1x y 10x")
        
        tiene_guita, saldo = self._tiene_plata(ctx.author.id, plata)
        if not tiene_guita:
            return await ctx.send(f"no tenes ${plata:,} (saldo: ${saldo:,})")
        if plata <= 0:
            return await ctx.send("aposta plata de verdad")
        
        ayuda = random.random() < 0.03
        
        if ayuda:
            punto_crash = round(objetivo + random.uniform(0.1, 1.0), 2)
        else:
            rand = random.random()
            if rand < 0.4:
                punto_crash = round(random.uniform(1.0, 2.0), 2)
            elif rand < 0.7:
                punto_crash = round(random.uniform(2.0, 4.0), 2)
            elif rand < 0.9:
                punto_crash = round(random.uniform(4.0, 7.0), 2)
            else:
                punto_crash = round(random.uniform(7.0, 15.0), 2)
        
        embed = discord.Embed(color=0xe67e22)
        embed.description = f"tu objetivo: {objetivo}x\ncrasheo en: **{punto_crash}x**"
        
        if punto_crash >= objetivo:
            premio = int(plata * objetivo)
            db.add_money(str(ctx.author.id), premio - plata, "wallet")
            embed.title = "🚨 GANASTE"
            embed.add_field(name="Premio", value=f"${premio:,}")
            embed.color = 0x2ecc71
            if ayuda:
                embed.set_footer(text="el sistema te dio una mano")
            await self._agregar_gif(embed, 'jackpot')
        else:
            db.remove_money(str(ctx.author.id), plata, "wallet")
            embed.title = "💥 CRASH"
            embed.add_field(name="F", value=f"perdiste ${plata:,}")
            embed.color = 0xe74c3c
            embed.set_footer(text="F en el chat")
            await self._agregar_gif(embed, 'lose')
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Gambling(bot))