import random
import json
import os
import atexit

SAVE_FILE = "fnaf_filya_save.json"

# ===== LOAD / SAVE =====
def save_game():
    data = {
        "best_night": best_night,
        "total_wins": total_wins,
        "total_losses": total_losses,
        "nights_completed": nights_completed,
        "character_stats": character_stats,
        "editor_unlocked": editor_unlocked,
        "editor_settings": editor_settings,
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("💾 Saved!")


def load_game():
    global best_night, total_wins, total_losses, nights_completed, character_stats
    global editor_unlocked, editor_settings
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        best_night = data.get("best_night", 0)
        total_wins = data.get("total_wins", 0)
        total_losses = data.get("total_losses", 0)
        nights_completed = data.get("nights_completed", [])
        character_stats = data.get("character_stats", {
            "🐈 Sima": 0, "🐈‍⬛ Filya": 0, "🐢 Godzik": 0,
        })
        editor_unlocked = data.get("editor_unlocked", False)
        editor_settings = data.get("editor_settings", {
            "speed": 1.0,
            "drain": 1.0,
            "nights": 8,
        })
        print("📂 Game loaded!")
    else:
        print("🆕 New game!")


def reset_stats():
    global best_night, total_wins, total_losses, nights_completed, character_stats
    best_night = 0
    total_wins = 0
    total_losses = 0
    nights_completed = []
    character_stats = {"🐈 Sima": 0, "🐈‍⬛ Filya": 0, "🐢 Godzik": 0}
    save_game()
    print("🔄 Stats reset!")


atexit.register(save_game)

# ===== VARIABLES =====
night = 1
energy = 100
time = 0
doors_closed = {"left": False, "right": False}
lights = {"left": False, "right": False}
cameras = 1
game_running = True

best_night = 0
total_wins = 0
total_losses = 0
nights_completed = []
character_stats = {"🐈 Sima": 0, "🐈‍⬛ Filya": 0, "🐢 Godzik": 0}
editor_unlocked = False
editor_settings = {
    "speed": 1.0,
    "drain": 1.0,
    "nights": 8,
}

# ===== CHARACTERS =====
characters = {
    "🐈 Sima": {"position": "kitchen", "speed": 0.3, "gender": "f", "side": "left"},
    "🐈‍⬛ Filya": {"position": "bedroom", "speed": 0.5, "gender": "m", "side": "right"},
    "🐢 Godzik": {"position": "living_room", "speed": 0.2, "gender": "m", "side": "random"},
}

locations = ["kitchen", "bedroom", "living_room", "bathroom", "hallway", "at_the_door"]


# ===== DISPLAY =====
def show_status():
    print(f"\n🌙 NIGHT {night} | ⏰ {time}:00 | ⚡ Energy: {energy}%")
    print(f"🚪 Left door: {'🔒 CLOSED' if doors_closed['left'] else '🔓 OPEN'}")
    print(f"🚪 Right door: {'🔒 CLOSED' if doors_closed['right'] else '🔓 OPEN'}")
    print(f"📹 Camera: {locations[cameras - 1]}")
    print(f"👥 Sima = left, Filya = right, Godzik = random")


def show_cameras():
    print(f"\n📹 CAMERA: {locations[cameras - 1]}")
    someone_there = False
    for name, c in characters.items():
        if c["position"] == locations[cameras - 1]:
            side = c["side"]
            print(f"  👀 {name} is here! (will go to: {side})")
            someone_there = True
    if not someone_there:
        print("  Empty...")


# ===== MOVEMENT =====
def move_characters():
    for name, c in characters.items():
        if random.random() < c["speed"]:
            index = locations.index(c["position"])
            if index < len(locations) - 1:
                c["position"] = locations[index + 1]
                print(f"\n🔔 {name} moved to the {c['position']}!")


def check_attack():
    for name, c in characters.items():
        if c["position"] == "at_the_door":
            if c["side"] == "random":
                side = random.choice(["left", "right"])
            else:
                side = c["side"]

            side_name = "left" if side == "left" else "right"

            if doors_closed[side]:
                print(f"\n🔒 {name} tried to enter through the {side_name} door, but it was closed!")
                c["position"] = "hallway"
            else:
                print(f"\n💀 {name} entered through the {side_name} door! You lost!")
                character_stats[name] += 1
                return False
    return True


# ===== ACTIONS =====
def close_door(side):
    global energy
    if energy < 3:
        print("❌ Not enough energy!")
        return
    doors_closed[side] = not doors_closed[side]
    energy -= 3
    if doors_closed[side]:
        print(f"🔒 {side.capitalize()} door closed (-3% energy)")
    else:
        print(f"🔓 {side.capitalize()} door opened (-3% energy)")


def use_light(side):
    global energy
    if energy < 5:
        print("❌ Not enough energy!")
        return
    lights[side] = not lights[side]
    energy -= 5
    if lights[side]:
        print(f"💡 {side.capitalize()} light on (-5% energy)")
        for name, c in characters.items():
            if c["position"] == "at_the_door":
                if c["side"] == side or c["side"] == "random":
                    print(f"  👀 {name} is at the {side} door!")
    else:
        print(f"💡 {side.capitalize()} light off")


def make_move():
    global time, energy
    time += 1

    # base drain with editor multiplier
    multiplier = editor_settings["drain"]

    if night == 8:
        energy -= 5 * multiplier
        for side, closed in doors_closed.items():
            if closed:
                energy -= 5 * multiplier
    elif night == 7:
        energy -= 4 * multiplier
        for side, closed in doors_closed.items():
            if closed:
                energy -= 4 * multiplier
    elif night == 6:
        energy -= 3 * multiplier
        for side, closed in doors_closed.items():
            if closed:
                energy -= 3 * multiplier
    else:
        energy -= 2 * multiplier
        for side, closed in doors_closed.items():
            if closed:
                energy -= 2 * multiplier

    move_characters()
    return check_attack()


# ===== STATISTICS =====
def show_statistics():
    print("\n📊 STATISTICS:")
    print(f"  🏆 Best night: {best_night}")
    print(f"  ✅ Total wins: {total_wins}")
    print(f"  ❌ Total losses: {total_losses}")
    print(f"  🌙 Nights completed: {nights_completed}")
    print("\n  👥 Who won:")
    for name, score in character_stats.items():
        print(f"    {name}: {score} times")
    print("\n  1 - Reset stats")
    print("  2 - Back")
    choice = input("Choice: ").strip()
    if choice == "1":
        reset_stats()


# ===== NIGHT EDITOR =====
def night_editor():
    global editor_settings

    if not editor_unlocked:
        print("🔒 The editor unlocks after completing all nights!")
        return

    print("\n🛠️ NIGHT EDITOR")
    print(f"1. Character speed: x{editor_settings['speed']}")
    print(f"2. Energy drain: x{editor_settings['drain']}")
    print(f"3. Number of nights: {editor_settings['nights']}")
    print("4. Reset to default")
    print("5. Back")

    choice = input("Choice: ").strip()

    if choice == "1":
        try:
            new_value = float(input("New speed (0.1 - 3.0): "))
            if 0.1 <= new_value <= 3.0:
                editor_settings["speed"] = new_value
                print(f"✅ Speed: x{new_value}")
                save_game()
            else:
                print("❌ From 0.1 to 3.0")
        except:
            print("❌ Error")
    elif choice == "2":
        try:
            new_value = float(input("New drain (0.1 - 5.0): "))
            if 0.1 <= new_value <= 5.0:
                editor_settings["drain"] = new_value
                print(f"✅ Drain: x{new_value}")
                save_game()
            else:
                print("❌ From 0.1 to 5.0")
        except:
            print("❌ Error")
    elif choice == "3":
        try:
            new_value = int(input("How many nights? (1 - 20): "))
            if 1 <= new_value <= 20:
                editor_settings["nights"] = new_value
                print(f"✅ Nights: {new_value}")
                save_game()
            else:
                print("❌ From 1 to 20")
        except:
            print("❌ Error")
    elif choice == "4":
        editor_settings = {"speed": 1.0, "drain": 1.0, "nights": 8}
        print("✅ Reset to default")
        save_game()


# ===== MAIN LOOP =====
def game():
    global night, game_running, best_night, total_wins, total_losses, nights_completed
    global time, energy, editor_unlocked, editor_settings

    load_game()

    print("=" * 50)
    print("   🐱 5 NIGHTS WITH FILYa, SIMA AND GODZIK v4.0")
    print("=" * 50)
    print("   🐈 Sima — left door")
    print("   🐈‍⬛ Filya — right door")
    print("   🐢 Godzik — random")

    while game_running and night <= editor_settings["nights"]:

        if night == 6:
            print(f"\n{'=' * 50}")
            print(f"   🕵️ SECRET NIGHT 6")
            print(f"{'=' * 50}")
            print("   ⚠️ ALL CHARACTERS ACTIVE!")
        elif night == 7:
            print(f"\n{'=' * 50}")
            print(f"   😱 NIGHT 7: NIGHTMARE")
            print(f"{'=' * 50}")
            print("   ⚠️ MAXIMUM DIFFICULTY!")
        elif night == 8:
            print(f"\n{'=' * 50}")
            print(f"   🌑 NIGHT 8: HELL")
            print(f"{'=' * 50}")
            print("   ⚠️ SURVIVAL IMPOSSIBLE?")
        else:
            print(f"\n{'=' * 50}")
            print(f"   🌙 NIGHT {night}")
            print(f"{'=' * 50}")

        # reset night
        time = 0
        energy = 100
        for side in doors_closed:
            doors_closed[side] = False
        for side in lights:
            lights[side] = False

        # difficulty with editor
        multiplier = editor_settings["speed"]

        if night == 8:
            difficulty = 1.5
        elif night == 7:
            difficulty = 1.0
        elif night == 6:
            difficulty = 0.8
        else:
            difficulty = 0.2 + night * 0.1

        difficulty *= multiplier

        for name, c in characters.items():
            if night == 8:
                c["position"] = "hallway"
            else:
                c["position"] = random.choice(locations[:3])
            c["speed"] = difficulty

        # night game loop
        while time < 6 and game_running:
            show_status()
            print("\n1. 📹 View cameras")
            print("2. 🚪 Left door")
            print("3. 🚪 Right door")
            print("4. 💡 Light left")
            print("5. 💡 Light right")
            print("6. 📹 Switch camera")
            print("7. ⏭️ Wait")
            print("8. 📊 Statistics")
            if editor_unlocked:
                print("9. 🛠️ Night editor")

            choice = input("\nYour choice: ").strip()

            if choice == "1":
                show_cameras()
            elif choice == "2":
                close_door("left")
            elif choice == "3":
                close_door("right")
            elif choice == "4":
                use_light("left")
            elif choice == "5":
                use_light("right")
            elif choice == "6":
                cameras = cameras % len(locations) + 1
                print(f"📹 Camera {cameras}: {locations[cameras - 1]}")
            elif choice == "7":
                if not make_move():
                    game_running = False
                    total_losses += 1
                    break
                if energy <= 0:
                    print("\n⚡ ENERGY RAN OUT! The animatronics activated!")
                    game_running = False
                    total_losses += 1
                    break
            elif choice == "8":
                show_statistics()
            elif choice == "9" and editor_unlocked:
                night_editor()
            else:
                print("❌ Unknown command!")

        # end of night
        if game_running and time >= 6:
            print(f"\n🌅 MORNING! Night {night} completed!")
            if night not in nights_completed:
                nights_completed.append(night)
            if night > best_night:
                best_night = night
            night += 1
        elif not game_running:
            break

    # finale
    if game_running and night > editor_settings["nights"]:
        total_wins += 1
        if not editor_unlocked:
            editor_unlocked = True
            print("\n🔓 NIGHT EDITOR UNLOCKED!")
        print("\n🎉🎉🎉 YOU COMPLETED ALL NIGHTS! 🎉🎉🎉")
        print("🏆 Achievement: LEGEND!")
        print("👑 You survived all nights!")
        save_game()


game()