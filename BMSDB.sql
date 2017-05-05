USE master;
GO

CREATE DATABASE BMSDB
ON 
( NAME = Em1,
    FILENAME = 'C:\users\chen\desktop\bmsdb\bmsdb.mdf',
    SIZE = 100MB,
    MAXSIZE = 200,
    FILEGROWTH = 20 )
    
LOG ON
( NAME = banklog1,
    FILENAME = 'C:\users\chen\desktop\bmsdb\bmsdb.ldf',
    SIZE = 100MB,
    MAXSIZE = 200,
    FILEGROWTH = 20 ) ;
GO

USE BMSDB;
GO

CREATE TABLE customer_info(
	customer_name CHAR(20) PRIMARY KEY,
	AGE int,
    SEX int,                            ---- 0:男,1:女
	ADDR CHAR(50),
)

CREATE TABLE account_info(
	account_id CHAR(20) PRIMARY KEY,
	customer_name CHAR(20) NOT NULL,
    account_psd CHAR(20) NOT NULL,
    balance int NOT NULL,
    account_status int NOT NULL,                           ----  0:账户正常,1:账户挂失/锁定,2:账户冻结,3:已销户
    
    FOREIGN KEY (customer_name) REFERENCES customer_info(customer_name)
);
GO

CREATE TABLE manager_info(
	manager_id CHAR(20) PRIMARY KEY,
	manager_psd CHAR(20) NOT NULL,                         
	manager_status int,                                    ----  0:管理员正常,1:管理员取消
);
GO

CREATE TABLE admin_info(
	admin_id CHAR(20) PRIMARY KEY,
	admin_psd CHAR(20) NOT NULL,
);
GO


CREATE TABLE log_info(
	log_id int identity(1,1) PRIMARY KEY,
	log_time char(30) NOT NULL,
	log_detail char(50),
	related_account CHAR(20),
	related_manager CHAR(20),
	related_admin CHAR(20),
	
	
	FOREIGN KEY (related_account) REFERENCES account_info(account_id),
	FOREIGN KEY (related_manager) REFERENCES manager_info(manager_id),
	FOREIGN KEY (related_admin) REFERENCES admin_info(admin_id),
);
GO
INSERT INTO customer_info VALUES('张三','30','0','西安');
INSERT into account_info VALUES('0','张三','123',100,0);
INSERT INTO manager_info VALUES('0','123','0') 