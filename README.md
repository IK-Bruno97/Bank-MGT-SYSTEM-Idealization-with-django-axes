# BANK MGT system
#Start rabbitmq(macOS)
brew services restart rabbitmq

#Start celery
python3 -m celery -A BankBrunoFoundation worker -l INFO




By default an unauthenticated user can only view the home/welcome page, then signup with an active email address for email authentication, receive the account activation link and once clicked, their acct becomes an active acct(user gets a default of $2000 on account activation) and thus be able to sign in and make transfers and deposits. The phone number provided on signup is used as acct number such that transfers to other users only succeeds if the acct number/phone exists in db.

Users can be able to change thier email address and password via the links that would be sent to thier existing email.

Alot more features can be added to this project to standardize it.



