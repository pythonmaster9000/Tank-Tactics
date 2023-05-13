import discord
from game import game, start_game, drawing
import json


class DiscordGameMethods:
    def __init__(self, discord_client: discord.Client, game_client: game.GameClient):
        self.client = discord_client
        self.instance = game_client

    async def move(self, direction):
        if self.instance.move(direction):
            await self.update_maps()
            return True
        return False

    async def attack(self, target):
        target = self.instance.get_coords_by_enemy(target)
        if not target:
            return False
        if self.instance.attack(target):
            await self.update_maps()
            return True
        return False

    async def give_ap(self, target):
        if self.instance.give_ap(target):
            await self.update_maps()
            return True
        return False

    async def add_range(self):
        if self.instance.add_range():
            await self.update_maps()
            return True
        return False

    async def update_maps(self):
        cserver = self.instance.server
        with open('viewdata.json') as file:
            view_data = json.load(file)
        for server in view_data:
            if server == cserver:
                for message_id in view_data[server]:
                    channel = self.client.get_channel(int(view_data[server][message_id]["channel_id"]))
                    msg = await channel.fetch_message(int(message_id))
                    if view_data[server][message_id]["player_id"] == '1103215651407020032':
                        if len(self.instance.remaining_players()) == 1:
                            await msg.edit(attachments=[drawing.DrawMap(cserver,self.instance.game_id).drawplayermap(spectate=True,win=True)],content=f'{self.instance.remaining_players()[0]} is a WEENER!!')
                            continue
                        await msg.edit(attachments=[drawing.DrawMap(cserver,self.instance.game_id).drawplayermap(spectate=True)])
                        continue
                    instance = game.GameClient(cserver, view_data[server][message_id]["player_id"])
                    if not instance.invalid():
                        await msg.edit(attachments=[instance.draw_map()])
                    else:
                        await msg.edit(content='you died',attachments=[], view=None)

    async def delete_channels(self):
        cserver = self.instance.server
        with open('viewdata.json') as file:
            view_data = json.load(file)
        for server in view_data:
            if server == cserver:
                for message_id in view_data[server]:
                    if view_data[server][message_id]["player_id"] == '1103215651407020032':
                        continue
                    channel = self.client.get_channel(int(view_data[server][message_id]["channel_id"]))
                    await channel.delete()
    # add delete game method here which also deletes all private channels
