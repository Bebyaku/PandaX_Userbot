# Copyright (C) 2021-2022 TeamUltroid
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

# Recode by @robotrakitangakbagus, @diemmmmmmmmmm
# Import PandaX_Userbot <https://github.com/ilhammansiz/PandaX_Userbot>
# t.me/PandaUserbot & t.me/TeamSquadUserbotSupport



class PandaUserbotError(Exception):
    ...


class TelethonMissingError(ImportError):
    ...


class DependencyMissingError(ImportError):
    ...


class RunningAsFunctionLibError(PandaUserbotError):
    ...

import sys
import os
from Panda.Var import Var
from Panda.core.logger import logging

LOGS = logging.getLogger("PandaUserbot")

run_as_module = False


def where_hosted():
    if os.getenv("DYNO"):
        return "heroku"
    if os.getenv("RAILWAY_STATIC_URL"):
        return "railway"
    if os.getenv("OKTETO_TOKEN"):
        return "okteto"
    if os.getenv("KUBERNETES_PORT"):
        return "qovery | kubernetes"
    if os.getenv("RUNNER_USER") or os.getenv("HOSTNAME"):
        return "github actions"
    if os.getenv("ANDROID_ROOT"):
        return "termux"
    return "local"


HOSTED_ON = where_hosted()

if sys.argv[0] == "-m":
    run_as_module = True

try:
    from redis import Redis
except ImportError:
    Redis = None

try:
    from pymongo import MongoClient
except ImportError:
    MongoClient = None
    if Var.MONGO_URI:
        LOGS.warning(
            "'pymongo' not found!\nInstall pymongo[srv] to use Mongo database.."
        )

try:
    import psycopg2
except ImportError:
    psycopg2 = None
    if Var.DB_URI:
        LOGS.warning("'psycopg2' not found!\nInstall psycopg2 to use SQL database..")


def get_data(self_, key):
    data = self_.get(str(key))
    if data:
        try:
            data = eval(data)
        except BaseException:
            pass
    return data


class MongoDB:
    def __init__(self, key):
        self.dB = MongoClient(key, serverSelectionTimeoutMS=5000)
        self.db = self.dB.BaseDB
        self.re_cache()

    def __repr__(self):
        return f"<Base.MonGoDB\n -total_keys: {len(self.keys())}\n>"

    @property
    def name(self):
        return "Mongo"

    @property
    def usage(self):
        return self.db.command("dbstats")["dataSize"]

    def re_cache(self):
        self._cache = {}
        for key in self.keys():
            self._cache.update({key: self.getdb(key)})

    def ping(self):
        if self.dB.server_info():
            return True

    def keys(self):
        return self.db.list_collection_names()

    def setdb(self, key, value):
        if key in self.keys():
            self.db[key].replace_one({"_id": key}, {"value": str(value)})
        else:
            self.db[key].insert_one({"_id": key, "value": str(value)})
        self._cache.update({key: value})
        return True

    def deldb(self, key):
        if key in self.keys():
            try:
                del self._cache[key]
            except KeyError:
                pass
            self.db.drop_collection(key)
            return True

    def getdb(self, key):
        if key in self._cache:
            return self._cache[key]
        if key in self.keys():
            value = get_data(self, key)
            self._cache.update({key: value})
            return value
        return None

    def get(self, key):
        if x := self.db[key].find_one({"_id": key}):
            return x["value"]

    def flushall(self):
        self.dB.drop_database("BaseDB")
        self._cache = {}
        return True


# --------------------------------------------------------------------------------------------- #

# Thanks to "Akash Pattnaik" / @BLUE-DEVIL1134
# for SQL Implementation in Ultroid.
#
# Please use https://elephantsql.com/ !


