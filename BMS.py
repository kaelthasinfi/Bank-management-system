#coding:utf-8
import odbc,time
timeformat='%Y-%m-%d %X'
class MSSQL:
    def __init__(self,dsn,uid,pwd):
        self.dsn=dsn
        self.uid=uid
        self.pwd=pwd
        self.cur=self.Connect()

    def Connect(self):
        if not self.dsn:
            raise(NameError,"no database!")
        self.db=odbc.odbc("dsn=%s;uid=%s;pwd=%s"%(self.dsn,self.uid,self.pwd))
        cur=self.db.cursor()
        if not cur:
            raise(NameError,"cursor wrong!")
        else:
            print("connected!")
        return cur

    def ExceQuery(self,sql):
        self.cur.execute(sql)
        resList=self.cur.fetchall()
        return resList

    def ExecNonQuery(self,sql):
        self.cur.execute(sql)
        self.db.commit()

    def endsql(self):
        self.db.close()

def Accwork(db):
    
    ###################账户登录#########################
    while(1):
        accid=input('(选择退出登录请输入666)请输入账户id:')
        if accid=='666':
            return
        sql='SELECT account_psd,account_status FROM account_info WHERE account_id=\'%s\''%(accid)
        res=db.ExceQuery(sql)
        if len(res)==0:
            print('不存在该账户！\n')
            continue
        elif res[0][1]==1:
            print('账户挂失/锁定,无法登录！\n')
            continue
        elif res[0][1]==2:
            print('账户冻结,无法登录！\n')
            continue
        elif res[0][1]==3:
            print('账户已销户！\n')
            continue
            
        accpwd=input('密码:')
        
        pwd=res[0][0].decode('gbk').strip()            ###编码问题,gbk

        if accpwd!=pwd:
            print('密码错误！\n')
            continue
        break
    ###################账户登录#########################

    ###################业务处理#########################
    while(1):
        kind=input('请选择业务类型(数字序号)：1.存款  2.取款  3.转账  4.查询余额  5.查询交易记录  6.修改个人信息  0.退出登录\n')
        
        if kind=='0':               #退出登录
            break
        elif kind=='1':             #存款
            sql='SELECT balance FROM account_info WHERE account_id=\'%s\''%(accid)
            balance=db.ExceQuery(sql)
            balance=balance[0][0]
            print('当前余额：%d'%balance)
            deposit=input('(退回业务选择请输入-1)请输入存款金额：')             
            if deposit=='-1':       
                continue

            sql='INSERT INTO log_info(log_time,log_detail,related_account) VALUES (\'%s\',\'存款%s\',\'%s\')'%(time.strftime(timeformat,time.localtime()),deposit,accid)
            db.ExecNonQuery(sql)
            
            sql='UPDATE account_info SET balance=balance+%s WHERE account_id=\'%s\''%(deposit,accid)
            db.ExecNonQuery(sql)
            print('存款成功！当前余额：%d\n '%(balance+int(deposit)))
            
            continue
        
        elif kind=='2':             #取款
            sql='SELECT balance FROM account_info WHERE account_id=\'%s\''%(accid)
            balance=db.ExceQuery(sql)
            balance=balance[0][0]
            print('当前余额：%d'%balance)
            while(1):
                draw=input('(退回业务选择请输入-1)请输入取款金额：')
                if draw=='-1':
                    break
                if balance<int(draw):
                    print('余额不足！\n')
                    continue
                break
            
            if draw=='-1':
                break

            sql='INSERT INTO log_info(log_time,log_detail,related_account) VALUES (\'%s\',\'取款%s\',\'%s\')'%(time.strftime(timeformat,time.localtime()),draw,accid)
            db.ExecNonQuery(sql)
            
            
            sql='UPDATE account_info SET balance=balance-%s WHERE account_id=\'%s\''%(draw,accid)
            db.ExecNonQuery(sql)
            print('取款成功！当前余额：%d\n '%(balance-int(draw)))
            continue
        
        elif kind=='3':             #转账
            sql='SELECT balance FROM account_info WHERE account_id=\'%s\''%(accid)
            balance=db.ExceQuery(sql)
            balance=balance[0][0]
            print('当前余额：%d'%balance)
            
            while(1):
                trans=input('(退回业务选择请输入-1)请输入转账金额：')
                if trans=='-1':
                    break
                if balance<int(trans):
                    print('余额不足！\n')
                    continue

                while(1):
                    aimid=input('(退回业务选择请输入-1)请输入转入账户id：\n')
                    if aimid=='-1':
                        break
                    sql='SELECT * FROM account_info WHERE account_id=\'%s\''%(aimid)
                    aimrs=db.ExceQuery(sql)
                    if aimrs==0:
                        print('不存在该账户！\n')
                        continue;
                    elif aimrs[0][4]==1:
                        print('账户挂失/锁定,无法登录！\n')
                        continue
                    elif aimrs[0][4]==2:
                        print('账户冻结,无法登录！\n')
                        continue
                    elif aimrs[0][4]==3:
                        print('账户已销户！\n')
                        continue
                    break
                if aimid=='-1':
                    break
                break

            if trans=='-1' or aimid=='-1':
                break

            sql='INSERT INTO log_info(log_time,log_detail,related_account) VALUES (\'%s\',\'转出%s到账户%s\',\'%s\')'%(time.strftime(timeformat,time.localtime()),trans,aimid,accid)
            db.ExecNonQuery(sql)

            sql='INSERT INTO log_info(log_time,log_detail,related_account) VALUES (\'%s\',\'从账户%s转入%s\',\'%s\')'%(time.strftime(timeformat,time.localtime()),aimid,trans,accid)
            db.ExecNonQuery(sql)

            sql='UPDATE account_info SET balance=balance-%s WHERE account_id=\'%s\''%(trans,accid)
            db.ExecNonQuery(sql)
            
            sql='UPDATE account_info SET balance=balance+%s WHERE account_id=\'%s\''%(trans,aimid)
            db.ExecNonQuery(sql)
            print('转账成功！当前余额：%d'%(balance-int(trans)))
            continue
        
        elif kind=='4':             #查询余额
            sql='SELECT account_id,customer_name,balance FROM account_info WHERE account_id=\'%s\''%(accid)
            res=db.ExceQuery(sql)
            balance=res[0][2]
            account_id=res[0][0].decode('gbk').strip()
            customer_name=res[0][1].decode('gbk').strip()

            sql='INSERT INTO log_info(log_time,log_detail,related_account) VALUES (\'%s\',\'查询余额\',\'%s\')'%(time.strftime(timeformat,time.localtime()),accid)
            db.ExecNonQuery(sql)
            
            print('账户id：%s    客户姓名：%s    余额：%d\n'%(account_id,customer_name,balance))
            continue
                        
        elif kind=='5':             #查询交易记录                ################交易记录的id为自动标号的int类型
            sql='SELECT log_time,log_detail FROM log_info WHERE related_account=\'%s\''%(accid)
            res=db.ExceQuery(sql)
            for i in res:
                t=i[0].decode('gbk').strip()
                d=i[1].decode('gbk').strip()
                print(t,'  ',d)
            continue

        elif kind=='6':             #修改个人信息
            sql='SELECT customer_info.customer_name,customer_info.AGE,customer_info.SEX,customer_info.ADDR FROM account_info,customer_info WHERE account_info.account_id=\'%s\' AND account_info.customer_name=customer_info.customer_name'%(accid)
            res=db.ExceQuery(sql)
            print('客户姓名：'+res[0][0].decode('gbk').strip())
            print('年龄：'+str(res[0][1]))
            if res[0][2]==0:
                print('性别：男')
            else:
                print('性别：女')
            print('用户地址：'+res[0][3].decode('gbk').strip())
            print('不改变信息请输入-1')
            age=input('客户年龄：？\n')
            if age=='-1':
                age=str(res[0][1])
            sex=input('客户性别：？0.男  1.女(请输入性别序号)\n')
            if sex=='-1':
                sex=str(res[0][2])
            addr=input('客户地址：？\n')
            if addr=='-1':
                addr=res[0][3].decode('gbk').strip()
            sql='UPDATE customer_info SET AGE=%s,SEX=%s,ADDR=\'%s\' WHERE customer_name=\'%s\''%(age,sex,addr,res[0][0].decode('gbk').strip())
            db.ExecNonQuery(sql)
            print('信息修改成功！')
            continue
        else:
            print('不存在该业务！\n')
            continue
       ###################业务处理######################### 


