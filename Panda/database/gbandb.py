from . import db_x as SqL


def gban_list():
    return SqL.getdb("GBAN") or {}


def gban_user(user, reason):
    ok = gban_list()
    ok.update({int(user): reason or "No Reason. "})
    return SqL.setdb("GBAN", ok)


def ungban_user(user):
    ok = gban_list()
    if ok.get(int(user)):
        del ok[int(user)]
        return SqL.setdb("GBAN", ok)


def gban_info(user):
    ok = gban_list()
    if ok.get(int(user)):
        return ok[int(user)]
