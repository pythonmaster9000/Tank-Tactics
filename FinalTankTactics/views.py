import discord
from game import game, start_game, discord_methods, drawing
import json
import requests
import asyncio


class Controller(discord.ui.View):
    def __init__(self, server_id, player_id, game_id, discord_client):
        super().__init__(timeout=None)
        self.discord_client = discord_client
        self.player_id = player_id
        self.game_id = game_id
        self.server_id = server_id
        self.instance = game.GameClient(self.server_id, self.player_id)
        self.menu_options = [discord.SelectOption(label='Nothing')]
        self.discord_methods = discord_methods.DiscordGameMethods(self.discord_client, self.instance)
        for enemy in self.instance.list_all_enemies():
            self.menu_options.append(discord.SelectOption(label=enemy[1], value=enemy[0]))
        self.add_item(AttackDropdown(self.menu_options, self.discord_methods, self.instance))
        self.add_item(GiveApDropdown(self.menu_options, self.discord_methods, self.instance))
        # DISABLED TEMP
        self.add_item(AddPlayerDropdown(self.menu_options, self.discord_methods, self.instance, self.discord_client))

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.blurple, custom_id='left')
    async def menu1(self, interaction: discord.interactions.Interaction, button):
        await interaction.response.defer()
        if str(interaction.user.id) != self.player_id or self.instance.invalid() or self.instance.game_over():
            return
        if await self.discord_methods.move('left'):
            await interaction.message.edit(content='You moved left')
            #await interaction.response.defer()
        else:
            await interaction.message.edit(content="You can't move like that buddy!")
            #await interaction.response.defer()

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.blurple, custom_id='right')
    async def menu2(self, interaction: discord.interactions.Interaction, button):
        await interaction.response.defer()
        if str(interaction.user.id) != self.player_id or self.instance.invalid() or self.instance.game_over():
            return
        if await self.discord_methods.move('right'):
            await interaction.message.edit(content='You moved right')
            #await interaction.response.defer()
        else:
            await interaction.message.edit(content="You can't move like that buddy!")
            #await interaction.response.defer()

    @discord.ui.button(label="🔽", style=discord.ButtonStyle.blurple, custom_id='down')
    async def menu3(self, interaction: discord.interactions.Interaction, button):
        await interaction.response.defer()
        if str(interaction.user.id) != self.player_id or self.instance.invalid() or self.instance.game_over():
            return
        if await self.discord_methods.move('up'):
            await interaction.message.edit(content='You moved down')
            #await interaction.response.defer()
        else:
            await interaction.message.edit(content="You can't move like that buddy!")
            #await interaction.response.defer()

    @discord.ui.button(label="🔼", style=discord.ButtonStyle.blurple, custom_id='up')
    async def menu4(self, interaction: discord.interactions.Interaction, button):
        await interaction.response.defer()
        if str(interaction.user.id) != self.player_id or self.instance.invalid() or self.instance.game_over():
            return
        if await self.discord_methods.move('down'):
            await interaction.message.edit(content='You moved up')
            #await interaction.response.defer()
        else:
            await interaction.message.edit(content="You can't move like that buddy!")
            #await interaction.response.defer()


    @discord.ui.button(label="Add Range", style=discord.ButtonStyle.blurple, custom_id='range')
    async def menu5(self, interaction: discord.interactions.Interaction, button):
        await interaction.response.defer()
        if str(interaction.user.id) != self.player_id or self.instance.invalid() or self.instance.game_over():
            return
        if await self.discord_methods.add_range():
            await interaction.message.edit(content='You added range')
            #await interaction.response.defer()
        else:
            await interaction.message.edit(content="You can't afford to do that pal")
            #await interaction.response.defer()



