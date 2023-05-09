import discord
from game import game, start_game
import json


class Controller(discord.ui.View):
    def __init__(self, server_id, player_id, game_id):
        super().__init__(timeout=None)
        self.player_id = player_id
        self.game_id = game_id
        self.server_id = server_id
        self.instance = game.GameClient(self.server_id, self.player_id)
        self.menu_options = []
        for enemy in self.instance.list_all_enemies():
            # get enemy coords later when selected
            self.menu_options.append(discord.SelectOption(label=enemy))
        self.add_item(AttackDropdown(self.menu_options))
        self.menu_options2 = []
        for enemy in self.instance.list_all_enemies():
            # get enemy coords later when selected
            self.menu_options2.append(discord.SelectOption(label=enemy+'2'))
        self.add_item(GiveApDropdown(self.menu_options2))

    @discord.ui.button(label="<-", style=discord.ButtonStyle.grey, custom_id='left')
    async def menu1(self, interaction: discord.interactions.Interaction, button):
        if str(interaction.user.id) != self.player_id or self.instance.invalid() or self.instance.game_over():
            print('no!')
            return
        await interaction.response.send_message(f"{self.player_id} Has gone left")
        # Write the update all func in here and then make my shit do things and shit and stuff
        #await bot.updateall(int(self.server_id))
        if len(self.instance.remaining_players()) == 1:
            await interaction.followup.send(f"{self.instance.remaining_players()[0]} has won!! :DD")
            start_game.delete_game(self.game_id, self.server_id)
            # delete persistent database !! TODO
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
        await interaction.response.send_message(f"{self.player_id} Has gone right")
        if len(self.instance.remaining_players()) == 1:
            await interaction.followup.send(f"{self.instance.remaining_players()[0]} has won!! :DD")
            start_game.delete_game(self.game_id, self.server_id)

    @discord.ui.button(label="v", style=discord.ButtonStyle.grey, custom_id='down')
    async def menu3(self, interaction: discord.interactions.Interaction, button):
        if str(interaction.user.id) != self.player_id or self.instance.invalid() or self.instance.game_over():
            print('no!')
            return
        await interaction.response.send_message(f"{self.player_id} Has gone down")
        if len(self.instance.remaining_players()) == 1:
            await interaction.followup.send(f"{self.instance.remaining_players()[0]} has won!! :DD")
            start_game.delete_game(self.game_id, self.server_id)

    @discord.ui.button(label="^", style=discord.ButtonStyle.grey, custom_id='up')
    async def menu4(self, interaction: discord.interactions.Interaction, button):
        if str(interaction.user.id) != self.player_id or self.instance.invalid() or self.instance.game_over():
            print('no!')
            return
        await interaction.response.send_message(f"{self.player_id} Has gone up")
        if len(self.instance.remaining_players()) == 1:
            await interaction.followup.send(f"{self.instance.remaining_players()[0]} has won!! :DD")
            start_game.delete_game(self.game_id, self.server_id)


class AttackDropdown(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder='Attack a tank!', min_values=1, max_values=1, options=options, custom_id='attacker')

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'You try to attack {self.values[0]}')


class GiveApDropdown(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder='Give an AP!', min_values=1, max_values=1, options=options, custom_id='giver')

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'You give 1 AP to {self.values[0]}')
