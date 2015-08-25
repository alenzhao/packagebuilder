import sys
import json
import time
import tempfile
import os
import subprocess
import platform
from datetime import datetime, date, time
from stompy import Stomp

## this may need to change:
num_builders = 4

bioc_r_map = {"2.7": "2.12", "2.8": "2.13", "2.9": "2.14",
    "2.10": "2.15", "2.14": "3.1", "3.0": "3.1", "3.1": "3.2", "3.2": "3.2"} 

# set up django environment
path = os.path.abspath(os.path.dirname(sys.argv[0]))
segs = path.split("/")
segs.pop()
path =  "/".join(segs)
sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'spb_history.settings'
# now you can do stuff like this:
#from spb_history.viewhistory.models import Package
#print Package.objects.count()

from spb_history.viewhistory.models import Job
from spb_history.viewhistory.models import Package
from spb_history.viewhistory.models import Build
from spb_history.viewhistory.models import Message
try:
    stomp = Stomp("broker.bioconductor.org", 61613)
    # optional connect keyword args "username" and "password" like so:
    # stomp.connect(username="user", password="pass")
    stomp.connect()
except:
    print("Cannot connect")
    raise

# do we want acks?
stomp.subscribe({'destination': "/topic/buildjobs", 'ack': 'client'})
stomp.subscribe({'destination': "/topic/builderevents", 'ack': 'client'})

def parse_time(time_str):
    """ take a string like 'Tue Nov 29 2011 11:55:40 GMT-0800 (PST)'
        and convert it to a DateTime """
    segs = time_str.split(" GMT")
    return(datetime.strptime(segs[0], "%a %b %d %Y %H:%M:%S"))

def handle_job_start(obj):
    pkg = obj['job_id'].split("_")[0]
    pkg = pkg.strip()
    try:
        existing_pkg = Package.objects.get(name=pkg)
    except Package.DoesNotExist:
        existing_pkg = Package(name=pkg)
        existing_pkg.save()
    
    j = Job(package=existing_pkg,
      job_id=obj['job_id'],
      time_started=parse_time(obj['time']),
      pkg_url=obj['svn_url'],
      force=obj['force'],
      client_id=obj['client_id'],
      bioc_version=obj['bioc_version'],
      r_version=bioc_r_map[obj['bioc_version']])
    j.save()

def handle_dcf_info(obj, build):
    build.maintainer = obj['maintainer']
    build.version = obj['version']
    build.save()

def handle_first_message(obj, parent_job):
    build = Build(job=parent_job,
      builder_id=obj['builder_id'],
      jid=obj['job_id'],
      maintainer='',
      version='0.0.0',
      preprocessing_result='',
      buildsrc_result='',
      checkinstall_result='',
      checksrc_result='',
      buildbin_result='',
      postprocessing_result='',
      svn_cmd='',
      check_cmd='',
      r_cmd='',
      r_buildbin_cmd='',
      os='',
      arch='',
      r_version='',
      platform='',
      invalid_url=False,
      build_not_required=False,
      build_product='',
      filesize=-1)
    build.save()
    return(build)

def handle_phase_message(obj):
    if obj.has_key('sequence'):
        sequence = obj['sequence']
    else:
        sequence = -1
    
    if obj.has_key('retcode'):
        retcode = obj['retcode']
    else:
        retcode = -1
    
    msg = Message(build = get_build_obj(obj),
      build_phase = obj['status'],
      sequence=sequence,
      retcode=retcode,
      body=obj['body'])
    msg.save()

def get_build_obj(obj):
    return(Build.objects.get(jid=obj['job_id'], builder_id=obj['builder_id']))


def handle_complete(obj, build_obj):
    
    if obj.has_key("result_code"):
        obj['retcode'] = obj['result_code']
    if obj['retcode'] == 0:
        if obj.has_key("warnings") and obj['warnings'] == True:
            result = "WARNINGS"
        else:
            result = "OK"
    else:
        result = "ERROR"
    print("in handle_complete(), status is %s and result is %s." % (obj['status'], result))
    if (obj['status'] == 'build_complete'):
        build_obj.buildsrc_result = result
        if result == "ERROR":
            build_obj.checksrc_result = "skipped"
            build_obj.buildbin_result = "skipped"
            build_obj.postprocessing_result = "skipped"
    elif (obj['status'] == 'check_complete'):
        if result == "ERROR":
            #build_obj.buildbin_result = "skipped"
            build_obj.postprocessing_result = "skipped"
        build_obj.checksrc_result = result
        if "Linux" in build_obj.os:
            build_obj.buildbin_result = "skipped"
    elif (obj['status'] == 'buildbin_complete'):
        if result == "ERROR":
            build_obj.postprocessing_result = "skipped"
        build_obj.buildbin_result = result
    elif (obj['status'] == 'post_processing_complete'):
        build_obj.postprocessing_result = result
    build_obj.save()

