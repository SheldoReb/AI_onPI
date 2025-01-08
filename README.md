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