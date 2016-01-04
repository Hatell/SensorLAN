#!/usr/bin/python
# vi: et sw=2 fileencoding=utf8
#
# python SensorGoogleFusionTablePlot.py \
# --id 28-000003ebf06a --color b \
# --id 28-000003eba295 --color r \
# --id 28-000003ebeaf7 --color g \
# --id 28-000003ebdfc2 --color k
 

from datetime import datetime

import sys
import json
import argparse

from apiclient.discovery import build
from httplib2 import Http
from oauth2client.client import SignedJwtAssertionCredentials


parser = argparse.ArgumentParser()
parser.add_argument(
  "--json-key",
  type=argparse.FileType("rb"),
  help="JSON private key file",
)
parser.add_argument(
  "--table",
  help="TableId",
)
parser.add_argument(
  "--min-date",
  metavar = "YYYY-DD-MM",
  default = datetime.now().strftime("%Y-%m-%d"),
)
parser.add_argument(
  "--max-date",
  metavar = "YYYY-DD-MM",
  default = datetime.now().strftime("%Y-%m-%d"),
)
parser.add_argument(
  "--date-view",
  default = False,
  action = "store_true",
)
parser.add_argument(
  "--id",
  default = [],
  action = "append",
  help = "Sensor id for example 28-000003ebdfc2",
)
parser.add_argument(
  "--color",
  default = None,
  action = "append",
  help = "Matlab color codes. r = red, b = blue etc."
)
args = parser.parse_args()

if args.color is not None:
  if len(args.color) != len(args.id):
    raise RuntimeError("define as many --color as --id")

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
  for r in result.get("items", []):
    print u" - %s, %s" % (r["tableId"], r["name"])

  sys.exit()

import pylab as pl
import numpy as np

x = {}
y = {}

for i in args.id:
  x[i] = []
  y[i] = []

if len(args.id) == 0:
  result = fusiontables.query().sql(
    sql="SELECT id, name FROM %s GROUP BY id, name" % (
      args.table,
    )
  ).execute()

  print u"Pleases select on or mode id:"

  for v in result["rows"]:
    print u" - %s, %s" % (v[0], v[1])

  sys.exit()

result = fusiontables.query().sql(
  sql="SELECT id, time, value FROM %s WHERE time >= '%s 00:00:00' AND time <= '%s 23:59:59' ORDER BY time" % (
    args.table,
    args.min_date,
    args.max_date,
  )
).execute()

for v in result["rows"]:
  v = dict(zip(result["columns"], v))

  if v["id"] not in x:
    x[v["id"]] = []
    y[v["id"]] = []

  x[v["id"]].append(datetime.strptime(v["time"], "%Y-%m-%d %H:%M:%S"))
  y[v["id"]].append(v["value"])

if args.color is not None:
  for i, c in zip(args.id, args.color):
    pl.plot_date(x[i], y[i], c + ".")
else:
  for i in args.id:
    pl.plot_date(x[i], y[i], "ro")

pl.show()
