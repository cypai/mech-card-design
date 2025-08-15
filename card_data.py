from wand.image import Image

# At 300 DPI
CARD_WIDTH = 750
CARD_HEIGHT = 1050

ICON_SIZE = int(CARD_WIDTH / 10)
LARGE_ICON_SIZE = int(ICON_SIZE * 1.5)

LARGE_FONT_SIZE = int(CARD_HEIGHT / 17.5)
TRACKER_FONT_SIZE = int(CARD_HEIGHT / 20)
SMALL_FONT_SIZE = int(CARD_HEIGHT / 28)

TRACKER_SIZE = int(CARD_HEIGHT / 10)


class Icons:
    def __init__(self):
        pass

    def __enter__(self):
        self.heat = Image(filename="textures/heat.png")
        self.melee = Image(filename="textures/melee.png")
        self.range = Image(filename="textures/range.png")
        self.ammo = Image(filename="textures/ammo.png")
        self.armor = Image(filename="textures/armor.png")
        self.card_rotation = Image(filename="textures/card-rotation.png")

        self.heat.resize(ICON_SIZE, ICON_SIZE)
        self.melee.resize(ICON_SIZE, ICON_SIZE)
        self.range.resize(ICON_SIZE, ICON_SIZE)
        self.ammo.resize(ICON_SIZE, ICON_SIZE)
        self.armor.resize(LARGE_FONT_SIZE, LARGE_FONT_SIZE)
        self.card_rotation.resize(LARGE_ICON_SIZE, LARGE_ICON_SIZE)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.heat.close()
        self.melee.close()
        self.range.close()
        self.ammo.close()
