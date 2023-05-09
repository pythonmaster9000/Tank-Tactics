import discord
from game import game, start_game, discord_methods
import json


class Controller(discord.ui.View):
    def __init__(self, server_id, player_id, game_id, discord_client):
        super().__init__(timeout=None)
        self.discord_client = discord_client
        self.player_id = player_id
        self.game_id = game_id
        self.server_id = server_id
        self.instance = game.GameClient(self.server_id, self.player_id)
        self.menu_options = []
        self.discord_methods = discord_methods.DiscordGameMethods(self.discord_client, self.instance)
        for enemy in self.instance.list_all_enemies():
            # get enemy coords later when selected
            self.menu_options.append(discord.SelectOption(label=enemy))
        self.add_item(AttackDropdown(self.menu_options, self.discord_methods))
        self.menu_options2 = []
        for enemy in self.instance.list_all_enemies():
            # get enemy coords later when selected
            self.menu_options2.append(discord.SelectOption(label=enemy))
        self.add_item(GiveApDropdown(self.menu_options2, self.discord_methods))

    @discord.ui.button(label="<-", style=discord.ButtonStyle.grey, custom_id='left')
    async def menu1(self, interaction: discord.interactions.Interaction, button):
        if str(interaction.user.id) != self.player_id or self.instance.invalid() or self.instance.game_over():
            print(str(interaction.user.id), self.player_id, self.instance.invalid(), self.instance.game_over() )
            print('no!')
            return
        if await self.discord_methods.move('left'):
            await interaction.response.send_message(f"{self.player_id} Has gone left", delete_after=5)
        else:
            await interaction.response.send_message(f"You can't move like that buddy", delete_after=5)


        if len(self.instance.remaining_players()) == 1:
            await interaction.followup.send(f"{self.instance.remaining_players()[0]} has won!! :DD")
            await self.discord_methods.delete_channels()
            start_game.delete_game(self.game_id, self.server_id)
            with open('viewdata.json') as file:
                view_data = json.load(file)
            view_data[self.server_id] = {}
            with open("viewdata.json", "w") as outfile:
                json.dump(view_data, outfile, indent=4)

    @discord.ui.button(label="->", style=discord.ButtonStyle.grey, custom_id='right')
    async def menu2(self, interaction: discord.interactions.Interaction, button):
        if str(interaction.user.id) != self.player_id or self.instance.invalid() or self.instance.game_over():
            print('no!')
            return
        if await self.discord_methods.move('right'):
            await interaction.response.send_message(f"{self.player_id} Has gone right", delete_after=5)
        else:
            await interaction.response.send_message(f"You can't move like that buddy", delete_after=5)


        if len(self.instance.remaining_players()) == 1:
            await interaction.followup.send(f"{self.instance.remaining_players()[0]} has won!! :DD")
            await self.discord_methods.delete_channels()
            start_game.delete_game(self.game_id, self.server_id)
            with open('viewdata.json') as file:
                view_data = json.load(file)
            view_data[self.server_id] = {}
            with open("viewdata.json", "w") as outfile:
                json.dump(view_data, outfile, indent=4)

    @discord.ui.button(label="v", style=discord.ButtonStyle.grey, custom_id='down')
    async def menu3(self, interaction: discord.interactions.Interaction, button):
        if str(interaction.user.id) != self.player_id or self.instance.invalid() or self.instance.game_over():
            print('no!')
            return
        if await self.discord_methods.move('up'):
            await interaction.response.send_message(f"{self.player_id} Has gone down", delete_after=5)
        else:
            await interaction.response.send_message(f"You can't move like that buddy", delete_after=5)

        if len(self.instance.remaining_players()) == 1:
            await interaction.followup.send(f"{self.instance.remaining_players()[0]} has won!! :DD")
            await self.discord_methods.delete_channels()
            start_game.delete_game(self.game_id, self.server_id)
            with open('viewdata.json') as file:
                view_data = json.load(file)
            view_data[self.server_id] = {}
            with open("viewdata.json", "w") as outfile:
                json.dump(view_data, outfile, indent=4)

    @discord.ui.button(label="^", style=discord.ButtonStyle.grey, custom_id='up')
    async def menu4(self, interaction: discord.interactions.Interaction, button):
        if str(interaction.user.id) != self.player_id or self.instance.invalid() or self.instance.game_over():
            print('no!')
            return
        if await self.discord_methods.move('down'):
            await interaction.response.send_message(f"{self.player_id} Has gone up", delete_after=5)
        else:
            await interaction.response.send_message(f"You can't move like that buddy", delete_after=5)

        if len(self.instance.remaining_players()) == 1:
            await interaction.followup.send(f"{self.instance.remaining_players()[0]} has won!! :DD")
            await self.discord_methods.delete_channels()
            start_game.delete_game(self.game_id, self.server_id)
            with open('viewdata.json') as file:
                view_data = json.load(file)
            view_data[self.server_id] = {}
            with open("viewdata.json", "w") as outfile:
                json.dump(view_data, outfile, indent=4)


