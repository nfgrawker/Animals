"""Main file to get, parse and post animals."""
from delegates.animals import AnimalsDelegate

if __name__ == "__main__":
    delegate = AnimalsDelegate()
    delegate.get_all_animals()
    delegate.expand_animal_stubs()
    delegate.parse_and_send_lists_of_animals()