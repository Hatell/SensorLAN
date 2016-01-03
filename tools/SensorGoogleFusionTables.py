#!/usr/bin/python
# vi: et sw=2 fileencoding=utf8
#

import argparse
import json
import sys

from apiclient.discovery import build
from httplib2 import Http
from oauth2client.client import SignedJwtAssertionCredentials

from decimal import Decimal
from datetime import datetime

from SensorLAN import SensorXML


parser = argparse.ArgumentParser()

parser.add_argument(
  "--json-key",
  help="Private JSON key file",
  type=argparse.FileType("rb"),
  required=True,
)
parser.add_argument(
  "--table",
  metavar="ID",
  help="Special value: new and delete-<table-id>",
)
parser.add_argument(
  "--input",
  "-i",
  type=argparse.FileType("rb"),
)

args = parser.parse_args()

key = json.loads(args.json_key.read())

credentials = SignedJwtAssertionCredentials(
  key["client_email"],
  key["private_key"],
  "https://www.googleapis.com/auth/fusiontables",
)

fusiontables = build("fusiontables", "v2", http=credentials.authorize(Http()))


if args.table is None:
  result = fusiontables.table().list().execute()

  print u"Please select one of tables:"
  print " - new, create new table"

  for r in result.get("items", []):
    print u" - %s, %s" % (r["tableId"], r["name"])

  sys.exit()

if args.table == "new":
  # FIXME Howto view created table with your account?
  #res = fusiontables.table().insert(body={
  #  "columns": [
  #    {
  #      "kind": "fusiontables#column",
  #      "columnId": 0,
  #      "name": "id",
  #      "type": "STRING",
  #      "description": "Sensor's ID",
  #    },
  #    {
  #      "kind": "fusiontables#column",
  #      "columnId": 1,
  #      "name": "name",
  #      "type": "STRING",
  #      "description": "Sensor's Name",
  #    },
  #    {
  #      "kind": "fusiontables#column",
  #      "columnId": 2,
  #      "name": "time",
  #      "type": "DATETIME",
  #      "description": "Timestamp",
  #    },
  #    {
  #      "kind": "fusiontables#column",
  #      "columnId": 3,
  #      "name": "value",
  #      "type": "NUMBER",
  #      "description": "Timestamp",
  #    },
  #  ],
  #  "isExportable": True,
  #  "name": "SensorLAN",
  #}).execute()

  #args.table = res["tableId"]
  print u"Create fusion table:"
  print u" - (id STRING, name STRING, time DATETIME, value NUMBER)"
  print u" - share it with this email %s" % key["client_email"]
  sys.exit()
elif args.table.startswith("delete-"):
  print u"Deleting table", args.table[7:]
  print fusiontables.table().delete(tableId=args.table[7:]).execute()
  sys.exit()


if args.input is None:
  sys.exit()

xml = SensorXML()
d = xml.parse(args.input.read())

time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

for s in d["Sensors"]:
  query = u"INSERT INTO %s (id, name, time, value) VALUES ('%s', '%s', '%s', '%s')" % (
    args.table,
    s["id"],
    s["name"],
    time,
    s["value"],
  )

  print fusiontables.query().sql(sql=query).execute()

