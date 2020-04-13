from dateutil import parser
from infrastructure.switchlang import switch
import program_hosts as hosts
import infrastructure.state as state
from program_hosts import error_msg, success_msg
import services.data_service as svc
import datetime


def run():
    print(' ****************** Welcome guest **************** ')
    print()

    show_commands()

    while True:
        action = hosts.get_action()

        with switch(action) as s:
            s.case('c', hosts.create_account)
            s.case('l', hosts.log_into_account)

            s.case('a', add_a_snake)
            s.case('y', view_your_snakes)
            s.case('b', book_a_cage)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')

            s.case('?', show_commands)
            s.case('', lambda: None)
            s.case(['x', 'bye', 'exit', 'exit()'], hosts.exit_app)

            s.default(hosts.unknown_command)

        state.reload_account()

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('[L]ogin to your account')
    print('[B]ook a cage')
    print('[A]dd a snake')
    print('View [y]our snakes')
    print('[V]iew your bookings')
    print('[M]ain menu')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def add_a_snake():
    print(' ****************** Add a snake **************** ')

    if not state.active_account:
        error_msg('You must login first to add a snake.')
        return

    name = input('What is the name of your snake? ')
    if not name:
        error_msg('Cancelled')
        return

    length = float(input('How long is your snake (in meters)? '))
    species = input('Species? ')
    is_venomous = input('Is your snake venomous [y,n]? ').lower().startswith('y')

    snake = svc.add_snake(state.active_account, name, length, species, is_venomous)
    state.reload_account()
    success_msg(f'Created {snake.name} with id {snake.id}.')


def view_your_snakes():
    print(' ****************** Your snakes **************** ')

    if not state.active_account:
        error_msg('You must login first to view your snakes.')
        return

    snakes = svc.get_snakes_for_user(state.active_account.id)
    print(f'You have {len(snakes)} snakes.')
    for s in snakes:
        print(f" * {s.name} is a {s.species} that is "
              f"{s.length}m long and is {('' if s.is_venomous else 'not ')}venomous.")


def book_a_cage():
    print(' ****************** Book a cage **************** ')
    if not state.active_account:
        error_msg('You must login first to book a cage.')
        return

    snakes = svc.get_snakes_for_user(state.active_account.id)
    if not snakes:
        error_msg('You must first [a]dd a snake before you can book a cage.')
        return

    print("Let's start by finding available cages")
    start_text = input("Check in date [yyyy-mm-dd]? ")
    if not start_text:
        error_msg('Cancelled')
        return

    checkin = parser.parse(start_text)
    checkout = parser.parse(
        input("Check out date [yyyy-mm-dd]? ")
    )

    if checkin > checkout:
        error_msg('Check in must be before checkout')
        return

    print()
    for idx, s in enumerate(snakes):
        print(f"{(idx + 1)}. {s.name} (length: {s.length}m, "
              f"venomous: {('yes' if s.is_venomous else 'no')})")

    snake = snakes[int(input("Which snake do you want book for (number)")) - 1]

    cages = svc.get_available_cages(checkin, checkout, snake)

    if not cages:
        error_msg('Sorry, no cages available for that date')

    print(f"There are {len(cages)} available during that time.")
    for idx, c in enumerate(cages):
        print(f" {(idx + 1)}. {c.name} with {c.square_meters}m, "
              f"carpeted: {('yes' if c.is_carpeted else 'no')}"
              f"has toys: {('yes' if c.has_toys else 'no')}.")

    cage = cages[int(input('Which cage would you like to book (number)? ')) - 1]

    svc.book_cage(state.active_account, snake, cage, checkin, checkout)

    success_msg(f"Successfully booked {cage.name} for {snake.name} "
                f"at €{cage.price} per night.")


def view_bookings():
    print(' ****************** Your bookings **************** ')

    if not state.active_account:
        error_msg('You must login first to view your bookings.')
        return

    snakes = {s.id: s for s in svc.get_snakes_for_user(state.active_account.id)}
    bookings = svc.get_bookings_for_user(state.active_account.email)

    print(f"You have {len(bookings)} bookings.")
    for b in bookings:
        print(f" * Snake: {snakes.get(b.guest_snake_id).name} is booked at"
              f" {b.cage.name} from "
              f"{datetime.date(b.check_in_date.year, b.check_in_date.month, b.check_in_date.day)}"
              f" for {(b.check_out_date - b.check_in_date).days} days.")