class AttackDropdown(discord.ui.Select):
    def __init__(self, options, discord_gmethods, instance):
        self.discord_gmethods = discord_gmethods
        self.instance = instance
        self.game_id = self.instance.game_id
        self.server_id = self.instance.server
        super().__init__(placeholder='Attack a tank!', min_values=1, max_values=1, options=options,
                         custom_id='attacker')

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if str(interaction.user.id) != self.instance.player_id or self.instance.invalid() or self.instance.game_over():
            return
        if self.values[0] == 'Nothing':
            #await interaction.response.defer()
            if len(self.instance.remaining_players()) == 1:
                await interaction.followup.send(f"{self.instance.remaining_players()[0]} has won!! :DD")
                await self.discord_gmethods.delete_channels()
                start_game.delete_game(self.game_id, self.server_id)
                with open('viewdata.json') as file:
                    view_data = json.load(file)
                view_data[self.server_id] = {}
                with open("viewdata.json", "w") as outfile:
                    json.dump(view_data, outfile, indent=4)
            return
        attack_victim = self.instance.get_player_by_id(self.values[0])
        if await self.discord_gmethods.attack(self.values[0]):
            await interaction.message.edit(content=f'You attacked {attack_victim}')
            #await interaction.response.defer()
        else:
            await interaction.message.edit(content=f"You don't got attack abilties like that pal")
            #await interaction.response.defer()
        if len(self.instance.remaining_players()) == 1:
            await interaction.followup.send(f"{self.instance.remaining_players()[0]} has won!! :DD")
            await self.discord_gmethods.delete_channels()
            start_game.delete_game(self.game_id, self.server_id)
            with open('viewdata.json') as file:
                view_data = json.load(file)
            view_data[self.server_id] = {}
            with open("viewdata.json", "w") as outfile:
                json.dump(view_data, outfile, indent=4)


class GiveApDropdown(discord.ui.Select):
    def __init__(self, options, discord_gmethods, instance):
        self.discord_gmethods = discord_gmethods
        self.instance = instance
        self.game_id = self.instance.game_id
        self.server_id = self.instance.server
        super().__init__(placeholder='Give an AP!', min_values=1, max_values=1, options=options, custom_id='giver')

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if str(interaction.user.id) != self.instance.player_id or self.instance.invalid() or self.instance.game_over():
            return
        if self.values[0] == 'Nothing':
            #await interaction.response.defer()
            return
        if await self.discord_gmethods.give_ap(self.values[0]):
            await interaction.message.edit(content=f'You gave AP to {self.instance.get_player_by_id(self.values[0])}')
            #await interaction.response.defer()
        else:
            await interaction.message.edit(content=f"You don't got AP like that pal")
            #await interaction.response.defer()


class AddPlayerDropdown(discord.ui.Select):
    def __init__(self, options, discord_gmethods, instance, discord_client):
        self.client = discord_client
        self.discord_gmethods = discord_gmethods
        self.instance = instance
        self.game_id = self.instance.game_id
        self.server_id = self.instance.server
        super().__init__(placeholder='Invite to War Room', min_values=1, max_values=1, options=options,
                         custom_id='inviter')

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if str(interaction.user.id) != self.instance.player_id or self.instance.invalid() or self.instance.game_over():
            return
        if self.values[0] == 'Nothing':
            #await interaction.response.defer()
            return
        guy = await self.client.fetch_user(int(self.values[0]))
        await interaction.channel.set_permissions(target=guy, overwrite=discord.PermissionOverwrite(view_channel=True))
        await interaction.followup.send(f"Hey {guy.mention}, {interaction.user.name} has added you to their War Room.")
        #await interaction.response.defer()
        # @ the person added


