from PIL import Image, ImageDraw, ImageFont
import json
from io import BytesIO
import discord


class DrawMap:
    def __init__(self, server, game_id, player_id=None):
        with open(r'C:\Users\riode\OneDrive\Desktop\TankTactics\gamedata.json') as file:
            game_data = json.load(file)
        self.game_info = game_data[server][game_id]
        self.player_id = player_id

    def drawfooter(self):
        player = self.player_id
        background = Image.open(r'C:\Users\riode\OneDrive\Desktop\TankTactics\footer.png')
        background.convert('RGBA')
        #print(background.info)
        font = ImageFont.truetype(r'C:\Users\riode\OneDrive\Desktop\TankTactics\Flome Regular.otf', size=95,
                                  encoding='utf-8')
        namefont = ImageFont.truetype(r'C:\Users\riode\OneDrive\Desktop\TankTactics\Flome Regular.otf', size=75,
                                      encoding='utf-8')


        tank = Image.open(fr'C:\Users\riode\OneDrive\Desktop\TankTactics\pfpcache\{player}.jpg').convert('RGBA')
        tank.thumbnail((250, 250))
        draw = ImageDraw.Draw(tank)
        draw.text((5, 50), str(self.game_info["players"][player]["ap"]), font=font, fill=(57, 62, 70), stroke_width=1,
                  stroke_fill=(238, 238, 238))
        #draw.text((132, 50), str(self.game_info["players"][player]["range"]), font=font, fill=(57, 62, 70),
        #          stroke_width=1, stroke_fill=(238, 238, 238))
        rangeoffset = 132 if len(str(self.game_info["players"][player]["range"])) > 1 else 190
        draw.text((rangeoffset, 50), str(self.game_info["players"][player]["range"]), font=font, fill=(57, 62, 70),
                  stroke_width=1, stroke_fill=(238, 238, 238))
        draw.text((0, 185), self.game_info["players"][player]["name"], font=namefont, fill=(57, 62, 70), stroke_width=1,
                  stroke_fill=(238, 238, 238))
        heart = Image.open(r'C:\Users\riode\OneDrive\Desktop\TankTactics\bigheart.png').convert('RGBA')
        heart.thumbnail((65,65))
        offset = 28
        for _ in range(self.game_info["players"][player]['life']):
            tank.paste(heart, (offset, 0), mask=heart)
            offset += 65
        background.paste(tank, (1080,85))
        with BytesIO() as image_binary:
            background.save(image_binary, 'PNG')
            image_binary.seek(0)
            #background.show()
            return discord.File(fp=image_binary, filename='background.png')
        #background.convert('RGBA')
        #background.show()
        #heart.show()

    def drawplayermap(self, spectate=False, win=False):
        background = Image.open(r'C:\Users\riode\OneDrive\Desktop\TankTactics\background3.jpg')
        background = background.convert('RGBA')
        # font = ImageFont.truetype('arial.ttf', size=45)
        font = ImageFont.truetype(r'C:\Users\riode\OneDrive\Desktop\TankTactics\Flome Regular.otf', size=40,
                                  encoding='utf-8')
        namefont = ImageFont.truetype(r'C:\Users\riode\OneDrive\Desktop\TankTactics\Flome Regular.otf', size=30,
                                      encoding='utf-8')

        victoryfont = ImageFont.truetype(r'C:\Users\riode\OneDrive\Desktop\TankTactics\Flome Regular.otf', size=90,
                                      encoding='utf-8')
        for player in self.game_info["players"]:
            if not spectate:
                if player == self.player_id:
                    # tank = Image.new('RGB', (100, 100), color='green')
                    tank = Image.open(fr'C:\Users\riode\OneDrive\Desktop\TankTactics\pfpcache\{player}.jpg')
                    tank = tank.convert('RGBA')
                    tank.thumbnail((100, 100))
                    heart = Image.open(r'C:\Users\riode\OneDrive\Desktop\TankTactics\bigheart.png').convert('RGBA')
                    heart.thumbnail((25,25))
                    offset = 13
                    for _ in range(self.game_info["players"][player]['life']):
                        tank.paste(heart, (offset, 0), mask=heart)
                        offset += 25
                    draw = ImageDraw.Draw(tank)
                    draw.text((2, 23), str(self.game_info["players"][player]["ap"]), font=font, fill=(57, 62, 70),
                              stroke_width=1, stroke_fill=(238, 238, 238))
                    rangeoffset = 52 if len(str(self.game_info["players"][player]["range"])) > 1 else 74
                    draw.text((rangeoffset, 23), str(self.game_info["players"][player]["range"]), font=font,
                              fill=(57, 62, 70),
                              stroke_width=1, stroke_fill=(238, 238, 238))
                    draw.text((0, 68), self.game_info["players"][player]["name"], font=namefont, fill=(57, 62, 70),
                              stroke_width=1, stroke_fill=(238, 238, 238))
                    background.paste(tank,
                                     (self.game_info["players"][player]["x"], self.game_info["players"][player]["y"]))
                    continue

            tank = Image.open(fr'C:\Users\riode\OneDrive\Desktop\TankTactics\pfpcache\{player}.jpg')
            tank = tank.convert('RGBA')
            tank.thumbnail((100, 100))
            heart = Image.open(r'C:\Users\riode\OneDrive\Desktop\TankTactics\bigheart.png').convert('RGBA')
            heart.thumbnail((25,25))
            offset = 13
            for _ in range(self.game_info["players"][player]['life']):
                tank.paste(heart, (offset, 0), mask=heart)
                offset += 25
            draw = ImageDraw.Draw(tank)
            draw.text((0, 68), self.game_info["players"][player]["name"], font=namefont, fill=(57, 62, 70),
                      stroke_width=1, stroke_fill=(238, 238, 238))
            draw.text((2, 23), str(self.game_info["players"][player]["ap"]), font=font, fill=(57, 62, 70),
                      stroke_width=1, stroke_fill=(238, 238, 238))
            rangeoffset = 52 if len(str(self.game_info["players"][player]["range"])) > 1 else 74
            draw.text((rangeoffset, 23), str(self.game_info["players"][player]["range"]), font=font, fill=(57, 62, 70),
                      stroke_width=1, stroke_fill=(238, 238, 238))
            background.paste(tank, (self.game_info["players"][player]["x"], self.game_info["players"][player]["y"]))
            if win:
                wdraw = ImageDraw.Draw(background)
                wdraw.text((600,100),self.game_info['players'][list(self.game_info['players'].keys())[0]]['name'],font=victoryfont, fill=(0,173,181), stroke_width=3, stroke_fill=(238,238,238))
                wdraw.text((200,200), f"secured the victory royale", font=victoryfont, fill=(0,173,181), stroke_width=3, stroke_fill=(238,238,238))
                winav = Image.open(fr"C:\Users\riode\OneDrive\Desktop\TankTactics\pfpcache\{list(self.game_info['players'].keys())[0]}.jpg")
                winav.thumbnail((400,400))
                background.paste(winav,(600,400))
        with BytesIO() as image_binary:
            background.save(image_binary, 'PNG')
            image_binary.seek(0)
            #background.show()
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
