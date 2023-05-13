import discord
#from discord import app_commands
from discord.ext import commands, tasks
from game import drawing, game, start_game, discord_methods
import views
from io import BytesIO
import json
import asyncio

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)
print(client.tree)
recruitment_messages = {}
global_maps = {}
# add to this on ready aka setup hook and when creating controllers
controller_messages = {}


# call method to update all messages maps in the controller messages
# get msg object from ids and maybe need the view attached to it


def get_embed(name):
    em = discord.Embed(color=2, title=f"{name}'s War Room")
    em.set_footer(text="Tank Tactics!")
    return em


@client.event
async def on_ready():
    #await client.tree.sync()
    with open('viewdata.json') as file:
        view_data = json.load(file)
    for server in view_data:
        for message_id in view_data[server]:
            # view = views.Controller(server, view_data[server][message_id]["player_id"],
            #                                 view_data[server][message_id]["game_id"])
            try:
                client.add_view(views.Controller(server, view_data[server][message_id]["player_id"],
                                                 view_data[server][message_id]["game_id"], client),
                                message_id=int(message_id))
            except KeyError:
                pass
    dispense.start()


@tasks.loop(seconds=30)
async def dispense():
    with open('gamedata.json') as file:
        game_data = json.load(file)
    for server in game_data:
        for game_id in game_data[server]:
            if not game_data[server][game_id]["config"]['started']:
                continue
            for player in game_data[server][game_id]["players"]:
                game_data[server][game_id]["players"][player]['ap'] += 1
    with open("gamedata.json", "w") as outfile:
        json.dump(game_data, outfile, indent=4)


@client.tree.command()
async def start(interaction):
    if interaction.user.id != 193878633654386688:
        return
    view = views.RecruitmentController(client, str(interaction.guild.id))
    await interaction.response.send_message(f"Press to start/join", view=view)
    g = await interaction.original_response()
    gm = await g.fetch()
    gmes = gm.id
    with open('viewdata.json') as file:
        view_data = json.load(file)
    if str(interaction.guild.id) in view_data:
        view_data[str(interaction.guild.id)][str(gmes)] = {
            "player_id": '1103215651407020032',
            "game_id": 0,
            "channel_id": str(interaction.channel.id)
        }
    else:
        view_data[str(interaction.guild.id)] = {
            str(gmes): {
                "player_id": '1103215651407020032',
                "game_id": 0,
                "channel_id": str(interaction.channel.id)
            }
        }
    with open("viewdata.json", "w") as outfile:
        json.dump(view_data, outfile, indent=4)

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


async def updateall(cserver):
    # cserver = client.get_guild(server)
    with open('viewdata.json') as file:
        view_data = json.load(file)
    for server in view_data:
        if server == cserver:
            for message_id in view_data[server]:
                channel = await client.get_channel(int(view_data[server][message_id]["channel_id"]))
                msg = await channel.fetch_message(int(message_id))
                instance = game.GameClient(cserver, view_data[server][message_id]["player_id"])
                await msg.edit(content="get edited", attachments=[instance.draw_map()])


# AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
@client.command()
async def updateall1(ctx):
    cserver = str(ctx.guild.id)
    with open('viewdata.json') as file:
        view_data = json.load(file)
    for server in view_data:
        if server == cserver:
            for message_id in view_data[server]:
                channel = client.get_channel(int(view_data[server][message_id]["channel_id"]))
                msg = await channel.fetch_message(int(message_id))
                instance = game.GameClient(cserver, view_data[server][message_id]["player_id"])
                await msg.edit(content="get edited", attachments=[instance.draw_map()])


@client.command()
async def get(ctx):
    url = ctx.author.avatar.url
    print(url)


async def create_chan(server, user):
    overwrites = {
        await client.fetch_user(user): discord.PermissionOverwrite(view_channel=True),
        server.default_role: discord.PermissionOverwrite(view_channel=False)
    }
    for role in server.roles:
        if role.name == 'Tank Tactics Bot':
            overwrites[role] = discord.PermissionOverwrite(view_channel=True)
            continue
        overwrites[role] = discord.PermissionOverwrite(view_channel=False)
    newchan = await server.create_text_channel('secre23333', overwrites=overwrites)
    return newchan


@client.command()
async def channel(ctx):
    overwrites = {
        await client.fetch_user(832110269554884608): discord.PermissionOverwrite(view_channel=True),
        ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False)
    }
    for role in ctx.guild.roles:
        overwrites[role] = discord.PermissionOverwrite(view_channel=False)
    newchan = await ctx.guild.create_text_channel('secre23333', overwrites=overwrites)


@client.command()
async def gmap(ctx):
    instance = game.GameClient(str(ctx.guild.id), str(ctx.message.author.id))
    if instance.invalid():
        return
    with open('viewdata.json') as file:
        view_data = json.load(file)
    v = views.Controller(str(ctx.guild.id), str(ctx.message.author.id), '0', client)
    sec_channel = await create_chan(ctx.guild, ctx.message.author.id)
    msgmap = await sec_channel.send(file=instance.draw_map(), view=v)
    if str(ctx.guild.id) in view_data:
        view_data[str(ctx.guild.id)][str(msgmap.id)] = {
            "player_id": str(ctx.message.author.id),
            "game_id": 0,
            "channel_id": str(sec_channel.id)
        }
    else:
        view_data[str(ctx.guild.id)] = {
            str(msgmap.id): {
                "player_id": str(ctx.message.author.id),
                "game_id": 0,
                "channel_id": str(sec_channel.id)
            }
        }
    with open("viewdata.json", "w") as outfile:
        json.dump(view_data, outfile, indent=4)
    global_maps[str(ctx.guild.id)] = msgmap

    # await asyncio.sleep(5)
    # await msgmap.edit(attachments=[instance.draw_map()])


@client.command()
async def slashstart(ctx):
    view = views.RecruitmentController(client, str(ctx.guild.id))
    gmes = await ctx.send(f"Press to start/join", view=view)
    with open('viewdata.json') as file:
        view_data = json.load(file)
    if str(ctx.guild.id) in view_data:
        view_data[str(ctx.guild.id)][str(gmes.id)] = {
            "player_id": '1103215651407020032',
            "game_id": 0,
            "channel_id": str(ctx.channel.id)
        }
    else:
        view_data[str(ctx.guild.id)] = {
            str(gmes.id): {
                "player_id": '1103215651407020032',
                "game_id": 0,
                "channel_id": str(ctx.channel.id)
            }
        }
    with open("viewdata.json", "w") as outfile:
        json.dump(view_data, outfile, indent=4)


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
    print(len(game_data[str(ctx.guild.id)][gameid]["players"]), 'if 1 dont start')
    if len(game_data[str(ctx.guild.id)][gameid]["players"]) <= 1:
        return
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
