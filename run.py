#!flask/bin/python

from app import app
app.run(host="192.168.57.223", port=9000, debug=True)