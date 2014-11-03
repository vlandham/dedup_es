#!/usr/bin/env python

import json
import sys
import sys
import glob
import os
import csv
import math
from pprint import pprint

# def weight_score(score, module_id, module_count):
  # weights = [0.55, 0.30, 0.15, 0.15, 0.15, 0.15, 0.15]
  # return (score * weights[module_id])

def generate_weights(module_count):
  weights = [pow(0.5,i) for i in range(1, module_count + 1)]
  weights_sum = sum(weights)
  weights = [weight / weights_sum for weight in weights]
  return weights

def parse_affinities(customers, filepath, email_id, module_id, module_count):
  weights = generate_weights(module_count)
  with open(filepath) as f:
    for line in f:
      line = json.loads(line)
      data = {'party_id':line["party_id"], 'score':float(line["nscore"])}

      cust_id = data['party_id']
      if cust_id not in customers:
        customers[cust_id] = {}

      if email_id not in customers[cust_id]:
        customers[cust_id][email_id] = {'score':0, 'email':email_id}

      w_score = round(data['score'] * weights[module_id], 4)
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
  print "mod count"
  print len(module_files)
  if len(module_files) == 0:
    print "no modules for " + email_id + " - skipping"
    continue

  for i, module_file in enumerate(sorted(module_files)):
    print module_file + "\n"
    customers = parse_affinities(customers, module_file, email_id, i, len(module_files))
    print "cust size:"
    print len(customers)



output_filename = os.path.abspath(campaign_filepath + "/" + campaign_id + ".tsv")
print "writing to:"
print output_filename
file = open(output_filename, 'w')
headers = ['party_id', 'email_id', 'score']
writer = csv.writer(file, delimiter="\t")
writer.writerow(headers)
for cust_id, email_dict in customers.iteritems():
  # print cust_id
  # pprint(email_dict)
  top_email = find_top(email_dict.values())
  # pprint(top_email)
  data = [cust_id, top_email['email'], top_email['score']]
  writer.writerow(data)

file.close()
  
