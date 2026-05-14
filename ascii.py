if __name__ == "__main__":
    name = input("COME TI CHIAMI? ")
    print("\nNUMERI:")
    for c in name:
        print(f"    '{c}' : {ord(c)}")

    print(f"\n  {name} = {', '.join(str(ord(c)) for c in name)}")
