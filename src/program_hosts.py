import services.data_service as svc
from infrastructure import state

def create_account():
    print('****************** REGISTER ******************')

    name = input("What is your name? ")
    email = input("What is your email address? ")

    state.active_account = svc.create_account(name, email)