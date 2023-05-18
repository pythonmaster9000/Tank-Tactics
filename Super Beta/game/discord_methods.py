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
        pid = str(target)
        target = self.instance.get_coords_by_enemy(target)
        if not target:
            return False
        if self.instance.attack(target):
            await self.update_maps(f'{self.instance.get_player_by_id(self.instance.player_id)} attacked {self.instance.get_player_by_id(pid)}')
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

    async def update_maps(self, event= None):
        cserver = self.instance.server
        with open('viewdata.json') as file:
            view_data = json.load(file)
        for server in view_data:
            if server == cserver:
                for message_id in view_data[server]:
                    channel = self.client.get_channel(int(view_data[server][message_id]["channel_id"]))
                    # maybe put try except here for when deleting channels
                    if not channel:
                        continue
                    msg = await channel.fetch_message(int(message_id))
                    if view_data[server][message_id]["player_id"] == '1103215651407020032':
                        if len(self.instance.remaining_players()) == 1:
                            # put random assortment of w messages
                            emb = discord.Embed(title="Huge W for the boy", description=f'{self.instance.remaining_players()[0]} = massive W', color=44469)
                            await msg.edit(embed=emb, attachments=[drawing.DrawMap(cserver,self.instance.game_id).drawplayermap(spectate=True,win=True)],content=None)
                            continue
                        mesemb = msg.embeds[0]
                        embcont = mesemb.description
                        if event:
                            emb = discord.Embed(title="Spectate", description=f"{embcont}\n{event}", color=44469)
                        else:
                            emb = mesemb
                        await msg.edit(embed=emb,attachments=[drawing.DrawMap(cserver,self.instance.game_id).drawplayermap(spectate=True)])
                        continue
                    instance = game.GameClient(cserver, view_data[server][message_id]["player_id"])
                    if not instance.invalid():
                        if view_data[server][message_id]["footer"]:
                            await msg.edit(attachments=[instance.draw_footer()])
                        else:
                            try:
                                await msg.edit(attachments=[instance.draw_map()])
                            except discord.errors.NotFound:
                                pass
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
                    try:
                        await channel.delete()
                    except:
                        pass
    # add delete game method here which also deletes all private channels
