import time
import displayio
from mental import profile_config
import adafruit_imageload
from adafruit_magtag.magtag import MagTag
from adafruit_progressbar.progressbar import ProgressBar

profile_id = profile_config['profile_id']

mode = "hp"
hp_bar = None
poison_sprite = None
sleep_sprite = None
hungry_sprite = None
sad_sprite = None

magtag = MagTag()

def fetch_profile():
    try:
        res = magtag.network.fetch(f"https://deusprogrammer.com/api/mental/public/profiles/{profile_id}")
        return res.json()
    except:
        return {"username": "NO WIFI", "hp": 0, "level": 0, "statuses": []}

def update_screen():
    profile = fetch_profile()
    level = profile['level']
    name = profile['username']

    statuses = profile['statuses']
    sleep_sprite.hidden = not ('tired' in statuses)
    poison_sprite.hidden = not ('sick' in statuses)
    hungry_sprite.hidden = not ('hungry' in statuses)
    sad_sprite.hidden = not ('sad' in statuses)

    hp_bar.progress = float(profile['hp']/100)
    name = name if len(name) <= 12 else name[0:10] + "..."
    magtag.set_text(f"{name} LVL {level}", 0, False)
    magtag.refresh()

# set progress bar width and height relative to board's display
BAR_WIDTH = magtag.graphics.display.width - 35
BAR_HEIGHT = 30

PROGRESS_AMOUNT = 0.1
TIME_TO_REFRESH = magtag.graphics.display.time_to_refresh
MODE_TEXTS = {"hp" : "hp     ", "status" : "status ", "level" : "level  "}
MODE_FSM = {"hp" : "status", "status" : "level", "level" : "hp"}

refresh_timer = time.monotonic()
button_timer = time.monotonic()
fetch_timer = time.monotonic()

# Add class icon
sword_sprite_sheet, palette = adafruit_imageload.load(
                            f"/images/sword.bmp",
                            bitmap=displayio.Bitmap,
                            palette=displayio.Palette,
                        )
sword_sprite = displayio.TileGrid(
            sword_sprite_sheet,
            pixel_shader=palette,
            width=1,
            height=1,
            tile_width=32,
            tile_height=32,
            x=5,
            y=5,
        )

# Add poison icon
poison_sprite_sheet, palette = adafruit_imageload.load(
                            f"/images/poison.bmp",
                            bitmap=displayio.Bitmap,
                            palette=displayio.Palette,
                        )
poison_sprite = displayio.TileGrid(
            poison_sprite_sheet,
            pixel_shader=palette,
            width=1,
            height=1,
            tile_width=32,
            tile_height=32,
            x=90,
            y=75,
        )

# Add sleep icon
sleep_sprite_sheet, palette = adafruit_imageload.load(
                            f"/images/sleep.bmp",
                            bitmap=displayio.Bitmap,
                            palette=displayio.Palette,
                        )
sleep_sprite = displayio.TileGrid(
            sleep_sprite_sheet,
            pixel_shader=palette,
            width=1,
            height=1,
            tile_width=32,
            tile_height=32,
            x=130,
            y=75,
        )

# Add hungry icon
hungry_sprite_sheet, palette = adafruit_imageload.load(
                            f"/images/hungry.bmp",
                            bitmap=displayio.Bitmap,
                            palette=displayio.Palette,
                        )
hungry_sprite = displayio.TileGrid(
            hungry_sprite_sheet,
            pixel_shader=palette,
            width=1,
            height=1,
            tile_width=32,
            tile_height=32,
            x=170,
            y=75,
        )

# Add sleep icon
sad_sprite_sheet, palette = adafruit_imageload.load(
                            f"/images/sad.bmp",
                            bitmap=displayio.Bitmap,
                            palette=displayio.Palette,
                        )
sad_sprite = displayio.TileGrid(
            sad_sprite_sheet,
            pixel_shader=palette,
            width=1,
            height=1,
            tile_width=32,
            tile_height=32,
            x=210,
            y=75,
        )

poison_sprite.hidden = True
sleep_sprite.hidden = True
hungry_sprite.hidden = True
sad_sprite.hidden = True

