import sys

if __name__ == "__main__":
    fname = sys.argv[1]
    opened = open(fname, "rb")
    first_bytes = opened.read(40)
    print(f"INIZIO DI '{fname}':")
    print("    ", end="")
    for b in first_bytes:
        print(b, end="  ")
    print(" ... ...")
