#!flask/bin/python

from app import app
app.run(host="192.168.0.16", port=9000, debug=True)