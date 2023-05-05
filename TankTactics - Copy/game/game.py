import json


def inbounds(xy):
    return xy[0] in range(0, 776) and xy[1] in range(0, 451)


# TODO: use context manager for saving json file stuff

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
        if not self.game_id:
            print("No player found")
        if self.game_id:
            self.game_info = game_data[server][self.game_id]

    def invalid(self):
        return self.game_id is None

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

    def list_all_enemies(self):
        enemies = []
        for coord in self.get_enemy_coords():
            enemies.append(self.get_enemy_by_coords(coord))
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
        directions = {
            "up": {'x': 0, 'y': 25},
            "down": {'x': 0, 'y': -25},
            "left": {'x': -25, 'y': 0},
            "right": {'x': 25, 'y': 0},
            "upleft": {'x': -25, 'y': 25},
            "upright": {'x': 25, 'y': 25},
            "downleft": {'x': -25, 'y': -25},
            "downright": {'x': 25, 'y': -25}
        }
        playercoords = self.get_player_coords()
        if not inbounds((playercoords[0] + directions[direction]['x'], playercoords[1] + directions[direction]['y'])):
            return False
        enemycoords = self.get_enemy_coords()
        if (playercoords[0] + directions[direction]['x'], playercoords[1] + directions[direction]['y']) in enemycoords:
            return False
        self.set_player_coords(playercoords[0] + directions[direction]['x'],
                               playercoords[1] + directions[direction]['y'])
        return True

    def attack(self, enemy_coords):
        if self.check_ap() <= 0:
            return False
        if abs(enemy_coords[0] - self.get_player_coords()[0]) <= 2 * 25 and abs(
                enemy_coords[1] - self.get_player_coords()[1] <= 2 * 25):
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


if __name__ == '__main__':
    instance = GameClient('1103112924601532466', '193878633654386688')
    instance.move('left')
