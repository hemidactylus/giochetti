import sys

if __name__ == "__main__":
    fname = sys.argv[1]
    nbytes: int
    if len(sys.argv) > 2:
        nbytes = int(sys.argv[2])
    else:
        nbytes = 40
    opened = open(fname, "rb")
    first_bytes = opened.read(nbytes)
    print(f"INIZIO DI '{fname}':")
    print("    ", end="")
    for b in first_bytes:
        print(b, end="  ")
    print(" ... ...")
