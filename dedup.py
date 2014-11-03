#!/usr/bin/env python

import json
import sys
import sys
import glob
import os
import csv

def weight_score(score, module_id):
  weights = [0.55, 0.30, 0.15]
  return (score * weights[module_id - 1])

def parse_affinities(customers, filepath, email_id, module_id):
  with open(filepath) as f:
    for line in f:
      line = json.loads(line)
      data = {'id':line["id"], 'score':float(line["norm_score"])}

      cust_id = data['id']
      if cust_id not in customers:
        customers[cust_id] = {}

      if email_id not in customers[cust_id]:
        customers[cust_id][email_id] = {'score':0, 'email':email_id}

      w_score = weight_score(data['score'], module_id)
      customers[cust_id][email_id]['score'] += w_score

  return(customers)

def find_top(emails):
  return sorted(emails, key=lambda email: float(email['score']), reverse=True)[0]

if len(sys.argv) < 2:
  print "ERROR: call with campaign directory"
  print "Example: ./dedup ./campaigns/tuesday_2_24"
  sys.exit(1)

campaign_filepath = sys.argv[1]
if os.path.isdir(campaign_filepath):
  print "scanning: " + campaign_filepath + " for email modules"
else:
  print "ERROR: input must be the campaign directory"
  print campaign_filepath + " is not a directory"
  sys.exit(1)

campaign_dirs = campaign_filepath.split("/")
campaign_dirs = filter(None, campaign_dirs)

print campaign_dirs
campaign_id = campaign_dirs[-1]

print "campaign id: " + campaign_id


email_dirs = glob.glob(campaign_filepath + "/*")

customers = {}
for email_dir in email_dirs:
  if not (os.path.isdir(email_dir)):
    continue

  print email_dir + "\n"
  email_id = os.path.basename(email_dir)
  print email_id + "\n"


  module_files = glob.glob(email_dir + "/*.out")
  if len(module_files) == 0:
    print "no modules for " + email_id + " - skipping"
    continue

  for i, module_file in enumerate(module_files):
    print module_file + "\n"
    customers = parse_affinities(customers, module_file, email_id, (i + 1))
    print len(customers)



output_filename = campaign_filepath + "/" + campaign_id + ".tsv"
file = open(output_filename, 'w')
headers = ['id', 'email_id', 'score']
writer = csv.writer(file, delimiter="\t")
writer.writerow(headers)
for cust_id, email_dict in customers.iteritems():
  top_email = find_top(email_dict.values())
  data = [cust_id, top_email['email'], top_email['score']]
  writer.writerow(data)

file.close()
  
