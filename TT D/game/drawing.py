from PIL import Image, ImageDraw, ImageFont
import json
from io import BytesIO
import discord


class DrawMap:
    def __init__(self, server, game_id, player_id=None):
        with open('gamedata.json') as file:
            game_data = json.load(file)
        self.game_info = game_data[server][game_id]
        self.player_id = player_id

    def drawplayermap(self, spectate=False, win=False):
        background = Image.open('background3.jpg')
        background = background.convert('RGBA')
        font = ImageFont.truetype('arial.ttf', size=45)
        namefont = ImageFont.truetype('arial.ttf', size=42)
        for player in self.game_info["players"]:
            if not spectate:
                if player == self.player_id:
                    #tank = Image.new('RGB', (100, 100), color='green')
                    tank = Image.open(fr'pfpcache\{player}.jpg')
                    tank = tank.convert('RGBA')
                    tank.thumbnail((100,100))
                    heart = Image.open('heart.png')
                    heart = heart.convert('RGBA')
                    offset = 0
                    for _ in range(self.game_info["players"][player]['life']):
                        tank.paste(heart, (offset,0))
                        offset += 25
                    draw = ImageDraw.Draw(tank)
                    draw.text((0, 23), str(self.game_info["players"][player]["ap"]), font=font, fill='black',stroke_width=1, stroke_fill='white')
                    draw.text((0, 60), self.game_info["players"][player]["name"], font=namefont, fill='black',stroke_width=1, stroke_fill='white')
                    background.paste(tank, (self.game_info["players"][player]["x"], self.game_info["players"][player]["y"]))
                    continue

            tank = Image.open(fr'pfpcache\{player}.jpg')
            tank = tank.convert('RGBA')
            tank.thumbnail((100, 100))
            heart = Image.open('heart.png')
            heart = heart.convert('RGBA')
            offset = 0
            for _ in range(self.game_info["players"][player]['life']):
                tank.paste(heart, (offset, 0))
                offset += 25
            draw = ImageDraw.Draw(tank)
            draw.text((0, 60), self.game_info["players"][player]["name"], font=namefont, fill='black',stroke_width=1, stroke_fill='white')
            draw.text((0, 23), str(self.game_info["players"][player]["ap"]), font=font, fill='black',stroke_width=1, stroke_fill='white')
            background.paste(tank, (self.game_info["players"][player]["x"], self.game_info["players"][player]["y"]))
            if win:
                victory = Image.open('wub.png')
                background.paste(victory,(300,100))
        with BytesIO() as image_binary:
            background.save(image_binary, 'PNG')
            image_binary.seek(0)
            return discord.File(fp=image_binary, filename='background.png')



if __name__ == "__main__":
    ...
    # with open('gamedata.json') as f:
    #    game_data = json.load(f)
    ## print(game_data)
    # for key in game_data:
    #    print(game_data[key])
    # background = Image.open('background3.jpg')
    # tank = Image.new('RGB', (25, 25), color='green')
    # draw = ImageDraw.Draw(tank)
    # font = ImageFont.truetype('arial.ttf', size=20)
    # draw.text((0, 0), '53', font=font, fill='black')
    ##tank.paste(Image.new('RGB', (10,10), color='red'))
    # background.paste(tank, (100, 100))
#
# background.show()
