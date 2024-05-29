import arcade
import config  # Settings file
from EMenus import MenuView  # Import the MenuView from the EMenus file
from EGame import CubicGame


# The ViewManager class to switch between screens was written by Copilot
class ViewManager:
    def __init__(self, window):
        self.window = window
        self.menu_view = MenuView(self)  # Pass the ViewManager to the views
        self.game_view = CubicGame(self)

    def show_menu(self):
        self.window.show_view(self.menu_view)

    def show_game(self):
        self.window.show_view(self.game_view)


def main():
    # generate images for box use
    config.create_Boxes()
    config.create_Rect()
    config.create_Bubble_1()

    window = arcade.Window(
        config.SCREEN_WIDTH, config.SCREEN_HEIGHT, config.WINDOW_TITLE
    )
    view_manager = ViewManager(window)
    view_manager.show_menu()  # Show the menu at the start of the game
    arcade.run()


if __name__ == "__main__":
    main()
