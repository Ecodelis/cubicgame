import arcade
import config
from config import LANE_AXIS, LEVEL_PROG_TIME

# Sprite Classes
from ESprites import Cubic, Block, Bubble, Wall

import pathlib
import math
from pyglet.gl import GL_NEAREST  # To create pixelated look
from random import choice, randint, uniform
from enum import Enum
from sys import exit

# CONSTANTS AND VARIABLES //////////////////////////////////////////////////////////
DEBUG = False

#  [State machines]
PlayerStates = Enum("PlayerStates", "IDLING RUNNING JUMPING DUCKING CRASHING")
GameStates = Enum("GameStates", "WAITING PLAYING PAUSED GAMEOVER")




# Names of the image files we need to load:
ALL_TEXTURES = ["box-1", "rect-1"]


# /////////////////////////////////////////////////////////////////////////////////


class CubicGame(arcade.View):

    def __init__(self, view_manager):
        super().__init__()
        self.view_manager = view_manager  # Store the ViewManager

        self.window.set_mouse_visible(False)

        # Load Audio (streaming means load from disk)
        # SoundTracks
        self.background_music = arcade.Sound(config.MUSIC_2, streaming=True)

        # Sound Effects
        self.death1_sound = arcade.load_sound(config.death_1, streaming=False)
        self.powerup1_sound = arcade.load_sound(config.powerup_1, streaming=False)
        self.up1_sound = arcade.load_sound(config.up_1, streaming=False)
        self.down1_sound = arcade.load_sound(config.down_1, streaming=False)
        self.bubble1_sound = arcade.load_sound(config.bubble_1, streaming=False)

        arcade.set_background_color(config.BACKGROUND_COLOR)

        # Player initially
        self.player_state = PlayerStates.IDLING

        self.setup()

    # Initialize sprites and lists
    def setup(self):

        # Player objects for each sound
        self.music_player = None
        self.death1_player = None
        self.powerup1_player = None
        self.up1_player = None
        self.down1_player = None
        self.bubble1_player = None


        self.camera_sprites = arcade.Camera(
            config.SCREEN_WIDTH, config.SCREEN_HEIGHT  # Camera that moves
        )

        self.camera_gui = arcade.Camera(
            config.SCREEN_WIDTH,
            config.SCREEN_HEIGHT,  # GUI camera, rooted at 0,0 at window
        )

        # Scene setup
        self.scene = arcade.Scene()

        # CONSTANTS ============================================================================================
        
        # Making the lanes sequential
        self.lane_indices = {lane: index for index, lane in enumerate([5, 3, 1, 0, 2, 4])}

        # ======================================================================================================

        # VARIABLES ============================================================================================
        self.elapsed_time = 0.0  # Elapsed time (floating point)
        self.total_score = 0 # total score
        self.timed_score = 0  # Score based on time survived
        self.bubble_score = 0 # Additional score, based on bubbles collected
        self.level_difficulty = 1  # CURRENT DIFFICULTY (each level is +1 lane)
        self.next_grid = 0

        self.last_item_spawned = None # Keeps track of last item spawned
        self.bubbles_in_a_row = 0 # How many bubble sets spawned in a row
        self.blockers_in_a_row = 0 # How many blocker sets spawned in a row
        self.bubble_scarcity = 2 # how many bubbles in a row until garuenteed blocker
        self.blocker_scarcity = 4 # how many blockers in a row until garuenteed bubble

        self.player_travel_speed = config.PLAYER_SPEED # start speed
        self.player_top_bound = None
        self.player_bot_bound = None
        self.topmost_lane = 1
        self.bottommost_lane = 0
        self.player_current_lane = None

        self.spawn_interval = 0

        self.game_state = GameStates.WAITING
        

        # ======================================================================================================

        # Dictionary for textures
        self.textures = {
            tex: arcade.load_texture(config.ASSETS_PATH / f"{tex}.png")
            for tex in ALL_TEXTURES
        }

        # List of all Sprites
        SpritesList = []

        # AFTERIMAGE EFFECT SETUP ==========================================================================================
        self.afterimage_list = arcade.SpriteList()

        # ==================================================================================================================


        # PLAYER SETUP =====================================================================================================
        self.player_current_lane = randint(0,1)
        self.player_sprite = Cubic(config.GRID_SIZE, config.GRID_SIZE, 200, LANE_AXIS[self.player_current_lane])  # Make player sprite
        self.player_sprite.change_x = self.player_travel_speed

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)

        self.scene.add_sprite(
            "player", self.player_sprite
        )  # scene contains player sprite list
        # ===================================================================================================================

        # BOUNDARY SETUP =====================================================================================================
        self.wall_list = arcade.SpriteList()
        # Initial Spawn Locations
        spawn_locations = [
            (
                config.SCREEN_WIDTH / 2,
                LANE_AXIS[3] + config.SCREEN_HEIGHT / 2 - config.GRID_SIZE / 2,
            ),
            (
                config.SCREEN_WIDTH / 2,
                LANE_AXIS[2] - config.SCREEN_HEIGHT / 2 + config.GRID_SIZE / 2,
            ),
        ]

        # Create two wall sprites
        for n in range(2):
            self.wall_sprite = Wall(spawn_locations[n][0],spawn_locations[n][1])  # Make wall sprite
            self.wall_list.append(self.wall_sprite)


        self.player_top_bound = self.wall_list[0].bottom # ciel
        self.player_bot_bound = self.wall_list[1].top # ground
        self.scene.add_sprite_list("wall", self.wall_list)
        # ===================================================================================================================

        # BLOCKERS SETUP =====================================================================================================
        self.blocker_list = arcade.SpriteList()

        # ===================================================================================================================

        # BUBBLES SETUP =====================================================================================================
        self.bubble_list = arcade.SpriteList()

        # ===================================================================================================================

        # When game starts set to RUN
        self.player_state = PlayerStates.RUNNING

        # PHYSICS
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            [],
            gravity_constant=0,
        )

    def on_show(self):
        # SOUNDTRACK at start of game
        self.music_player = self.background_music.play(volume=1, loop=True)


        arcade.set_background_color(config.BACKGROUND_COLOR)

        self.score_text = arcade.Text(
            f"{self.total_score:05}",  # 5 leading zeros
            config.SCREEN_WIDTH - 2,
            config.SCREEN_HEIGHT - 10,
            arcade.color.WHITE,
            font_size=20,
            anchor_x="right",
            anchor_y="top",
            font_name="EcoPixelFont-2",  # font name
        )

        # START SCHEDULING TO SPAWN
        arcade.schedule(self.spawning_event, uniform(0.5,1))




        # START PLAYING
        self.game_state = GameStates.PLAYING

    def on_draw(self):
        arcade.start_render()

        self.camera_gui.use()
        # Draw Background Lane Lines
        width = 5
        arcade.draw_rectangle_filled(config.SCREEN_WIDTH/2, LANE_AXIS[0], config.SCREEN_WIDTH + 200, width, (169, 169, 169, 100))
        arcade.draw_rectangle_filled(config.SCREEN_WIDTH/2, LANE_AXIS[1], config.SCREEN_WIDTH + 200, width, (169, 169, 169, 100))
        arcade.draw_rectangle_filled(config.SCREEN_WIDTH/2, LANE_AXIS[2], config.SCREEN_WIDTH + 200, width, (169, 169, 169, 100))
        arcade.draw_rectangle_filled(config.SCREEN_WIDTH/2, LANE_AXIS[3], config.SCREEN_WIDTH + 200, width, (169, 169, 169, 100))
        arcade.draw_rectangle_filled(config.SCREEN_WIDTH/2, LANE_AXIS[4], config.SCREEN_WIDTH + 200, width, (169, 169, 169, 100))
        arcade.draw_rectangle_filled(config.SCREEN_WIDTH/2, LANE_AXIS[5], config.SCREEN_WIDTH + 200, width, (169, 169, 169, 100))

        # Draw after images
        self.afterimage_list.draw()

        self.camera_sprites.use()  # call this before you do any drawing, all drawings will now be related to this camera
        # self.scene.draw(filter=GL_NEAREST)  # Streak artifacts appear without GL_NEAREST

        

        # Draw walls
        self.wall_list.draw(filter=GL_NEAREST)

        # Draw Player
        self.player_sprite.draw()  # I overided the draw class, cannot use list or scene

        # Draw Blockers
        self.blocker_list.draw(filter=GL_NEAREST)

        # Draw Bubbles
        self.bubble_list.draw(filter=GL_NEAREST)

        # SEE HITBOXES ===================================================================
        if DEBUG:
            self.player_list.draw_hit_boxes(arcade.color.RED_DEVIL)
            self.wall_list.draw_hit_boxes(arcade.color.GO_GREEN)
            self.blocker_list.draw_hit_boxes(arcade.color.RED_DEVIL)
            self.bubble_list.draw_hit_boxes(arcade.color.PINK)

        # ================================================================================

        # GUI Camera (When you draw stuff under here, you are using a different camera)
        self.camera_gui.use()

        # Draw Score
        self.total_score = self.bubble_score + self.timed_score
        self.score_text.text = f"{self.total_score:05}"
        self.score_text.draw()

        if self.game_state == GameStates.PAUSED:
            self.draw_pause_screen()
        
        elif self.game_state == GameStates.GAMEOVER:
            self.draw_gameover_screen()


        arcade.finish_render()

    def on_update(self, delta_time):


        if self.game_state in [GameStates.GAMEOVER, GameStates.PAUSED]:
            self.background_music.stop(self.music_player)
            return  # i dont want to do any of the remaining calculations



        # DELTA TIME
        self.elapsed_time += delta_time

        # DISTANCE MOVED
        self.offset = int(self.elapsed_time * 10)

        self.player_list.update()
        self.wall_list.update() # update wall transitions
        self.afterimage_list.update()
        self.physics_engine.update()

        #print(self.elapsed_time)

        # SPAWN INTERVAL
        #self.spawn_interval = max(1, 3 - self.elapsed_time * 0.01)
        #arcade.unschedule(self.spawning_event)
        #arcade.schedule(self.spawning_event, self.spawn_interval)

        # LEVEL PROGRESSION CHECK ===================================================================================================
        if self.elapsed_time >= LEVEL_PROG_TIME[2] and self.elapsed_time < LEVEL_PROG_TIME[3] and self.level_difficulty < 2:
            self.level_difficulty = 2
            self.bottommost_lane = 2
            # Update boundaries
            self.player_bot_bound = self.wall_list[1].top
            print("2ND LEVEL")

        elif self.elapsed_time >= LEVEL_PROG_TIME[3] and self.elapsed_time < LEVEL_PROG_TIME[4] and self.level_difficulty < 3:
            self.level_difficulty = 3
            self.topmost_lane = 3
            # Update boundaries
            self.player_top_bound = self.wall_list[0].bottom
            print("3RD LEVEL")

        elif self.elapsed_time >= LEVEL_PROG_TIME[4] and self.elapsed_time < LEVEL_PROG_TIME[5] and self.level_difficulty < 4:
            self.level_difficulty = 4 
            self.bottommost_lane = 4
        # Update boundaries 
            self.player_bot_bound = self.wall_list[1].top
            print("4TH LEVEL")

        elif self.elapsed_time >= LEVEL_PROG_TIME[5] and self.level_difficulty < 5:
            self.level_difficulty = 5 # max is 5 rn
            self.topmost_lane = 5 # honestly you could find odd and even but eh for topmost and bottom most lans
            # Update boundaries
            self.player_top_bound = self.wall_list[0].bottom
            print("5TH LEVEL")

            # Increase spawning rate   LVL5  
            arcade.unschedule(self.spawning_event)
            arcade.schedule(self.spawning_event, uniform(0.1,0.7))
        

        # WALL ANIMATION FOR LEVEL (Will always be 3s behind level difficulty change) also they must occupy a layer
        animation_time = 1.5
        if self.elapsed_time >= LEVEL_PROG_TIME[2] - animation_time and self.elapsed_time < LEVEL_PROG_TIME[3] - animation_time:
            self.wall_list[1].target_y = LANE_AXIS[4] - config.SCREEN_HEIGHT / 2 + config.GRID_SIZE / 2 # bot wall
        
        elif self.elapsed_time >= LEVEL_PROG_TIME[3] - animation_time and self.elapsed_time < LEVEL_PROG_TIME[4] - animation_time:
            self.wall_list[0].target_y = LANE_AXIS[5] + config.SCREEN_HEIGHT / 2 - config.GRID_SIZE / 2 # top wall

        elif self.elapsed_time >= LEVEL_PROG_TIME[4] - animation_time and self.elapsed_time < LEVEL_PROG_TIME[5] - animation_time:
            self.wall_list[1].target_y = LANE_AXIS[6] - config.SCREEN_HEIGHT / 2 + config.GRID_SIZE / 2 # bot wall

        elif self.elapsed_time >= LEVEL_PROG_TIME[5] - animation_time and self.elapsed_time < LEVEL_PROG_TIME[6] - animation_time:
            self.wall_list[0].target_y = LANE_AXIS[7] + config.SCREEN_HEIGHT / 2 - config.GRID_SIZE / 2 # top wall

        # COLLISION CHECK ===================================================================================================
        
        # This code block is written by Copilot, the rest is coded by me with ref to this block
        # Iterate over a copy of the block list so we can remove sprites while iterating
        for blocker in self.blocker_list:
            # If the block is off-screen
            if blocker.right < self.camera_sprites.goal_position[0]:
                # Remove the block
                blocker.kill()
        
        # Check Collisions between the player and the blockers
        blocker_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.blocker_list
        )
        for block in blocker_hit_list:
            self.death1_player = self.death1_sound.play(volume=0.5, loop=False)
            if DEBUG == True:
                print("Hit!")
            else:
                self.game_state = GameStates.GAMEOVER
                self.player_sprite.kill()

    
        # bubble spawning / deletion check
        for bubble in self.bubble_list:
            # Check if bubble is colliding with any blockers
            bubble_in_blocker = arcade.check_for_collision_with_list(bubble, self.blocker_list)
            
            if bubble_in_blocker:
                # Collision = remove the bubble
                bubble.kill()
                print("removed bubble!")

            elif bubble.right < self.camera_sprites.goal_position[0]:
                # Remove the bubble
                bubble.kill()

        # Collision: Bubble w/ Player
        bubble_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.bubble_list
        )
        for bubble in bubble_hit_list:
            bubble.kill()
            self.bubble1_player = self.bubble1_sound.play(volume=0.9, loop=False)
            self.bubble_score += 100
            print("Score!")
            # Maybe put text saying 100 PTS!




        # Update the sprites in the sprite_list
        for sprite in self.wall_list:
            sprite.center_x = self.player_sprite.center_x + 383

        # MOVE PLAYER by PLAYER_SPEED amount for every DELTA TIME (and move cam)
        accel = 0.01
        if self.player_travel_speed < 15:
            self.player_travel_speed += accel
            #print(self.player_travel_speed)
        self.player_sprite.change_speed(self.player_travel_speed, 0)

        # CAMERA MOVE W/ PLAYER
        self.camera_sprites.move((self.player_sprite.left - 100, 0))

        # score increases as player moves right
        self.timed_score = int(self.player_sprite.left) // 10


    # SPAWN RATE PROGRESSION
    
    # ENTITY SPAWN HANDLING =======================================================

    def next_grid_x(self, player_x, grid_size):
        cells_passed = player_x / grid_size
        next_cell = math.ceil(cells_passed) # rounds up the number
        next_x = next_cell * config.GRID_SIZE 
        return next_x # returns the grid next to player on the right

    def spawn_blockers(self, spawn_x, spawn_y, random):
        x = spawn_x # spawn right of screen (spawner follows player x-axis)
        y = spawn_y

        if random == True: # Spawn each blocker randomly
            y = LANE_AXIS[randint(0, self.level_difficulty)]

        self.blocker_sprite = Block(x, y)  # Replace with your enemy image and scale
        self.blocker_list.append(self.blocker_sprite)
        print("BLOCKER(S) HAS BEEN SPAWNED")

    def spawn_bubbles(self, spawn_x, spawn_y, random):
        x = spawn_x
        y = spawn_y

        if random == True: # Spawn each bubble randomly
            y = LANE_AXIS[randint(0, self.level_difficulty)]
        

        self.bubble_sprite = Bubble(x, y)  # Replace with your enemy image and scale
        self.bubble_list.append(self.bubble_sprite)
        print("BUBBLE(S) HAS BEEN SPAWNED")


    def spawning_event(self, delta_time):
        # Calculate next x grid coordinate
        next_x = self.next_grid_x(self.player_sprite.right, config.GRID_SIZE)
        spawn_x = next_x + config.SCREEN_WIDTH

        # Choosing a lane...
        spawn_y = LANE_AXIS[randint(0, self.level_difficulty)]

        # Spawning items in a row event
        if self.bubbles_in_a_row > self.bubble_scarcity:
            spawn = "blockers"
            self.bubbles_in_a_row = 0
            print("spawning GAUR blockers")
        elif self.blockers_in_a_row > self.blocker_scarcity:
            spawn = "bubbles"
            self.blockers_in_a_row = 0
            print("spawning GAUR bubbles")
        else:
            # Randomly choose what to spawn
            spawn = choice(["blockers", "bubbles"],)






        if spawn in "blockers":
            # Write more complex code like walls here...
            variant = randint(1,5)
            print(variant)
            
            if variant == 1 and self.level_difficulty >= 3: # Walls
                random = True # Spawn in different y-axis
                amount_of_blockers = randint(2, self.level_difficulty) # There will always be one lane open

                for i in range(1, amount_of_blockers):
                    self.spawn_blockers(spawn_x, spawn_y, random)

            elif variant == 2 and self.level_difficulty >= 4: # Minefield Blockers
                random = True # Spawn in different y-axis

                for i in range(randint(2, self.level_difficulty)): # width
                    for n in range(randint(2, self.level_difficulty)): # height (random)
                        self.spawn_blockers(spawn_x + config.GRID_SIZE * 4 * i , spawn_y, random)


            elif variant == 3 and self.level_difficulty >= 5: # Big Blocks
                random = False
                y_dir = choice([-1, 1])
                
                for i in range(randint(2, self.level_difficulty)): # width
                    for n in range(randint(2, self.level_difficulty)): # height
                        self.spawn_blockers(spawn_x + config.GRID_SIZE * i , spawn_y + config.GRID_SIZE * y_dir * n, random)

            else:
                
                if self.level_difficulty >= 3 and randint(1,3) != 1:
                    amount_of_blockers = randint(2, 7)
                elif self.level_difficulty >= 2 and randint(1,2) != 1:
                    amount_of_blockers = randint(1, self.level_difficulty)
                else:
                    amount_of_blockers = 2 # needs to be 2 because of range()

                # Should blockers spawn in random lanes 1 in 5 chance
                if randint(1,5) == 1:
                    random = True
                else:
                    random = False

                for i in range(1, amount_of_blockers): # basically spits out 1 (kept randomizer for later use)
                    self.spawn_blockers(spawn_x + config.GRID_SIZE * i, spawn_y, random)

            
            self.blockers_in_a_row += 1
            print(f'blockers in a row: {self.blockers_in_a_row}')

        elif spawn in "bubbles":
            if self.last_item_spawned == "blockers":
                amount_of_bubbles = randint(2, 7) # spawn a bunch of bubbles after a blocker
            else:
                amount_of_bubbles = randint(1, 3) # two in a row bubble spawn = less bubbles
            
            # Should bubbles spawn in random lanes 1 in 5 chance
            if randint(1,5) == 1:
                random = True
            else:
                random = False

            for i in range(amount_of_bubbles):
                self.spawn_bubbles(spawn_x + config.GRID_SIZE * i, spawn_y, random)  # spawn bubbles
            self.bubbles_in_a_row += 1
            print(f'bubbles in a row: {self.bubbles_in_a_row}')
        
        # Keep track of last_item_spawned
        self.last_item_spawned = spawn

    def create_afterimage(self):
        afterimage = Afterimage(self.player_sprite.texture)
        afterimage.center_x = self.player_sprite.center_x
        afterimage.center_y = self.player_sprite.center_y
        self.afterimage_list.append(afterimage)


    def on_key_press(self, key, _modifiers):
        if key == arcade.key.ENTER and self.game_state == GameStates.GAMEOVER:
            self.music_player = self.background_music.play(volume=0.5, loop=True)
            self.setup()

        if key == arcade.key.Q:
            self.view_manager.show_menu()
            self.background_music.stop(self.music_player)

        if key == arcade.key.ESCAPE:
            if self.game_state == GameStates.PLAYING:
                self.game_state = GameStates.PAUSED
                self.background_music.stop(self.music_player)
            elif self.game_state == GameStates.PAUSED:
                self.game_state = GameStates.PLAYING
                self.music_player = self.background_music.play(volume=0.5, loop=True)

        if key == arcade.key.UP:
            self.switch_lane_up()

        elif key == arcade.key.DOWN:
            self.switch_lane_down()

        elif key == arcade.key.LEFT:
            self.tele_lane_up()
        
        elif key == arcade.key.RIGHT:
            self.tele_lane_down()
        
        # LANE KEYS
        elif key == arcade.key.H and self.level_difficulty >= 0:
            self.player_sprite.target_y = LANE_AXIS[0]
            self.player_current_lane = 0
        elif key == arcade.key.G and self.level_difficulty >= 1:
            self.player_sprite.target_y = LANE_AXIS[1]
            self.player_current_lane = 1
        elif key == arcade.key.J and self.level_difficulty >= 2:
            self.player_sprite.target_y = LANE_AXIS[2]
            self.player_current_lane = 2
        elif key == arcade.key.F and self.level_difficulty >= 3:
            self.player_sprite.target_y = LANE_AXIS[3]
            self.player_current_lane = 3
        elif key == arcade.key.K and self.level_difficulty >= 4:
            self.player_sprite.target_y = LANE_AXIS[4]
            self.player_current_lane = 4
        elif key == arcade.key.D and self.level_difficulty >= 5:
            self.player_sprite.target_y = LANE_AXIS[5]
            self.player_current_lane = 5

        

        if DEBUG == True and key == arcade.key.P:
            self.spawn_blockers()
        elif DEBUG == True and key == arcade.key.O:
            self.spawn_bubbles()

    def on_key_release(self, key, _modifiers):
        pass

    def switch_lane_up(self):
        if self.up1_player:
            arcade.stop_sound(self.up1_player)


        if self.player_sprite.target_y < self.player_top_bound - config.GRID_SIZE:
            self.player_sprite.target_y += config.GRID_SIZE
            self.up1_player = arcade.play_sound(self.up1_sound, volume=0.3)

    def switch_lane_down(self):
        if self.down1_player:
            arcade.stop_sound(self.down1_player)

        if self.player_sprite.target_y > self.player_bot_bound + config.GRID_SIZE:
            self.player_sprite.target_y -= config.GRID_SIZE 
            self.down1_player = arcade.play_sound(self.down1_sound, volume=0.3)

    def tele_lane_up(self):
        # Store the current lane index
        current_lane_index = self.lane_indices[self.topmost_lane]

        # Move the player
        self.player_sprite.target_y = LANE_AXIS[self.topmost_lane]

        # If the player moved across 2 or more lanes, create an afterimage
        if abs(self.lane_indices[self.topmost_lane] - current_lane_index) >= 2:
            self.create_afterimage()
    
    def tele_lane_down(self):
        self.player_sprite.target_y = LANE_AXIS[self.bottommost_lane]

    def draw_pause_screen(self):
        arcade.draw_rectangle_filled(config.SCREEN_WIDTH/2, config.SCREEN_HEIGHT/2, config.SCREEN_WIDTH + 200, config.SCREEN_HEIGHT, (0, 0, 0, 100))
        
        arcade.Text(
            "- PAUSED -",
            config.SCREEN_WIDTH/2,
            config.SCREEN_HEIGHT/2 - 210,
            arcade.color.GRAY,
            font_size=40,
            anchor_x="center",
            anchor_y="center",
            font_name="EcoPixelFont-1",
        ).draw()

        arcade.Text(
            "- PAUSED -",
            config.SCREEN_WIDTH/2,
            config.SCREEN_HEIGHT/2 - 205,
            arcade.color.WHITE,
            font_size=40,
            anchor_x="center",
            anchor_y="center",
            font_name="EcoPixelFont-1",
        ).draw()

    def draw_gameover_screen(self):
        arcade.draw_rectangle_filled(config.SCREEN_WIDTH/2, config.SCREEN_HEIGHT/2, config.SCREEN_WIDTH + 200, config.SCREEN_HEIGHT, (0, 0, 0, 150))

        arcade.Text(
            "GAME OVER",
            config.SCREEN_WIDTH/2,
            config.SCREEN_HEIGHT/2 + 140,
            arcade.color.GRAY,
            font_size=60,
            anchor_x="center",
            anchor_y="center",
            font_name="EcoPixelFont-1", 
        ).draw()

        arcade.Text(
            "GAME OVER",
            config.SCREEN_WIDTH/2,
            config.SCREEN_HEIGHT/2 + 150,
            arcade.color.WHITE,
            font_size=60,
            anchor_x="center",
            anchor_y="center",
            font_name="EcoPixelFont-1", 
        ).draw()

        arcade.Text(
            f"TIME: {self.elapsed_time:.1f}",
            config.SCREEN_WIDTH/2,
            config.SCREEN_HEIGHT/2 + 10,
            arcade.color.WHITE,
            font_size=30,
            anchor_x="center",
            anchor_y="center",
            font_name="EcoPixelFont-1", 
        ).draw()

        arcade.Text(
            f"SCORE: {self.total_score}",
            config.SCREEN_WIDTH/2,
            config.SCREEN_HEIGHT/2 - 40,
            arcade.color.WHITE,
            font_size=30,
            anchor_x="center",
            anchor_y="center",
            font_name="EcoPixelFont-1", 
        ).draw()

        arcade.Text(
            "- ENTER TO CONTINUE -",
            config.SCREEN_WIDTH/2,
            config.SCREEN_HEIGHT/2 - 200,
            arcade.color.WHITE,
            font_size=30,
            anchor_x="center",
            anchor_y="center",
            font_name="EcoPixelFont-1",
        ).draw()
