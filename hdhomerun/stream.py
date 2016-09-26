import subprocess as sub
import signal
import os
import glob
import os.path
import time
import json
import cfg

def hasFFMPEG():
    ''' Checks for presence of ffmpeg '''
    try:
        status = sub.check_output(["which", "ffmpeg"])
    except:
        raise OSError("ffmpeg not found!")

def getPath(channel):
    path = "./static/streams/"
    
    if os.path.isdir(path) == False:
        os.mkdir(path)

    return path+channel

def getPid(channel):
    ''' Returns pid for requested channel '''
    
    streamPath = getPath(channel)
    
    # Check for current pid
    pidfile = os.path.isfile(streamPath+".pid")
    pid = None
    try:
        with open(streamPath+".pid") as f:
            pid = int(f.readline().rstrip())
            
    except:
        print 'Bad Pid file for '+channel
        
    return pid

def getStatus(channel):
    ''' Returns status for requested channel '''
    
    streamPath = getPath(channel)
    
    # Check if channel's m3u8 exists
    ready = os.path.isfile(streamPath+".m3u8")
    mtime = None
    if ready:
        mtime = time.ctime(os.path.getmtime(streamPath+".m3u8"))
    
    pid = getPid(channel)
    
    return json.dumps({"channel": channel, "ready": ready, "last_read": mtime, "pid": pid})

def stopStream(channel):
    ''' Find pid file, stop process, cleanup related stream files '''
    
    streamPath = getPath(channel)
    
    # Get pid
    pid = getPid(channel)
    
    # Stop ffmpeg process
    try:
        os.kill(pid, signal.SIGKILL)
    except:
        print "Processed already stopped or error stopping."
    
    # Remove .m3u8 and .ts files
    filelist = glob.glob(streamPath+"*")
    for f in filelist:
        os.remove(f)
    
def startStream(channel,devices,quality):
    ''' Finds available tuner and starts ffmpeg process for channel, saves pid file '''
    
    #Check for available tuner 
    for device in devices:
        status = cfg.getTunerStatus(device["dev"])
    
    ip = device["ip"]
    
    streamPath = getPath(channel)
    
    # ffmpeg invocation: input from hdhomerun URL stream, video codec
    # set to copy, audio codec set to mp3, hls_flags set to delete so
    # we don't fill the disk when we watch, output to m3u8 file in
    # static/streams directory.
    pid = sub.Popen(["ffmpeg", "-i", "http://"+ip+":5004/auto/v"+channel+"?transcode="+quality, "-hls_flags", "delete_segments", "-vcodec", "copy", "-acodec", "mp3", "./static/streams/"+channel+".m3u8"]).pid
    
    with open(streamPath+".pid","w") as f:
            f.write(str(pid))
    
    return pid
    
    
