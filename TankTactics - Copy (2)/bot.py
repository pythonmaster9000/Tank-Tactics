import discord
from discord.ext import commands, tasks
from game import drawing, game, start_game
from io import BytesIO
import json
import asyncio

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)

recruitment_messages = {}
global_maps = {}

@client.event
async def on_ready():
    ...


@client.event
async def on_raw_reaction_add(reaction):
    try:
        recruitment_messages[reaction.message_id].add_player(str(reaction.member.id))
    except KeyError:
        print('random message')


async def update_map(guild, instance):
    await global_maps[guild].edit(attachments=[instance.draw_map()])


@client.command()
async def gmap(ctx):
    instance = game.GameClient(str(ctx.guild.id), str(ctx.message.author.id))
    if instance.invalid():
        return
    msgmap = await ctx.send(file=instance.draw_map())
    global_maps[str(ctx.guild.id)] = msgmap
    #await asyncio.sleep(5)
    #await msgmap.edit(attachments=[instance.draw_map()])


@client.command()
async def recruit(ctx):
    # accumulate players
    instance = start_game.StartGame(str(ctx.guild.id), max_players=10, ap_speed=24, lives=3)
    # rec = await ctx.send("Recruiting phase for game ", instance.game_id)
    rec = await ctx.send(f"Recruiting phase for game {instance.game_id}")
    await rec.add_reaction('💀')
    recruitment_messages[rec.id] = instance


@client.command()
async def start(ctx, gameid):
    with open('gamedata.json') as file:
        game_data = json.load(file)
    game_data[str(ctx.guild.id)][gameid]["config"]["started"] = True
    with open("gamedata.json", "w") as outfile:
        json.dump(game_data, outfile, indent=4)


@client.command()
async def cmap(ctx):
    instance = game.GameClient(str(ctx.guild.id), str(ctx.message.author.id))
    if instance.invalid():
        return
    await ctx.send(file=instance.draw_map())


@client.command()
async def cmove(ctx, direction):
    instance = game.GameClient(str(ctx.guild.id), str(ctx.message.author.id))
    if instance.invalid():
        return
    instance.move(direction)
    await update_map(str(ctx.guild.id), instance)


@client.command()
async def cattack(ctx, target):
    # for final controller, add method to game for all available attack targets
    instance = game.GameClient(str(ctx.guild.id), str(ctx.message.author.id))
    if instance.invalid():
        return
    coords = instance.get_coords_by_enemy(target)
    if not coords:
        return False
    instance.attack((int(coords[0]), int(coords[1])))
    await update_map(str(ctx.guild.id), instance)


@client.command()
async def testdraw(ctx):
    await ctx.send(
        file=drawing.DrawMap(server='1103112924601532466', game_id='1', player_id='193878633654386688').drawplayermap())


@client.command()
async def testmove(ctx, dir):
    instance = game.GameClient('1103112924601532466', '193878633654386688')
    if instance.invalid():
        return
    instance.move(dir)
    await ctx.invoke(client.get_command('testdraw'))


@client.command()
async def testhit(ctx, coords):
    coords = coords.split(',')
    instance = game.GameClient('1103112924601532466', '193878633654386688')
    if instance.invalid():
        return
    instance.attack((int(coords[0]), int(coords[1])))
    await ctx.invoke(client.get_command('testdraw'))


@client.command()
async def testgive(ctx):
    instance = game.GameClient('1103112924601532466', '193878633654386688')
    if instance.invalid():
        return
    instance.give_ap('12345678')
    await ctx.invoke(client.get_command('testdraw'))


@client.command()
async def teststart(ctx):
    instance = start_game.StartGame(str(ctx.guild.id), max_players=10, ap_speed=24, lives=3)
    instance.add_player('193878633654386688')
    instance2 = game.GameClient('1103112924601532466', '193878633654386688')
    if instance2.invalid():
        print('broken')
        return
    await ctx.send(
        file=drawing.DrawMap(server=str(ctx.guild.id), game_id='0', player_id='193878633654386688').drawplayermap())


@client.command()
async def testdelete(ctx):
    start_game.delete_game('0', str(ctx.guild.id))
    await ctx.send('success')
    # await ctx.send(
    #    file=drawing.DrawMap(server=str(ctx.guild.id), game_id='0', player_id='193878633654386688').drawplayermap())


client.run('MTEwMzIxNTY1MTQwNzAyMDAzMg.GF_gOg.fR-qzKmTt-IaelD7DoFGLVSzkueG5_YJxsnbe4')
