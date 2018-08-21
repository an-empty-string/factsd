# factsd

Factsd is the **facts daemon**. It lets you get/set variables (facts) over HTTP,
so you can access them from multiple machines. It supports flexible access
control, so you can give certain devices specific access to factsd.

# Installation

- `pip install git+https://github.com/an-empty-string/factsd.git`
- `factsd initdb`
- `factsd serve`

# Use cases

- Tasker on your phone sets a parking location fact when you get out of your
  car. You can view a map of it on your computer or retrieve it on your phone.
- [Your tea coaster](https://blog.benjojo.co.uk/post/tealemetry-IOT-tea-coaster)
  sets a fact about the temperature of your tea. You set up a change handler
  webhook that sends you a notification on Slack when your tea is at a drinkable
  temperature.
- You send your currently associated wifi network to a fact in factsd, then use
  factsd's history functionality to automatically fill out a timesheet with the
  time you spent at work.
