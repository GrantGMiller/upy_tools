import subprocess

def GetSSIDs():
    results = subprocess.check_output(["netsh", "wlan", "show", "network"])
    #TODO - parse SSIDs only

def ConnectToNetwork(ssid, pw):
    pass