class SqlDB:
    def __init__(self, url):
        self._url = url
        self._connection = None
        self._cursor = None
        try:
            self._connection = psycopg2.connect(dsn=url)
            self._connection.autocommit = True
            self._cursor = self._connection.cursor()
            self._cursor.execute(
                "CREATE TABLE IF NOT EXISTS PandaUserbot)"
            )
        except Exception as error:
            LOGS.exception(error)
            LOGS.info("Invaid SQL Database")
            if self._connection:
                self._connection.close()
            sys.exit()
        self.re_cache()

    @property
    def name(self):
        return "SQL"

    @property
    def usage(self):
        self._cursor.execute(
            "SELECT pg_size_pretty(pg_relation_size('PandaUserbot')) AS size"
        )
        data = self._cursor.fetchall()
        return int(data[0][0].split()[0])

    def re_cache(self):
        self._cache = {}
        for key in self.keys():
            self._cache.update({key: self.getdb(key)})

    def keys(self):
        self._cursor.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name  = 'panda'"
        )  # case sensitive
        data = self._cursor.fetchall()
        return [_[0] for _ in data]

    def ping(self):
        return True

    def getdb(self, variable):
        if variable in self._cache:
            return self._cache[variable]
        get_ = get_data(self, variable)
        self._cache.update({variable: get_})
        return get_

    def get(self, variable):
        try:
            self._cursor.execute(f"SELECT {variable} FROM Panda")
        except psycopg2.errors.UndefinedColumn:
            return None
        data = self._cursor.fetchall()
        if not data:
            return None
        if len(data) >= 1:
            for i in data:
                if i[0]:
                    return i[0]

    def setdb(self, key, value):
        try:
            self._cursor.execute(f"ALTER TABLE Panda DROP COLUMN IF EXISTS {key}")
        except (psycopg2.errors.UndefinedColumn, psycopg2.errors.SyntaxError):
            pass
        except BaseException as er:
            LOGS.exception(er)
        self._cache.update({key: value})
        self._cursor.execute(f"ALTER TABLE Panda ADD {key} TEXT")
        self._cursor.execute(f"INSERT INTO Panda ({key}) values (%s)", (str(value),))
        return True

    def deldb(self, key):
        if key in self._cache:
            del self._cache[key]
        try:
            self._cursor.execute(f"ALTER TABLE Panda DROP COLUMN {key}")
        except psycopg2.errors.UndefinedColumn:
            return False
        return True

    delete = deldb

    def flushall(self):
        self._cache.clear()
        self._cursor.execute("DROP TABLE PandaUserbot")
        self._cursor.execute(
            "CREATE TABLE IF NOT EXISTS PandaUserbot)"
        )
        return True

    def rename(self, key1, key2):
        _ = self.getdb(key1)
        if _:
            self.deldb(key1)
            self.setdb(key2, _)
            return 0
        return 1


# --------------------------------------------------------------------------------------------- #



class RedisDB:
    def __init__(
        self,
        host,
        port,
        password,
        platform="",
        logger=LOGS,
        *args,
        **kwargs,
    ):
        if not Redis:
            raise DependencyMissingError(
                "'redis' module is not installed!\nInstall it to use RedisDB"
            )
        if host and ":" in host:
            spli_ = host.split(":")
            host = spli_[0]
            port = int(spli_[-1])
            if host.startswith("http"):
                logger.error("Your REDIS_URI should not start with http !")
                import sys

                sys.exit()
        elif not host or not port:
            logger.error("Port Number not found")
            import sys

            sys.exit()
        kwargs["host"] = host
        kwargs["password"] = password
        kwargs["port"] = port

        if platform.lower() == "qovery" and not host:
            var, hash_, host, password = "", "", "", ""
            for vars_ in os.environ:
                if vars_.startswith("QOVERY_REDIS_") and vars.endswith("_HOST"):
                    var = vars_
            if var:
                hash_ = var.split("_", maxsplit=2)[1].split("_")[0]
            if hash:
                kwargs["host"] = os.environ(f"QOVERY_REDIS_{hash_}_HOST")
                kwargs["port"] = os.environ(f"QOVERY_REDIS_{hash_}_PORT")
                kwargs["password"] = os.environ(f"QOVERY_REDIS_{hash_}_PASSWORD")
        self.db = Redis(**kwargs)
        self.set = self.db.set
        self.get = self.db.get
        self.keys = self.db.keys
        self.ping = self.db.ping
        self.delete = self.db.delete
        self.re_cache()

    # dict is faster than Redis
    def re_cache(self):
        self._cache = {}
        for keys in self.keys():
            self._cache.update({keys: self.getdb(keys)})

    @property
    def name(self):
        return "Redis"

    @property
    def usage(self):
        return sum(self.db.memory_usage(x) for x in self.keys())

    def setdb(self, key, value):
        value = str(value)
        try:
            value = eval(value)
        except BaseException:
            pass
        self._cache.update({key: value})
        return self.set(str(key), str(value))

    def getdb(self, key):
        if key in self._cache:
            return self._cache[key]
        _ = get_data(self, key)
        self._cache.update({key: _})
        return _

    def deldb(self, key):
        if key in self._cache:
            del self._cache[key]
        return bool(self.delete(str(key)))


# --------------------------------------------------------------------------------------------- #



def BaseDB():
    if MongoClient and Var.MONGO_URI:
        return MongoDB(Var.MONGO_URI)

    if psycopg2 and Var.DB_URI:
        return SqlDB(Var.DB_URI)

    if Var.REDIS_URI or Var.REDISHOST:
        return RedisDB(host=Var.REDIS_URI or Var.REDISHOST, password=Var.REDIS_PASSWORD or Var.REDISPASSWORD, port=Var.REDISPORT, platform=HOSTED_ON, decode_responses=True, socket_timeout=5, retry_on_timeout=True,)
    
