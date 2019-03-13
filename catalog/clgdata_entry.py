from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from database import *

engine = create_engine('sqlite:///eng_clgs.db')
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

# Delete BykesCompanyName if exisitng.
session.query(StateName).delete()
# Delete BykeName if exisitng.
session.query(EclgName).delete()
# Delete User if exisitng.
session.query(User).delete()

# Create sample users data
ur1 = User(name="prasanna badugu",
           picture="",
           email="prasanna964296@gamil.com")
session.add(ur1)
session.commit()
print ("Successfully Add First User")
# Create sample byke companys
stname1 = StateName(st_name="andhra pradesh",
                    user_id=1)
session.add(stname1)
session.commit()
# Populare a bykes with models for testing
# Using different users for bykes names year also
clg1 = EclgName(clg_name="Narasaraopeta Engineering College",
                branches="cse,ece,mechanical,eee,civil",
                esta_year="1998",
                clg_phn="08647239904",
                clg_email="info@nrtec.ac.in",
                web_site="www.nrtec.ac.com",
                statenameid=1,
                user_id=1)
session.add(clg1)
session.commit()
clg2 = EclgName(clg_name="Tirumala Engineering College",
                branches="cse,ece,mechanical,eee,civil",
                esta_year="2008",
                clg_phn="08647219083",
                clg_email="tecnrt@gmail.com",
                web_site="www.tmecnrt.org",
                statenameid=1,
                user_id=1)


session.add(clg2)
session.commit()
clg3 = EclgName(clg_name="Bapatla Engineering College",
                branches="cse,ece,mechanical,eee,civil,IT",
                esta_year="2008",
                clg_phn="+91-8643-224244",
                clg_email=" bec_principal@yahoo.com",
                web_site="www.becbapatla.ac.in",
                statenameid=1,
                user_id=1)
session.add(clg3)
session.commit()
clg4 = EclgName(clg_name="Bapatla Engineering College",
                branches="cse,ece,mechanical,eee,civil,IT",
                esta_year="1962",
                clg_phn="+91-8643-224244",
                clg_email=" bec_principal@yahoo.com",
                web_site="www.becbapatla.ac.in",
                statenameid=1,
                user_id=1)
session.add(clg4)
session.commit()
clg5 = EclgName(clg_name="RVR & JC College of Engioneering",
                branches="cse,ece,mechanical,eee,civil,IT",
                esta_year="1998",
                clg_phn="94910 73317 ",
                clg_email="principal@rvrjc.ac.in",
                web_site="www.rvrjcce.ac.in",
                statenameid=1,
                user_id=1)
session.add(clg5)
session.commit()

print("Your colleges database has been inserted!")
