"""Thin connection to DaVinci Resolve Studio's scripting API."""
import sys
sys.path.append("/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules")
import DaVinciResolveScript as dvr


def connect():
    r = dvr.scriptapp("Resolve")
    if not r:
        sys.exit("Resolve not reachable: open Resolve Studio and set Preferences > System > General > External scripting = Local")
    return r


def open_project(name, create=False):
    pm = connect().GetProjectManager()
    cur = pm.GetCurrentProject()
    if cur and cur.GetName() == name:
        return cur
    pm.GotoRootFolder()
    p = pm.LoadProject(name)
    if not p and create:
        p = pm.CreateProject(name)
    if not p:
        sys.exit(f"project not found: {name}")
    return p


def find_clip(folder, name):
    for c in folder.GetClipList() or []:
        if c.GetName() == name:
            return c
    for s in folder.GetSubFolderList() or []:
        hit = find_clip(s, name)
        if hit:
            return hit
    return None


def find_folder(folder, name):
    if folder.GetName() == name:
        return folder
    for s in folder.GetSubFolderList() or []:
        hit = find_folder(s, name)
        if hit:
            return hit
    return None
