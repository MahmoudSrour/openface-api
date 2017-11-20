import pymysql
import math
import time

class Adabas:
    def __init__(self, config, logger):
        self.logger = logger
        self.config = config

    def getData(self, sql):
        print "Start: {}".format(time.time())
        connection, cursor = self.getConnection()

        try:
            self.logger.info("Start execute sql: {}".format(sql))
            count = cursor.execute(sql)
            data = cursor.fetchall()
            print "End: {}".format(time.time())
        finally:
            cursor.close()
            connection.close()

        return count, data

    def getCount(self, sql):
        connection, cursor = self.getConnection()
        try:
            count = cursor.execute(sql)
        finally:
            cursor.close()
            connection.close()
        return count

    def getJobs(self, table, filter, page=-1):

        sql = "select * from {}".format(table)
        if filter is not None:
            sql += ' where ' + filter + ' '
        if(page != -1):
            count = self.getCount(sql)

            pages = int(math.ceil(count / float(page)))
            sqls = []

            for i in range(0, pages):
                sqls.append("{0} LIMIT {1}, {2}".format(sql,i * page,  page))
        else:
            sqls = []
            sqls.append(sql)

        return sqls

    def getSplitJobs(self, table, filter, split=-1):

        sql = "select * from {}".format(table)
        if filter is not None:
            sql += ' where ' + filter + ' '
        if(split != -1):
            count = self.getCount(sql)

            limit = int(math.ceil(count / float(split)))
            sqls = []

            for i in range(0, split):
                sqls.append("{0} LIMIT {1}, {2}".format(sql, i * limit, limit))
        else:
            sqls = []
            sqls.append(sql)

        return sqls

    def getConnection(self):
        con = pymysql.connect(host=self.config.db['host'],
                              user=self.config.db['user'],
                              password=self.config.db['password'],
                              db=self.config.db['schema'])
        c = con.cursor()
        return con, c
