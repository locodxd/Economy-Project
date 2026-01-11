from typing import List, Callable, Optional
import discord
from discord import ui

class EventView(ui.View):
    def __init__(self, ctx, choices: List[str], timeout: int = 30):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.choice: Optional[int] = None
        self.result_payload = None

        # create up to 3 numeric buttons (1,2,3)
        for idx, label in enumerate(choices[:3], start=1):
            self.add_item(_EventButton(str(idx), label))

class _EventButton(ui.Button):
    def __init__(self, number_label: str, text_label: str):
        super().__init__(label=number_label, style=discord.ButtonStyle.primary)
        self.text_label = text_label

    async def callback(self, interaction: discord.Interaction):
        view: EventView = self.view  # type: ignore
        if interaction.user.id != view.ctx.author.id:
            await interaction.response.send_message("No puedes usar este botón.", ephemeral=True)
            return
        # store selected index and label
        view.choice = int(self.label)
        view.result_payload = self.text_label
        # disable buttons
        for item in view.children:
            item.disabled = True
        await interaction.response.edit_message(content=f"Has elegido: {self.label} - {self.text_label}", view=view)
        view.stop()

async def maybe_trigger_event(ctx, chance: float, choices: List[str], timeout: int = 30):
    """If random chance triggers, send an EventView and wait for user's choice.
    Returns (selected_label or None)"""
    import random
    roll = random.random()
    if roll >= chance:
        return None

    view = EventView(ctx, choices, timeout=timeout)
    msg = await ctx.send(f"Evento aleatorio: ¿Qué haces?", view=view)
    await view.wait()
    # if timed out
    if view.choice is None:
        # disable buttons
        for item in view.children:
            item.disabled = True
        try:
            await msg.edit(content="No respondiste a tiempo.", view=view)
        except Exception:
            pass
        return None
    return view.result_payload
