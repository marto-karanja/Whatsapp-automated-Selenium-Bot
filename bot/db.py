import os
import sys
import wx
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#https://www.pythoncentral.io/introductory-tutorial-python-sqlalchemy/
#https://overiq.com/sqlalchemy-101/crud-using-sqlalchemy-orm/
Base = declarative_base()

class GroupNames(Base):
    __tablename__ = 'GroupNames'

    id = Column(Integer, primary_key=True) 
    group_name = Column(String(1000), unique = True)
    message = Column(String(1000000))

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.]



#engine = create_engine('sqlite:///bot.db', echo = True)
engine = create_engine('sqlite:///bot.db', echo = False)
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)


 
 

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()
 

def addGroupNames(group_names, messages):
    for name, message in zip(group_names, messages):
        if not fetchGroupName(name):
            group_name = GroupNames (group_name = name, message = message)
            session.add(group_name)
            commit = True
        else:
            msg = "{0} already in database".format(name)
            wx.MessageBox(msg, "Error", wx.OK | wx.ICON_ERROR)
    if commit:
        try:
            session.commit()
        except Exception as e:
            #log your exception in the way you want -> log to file, log as error with default logging, send by email. It's upon you
            session.rollback()
            session.flush() # for resetting non-commited .add()
            wx.MessageBox("There was an unexpected error", "Error Saving", wx.OK | wx.ICON_ERROR)
            return False
        else:
            wx.MessageBox("Successfully saved", "Success", wx.OK | wx.ICON_INFORMATION)
            return True
    else:
        return False

def updateGroupNames(group_names, messages):
    for name, message in zip(group_names, messages):
        # check if group name is in datanase
        if fetchGroupName(name):
            # update record
            print(message)
            session.query(GroupNames).filter(GroupNames.group_name == name).update({"message": message})
        else:
            # save record in database
            group_name = GroupNames (group_name = name, message = message)
            session.add(group_name)
        try:
            session.commit()
        except Exception as e:
            #log your exception in the way you want -> log to file, log as error with default logging, send by email. It's upon you
            session.rollback()
            session.flush() # for resetting non-commited .add()
            wx.MessageBox("There was an unexpected error", "Error Saving", wx.OK | wx.ICON_ERROR)
            
    wx.MessageBox("Successfully saved", "Success", wx.OK | wx.ICON_INFORMATION)
            
        
    return
            
    

def readGroupNames():
    results = session.query(GroupNames)
    saved_names = {}
    for result in results:
        saved_names [result.group_name] = result.message
    return saved_names


#----------------------------------------------------
def fetchGroupMessages(groupnames):
    query = session.query(GroupNames).filter(GroupNames.group_name.in_(groupnames))
    #print(str(query))
    results = query.all()
    return results


######
#--------------------------------------------------------------------------
def fetch_messages(group_name):
    result = session.query(GroupNames).filter(GroupNames.group_name == group_name).first()
    return result.message


def fetchGroupName(name):
    results = session.query(GroupNames).filter(GroupNames.group_name == name)
    if results.count() > 0:
        return True
    else :
        return False

def deleteGroupName(name):
    if fetchGroupName(name):

        group = session.query(GroupNames).filter(GroupNames.group_name == name).one()
        session.delete(group)
        try:
            session.commit()
        except Exception as e:
            #log your exception in the way you want -> log to file, log as error with default logging, send by email. It's upon you
            session.rollback()
            session.flush() # for resetting non-commited .add()
            wx.MessageBox("There was an unexpected error deleting the object", "Error Saving", wx.OK | wx.ICON_ERROR)
            return False
        else:
            return True
    else:
        msg = "Unable to delete {0}. Not saved in database yet".format(name)
        wx.MessageBox(msg, "Error Saving", wx.OK | wx.ICON_ERROR)


        


    #----SQL Database Clean Up codes
TABLE_PARAMETER = "{TABLE_PARAMETER}"
DROP_TABLE_SQL = f"DROP TABLE {TABLE_PARAMETER};"
GET_TABLES_SQL = "SELECT name FROM sqlite_schema WHERE type='table';"


def delete_all_tables(con):
    tables = get_tables(con)
    delete_tables(con, tables)


def get_tables(con):
    cur = con.cursor()
    cur.execute(GET_TABLES_SQL)
    tables = cur.fetchall()
    cur.close()
    return tables


def delete_tables(con, tables):
    cur = con.cursor()
    for table, in tables:
        sql = DROP_TABLE_SQL.replace(TABLE_PARAMETER, table)
        cur.execute(sql)
    cur.close()