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
