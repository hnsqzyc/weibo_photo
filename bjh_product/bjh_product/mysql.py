import json


class db():
    def __init__(self, conn):
        self.conn = conn

    def Insert(self, table, data):
        # insert data (pairs of column and value) into table
        strCol = ''
        strVal = ''

        for k in data.keys():
            strCol += ',`' + k + '`'
            if isinstance(data[k], list):
                dataValue = '|'.join(data[k])
            elif isinstance(data[k], dict):
                dataValue = json.dumps(data[k], ensure_ascii=False)
            elif not isinstance(data[k], str):
                dataValue = str(data[k])
            else:
                dataValue = data[k]

            strVal += ",'" + self.conn.escape_string(dataValue) + "'"

        qs = "INSERT INTO `%s` (%s) VALUES (%s)" % (table, strCol[1:], strVal[1:])
        self.conn.query(qs)

        return self.conn.insert_id()

    def runQueryReturnOne(self, sql):
        cur = self.conn.cursor()
        # cur.execute(sql)
        # return cur.fetchone()
        try:
            cur.execute(sql)  # 执行sql语句
            print(cur.fetchall())
            self.conn.commit()  # 提交到数据库执行

        except:
            self.conn.rollback()  # 发生错误后回滚
            # db.close()  # 关闭数据库


    def runQueryReturnAll(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql)
        return cur.fetchall()

