# bot-downloader-videos-twitter

## Steps to run the code

### Create an App in developer portal in Dropbox:
https://www.dropbox.com/developers/apps/create

### Create an app in Twitter developer portal

https://developer.twitter.com/en/portal/dashboard


#### Replace the token and keys in:
```bash
config_example.yaml
```
and replace as:
```bash
config.yaml
```
it should look like this:
```yaml
authentication:
  api_key: "xxxxxxxxxx"
  api_secret_key: "xxxxxxxxxxxxxx"
  access_token: "xxxx-xxxxxxxxxx"
  access_token_secret: "xxxxxxxxxxxxxxxx"
  dropbox_acess_token: "sl.xxxxxxxxxxxxx-xxxxxxxxxxxx-xxxxxxxxxxxxxx"
```

Execute python runner file:
```bash
python3 runner.py
```
