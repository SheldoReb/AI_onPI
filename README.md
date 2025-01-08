# AI_onPI

```bash
docker build -t ag2_base_img:latest .
```

```bash
docker run -it -v $(pwd):/home/ag2ai/aiONpi ag2_img:latest python /home/ag2ai/aiONpi/captain.py
```

For Windows:
```bash
docker run -it -v //var/run/docker.sock:/var/run/docker.sock -v C:/Users/Sheldon/Documents/GIT/AI_onPI:/home/ag2ai/aiONpi ag2_img:latest
```

```bash
docker run --name=appdaemon -d -p 5050:5050   -e HA_URL="http://localhost:8123"   -e TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJiMjc5MDMwZWZhOWE0NGI4YjkzZWQ0YTFmZDQ3YzkzOCIsImlhdCI6MTczNjI4NDcxOSwiZXhwIjoyMDUxNjQ0NzE5fQ.BsjZQaYISpDL1q7pQibgv-RUK65JdHjdmazmeSZ-GSc"   -e DASH_URL="http://$HOSTNAME:5050" --network="host" -v /home/pi/docker/appdaemon:/conf  -v /home/pi/docker/homeassistant/appdaemon/apps/:/homeassistant/appdaemon/apps acockburn/appdaemon:latest
```
