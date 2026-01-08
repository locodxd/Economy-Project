import pytest
from src.bot.main import bot

@pytest.mark.asyncio
async def test_daily_command():
    # Simulate a user invoking the daily command
    ctx = await bot.get_context(message)  # Replace 'message' with a mock message object
    await bot.get_cog('EconomyBasic').daily(ctx)
    
    # Check if the user received a response
    assert ctx.send.called
    response = ctx.send.call_args[0][0]
    assert "recompensa diaria" in response.description.lower()

@pytest.mark.asyncio
async def test_work_command():
    ctx = await bot.get_context(message)  # Replace 'message' with a mock message object
    await bot.get_cog('EconomyBasic').work(ctx)
    
    assert ctx.send.called
    response = ctx.send.call_args[0][0]
    assert "trabajo" in response.description.lower()

@pytest.mark.asyncio
async def test_transfer_command():
    ctx = await bot.get_context(message)  # Replace 'message' with a mock message object
    await bot.get_cog('EconomyBasic').transfer(ctx, member, amount)  # Replace 'member' and 'amount' with mock values
    
    assert ctx.send.called
    response = ctx.send.call_args[0][0]
    assert "transferido" in response.description.lower()

@pytest.mark.asyncio
async def test_weekly_command():
    ctx = await bot.get_context(message)  # Replace 'message' with a mock message object
    await bot.get_cog('EconomyBasic').weekly(ctx)
    
    assert ctx.send.called
    response = ctx.send.call_args[0][0]
    assert "recompensa semanal" in response.description.lower()

@pytest.mark.asyncio
async def test_beg_command():
    ctx = await bot.get_context(message)  # Replace 'message' with a mock message object
    await bot.get_cog('EconomyBasic').beg(ctx)
    
    assert ctx.send.called
    response = ctx.send.call_args[0][0]
    assert "pedir dinero" in response.description.lower()