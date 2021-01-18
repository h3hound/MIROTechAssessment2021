'''
Created on Jan 17, 2021

@author: h3usr
MIRO Tech test
list all jobs with a given job requirement skill
required skill: 'engineering and technology'
'''
# import required libs
import requests
import json
import datetime
import logging
import sys

# constant for destination
RBIN_URL='http://requestbin.net/r/1fna7l31'

# configure logging level  - could create a command line option  for level
logging.basicConfig(filename='appexp.log', filemode='a', format='%(asctime)s -%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
startRun = str(datetime.datetime.now())

# required skill search string - could create as command line arg1
strSkill = "engineering and technology"

# setup func to handle api urls
def get_request_data(url):
    try:
        response = requests.get(url)
# if we are not OK then error       
        if (response.status_code != 200):
           raise Exception("Problem with url {} reported status code: {} ; reason: {}".format(url,response.status_code,response.reason))
        return response
    except Exception as error:
        logging.error(error)
        sys.exit(1)

# get json response and build dictionary 
def get_json_from_url(url):
    try:
        output=get_request_data(url)
        return json.loads(output.text)
    except Exception as error:
        logging.error("Error with json parse for request {} :".format(url))
        sys.exit(1)

# Requirement: extract skill uuid for the search string
def get_jobs():
# get the uuid     
    skill_json=get_json_from_url("http://api.dataatwork.org/v1/skills/autocomplete?contains={}".format(strSkill))
    uuidSkill = skill_json[0]['uuid']
# get jobs with required  skill
    return (get_json_from_url("http://api.dataatwork.org/v1/skills/{}/related_jobs".format(uuidSkill)), uuidSkill)

# create a delimited file  - semi colon -  file of returned jobs in a numbered list
# could switch to use csv library
# Requirement: list all the jobs that have this skill in the job requirement
def write_jobs_to_file(jobs):
    jobRpt=open(strSkill +"jobsrpt_"+ str(datetime.datetime.now())  + ".csv", "a")
    rownum = 0
# iterate through all jobs in dictionary
    for i in jobs['jobs']:
        rownum = rownum + 1
        jobRpt.write(str(rownum) + ";" + i['job_uuid'] + ";" + i['job_title']+"\n")
    jobRpt.close()

# interface  - send json array of required skill jobs to destination
# decoode response to text and create backup of payload, send to bin, report processing
# Bonus requirement: Create an array of all the jobs with the skill and push the payload to a requestbin
def post_jobs_to_requestbin(jobs,uuidSkill):
    try:
        numJobs=0
        numJobs+=len(jobs['jobs'])
        plbkup=open(strSkill +"payload_"+ str(datetime.datetime.now())  + ".json", "w")
        backup_jobs_payload=json.dumps(jobs, indent=2)
        plbkup.write(backup_jobs_payload)
        plbkup.close()

# POST
        r_bin = requests.post(RBIN_URL, data=backup_jobs_payload)
        if (r_bin.status_code != 200):
           raise Exception("Problem with RequestBin reported status code: {} ; reason: {}".format(r_bin.status_code,r_bin.reason))
        return r_bin
   
# write a processing log 
        procRpt=open("procrpt_"+ str(datetime.datetime.now())  + ".txt", "a")
        procRpt.write("UUID: " + uuidSkill + " : " + strSkill+ "\n")
        procRpt.write("Start: " + startRun + " -  End: " + str(datetime.datetime.now()) + "\n")
        procRpt.write("Total jobs retrieved: " + str(numJobs) + "\n")
        procRpt.write("Bin POST: " + str(r_bin.status_code) + " " + r_bin.reason)
        procRpt.close()
        
    except Exception as error:
        logging.error(error)
        sys.exit(1) 

# main thing
jobs,uuidSkill = get_jobs()
write_jobs_to_file(jobs)
post_jobs_to_requestbin(jobs,uuidSkill)
