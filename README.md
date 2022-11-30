# Too Good To Go Favorites Notifier


This Python script will check your Too Good To Go account for your favorite items and alert you when an item goes from sold out to available. 

This is useful for stores that get sold out quickly and you want to know as soon you can order. 

This will only notify you, you must still actually place the order in the app yourself.

## Usage

You'll need [`pipenv`](https://pipenv.pypa.io/en/latest/).

#### Checkout the repo:
```bash
$ git clone https://github.com/amandeepg/tgtg-fav-notifier.git
$ cd tgtg-fav-notifier
```

#### Before setting up alerts, you must login:
```bash
$ pipenv run python main.py --login
```

#### Then you can add the script to run periodically via cron:
```bash
$ crontab -e
```
#### And add a line like:
```
*/5 * * * * cd /home/{user}/tgtg-fav-notifier && /home/{user}/.local/bin/pipenv run python main.py >> /home/am/.tgtg-fav-notifier.cron.log 2>&1
```
Making the appropriate changes for `{user}` and wherever your `pipenv` (`which pipenv`) is.

Now every 5 minutes the script will check if any favorite went from sold out to available and send an OS notification locally.

### Optional hook
By default the script only alerts you with an OS notification, but if you want to do anything custom, the script supports an optional hook.
The script will call `~/.tgtg-fav-notifier-hook.sh` with 2 parameters: 1) the title of alert 2) the body of the alert, telling you which store now has stock

#### Example
You could have your phone also be notified by using [IFFFT's webhooks](https://help.ifttt.com/hc/en-us/articles/115010230347):

```bash
#!/usr/bin/env bash

curl -X POST -H "Content-Type: application/json" -d "{ \"value1\" : \"$1\", \"value2\" : \"$2\" }" http://maker.ifttt.com/trigger/{event_name}/with/key/{key}
```
