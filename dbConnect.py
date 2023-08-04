import pymysql

#MySQL 연결

def insert(self, vo):
    self.conn = pymysql.connect(host='localhost', user='root', password='1234', db='encore', charset='utf8')
    cur = self.conn.cursor()
    sql = "insert into members values(%s, %s, %s, %s)"
    vals = (vo.id, vo.pwd, vo.name, vo.email)
    cur.execute(sql, vals)
    self.conn.commit()
    self.conn.close()



insert()