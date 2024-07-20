# This work is licensed under a Creative Commons Attribution 4.0 International License.
# You must give appropriate credit, provide a link to the license, and indicate if changes were made.
# Details: https://creativecommons.org/licenses/by/4.0/

banner_displayed = False

def display_banner():
    global banner_displayed
    if not banner_displayed:
        banner = """
        ===================================================
        ====  __                             __  _____ ====
        ==== / _\  ___  _ __  __ _  _ __    /__\/ _  / ====
        ==== \ \  / __|| '__|/ _` || '_ \  /_\  \// /  ====
        ==== _\ \| (__ | |  | (_| || |_) |//__   / //\ ====
        ==== \__/ \___||_|   \__,_|| .__/ \__/  /____/ ====
        ==== ScrapEZ webscraper    |_|      by jakk-er ====
        ===================================================
              \n \n"""
        print(banner)
        banner_displayed = True

if __name__ == "__main__":
    display_banner()