def Manawork(db):
    ######################管理员登录########################
    while(1):
        macid=input('(选择退出登录请输入666)请输入管理员id:')
        if macid=='666':
            return
        sql='SELECT manager_psd,manager_status FROM manager_info WHERE manager_id=\'%s\''%(macid)
        res=db.ExceQuery(sql)
        if len(res)==0:
            print('不存在该管理员！\n')
            continue
        elif res[0][1]==1:
            print('管理员权限已取消！\n')
            continue
            
        mapwd=input('密码:')
        
        pwd=res[0][0].decode('gbk').strip()            ###编码问题,gbk

        if mapwd!=pwd:
            print('密码错误！\n')
            continue
        break
    ######################管理员登录########################

    ######################处理业务##########################
    while(1):
        makind=input('请选择操作类型(数字序号)：1.获取客户授权  2.开户  3.查询操作记录  0.退出登录\n')
        if makind=='0':
            break
        elif makind=='1':
            ##########授权#########
            while(1):
                accid=input('(选择退出授权请输入666)请输入账户id:')
                if accid=='666':
                    return
                sql='SELECT account_psd,account_status FROM account_info WHERE account_id=\'%s\''%(accid)
                accres=db.ExceQuery(sql)
                if len(accres)==0:
                    print('不存在该账户！\n')
                    continue
                elif accres[0][1]==2:
                    print('账户冻结,无法授权！\n')
                    continue
                elif accres[0][1]==3:
                    print('账户已销户！\n')
                    continue
            
                inpwd=input('密码:')
        
                accpwd=accres[0][0].decode('gbk').strip()            ###编码问题,gbk

                if accpwd!=inpwd:
                    print('密码错误！\n')
                    continue
                break
            ##########授权#########

            ########授权业务#######
            while(1):
                acckind=input('请选择授权业务类型(数字序号)：1.存款  2.取款  3.转账  4.查询余额  5.查询交易记录  6.修改个人信息  7.挂失账户/解除挂失(锁定)  8.修改账号密码  0.退出授权\n')
                if acckind=='0':
                    break
                elif acckind=='1':
                    sql='SELECT balance FROM account_info WHERE account_id=\'%s\''%(accid)
                    balance=db.ExceQuery(sql)
                    balance=balance[0][0]
                    print('当前余额：%d'%balance)
                    deposit=input('(退回业务选择请输入-1)请输入存款金额：')             
                    if deposit=='-1':       
                        continue
    
                    sql='INSERT INTO log_info(log_time,log_detail,related_account,related_manager) VALUES (\'%s\',\'存款%s\',\'%s\',\'%s\')'%(time.strftime(timeformat,time.localtime()),deposit,accid,macid)
                    db.ExecNonQuery(sql)
            
                    sql='UPDATE account_info SET balance=balance+%s WHERE account_id=\'%s\''%(deposit,accid)
                    db.ExecNonQuery(sql)
                    print('存款成功！当前余额：%d\n '%(balance+int(deposit)))
                elif acckind=='2':
                    sql='SELECT balance FROM account_info WHERE account_id=\'%s\''%(accid)
                    balance=db.ExceQuery(sql)
                    balance=balance[0][0]
                    print('当前余额：%d'%balance)
                    while(1):
                        draw=input('(退回业务选择请输入-1)请输入取款金额：')
                        if draw=='-1':
                            break
                        if balance<int(draw):
                            print('余额不足！\n')
                            continue
                        break
            
                    if draw=='-1':
                        break
    
                    sql='INSERT INTO log_info(log_time,log_detail,related_account,related_manager) VALUES (\'%s\',\'取款%s\',\'%s\',\'%s\')'%(time.strftime(timeformat,time.localtime()),draw,accid,macid)
                    db.ExecNonQuery(sql)
            
                    sql='UPDATE account_info SET balance=balance-%s WHERE account_id=\'%s\''%(draw,accid)
                    db.ExecNonQuery(sql)
                    print('取款成功！当前余额：%d\n '%(balance-int(draw)))
                    continue
        
                elif acckind=='3':             #转账
                    sql='SELECT balance FROM account_info WHERE account_id=\'%s\''%(accid)
                    balance=db.ExceQuery(sql)
                    balance=balance[0][0]
                    print('当前余额：%d'%balance)
            
                    while(1):
                        trans=input('(退回业务选择请输入-1)请输入转账金额：')
                        if trans=='-1':
                            break
                        if balance<int(trans):
                            print('余额不足！\n')
                            continue

                        while(1):
                            aimid=input('(退回业务选择请输入-1)请输入转入账户id：\n')
                            if aimid=='-1':
                                break
                            sql='SELECT * FROM account_info WHERE account_id=\'%s\''%(aimid)
                            aimrs=db.ExceQuery(sql)
                            if aimrs==0:
                                print('不存在该账户！\n')
                                continue;
                            elif aimrs[0][4]==1:
                                print('账户挂失/锁定,无法登录！\n')
                                continue
                            elif aimrs[0][4]==2:
                                print('账户冻结,无法登录！\n')
                                continue
                            elif aimrs[0][4]==3:
                                print('账户已销户！\n')
                                continue
                            break
                        if aimid=='-1':
                            break
                        break
        
                    if trans=='-1' or aimid=='-1':
                        break

                    sql='INSERT INTO log_info(log_time,log_detail,related_account,related_manager) VALUES (\'%s\',\'转出%s到账户%s\',\'%s\',\'%s\')'%(time.strftime(timeformat,time.localtime()),trans,aimid,accid,macid)
                    db.ExecNonQuery(sql)
        
                    sql='INSERT INTO log_info(log_time,log_detail,related_account,related_manager) VALUES (\'%s\',\'从账户%s转入%s\',\'%s\',\'%s\')'%(time.strftime(timeformat,time.localtime()),aimid,trans,accid.macid)
                    db.ExecNonQuery(sql)

                    sql='UPDATE account_info SET balance=balance-%s WHERE account_id=\'%s\''%(trans,accid)
                    db.ExecNonQuery(sql)
            
                    sql='UPDATE account_info SET balance=balance+%s WHERE account_id=\'%s\''%(trans,aimid)
                    db.ExecNonQuery(sql)
                    print('转账成功！当前余额：%d'%(balance-int(trans)))
                    continue
                
                elif acckind=='4':             #查询余额
                    sql='SELECT account_id,customer_name,balance FROM account_info WHERE account_id=\'%s\''%(accid)
                    res=db.ExceQuery(sql)
                    balance=res[0][2]
                    account_id=res[0][0].decode('gbk').strip()
                    customer_name=res[0][1].decode('gbk').strip()

                    sql='INSERT INTO log_info(log_time,log_detail,related_account,related_manager) VALUES (\'%s\',\'查询余额\',\'%s\',\'%s\')'%(time.strftime(timeformat,time.localtime()),accid,macid)
                    db.ExecNonQuery(sql)
            
                    print('账户id：%s    客户姓名：%s    余额：%d\n'%(account_id,customer_name,balance))
                    continue
                                
                elif acckind=='5':             #查询交易记录                ################交易记录的id为自动标号的int类型
                    sql='SELECT log_time,log_detail FROM log_info WHERE related_account=\'%s\''%(accid)
                    res=db.ExceQuery(sql)
                    for i in res:
                        t=i[0].decode('gbk').strip()
                        d=i[1].decode('gbk').strip()
                        print(t,'  ',d)
                    continue

                elif acckind=='6':             #修改个人信息
                    sql='SELECT customer_info.customer_name,customer_info.AGE,customer_info.SEX,customer_info.ADDR FROM account_info,customer_info WHERE account_info.account_id=\'%s\' AND account_info.customer_name=customer_info.customer_name'%(accid)
                    res=db.ExceQuery(sql)
                    print('客户姓名：'+res[0][0].decode('gbk').strip())
                    print('年龄：'+str(res[0][1]))
                    if res[0][2]==0:
                        print('性别：男')
                    else:
                        print('性别：女')
                    print('用户地址：'+res[0][3].decode('gbk').strip())
                    print('不改变信息请输入-1')
                    age=input('客户年龄：？\n')
                    if age=='-1':
                        age=str(res[0][1])
                    sex=input('客户性别：？0.男  1.女(请输入性别序号)\n')
                    if sex=='-1':
                        sex=str(res[0][2])
                    addr=input('客户地址：？\n')
                    if addr=='-1':
                        addr=res[0][3].decode('gbk').strip()
                    sql='UPDATE customer_info SET AGE=%s,SEX=%s,ADDR=\'%s\' WHERE customer_name=\'%s\''%(age,sex,addr,res[0][0].decode('gbk').strip())
                    db.ExecNonQuery(sql)
                    print('信息修改成功！')
                    continue
                
                else:
                    print('不存在该业务！\n')
                    continue   

            ########授权业务#######
            


    ######################处理业务##########################

def main():
    bmsdb=MSSQL('SQLServer','BMS','bankmanager')
    while(1):
        kind=input('请选择登录用户类型(数字序号)：1.普通账户  2.管理员  3.超级管理员  0.退出系统\n')
        if kind=='1':
            Accwork(bmsdb)
        elif kind=='2':
            Manawork(bmsdb)
        elif kind=='3':
            Adminwork(bmsdb)
        elif kind=='0':
            break
        else:
            print("请输入正确用户类型！\n")
            continue
    bmsdb.endsql()
    print('感谢使用！\n')

if __name__=='__main__':
    main()
