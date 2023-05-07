import discord
from discord.ext import commands, tasks
from game import drawing, game, start_game
import views
from io import BytesIO
import json
import asyncio

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)

recruitment_messages = {}
global_maps = {}
# add to this on ready aka setup hook and when creating controllers
controller_messages = {}
#call method to update all messages maps in the controller messages
# get msg object from ids and maybe need the view attached to it


@client.event
async def on_ready():
    with open('viewdata.json') as file:
        view_data = json.load(file)
    for server in view_data:
        for message_id in view_data[server]:
            client.add_view(views.Controller(server, view_data[server][message_id]["player_id"],
                                             view_data[server][message_id]["game_id"]), message_id=int(message_id))


@client.event
async def on_raw_reaction_add(reaction):
    try:
        recruitment_messages[reaction.message_id].add_player(str(reaction.member.id))
    except KeyError:
        print('random message')


async def update_map(guild, instance):
    await global_maps[guild].edit(attachments=[instance.draw_map()])


async def update_personal_map(instance, message):
    await message.edit(attachments=[instance.draw_map()])


# do not use partial message, get the channel id the message is in (save it in the DB when creating message), then get the
# channel object which you can .fetch_message() from
# AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
@client.command()
async def updateall(ctx):
    cserver = str(ctx.guild.id)
    with open('viewdata.json') as file:
        view_data = json.load(file)
    for server in view_data:
        if server == cserver:
            for message_id in view_data[server]:
                msg = client.get_partial_messageable(message_id)
                instance = game.GameClient(cserver, view_data[server][message_id]["player_id"])
                await msg.edit(attachments=[instance.draw_map()])


@client.command()
async def gmap(ctx):
    instance = game.GameClient(str(ctx.guild.id), str(ctx.message.author.id))
    if instance.invalid():
        return
    with open('viewdata.json') as file:
        view_data = json.load(file)
    v = views.Controller(str(ctx.guild.id), str(ctx.message.author.id), '0')
    msgmap = await ctx.send(file=instance.draw_map(), view=v)
    if str(ctx.guild.id) in view_data:
        view_data[str(ctx.guild.id)][str(msgmap.id)] = {
            "player_id": str(ctx.message.author.id),
            "game_id": 0
        }
    else:
        view_data[str(ctx.guild.id)] = {
            str(msgmap.id): {
                "player_id": str(ctx.message.author.id),
                "game_id": 0
            }
        }
    with open("viewdata.json", "w") as outfile:
        json.dump(view_data, outfile, indent=4)
    global_maps[str(ctx.guild.id)] = msgmap
    # await asyncio.sleep(5)
    # await msgmap.edit(attachments=[instance.draw_map()])


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


client.run('')
