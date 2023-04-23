# Run this by putting "t" in the interpreter options
# when prompted


def ASCIIfier():
    string: str = input("Enter the string you'd like to ASCIIfy:\n")

    output_method: str = input(
        "Please enter the place you'd like ASCIIfier to output to (either \"file\" or \"console\"): "
    )

    ascii_string = [str(ord(i)) for i in string]

    # Step two: figure which way of pushing
    # is the most efficient character-wise

    # How many characters would be used
    # if we did a * for each character
    star_method_xtra = len(string)

    # How many characters would be used
    # if we did *20 45 ... 45
    map_method_xtra = 8

    if map_method_xtra < star_method_xtra:
        push_method = "map"
    else:
        push_method = "star"

    # Step three: Generate the Numbers code
    if push_method == "map":
        numbers_code = f"*20 45 {' '.join(ascii_string)} 45"
    else:
        numbers_code = "*" + " *".join(ascii_string)

    #Step four: Output
    if output_method == "file":
        try:
            with open("asciifier_output.txt", "x") as f:
                f.write(numbers_code)
        except FileExistsError:
            with open("asciifier_output.txt", "w") as f:
                f.write(numbers_code)
        print("Outputted the code into asciifier_output.txt!")
    else:
        print(numbers_code)


def debugger():
    pass


def tool_selector():
    print(
        "Tools! These tools are useful for doing certain tasks which are Numbers-adjacent."
    )
    print("Select the tool you'd like from the ones below:")
    print(
        "1. ASCIIfier\n\tGives the most optimal way to push a string to the stack in Numbers"
    )
    print("\nType q to quit")

    while True:
        selected = input()

        if selected == "q":
            quit("Quitting...")
        elif selected == "1":
            ASCIIfier()
        else:
            print(
                "Your input wasn't one of the available options. Please try again: "
            )
            continue
        quit()