import data.mongo_setup as mongo_setup


def main():
    mongo_setup.global_init()

    print_header()


def print_header():
    print("*******************************************")
    print("       Welcome to Snake BnB")
    print("*******************************************")
    print()
