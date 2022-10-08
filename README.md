# Repost to discord bot

## Setup

1. download with git or cURL
2. cd into the git directory

```
nano ./main.py 
```

3. in the file add your discord webhook url into the *webhook* variable 
4. add your bearer token into the *bear_token* variable
5. add the twitter users into the *at* (only the part after the @ sign ) --> for https://twitter.com/NASA add "NASA" to list
6. save the file


```
pip install -r requirements.txt
sudo chmod +x ./bot.py
```

### Or add as a cronjob to execute after startup

```
crontab -e
```

add: *@reboot python3 path/to/file/main.py* to file