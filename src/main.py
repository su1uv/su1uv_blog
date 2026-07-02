from generate import generate, generate_pages_recursive


def main():
    generate("./public", "./static")
    generate_pages_recursive("./content", "template.html", "./public")


if __name__ == "__main__":
    main()
