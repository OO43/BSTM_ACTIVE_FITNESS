from sqlalchemy import Column, String, Integer, ForeignKey, Date, Numeric, CHAR, VARCHAR
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customer'
    Customer_ID = Column(String(5), primary_key=True)
    First_Name = Column(CHAR(20))
    Last_Name = Column(CHAR(20))
    Address = Column(VARCHAR(30))
    Phone_No = Column(String(15))  # Use string for phone numbers
    Activity_Preference = Column(CHAR(30))
    memberships = relationship('Membership', back_populates='customer')
    payments = relationship('Payment', back_populates='customer')

class Staff(Base):
    __tablename__ = 'staff'
    Staff_ID = Column(String(5), primary_key=True)
    First_Name = Column(CHAR(20))
    Last_Name = Column(CHAR(20))
    Role = Column(CHAR(30))
    Qualification = Column(CHAR(20))
    Salary = Column(Integer)
    manager = relationship('Manager', back_populates='staff', uselist=False)
    branch_id = Column(String(10), ForeignKey('branch.Branch_ID'))
    branch = relationship('Branch', back_populates='staff')

class Branch(Base):
    __tablename__ = 'branch'
    Branch_ID = Column(String(10), primary_key=True)
    Branch_Name = Column(CHAR(20))
    Branch_Location = Column(CHAR(15))
    Postcode = Column(VARCHAR(10))
    staff = relationship('Staff', back_populates='branch')
    facilities = relationship('Facility', back_populates='branch')
    vendor_id = Column(String(10), ForeignKey('vendor.Vendor_ID'))
    vendor = relationship('Vendor', back_populates='branches')
    manager = relationship('Manager', back_populates='branch', uselist=False)

class Vendor(Base):
    __tablename__ = 'vendor'
    Vendor_ID = Column(String(10), primary_key=True)
    Service_Rendered = Column(CHAR(30))
    Contract_Length = Column(VARCHAR(15))
    Payment_Period = Column(CHAR(10))
    branches = relationship('Branch', back_populates='vendor')

class Manager(Base):
    __tablename__ = 'manager'
    Manager_ID = Column(String(10), primary_key=True)
    Full_Name = Column(CHAR(15))
    Department = Column(CHAR(30))
    Branch_Location = Column(CHAR(10))
    Staff_ID = Column(String(10), ForeignKey('staff.Staff_ID'))
    staff = relationship('Staff', back_populates='manager')
    Branch_ID = Column(String(10), ForeignKey('branch.Branch_ID'))
    branch = relationship('Branch', back_populates='manager')

class Membership(Base):
    __tablename__ = 'membership'
    MembershipCard_ID = Column(Integer, primary_key=True)
    Membership_Type = Column(CHAR(10))
    Subscription_Length = Column(VARCHAR(10))
    Customer_ID = Column(String(10), ForeignKey('customer.Customer_ID'))
    customer = relationship('Customer', back_populates='memberships')

class Payment(Base):
    __tablename__ = 'payment'
    Transaction_ID = Column(String(5), primary_key=True)
    Payment_Method = Column(CHAR(10))
    Amount_Paid = Column(Numeric(7,2))
    Payment_Date = Column(Date)
    Customer_ID = Column(String(10), ForeignKey('customer.Customer_ID'))
    customer = relationship('Customer', back_populates='payments')

class Facility(Base):
    __tablename__ = 'facility'
    Facility_ID = Column(String(5), primary_key=True)
    Facility_Type = Column(CHAR(15))
    Capacity = Column(Integer)
    Maintenance_Schedule = Column(VARCHAR(10))
    Branch_ID = Column(String(10), ForeignKey('branch.Branch_ID'))
    branch = relationship('Branch', back_populates='facilities')

# Optional: Trainer and Issue tables if needed
class Trainer(Base):
    __tablename__ = 'trainer'
    Trainer_ID = Column(String(10), primary_key=True)
    # Add more fields as needed

class Issue(Base):
    __tablename__ = 'issue'
    Issue_ID = Column(String(10), primary_key=True)
    # Add more fields as needed
