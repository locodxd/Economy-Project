from discord import Embed

class EmbedDesigner:
    @staticmethod
    def create_money_embed(amount: int, action: str, fields: list = None, footer: str = None, gif_url: str = None) -> Embed:
        embed = Embed(title=f"{action}!", description=f"Has ganado ${amount:,}!", color=0x00FF00)
        if fields:
            for field in fields:
                embed.add_field(name=field["name"], value=field["value"], inline=field.get("inline", False))
        if footer:
            embed.set_footer(text=footer)
        if gif_url:
            embed.set_image(url=gif_url)
        return embed

    @staticmethod
    def create_error_embed(title: str, description: str, reason: str = None) -> Embed:
        embed = Embed(title=title, description=description, color=0xFF0000)
        if reason:
            embed.add_field(name="Razón", value=reason, inline=False)
        return embed

    @staticmethod
    def create_cooldown_embed(title: str, remaining_seconds: int, action_hint: str = None) -> Embed:
        embed = Embed(title=title, description=f"Espera {remaining_seconds} segundos para volver a usar este cmd.", color=0xFFA500)
        if action_hint:
            embed.add_field(name="Sugerencia", value=action_hint, inline=False)
        return embed

    @staticmethod
    def create_generic_embed(title: str, description: str, footer: str = None) -> Embed:
        embed = Embed(title=title, description=description, color=0x3498DB)
        if footer:
            embed.set_footer(text=footer)
        return embed