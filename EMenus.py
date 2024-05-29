import arcade
import config
from EGame import CubicGame  # Import the GameView from the ERunner file


class MenuView(arcade.View):
    def __init__(self, view_manager):
        super().__init__()
        self.view_manager = view_manager  # Store the ViewManager

    def on_show(self):
        arcade.set_background_color(arcade.color.WHITE)
        self.start_text = arcade.Text(
            "START",
            config.SCREEN_WIDTH / 2,  # start_x
            config.SCREEN_HEIGHT / 2,  # start_y
            arcade.color.BLACK,  # color
            font_size=50,
            anchor_x="center",  # anchor x
            anchor_y="center",  # anchor y
            font_name="EcoPixelFont-1",  # font name
        )

    def on_draw(self):
        arcade.start_render()
        self.start_text.draw()

        arcade.finish_render()

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        print("touched")
        self.view_manager.show_game()  # Switch to the game view using the ViewManager
