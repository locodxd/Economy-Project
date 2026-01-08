import os

def main():
    print("Welcome to the Economy Project Launcher!")
    print("Choose an option:")
    print("1. Run Discord Bot")
    print("2. Run Pygame Game")
    
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == '1':
        os.system('python src/bot/main.py')
    elif choice == '2':
        os.system('python src/game/main.py')
    else:
        print("Invalid choice. Please select 1 or 2.")

if __name__ == "__main__":
    main()