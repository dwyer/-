#!/bin/sh
filename="${HOME}/Dropbox/yanjiu.db.sqlite3.$(date '+%Y-%m-%d').tar.gz"
tar czf "${filename}" db.sqlite3
echo "${filename}"
