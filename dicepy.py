# A script that records a list of dice throws and calculates the chances of the dice being loaded.

import matplotlib.pyplot as plt
import math

class RollCounter:
    def __init__(self, sides = 0):
        self.sides = sides
        self.counter = [0 for i in range(sides)]

        self.__iter_index = 0
    
    def count(self, roll):
        self.counter[roll - 1] += 1
    
    def reset(self, sides = None):
        if sides == None:
            self.counter = [0 for i in range(self.sides)]
        else:
            self.sides = sides
            self.counter = [0 for i in range(sides)]

    def __str__(self):
        return str(self.counter)

    def __iter__(self):
        self.__iter_index = 0
        return self.counter
    
    def __next__(self):
        if self.__iter_index >= self.sides:
            raise StopIteration
        else:
            self.__iter_index += 1
            return self.counter[self.__iter_index - 1]


class Menu:
    def __init__(self, title):
        self.title = title
        self.options = []
    
    def add_option(self, title, select_val, output_val, desc):
        option = MenuOption(title, select_val, output_val, desc)
        self.options.append(option)
    
    def select_option(self, select_val):
        for option in self.options:
            if select_val == option.select_val:
                return option.output_val
        return None

    def __str__(self):
        menu_str = self.title.center(32, "-") + "\n"
        menu_str += "Title".ljust(16) + "Select".ljust(8) + "\n"
        for option in self.options:
            menu_str += option.title.ljust(16) + f"({option.select_val})".ljust(8) + "\n"
        menu_str += "Enter the select value for the option you wish to choose: "
        return menu_str
    
    def __repr__(self):
        return f"Menu({self.title})"
    
    def __len__(self):
        return len(self.options)
                    

class MenuOption:
    def __init__(self, title, select_val, output_val, desc):
        self.title = title
        self.select_val = select_val
        self.output_val = output_val
        self.desc = desc


def options_state():
    # This state allows the user to navigate between different states of the program.
    menu = Menu("Options")
    menu.add_option("Input data", "In", 1, "Enter the dice throws.")
    menu.add_option("Output data", "Out", 2, "Calculate the chances of the dice being loaded.")
    menu.add_option("Save data", "Save", 3, "Save the dice throws to a file.")
    menu.add_option("Load data", "Load", 4, "Load the dice throws from a file.")
    menu.add_option("Exit", "Exit", -1, "Exit the program.")
    print(menu)
    while True:
        select_val = input()
        output_val = menu.select_option(select_val)
        if output_val is not None:
            return output_val
        else:
            print("Invalid input. Please Select an option from the menu.")

def input_data_state(**kwargs):
    # This state allows the user to enter data into the global dice roll counter.
    roll_counter = kwargs.get("roll_counter")
    print("Input data".center(32, "-"))
    while True:
        try:
            sides = int(input(f"How many sides does your dice have? (Current loaded data has {roll_counter.sides} sides.) "))
            if sides < 1:
                raise ValueError
        except ValueError:
            print("Invalid input. Please enter a positive integer.")
            continue
        else:
            if sides != roll_counter.sides:
                check = input(f"Are you sure you want to change the number of sides from {roll_counter.sides} to {sides}? This will clear the data you have loaded in the roll counter. (y/n) ")
                if check.lower().strip() in ("y", "yes"):
                    roll_counter.reset(sides)
                    print(f"Roll counter has been reset to {sides} sides.")
                    break
            else:
                break

    print("Enter each dice throw on a new line, enter '-1' or 'done' to finish.")
    while True:
        data = input()
        if data in ("-1", "done"):
            break
        else:
            try:
                data = int(data)
                if data < 1 or data > sides:
                    raise ValueError
            except ValueError:
                print("Invalid input.")
            else:
                roll_counter.count(data)
    print("Data entered successfully.")
    return 0

def resample(data):
    # This function resamples the data to a 2 roll system.
    resampled_data = [0]*(len(data)*2)
    for i, counti in enumerate(data): # We do alomst twice the amount of calculations necessary here, but shuold be fine.
        for j, countj in enumerate(data):
            resampled_data[i + j + 1] += counti + countj
    return resampled_data

def print_table_of_stats(data):
    sum_rolls = sum(data)
    print("Rolls".ljust(8) +
          "Count".ljust(8) +
          "Proportion".ljust(8) )
    for i, count in enumerate(data):
        print(f"{i + 1}".ljust(8) +
              f"{count}".ljust(8) +
              f"{count / sum_rolls:.4f}".ljust(8) )
    print("Total".ljust(8) + f"{sum_rolls}".ljust(8) + "1.0".ljust(8))

