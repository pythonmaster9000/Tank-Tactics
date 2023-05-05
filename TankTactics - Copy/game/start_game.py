import json
import random


def get_rand_coords():
    return random.randint(0, 31)*25, random.randint(0, 18)*25


class StartGame:
    def __init__(self, server, max_players=None, ap_speed=24, lives=3):
        self.max_players = max_players
        self.ap_speed = ap_speed
        self.lives = lives
        self.server = server
        self.player_positions = []
        with open('gamedata.json') as file:
            game_data = json.load(file)
        if server not in game_data:
            game_data[self.server] = {
                '0': {
                    'players': {},
                    'config': {
                        'apspeed': self.ap_speed,
                        'max_players': self.max_players
                    }
                }
            }
            self.game_id = '0'

        else:
            gid = 0
            for game in game_data[self.server]:
                gid += 1
            self.game_id = str(gid)
            game_data[server][self.game_id] = {
                'players': {},
                'config': {
                    'apspeed': self.ap_speed,
                    'max_players': self.max_players
                }
            }
        with open("gamedata.json", "w") as outfile:
            json.dump(game_data, outfile, indent=4)

    def add_player(self, player_id):
        with open('gamedata.json') as file:
            game_data = json.load(file)
            print(player_id, self.server, self.game_id)
            x, y = get_rand_coords()
            while (x, y) in self.player_positions:
                x, y = get_rand_coords()
            game_data[self.server][self.game_id]["players"][player_id] = {
                'x': x,
                'y': y,
                'ap': 1,
                'life': 3
            }
        with open("gamedata.json", "w") as outfile:
            json.dump(game_data, outfile, indent=4)


def delete_game(game_id, server):
    with open('gamedata.json') as file:
        game_data = json.load(file)
    game_data[server].pop(game_id)
    with open("gamedata.json", "w") as outfile:
        json.dump(game_data, outfile, indent=4)