class RecruitmentController(discord.ui.View):
    def __init__(self, discord_client, guild_id: str, max_players=20, ap_speed=12, lives=3):
        super().__init__(timeout=None)
        self.client = discord_client
        self.guild_id = guild_id
        self.max_players = max_players
        self.ap_speed = ap_speed
        self.lives = lives
        self.instance = start_game.StartGame(guild_id, max_players=self.max_players, ap_speed=self.ap_speed,
                                             lives=self.lives)
        with open('gamedata.json') as file:
            game_data = json.load(file)
        try:
            self.player_count = set([int(player_id) for player_id in game_data[self.guild_id]['0']['players']])
        except KeyError:
            self.player_count = set()

    @discord.ui.button(label="Join", style=discord.ButtonStyle.green, custom_id='joingame')
    async def join(self, interaction: discord.interactions.Interaction, button):
        if interaction.user.id in self.player_count:
            await interaction.response.defer()
            return
        self.instance.add_player(str(interaction.user.id), interaction.user.name)
        with open(rf'pfpcache\{str(interaction.user.id)}.jpg', 'wb') as f:
            pic = requests.get(interaction.user.avatar.url).content
            f.write(pic)
        self.player_count.add(interaction.user.id)
        await interaction.response.send_message("You joined the game.", ephemeral=True)
        with open('viewdata.json') as file:
            view_data = json.load(file)
        messageid = list(view_data[self.guild_id].keys())[0]
        message = await interaction.channel.fetch_message(int(messageid))
        emb = message.embeds[0]
        emb_desc = emb.description
        updated_emb = discord.Embed(title='Press to join', description=f'{emb_desc}\n{interaction.user.name}')
        await message.edit(embed=updated_emb)
        #await message.edit(content=f'{message.content}\n{interaction.user.name}' if message.content else f'{interaction.user.name}')

    @discord.ui.button(label="Start", style=discord.ButtonStyle.danger, custom_id='startgame')
    async def start(self, interaction: discord.interactions.Interaction, button):
        if interaction.user.id != 193878633654386688:
            await interaction.response.defer()
            return
        if len(self.player_count) <= 1:
            await interaction.response.defer()
            return
        await interaction.response.send_message('started game', ephemeral=True)
        emb = discord.Embed(title="Spectate", description='Recent Events:', color=44469)
        await interaction.message.edit(embed=emb, attachments=[
            drawing.DrawMap(str(interaction.guild.id), '0').drawplayermap(spectate=True)], view=None)
        with open('gamedata.json') as file:
            game_data = json.load(file)
        if len(game_data[str(interaction.guild.id)]['0']["players"]) <= 1:
            return
        game_data[str(interaction.guild.id)]['0']["config"]["started"] = True
        with open("gamedata.json", "w") as outfile:
            json.dump(game_data, outfile, indent=4)
        with open('viewdata.json') as file:
            view_data = json.load(file)
        for player in game_data[str(interaction.guild.id)]['0']['players']:
            v = Controller(str(interaction.guild.id), player, '0', self.client)
            overwrites = {
                await self.client.fetch_user(int(player)): discord.PermissionOverwrite(view_channel=True),
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False)
            }
            for role in interaction.guild.roles:
                if role.name == 'Tank Tactics Bot':
                    # overwrites[role] = discord.PermissionOverwrite(view_channel=True, manage_permissions=True)
                    overwrites[role] = discord.PermissionOverwrite(view_channel=True)
                    continue
                overwrites[role] = discord.PermissionOverwrite(view_channel=False)
            sec_channel = await interaction.guild.create_text_channel('War Room', overwrites=overwrites)
            await sec_channel.send(embed=discord.Embed(title='Welcome', description='This is your own personal channel, you can invite other players in here to conspire and team up. Kick them out with !kickplayer @username.', color= 44469))
            game_instance = game.GameClient(str(interaction.guild.id), player)
            #msgmap = await sec_channel.send(file=game_instance.draw_map(), view=v)
            msgmap = await sec_channel.send(file=game_instance.draw_map())
            if str(interaction.guild.id) in view_data:
                view_data[str(interaction.guild.id)][str(msgmap.id)] = {
                    "player_id": player,
                    "game_id": 0,
                    "channel_id": str(sec_channel.id),
                    "footer": False
                }
            else:
                view_data[str(interaction.guild.id)] = {
                    str(msgmap.id): {
                        "player_id": player,
                        "game_id": 0,
                        "channel_id": str(sec_channel.id),
                        "footer": False
                    }
                }
            footmes = await sec_channel.send(file=game_instance.draw_footer(), view=v)
            view_data[str(interaction.guild.id)][str(footmes.id)] = {
                "player_id": player,
                "game_id": 0,
                "channel_id": str(sec_channel.id),
                "footer": True
            }
        with open("viewdata.json", "w") as outfile:
            json.dump(view_data, outfile, indent=4)
        # await interaction.response.send_message('started game', ephemeral=True)