magtag.graphics.splash.append(sword_sprite)
magtag.graphics.splash.append(poison_sprite)
magtag.graphics.splash.append(sleep_sprite)
magtag.graphics.splash.append(hungry_sprite)
magtag.graphics.splash.append(sad_sprite)

# Progress bar
x = 30
y = magtag.graphics.display.height // 3
progress_cache = 0.0
hp_bar = ProgressBar(
    x, y, BAR_WIDTH, BAR_HEIGHT, progress_cache, bar_color=0x999999, outline_color=0x000000
)
magtag.graphics.splash.append(hp_bar)

# Add text
magtag.add_text(
    text_position=(
        40,
        2,
    ),
    text_scale=2,
    text_anchor_point=(0.0, 0.0)
)
magtag.add_text(
    text_position=(
        5,
        40,
    ),
    text_scale=2,
    text_anchor_point=(0.0, 0.0)
)
magtag.add_text(
    text_position=(
        5,
        75,
    ),
    text_scale=2,
    text_anchor_point=(0.0, 0.0)
)
magtag.add_text(
    text_position=(3, 120),
    text_scale=1,
)

magtag.set_text("HP", 1, False)
magtag.set_text("Status:", 2, False)
magtag.set_text(f"  {MODE_TEXTS[mode]}       +           -         fetch", 3, False)
update_screen()

magtag.refresh()

magtag.peripherals.neopixels.fill((0, 255, 0))
magtag.peripherals.neopixel_disable = True

dirty = False
while True:
    # Adjust progress based on button presses
    if magtag.peripherals.button_a_pressed:
        mode = MODE_FSM[mode]
        magtag.set_text(f"  {MODE_TEXTS[mode]}       +           -         fetch", 3, False)
        button_timer = time.monotonic()
        magtag.peripherals.play_tone(500, 0.25)
        dirty = True
    elif magtag.peripherals.button_b_pressed:
        if mode == "hp":
            hp_bar.progress = 1.0 if hp_bar.progress + PROGRESS_AMOUNT > 1 else hp_bar.progress + PROGRESS_AMOUNT
        elif mode == "level":
            level = level + 1
            magtag.set_text(f"{name} LVL {level}", 0, False)
        elif mode == "status":
            status = status + 1
            if status > 3: status = 0
        button_timer = time.monotonic()
        magtag.peripherals.play_tone(1047, 0.25)
        dirty = True
    elif magtag.peripherals.button_c_pressed:
        if mode == "hp":
            hp_bar.progress = 0 if hp_bar.progress - PROGRESS_AMOUNT < 0 else hp_bar.progress - PROGRESS_AMOUNT
        elif mode == "level":
            level = level - 1
            if (level < 0): level = 0
            magtag.set_text(f"{name} LVL {level}", 0, False)
        elif mode == "status":
            status = status - 1
            if status < 0: status = 3
        button_timer = time.monotonic()
        magtag.peripherals.play_tone(1568, 0.25)
        dirty = True
    elif magtag.peripherals.button_d_pressed:
        # Fetch updated stats
        update_screen()
        

    # Change lights based on HP
    # if progress_cache > 0.75:
    #     magtag.peripherals.neopixels.fill((0, 255, 0))
    # elif 0.5 < progress_cache <= 0.75:
    #     magtag.peripherals.neopixels.fill((255, 255, 0))
    # else:
    #     magtag.peripherals.neopixels.fill((255, 0, 0))

    # Handle magtag refresh
    time_since_refresh = time.monotonic() - refresh_timer
    time_since_press = time.monotonic() - button_timer
    time_since_fetch = time.monotonic() - fetch_timer
    if time_since_refresh >= TIME_TO_REFRESH and time_since_press > 1 and dirty:
            dirty = False
            magtag.peripherals.neopixel_disable = False
            magtag.peripherals.neopixels.fill((0, 255, 0))
            magtag.refresh()
            magtag.peripherals.neopixel_disable = True
            time_since_refresh = time.monotonic()

    if time_since_fetch >= 30:
        update_screen()
        fetch_timer = time.monotonic()