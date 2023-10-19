from colorama import Fore, Back, Style

from src.schemas.wallet_data import WalletData
from utils.repr.private_key import blur_private_key

MODULE_NAME_MAX_LENGTH = 24

COLOR_LENGTH = 5

donation_messages = [
    "Cheers for the caffeine boost!",
    "Your coffee donation made my day!",
    "Thanks for fueling my productivity!",
    "Thanks for the sip of happiness!",
    "Your donation is my cup of tea, thanks!",
    "You espresso'd your kindness, thank you!",
    "You've bean amazing, thanks for the coffee!",
    "Cheers for the coffee, you're a lifesaver!",
    "You're the cream to my coffee, thanks!",
    "Thanks for the coffee, you're a brew-tiful person!",
    "Grateful for the steamy support!",
    "Thanks for the coffee, you're a real mug!",
    "Your donation is the perfect blend, thanks!",
    "Thanks for the coffee, you've stirred my gratitude!",
    "Java-tastic donation, you rock!",
    "You've unleashed the caffeinated beast in me, thanks!",
    "You're the sugar, spice, and everything nice in my coffee!",
    "Thanks for the coffee, you're the espresso to my depresso!",
    "You've mocha'd my day, thank you!",
    "Thanks for the cosmic caffeine infusion!",
    "You're the wizard behind my magical brew, thanks!",
    "Thanks for the coffee, you're my caffeine superhero!",
    "You've just powered my coffee-fueled coding spree, thanks!",
    "Thanks for the coffee, you're the alchemist of my day!",
    "You've just caffeinated my soul, thank you!",
    "Thanks for the coffee, you're the unicorn in my fairy tale!",
    "You're the rocket fuel for my spaceship, thanks!",
    "Thanks for the coffee, you've activated my superpowers!",
    "You're the Dumbledore of coffee donations, thank you!",
    "Thanks for the coffee, you're the genie in my lamp!",
    "You've just brewed a potion of awesomeness, thanks!",
    "Thanks for the coffee, you're the Gandalf of my Middle-Earth!",
    "You're the Yoda of coffee wisdom, thank you!",
    "Coffee cheers, thanks!",
    "You made my day better!",
    "Thanks for the pick-me-up!",
    "You're awesome, thanks!",
    "Thanks, you're a gem!",
    "Coffee = happiness, thanks!",
    "Thanks for the energy!",
    "Thanks for the boost!",
    "You're a lifesaver!",
    "Thanks, you're the best!",
    "Thanks for the warmth!",
    "You brightened my day!",
    "Thanks for the smile!",
    "You're cool, thanks!",
    "Thanks for the joy!",
    "You're kind, thanks!",
    "Thanks for the lift!",
    "You're sweet, thanks!"
]


class Symbol:
    left_top = "╔"
    right_top = "╗"
    left_bottom = "╚"
    right_bottom = "╝"

    left = "║"
    right = "║"
    top = "═"
    bottom = "═"
    center = "║"

    left_middle = "╠"
    right_middle = "╣"
    top_middle = "╦"
    bottom_middle = "╩"


class Colors:
    BORDER = Fore.LIGHTBLUE_EX

    MODULE_NAME = Fore.LIGHTMAGENTA_EX
    MODULE_HEADER_TEXT = Fore.LIGHTCYAN_EX

    CONFIG_KEY_COLOR = Fore.LIGHTMAGENTA_EX
    CONFIG_VALUE_COLOR = Fore.LIGHTCYAN_EX


class AsciiPrints:
    pre_config_1 = '''
     ______   __  ___                          
    / ____/  /  |/  /_  _______________  __  __
   / /_     / /|_/ / / / / ___/ ___/ _ \/ / / /
  / __/    / /  / / /_/ / /  / /  /  __/ /_/ / 
 /_/      /_/  /_/\__,_/_/  /_/   \___/\__, /  
                                       /___/   '''


def print_logo():
    print(f"{Fore.LIGHTMAGENTA_EX}{AsciiPrints.pre_config_1}{Fore.RESET}\n")


def print_wallet_execution(wallet: "WalletData", wallet_index: int):
    print(
        f"\n"
        f"{Colors.BORDER}[{Fore.RESET}"
        f"{wallet_index + 1}"
        f"{Colors.BORDER}]{Fore.RESET} "
        f"{Colors.CONFIG_KEY_COLOR}{wallet.name}{Fore.RESET}"
        f" - "
        f"{Colors.CONFIG_VALUE_COLOR}{wallet.address}{Fore.RESET}"
    )
    print(
        f"{Colors.CONFIG_KEY_COLOR}PK{Fore.RESET}"
        f" - "
        f"{Colors.CONFIG_VALUE_COLOR}{blur_private_key(wallet.private_key)}{Fore.RESET}"
    )


if __name__ == '__main__':
    wallet = WalletData(
        name="Aidar",
        private_key="0xbd910e6b3a04f879602656546b97291ca035cd46a01b812ef6bc66c97f75b477",
    )

    print_wallet_execution(wallet, 3)
