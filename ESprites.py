import arcade


# Player Sprite
class Cubic(arcade.Sprite):
    def __init__(self, width, height, x, y):
        super().__init__()
        self.width = width
        self.height = height
        self.center_x = x
        self.center_y = y
        self.target_x = x
        self.target_y = y
        self.speed = 0.9 # animation speed

        # Initialize color
        self.color = arcade.color.BLACK

    def draw(self):

        arcade.draw_rectangle_filled(
            self.center_x, self.center_y, self.width, self.height, self.color
        )

    def update(self):
        # Smooth animation of wall moving
        #self.center_x = arcade.lerp(self.center_x, self.target_x, self.speed)
        self.center_y = arcade.lerp(self.center_y, self.target_y, self.speed)

        

    def change_color(self, new_color):
        # Change the color of the sprite
        self.color = new_color

    def change_size(self, new_width, new_height):
        # Change the size of the sprite
        self.target_width = new_width
        self.target_height = new_height

    def change_speed(self, change_x, change_y):
        self.change_x = change_x
        self.change_y = change_y


# Blocker Sprite
class Block(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.texture = arcade.load_texture(
            "Assets/box-1.png"
        ) 
        self.center_x = x
        self.center_y = y

# Bubble (collectables) Sprite
class Bubble(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.texture = arcade.load_texture(
            "Assets/bubble-1.png"
        )
        self.center_x = x
        self.center_y = y
    
    def update(self):
        pass

# Wall Sprite
class Wall(arcade.Sprite):

    def __init__(self, x, y):
        super().__init__()
        self.texture = arcade.load_texture(
            "Assets/rect-1.png"
        ) 
        self.center_x = x
        self.center_y = y
        self.target_x = x
        self.target_y = y
        self.speed = 0.050

    def update(self):
        # Smooth animation of wall moving
        self.center_x = arcade.lerp(self.center_x, self.target_x, self.speed)
        self.center_y = arcade.lerp(self.center_y, self.target_y, self.speed)

# AfterImage class from Copilot
class Afterimage(arcade.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lifespan = 0.5  # lifespan of 0.5 seconds

    def update(self):
        super().update()
        self.lifespan -= 1/60  # assuming 60 frames per second
        self.alpha = int(255 * max(0, self.lifespan / 0.5))  # fade out over time
        if self.lifespan <= 0:
            self.remove_from_sprite_lists()  # remove the sprite when its lifespan is over
