cd ..
gunicorn -w 4 -p web_pid  -b 0.0.0.0:8080 --error-logfile=log/gunicorn_web.log -D  api.wsgi > log/out.log
