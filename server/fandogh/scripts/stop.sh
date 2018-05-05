lsof -i :8080 | tail -n +2 | awk '{print $2}' | xargs -n 1 kill -9
rm -f ../web_pid