class AttackDropdown(discord.ui.Select):
    def __init__(self, options, discord_gmethods):
        self.discord_gmethods = discord_gmethods
        super().__init__(placeholder='Attack a tank!', min_values=1, max_values=1, options=options, custom_id='attacker')

    async def callback(self, interaction: discord.Interaction):
        if await self.discord_gmethods.attack(self.values[0]):
            await interaction.response.send_message(f'You try to attack {self.values[0]}', delete_after=5)
        else:
            await interaction.response.send_message(f'Invalid attack! >:(', delete_after=5)


class GiveApDropdown(discord.ui.Select):
    def __init__(self, options, discord_gmethods):
        self.discord_gmethods = discord_gmethods
        super().__init__(placeholder='Give an AP!', min_values=1, max_values=1, options=options, custom_id='giver')

    async def callback(self, interaction: discord.Interaction):
        if await self.discord_gmethods.give_ap(self.values[0]):
            await interaction.response.send_message(f'You give 1 AP to {self.values[0]}', delete_after=5)
        else:
            await interaction.response.send_message(f'You aint got AP like that!', delete_after=5)


class RecruitmentController(discord.ui.View):
    def __init__(self,discord_client, guild_id: str, max_players=20, ap_speed=12, lives=3):
        super().__init__(timeout=None)
        self.client = discord_client
        self.guild_id = guild_id
        self.max_players = max_players
        self.ap_speed = ap_speed
        self.lives = lives
        self.instance = start_game.StartGame(guild_id, max_players=self.max_players, ap_speed=self.ap_speed, lives=self.lives)

    @discord.ui.button(label="Join", style=discord.ButtonStyle.grey, custom_id='joingame')
    async def join(self, interaction: discord.interactions.Interaction, button):
        self.instance.add_player(str(interaction.user.id))
        await interaction.response.send_message("Player has joined")

    @discord.ui.button(label="Start", style=discord.ButtonStyle.grey, custom_id='startgame')
    async def start(self, interaction: discord.interactions.Interaction, button):
        print('starting game')
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
            print("PLAYER!!!!", player)
            v = Controller(str(interaction.guild.id), player, '0', self.client)
            overwrites = {
                await self.client.fetch_user(int(player)): discord.PermissionOverwrite(view_channel=True),
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False)
            }
            for role in interaction.guild.roles:
                if role.name == 'Tank Tactics Bot':
                    overwrites[role] = discord.PermissionOverwrite(view_channel=True)
                    continue
                overwrites[role] = discord.PermissionOverwrite(view_channel=False)
            sec_channel = await interaction.guild.create_text_channel('War Room', overwrites=overwrites)
            game_instance = game.GameClient(str(interaction.guild.id), player)
            msgmap = await sec_channel.send(file=game_instance.draw_map(), view=v)
            if str(interaction.guild.id) in view_data:
                view_data[str(interaction.guild.id)][str(msgmap.id)] = {
                    "player_id": player,
                    "game_id": 0,
                    "channel_id": str(sec_channel.id)
                }
            else:
                view_data[str(interaction.guild.id)] = {
                    str(msgmap.id): {
                        "player_id": player,
                        "game_id": 0,
                        "channel_id": str(sec_channel.id)
                    }
                }
        print('saving game')
        with open("viewdata.json", "w") as outfile:
            json.dump(view_data, outfile, indent=4)
        await interaction.response.send_message('started game')