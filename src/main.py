import sys

from generate import generate, generate_pages_recursive


def main():
    basepath: str = sys.argv[0]
    if not basepath:
        basepath = "/"

    generate("./docs", "./static")
    generate_pages_recursive(basepath, "./content", "template.html", "./docs")


if __name__ == "__main__":
    main()
