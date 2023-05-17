import json
from game import drawing


def inbounds(xy):
    return xy[0] in range(0, 1501) and xy[1] in range(0, 801)


# TODO: use context manager for saving json file stuff
# FIX finding the game number a player is in and require gameID to be given as param, if invalid then yea
class GameClient:
    def __init__(self, server, player_id):
        self.player_id = player_id
        self.game_id = None
        self.server = server
        with open('gamedata.json') as file:
            game_data = json.load(file)
        for game in game_data[server]:
            for player in game_data[server][game]["players"]:
                if self.player_id == player:
                    self.game_id = game
        #if not self.game_id:
        #    print("No player found", self.game_id)
        if self.game_id:
            self.game_info = game_data[server][self.game_id]
            self.range = self.game_info["players"][self.player_id]["range"]

    def invalid(self):
        return self.game_id is None

    def game_over(self):
        with open('gamedata.json') as file:
            game_data = json.load(file)
        if self.game_id not in game_data[self.server]:
            return True
        return False

    def started(self):
        with open('gamedata.json') as file:
            game_data = json.load(file)
        return game_data[self.server][self.game_id]["config"]["started"]

    def draw_map(self):
        return drawing.DrawMap(server=self.server, game_id=self.game_id, player_id=self.player_id).drawplayermap()

    def draw_footer(self):
        return drawing.DrawMap(server=self.server, game_id=self.game_id, player_id=self.player_id).drawfooter()

    def remaining_players(self):
        players = []
        with open('gamedata.json') as file:
            game_data = json.load(file)
        for player in game_data[self.server][self.game_id]["players"]:
            players.append(game_data[self.server][self.game_id]["players"][player]['name'])
        return players

    def get_player_coords(self):
        with open('gamedata.json') as file:
            game_data = json.load(file)
            return game_data[self.server][self.game_id]["players"][self.player_id]['x'], \
                game_data[self.server][self.game_id]["players"][self.player_id]['y']

    def set_player_coords(self, x, y):
        with open('gamedata.json') as file:
            game_data = json.load(file)
            game_data[self.server][self.game_id]["players"][self.player_id]['x'] = x
            game_data[self.server][self.game_id]["players"][self.player_id]['y'] = y
        with open("gamedata.json", "w") as outfile:
            json.dump(game_data, outfile, indent=4)

    def get_enemy_coords(self):
        coords = []
        with open('gamedata.json') as file:
            game_data = json.load(file)
        for player in game_data[self.server][self.game_id]["players"]:
            if player == self.player_id:
                continue
            coords.append((game_data[self.server][self.game_id]["players"][player]['x'],
                           game_data[self.server][self.game_id]["players"][player]['y']))
        return coords

    def get_enemy_by_coords(self, coords):
        with open('gamedata.json') as file:
            game_data = json.load(file)
        for player in game_data[self.server][self.game_id]["players"]:
            if (game_data[self.server][self.game_id]["players"][player]['x'],
                game_data[self.server][self.game_id]["players"][player]['y']) == coords:
                return player
        return False

    def get_coords_by_enemy(self, enemy_id):
        with open('gamedata.json') as file:
            game_data = json.load(file)
        try:
            return game_data[self.server][self.game_id]["players"][enemy_id]['x'],game_data[self.server][self.game_id]["players"][enemy_id]['y']
        except KeyError:
            return False

    def list_all_enemies(self):
        enemies = []
        with open('gamedata.json') as file:
            game_data = json.load(file)
        for player in game_data[self.server][self.game_id]["players"]:
            if player == self.player_id:
                continue
            enemies.append((self.get_enemy_by_coords((game_data[self.server][self.game_id]["players"][player]['x'],
                           game_data[self.server][self.game_id]["players"][player]['y'])),game_data[self.server][self.game_id]["players"][player]["name"]))
        return enemies

    def get_enemy_health(self, enemy):
        with open('gamedata.json') as file:
            game_data = json.load(file)
        return game_data[self.server][self.game_id]["players"][enemy]["life"]

    def set_enemy_health(self, enemy):
        with open('gamedata.json') as file:
            game_data = json.load(file)
        game_data[self.server][self.game_id]["players"][enemy]["life"] -= 1
        with open("gamedata.json", "w") as outfile:
            json.dump(game_data, outfile, indent=4)

    def get_player_by_id(self, player_id: str):
        with open('gamedata.json') as file:
            game_data = json.load(file)
        return game_data[self.server][self.game_id]["players"][player_id]["name"]

    def take_ap(self):
        with open('gamedata.json') as file:
            game_data = json.load(file)
        game_data[self.server][self.game_id]["players"][self.player_id]["ap"] -= 1
        with open("gamedata.json", "w") as outfile:
            json.dump(game_data, outfile, indent=4)

    def check_ap(self):
        with open('gamedata.json') as file:
            game_data = json.load(file)
        return game_data[self.server][self.game_id]["players"][self.player_id]["ap"]

    def kill_enemy(self, enemy):
        with open('gamedata.json') as file:
            game_data = json.load(file)
        game_data[self.server][self.game_id]["players"].pop(enemy)
        with open("gamedata.json", "w") as outfile:
            json.dump(game_data, outfile, indent=4)

    def move(self, direction):
        if self.check_ap() <= 0:
            return False
        directions = {
            "up": {'x': 0, 'y': 100},
            "down": {'x': 0, 'y': -100},
            "left": {'x': -100, 'y': 0},
            "right": {'x': 100, 'y': 0},
            "upleft": {'x': -100, 'y': 100},
            "upright": {'x': 100, 'y': 100},
            "downleft": {'x': -100, 'y': -100},
            "downright": {'x': 100, 'y': -100}
        }
        playercoords = self.get_player_coords()
        if not inbounds((playercoords[0] + directions[direction]['x'], playercoords[1] + directions[direction]['y'])):
            return False
        enemycoords = self.get_enemy_coords()
        if (playercoords[0] + directions[direction]['x'], playercoords[1] + directions[direction]['y']) in enemycoords:
            return False
        self.set_player_coords(playercoords[0] + directions[direction]['x'],
                               playercoords[1] + directions[direction]['y'])
        self.take_ap()
        return True

    def add_range(self):
        if self.check_ap() < 1:
            return False
        self.take_ap()
        self.range += 1
        with open('gamedata.json') as file:
            game_data = json.load(file)
        game_data[self.server][self.game_id]["players"][self.player_id]['range'] += 1
        with open("gamedata.json", "w") as outfile:
            json.dump(game_data, outfile, indent=4)
        return True

    def attack(self, enemy_coords):
        if self.check_ap() <= 0:
            return False
        #print(self.range,enemy_coords[0] - self.get_player_coords()[0])
        if abs(enemy_coords[0] - self.get_player_coords()[0]) <= self.range * 100 and abs(
                enemy_coords[1] - self.get_player_coords()[1] <= self.range * 100):
            enemy = self.get_enemy_by_coords(enemy_coords)
            if self.get_enemy_health(enemy) != 1:
                self.set_enemy_health(enemy)
            else:
                self.kill_enemy(enemy)
            self.take_ap()
            return True
        return False

    def give_ap(self, enemy):
        if self.check_ap() > 0:
            self.take_ap()
            with open('gamedata.json') as file:
                game_data = json.load(file)
            game_data[self.server][self.game_id]["players"][enemy]["ap"] += 1
            with open("gamedata.json", "w") as outfile:
                json.dump(game_data, outfile, indent=4)
            return True
        else:
            return False

if __name__ == '__main__':
    instance = GameClient('1103112924601532466', '193878633654386688')
    instance.move('left')
