import discord
from discord.ext import commands, tasks
from game import drawing, game, start_game
from io import BytesIO

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)

recruitment_messages = []

@client.event
async def on_ready():
    ...

@client.event
async def on_raw_reaction_add(reaction):
    print(reaction)
    print(reaction.message_id)
    print(reaction.member.id, reaction.member)


@client.command()
async def recruit(ctx):
    # accumulate players
    #instance = start_game.StartGame(str(ctx.guild.id), max_players=10, ap_speed=24, lives=3)
    #rec = await ctx.send("Recruiting phase for game ", instance.game_id)
    rec = await ctx.send("Recruiting phase for game ")
    await rec.add_reaction('💀')

@client.command()
async def start(ctx, gameid):
    # dispense controllers perms for players
    # for testing purposes lets say a flag enables the interaction commands to be run by players and they specify which game they are in
    ...
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
    instance.attack((int(coords[0]),int(coords[1])))
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
    start_game.delete_game('1', str(ctx.guild.id))
    await ctx.send(
        file=drawing.DrawMap(server=str(ctx.guild.id), game_id='0', player_id='193878633654386688').drawplayermap())
client.run('hahaha dont reset my token :(')