def handle_builder_event(obj):
    phases = ["building", "checking", "buildingbin", "preprocessing",
      "post_processing"]
    parent_job = None
    job_id = None
    if (obj.has_key('job_id')):
        job_id = obj['job_id']
        try:
            parent_job = Job.objects.get(job_id=job_id)
        except Job.DoesNotExist:
            print("No parent job for %s; ignoring message." % job_id)
            return()
        except Job.MultipleObjectsReturned:
            print("Multiple objects returned!")
            return()
    else:
        print("Malformed message, ignoring it.")
        return
    build_obj = None
    if(obj.has_key('first_message') and obj['first_message'] == True):
        print("handling first message")
        build_obj = handle_first_message(obj, parent_job)
    if (obj.has_key('status')):
        status = obj['status']
        sys.stdout.flush()
        try:
            build_obj = get_build_obj(obj)
        except Exception as e:
            print "Caught  exception: ", e
            return
        if (status == 'dcf_info'):
            print("handling dcf info")
            handle_dcf_info(obj, build_obj)
        elif (status in phases):
            if obj['status'] == 'post_processing':
                if obj.has_key('build_product'):
                    build_obj.build_product = obj['build_product']
                if obj.has_key('filesize'):
                    build_obj.filesize = obj['filesize']
                    build_obj.save()
                    return()
            handle_phase_message(obj)
        elif (status == 'svn_cmd'):
            build_obj.svn_cmd = obj['body']
            build_obj.save()
        elif (status == 'check_cmd'):
            build_obj.check_cmd = obj['body']
            build_obj.save()
        elif (status=='r_cmd'):
            build_obj.r_cmd = obj['body']
            build_obj.save()
        elif (status=='r_buildbin_cmd'):
            build_obj.r_buildbin_cmd = obj['body']
            build_obj.save()
        elif (status=='skip_buildbin'):
            build_obj.buildbin_result = 'skipped'
            build_obj.save()
        elif (status in ['build_complete', 'check_complete',
          'buildbin_complete', 'post_processing_complete']):
            handle_complete(obj, build_obj)
        elif (status == 'node_info'):
            bioc_version = obj['bioc_version']
            build_obj.r_version = bioc_r_map[bioc_version]
            build_obj.os = obj['os']
            build_obj.arch = obj['arch']
            build_obj.platform = obj['platform']
            build_obj.save()
        elif (status == 'invalid_url'):
            build_obj.invalid_url = True
            build_obj.save()
            job = build_obj.job
            pkg = job.package
            pkg.delete()
            job.delete()
            build_obj.delete()
            return(1)
        elif (status == 'build_not_required'):
            build_obj.build_not_required = True
            build_obj.buildsrc_result = 'skipped'
            build_obj.preprocessing_message = "Build not required, versions identical in source and repository, and force not specified."
            build_obj.save()
        elif (status == 'build_failed'):
            build_obj.buildsrc_result = 'ERROR'
            build_obj.checksrc_result = 'skipped'
            build_obj.buildbin_result = 'skipped'
            build_obj.postprocessing_result = 'skipped'
            build_obj.save()
        else:
            print("ignoring message:%s" % obj)
    else:
        print("invalid message, no 'status' key: %s" % obj)
        # svn_result,
        # clear_check_console, starting_check,
        # starting_buildbin, svn_info,
        # chmod_retcode*,
        # normal_end

    

def callback(body, destination):
    print " [x] Received %r" % (body,)
    sys.stdout.flush() ## make sure we see everything
    received_obj = None
    try:
        received_obj = json.loads(body)
    except ValueError as e:
        print("!!!Received invalid JSON!!!")
        print("Invalid json was: %s" % body)
        return
    if('job_id' in received_obj.keys()): 
        if (destination == '/topic/buildjobs'):
            handle_job_start(received_obj)
        elif (destination == '/topic/builderevents'):
            handle_builder_event(received_obj)
        print("Destination: %s" % destination)
    else:
        print("Invalid json (no job_id key)")

print("Waiting for messages...")

while True:
    try:
        frame = stomp.receive_frame()
        stomp.ack(frame) # do this?
        callback(frame.body, frame.headers.get('destination'))
    except KeyboardInterrupt:
        stomp.disconnect()
        break