def output_data_state(**kwargs):
    # This displays the data in the roll counter, and does some statistics on it.
    roll_counter = kwargs.get("roll_counter")
    print("Output data".center(32, "-"))

    # Setup the figure
    sum_rolls = sum(roll_counter.counter)
    fig = plt.figure()
    fig.suptitle(f"Dice Roll Data (n = {sum_rolls})")

    # Printing the basic stuff
    print_table_of_stats(roll_counter.counter)
    u = (sum(count*(i + 1) for i, count in enumerate(roll_counter.counter))/sum_rolls)
    print(f"Average: {u:.4f}")
    SD = ( sum(count*(i + 1 - u)**2 for i, count in enumerate(roll_counter.counter))/sum_rolls )**0.5
    print(f"Standard Deviation: {SD:.4f}")
    ax1 = fig.add_subplot(221)
    ax1.title.set_text("Raw Roll Counts")
    x = [i + 1 for i in range(roll_counter.sides)]
    y = [count for count in roll_counter.counter]
    ax1.bar(x, y)

    # Expected values under 2 roll resampling
    print("\nExpected average and standard deviation under 2 roll resampling:")
    resampled_data = resample([1]*roll_counter.sides)
    print_table_of_stats(resampled_data)
    resample_expected_u = 1 + roll_counter.sides
    # u1 = (sum(count*(i + 1) for i, count in enumerate(resampled_data))/sum(resampled_data))
    print(f"Expected Average: {resample_expected_u:.4f}")
    resample_expected_SD = ( sum(count*(i + 1 - resample_expected_u)**2 for i, count in enumerate(resampled_data))/sum(resampled_data) )**0.5
    print(f"Expected Standard Deviation: {resample_expected_SD:.4f}")
    ax2 = fig.add_subplot(223)
    ax2.title.set_text("Expected 2 Roll Resampling")
    x = [i + 1 for i in range(len(resampled_data))]
    y = [count for count in resampled_data]
    ax2.bar(x, y)

    # Actual results under 2 roll resampling
    print("\nActual average and standard eeviation under 2 roll resampling:")
    resampled_data = resample(roll_counter.counter)
    print_table_of_stats(resampled_data)
    resample_actual_u = (sum(count*(i + 1) for i, count in enumerate(resampled_data))/sum(resampled_data))
    print(f"Actual Average: {resample_actual_u:.4f}")
    resample_actual_SD = ( sum(count*(i + 1 - resample_actual_u)**2 for i, count in enumerate(resampled_data))/sum(resampled_data) )**0.5
    print(f"Actual Standard Deviation: {resample_actual_SD:.4f}")
    ax3 = fig.add_subplot(224)
    ax3.title.set_text("Actual 2 Roll Resampling")
    x = [i + 1 for i in range(len(resampled_data))]
    y = [count for count in resampled_data]
    ax3.bar(x, y)

    # Little bit extra info
    print("\nSummary:")
    u_diff = resample_expected_u - resample_actual_u
    print(f"Average difference: {u_diff:.4f}")
    SD_diff = resample_expected_SD - resample_actual_SD
    print(f"Standard Deviation difference: {SD_diff:.4f}")
    plt.show()
    print("\n")
    return 0
    
def save_data_state(**kwargs):
    # In this state the user can save data to a file.
    roll_counter = kwargs.get("roll_counter")
    print("Save data".center(32, "-"))
    filename = input("Enter the filename you wish to save the data to: ") + ".drs" # drs = dice roll stats
    with open(filename, "w") as file:
        file.write(f"{roll_counter.sides}\n")
        file.write(" ".join(str(count) for count in roll_counter.counter))
    print(f"Data saved to {filename}.")
    return 0

def load_data_state(**kwargs):
    # In this state the user can load data from a file.
    roll_counter = kwargs.get("roll_counter")
    print("Load data".center(32, "-"))
    filename = input("Enter the filename you wish to load the data from: ") + ".drs" # drs = dice roll stats
    try:
        with open(filename, "r") as file:
            sides = int(file.readline())
            counter = [int(count) for count in file.readline().split()]
            roll_counter.reset(sides)
            for i, count in enumerate(counter):
                roll_counter.counter[i] = count
        print(f"Data loaded from '{filename}'.")
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
    except ValueError:
        print(f"Invalid data in file '{filename}'.")
    return 0

roll_counter = RollCounter()
def main():
    state = 0 # 0 = options, 1 = input data, 2 = output data, 3 = save data, 4 = load data, -1 = exit
    while True:
        if state == -1:
            break
        elif state == 0:
            state = options_state()
        elif state == 1:
            state = input_data_state(roll_counter = roll_counter)
        elif state == 2:
            state = output_data_state(roll_counter = roll_counter)
        elif state == 3:
            state = save_data_state(roll_counter = roll_counter)
        elif state == 4:
            state = load_data_state(roll_counter = roll_counter)
        else:
            print("Uh oh! Attempted to enter an invalid state. Redirecting to options state.")
            state = 0
    print("Goodbye!")

if __name__ == "__main__":
    main()
