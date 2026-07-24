from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import models
from database import engine, get_db
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Pydantic schemas
# Pydantic schemas
class CustomerBase(BaseModel):
    First_Name: str
    Last_Name: str
    Address: str
    Phone_No: str
    Activity_Preference: str

class StaffBase(BaseModel):
    First_Name: str
    Last_Name: str
    Role: str
    Qualification: str
    Salary: int

class StaffCreate(StaffBase):
    Staff_ID: str

class StaffOut(StaffBase):
    Staff_ID: str
    class Config:
        orm_mode = True

class CustomerCreate(CustomerBase):
    Customer_ID: str

class CustomerOut(CustomerBase):
    Customer_ID: str
    class Config:
        orm_mode = True

class BranchBase(BaseModel):
    Branch_Name: str
    Branch_Location: str
    Postcode: str

class BranchCreate(BranchBase):
    Branch_ID: str

class BranchOut(BranchBase):
    Branch_ID: str
    class Config:
        orm_mode = True

class VendorBase(BaseModel):
    Service_Rendered: str
    Contract_Length: str
    Payment_Period: str

class VendorCreate(VendorBase):
    Vendor_ID: str

class VendorOut(VendorBase):
    Vendor_ID: str
    class Config:
        orm_mode = True

class ManagerBase(BaseModel):
    Full_Name: str
    Department: str
    Branch_Location: str
    Staff_ID: str
    Branch_ID: str

class ManagerCreate(ManagerBase):
    Manager_ID: str

class ManagerOut(ManagerBase):
    Manager_ID: str
    class Config:
        orm_mode = True

class MembershipBase(BaseModel):
    Membership_Type: str
    Subscription_Length: str
    Customer_ID: str

class MembershipCreate(MembershipBase):
    MembershipCard_ID: int

class MembershipOut(MembershipBase):
    MembershipCard_ID: int
    class Config:
        orm_mode = True

class PaymentBase(BaseModel):
    Payment_Method: str
    Amount_Paid: float
    Payment_Date: str
    Customer_ID: str

class PaymentCreate(PaymentBase):
    Transaction_ID: str

class PaymentOut(PaymentBase):
    Transaction_ID: str
    class Config:
        orm_mode = True

class FacilityBase(BaseModel):
    Facility_Type: str
    Capacity: int
    Maintenance_Schedule: str
    Branch_ID: str

class FacilityCreate(FacilityBase):
    Facility_ID: str

class FacilityOut(FacilityBase):
    Facility_ID: str
    class Config:
        orm_mode = True

# User model (add to models.py for production use)
class User(BaseModel):
    username: str
    password: str

fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("adminpass"[:72])
    }
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token", tags=["Auth"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

# Example of a protected route
@app.get("/users/me", tags=["Auth"])
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user

@app.get("/", tags=["Root"])
def home():
    return {"Hello": "World"}

# CRUD for Customer
@app.post("/customers/", response_model=CustomerOut, tags=["Customers"])
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    db_customer = db.query(models.Customer).filter(models.Customer.Customer_ID == customer.Customer_ID).first()
    if db_customer:
        raise HTTPException(status_code=400, detail="Customer ID already exists")
    new_customer = models.Customer(**customer.dict())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

@app.get("/customers/", response_model=List[CustomerOut], tags=["Customers"])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    customers = db.query(models.Customer).offset(skip).limit(limit).all()
    return customers

@app.get("/customers/{customer_id}", response_model=CustomerOut, tags=["Customers"])
def read_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.Customer_ID == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.put("/customers/{customer_id}", response_model=CustomerOut, tags=["Customers"])
def update_customer(customer_id: str, customer: CustomerBase, db: Session = Depends(get_db)):
    db_customer = db.query(models.Customer).filter(models.Customer.Customer_ID == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    for key, value in customer.dict().items():
        setattr(db_customer, key, value)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@app.delete("/customers/{customer_id}", tags=["Customers"])
def delete_customer(customer_id: str, db: Session = Depends(get_db)):
    db_customer = db.query(models.Customer).filter(models.Customer.Customer_ID == customer_id).first()
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(db_customer)
    db.commit()
    return {"detail": "Customer deleted"}

# CRUD for Staff
@app.post("/staff/", response_model=StaffOut, tags=["Staff"])
def create_staff(staff: StaffCreate, db: Session = Depends(get_db)):
    db_staff = db.query(models.Staff).filter(models.Staff.Staff_ID == staff.Staff_ID).first()
    if db_staff:
        raise HTTPException(status_code=400, detail="Staff ID already exists")
    new_staff = models.Staff(**staff.dict())
    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)
    return new_staff

@app.get("/staff/", response_model=List[StaffOut], tags=["Staff"])
def read_staff(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    staff = db.query(models.Staff).offset(skip).limit(limit).all()
    return staff

@app.get("/staff/{staff_id}", response_model=StaffOut, tags=["Staff"])
def read_staff_member(staff_id: str, db: Session = Depends(get_db)):
    staff = db.query(models.Staff).filter(models.Staff.Staff_ID == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return staff

@app.put("/staff/{staff_id}", response_model=StaffOut, tags=["Staff"])
def update_staff(staff_id: str, staff: StaffBase, db: Session = Depends(get_db)):
    db_staff = db.query(models.Staff).filter(models.Staff.Staff_ID == staff_id).first()
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    for key, value in staff.dict().items():
        setattr(db_staff, key, value)
    db.commit()
    db.refresh(db_staff)
    return db_staff

@app.delete("/staff/{staff_id}", tags=["Staff"])
def delete_staff(staff_id: str, db: Session = Depends(get_db)):
    db_staff = db.query(models.Staff).filter(models.Staff.Staff_ID == staff_id).first()
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    db.delete(db_staff)
    db.commit()
    return {"detail": "Staff deleted"}

# CRUD for Branch
@app.post("/branches/", response_model=BranchOut, tags=["Branch"])
def create_branch(branch: BranchCreate, db: Session = Depends(get_db)):
    db_branch = db.query(models.Branch).filter(models.Branch.Branch_ID == branch.Branch_ID).first()
    if db_branch:
        raise HTTPException(status_code=400, detail="Branch ID already exists")
    new_branch = models.Branch(**branch.dict())
    db.add(new_branch)
    db.commit()
    db.refresh(new_branch)
    return new_branch

@app.get("/branches/", response_model=List[BranchOut], tags=["Branch"])
def read_branches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    branches = db.query(models.Branch).offset(skip).limit(limit).all()
    return branches

@app.get("/branches/{branch_id}", response_model=BranchOut, tags=["Branch"])
def read_branch(branch_id: str, db: Session = Depends(get_db)):
    branch = db.query(models.Branch).filter(models.Branch.Branch_ID == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch

@app.put("/branches/{branch_id}", response_model=BranchOut, tags=["Branch"])
def update_branch(branch_id: str, branch: BranchBase, db: Session = Depends(get_db)):
    db_branch = db.query(models.Branch).filter(models.Branch.Branch_ID == branch_id).first()
    if not db_branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    for key, value in branch.dict().items():
        setattr(db_branch, key, value)
    db.commit()
    db.refresh(db_branch)
    return db_branch

@app.delete("/branches/{branch_id}", tags=["Branch"])
def delete_branch(branch_id: str, db: Session = Depends(get_db)):
    db_branch = db.query(models.Branch).filter(models.Branch.Branch_ID == branch_id).first()
    if not db_branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    db.delete(db_branch)
    db.commit()
    return {"detail": "Branch deleted"}

# CRUD for Vendor
@app.post("/vendors/", response_model=VendorOut, tags=["Vendor"])
def create_vendor(vendor: VendorCreate, db: Session = Depends(get_db)):
    db_vendor = db.query(models.Vendor).filter(models.Vendor.Vendor_ID == vendor.Vendor_ID).first()
    if db_vendor:
        raise HTTPException(status_code=400, detail="Vendor ID already exists")
    new_vendor = models.Vendor(**vendor.dict())
    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)
    return new_vendor

@app.get("/vendors/", response_model=List[VendorOut], tags=["Vendor"])
def read_vendors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    vendors = db.query(models.Vendor).offset(skip).limit(limit).all()
    return vendors

@app.get("/vendors/{vendor_id}", response_model=VendorOut, tags=["Vendor"])
def read_vendor(vendor_id: str, db: Session = Depends(get_db)):
    vendor = db.query(models.Vendor).filter(models.Vendor.Vendor_ID == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor

@app.put("/vendors/{vendor_id}", response_model=VendorOut, tags=["Vendor"])
def update_vendor(vendor_id: str, vendor: VendorBase, db: Session = Depends(get_db)):
    db_vendor = db.query(models.Vendor).filter(models.Vendor.Vendor_ID == vendor_id).first()
    if not db_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    for key, value in vendor.dict().items():
        setattr(db_vendor, key, value)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

@app.delete("/vendors/{vendor_id}", tags=["Vendor"])
def delete_vendor(vendor_id: str, db: Session = Depends(get_db)):
    db_vendor = db.query(models.Vendor).filter(models.Vendor.Vendor_ID == vendor_id).first()
    if not db_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    db.delete(db_vendor)
    db.commit()
    return {"detail": "Vendor deleted"}

# CRUD for Manager
@app.post("/managers/", response_model=ManagerOut, tags=["Manager"])
def create_manager(manager: ManagerCreate, db: Session = Depends(get_db)):
    db_manager = db.query(models.Manager).filter(models.Manager.Manager_ID == manager.Manager_ID).first()
    if db_manager:
        raise HTTPException(status_code=400, detail="Manager ID already exists")
    new_manager = models.Manager(**manager.dict())
    db.add(new_manager)
    db.commit()
    db.refresh(new_manager)
    return new_manager

@app.get("/managers/", response_model=List[ManagerOut], tags=["Manager"])
def read_managers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    managers = db.query(models.Manager).offset(skip).limit(limit).all()
    return managers

@app.get("/managers/{manager_id}", response_model=ManagerOut, tags=["Manager"])
def read_manager(manager_id: str, db: Session = Depends(get_db)):
    manager = db.query(models.Manager).filter(models.Manager.Manager_ID == manager_id).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    return manager

@app.put("/managers/{manager_id}", response_model=ManagerOut, tags=["Manager"])
def update_manager(manager_id: str, manager: ManagerBase, db: Session = Depends(get_db)):
    db_manager = db.query(models.Manager).filter(models.Manager.Manager_ID == manager_id).first()
    if not db_manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    for key, value in manager.dict().items():
        setattr(db_manager, key, value)
    db.commit()
    db.refresh(db_manager)
    return db_manager

@app.delete("/managers/{manager_id}", tags=["Manager"])
def delete_manager(manager_id: str, db: Session = Depends(get_db)):
    db_manager = db.query(models.Manager).filter(models.Manager.Manager_ID == manager_id).first()
    if not db_manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    db.delete(db_manager)
    db.commit()
    return {"detail": "Manager deleted"}

# CRUD for Membership
@app.post("/memberships/", response_model=MembershipOut, tags=["Membership"])
def create_membership(membership: MembershipCreate, db: Session = Depends(get_db)):
    db_membership = db.query(models.Membership).filter(models.Membership.MembershipCard_ID == membership.MembershipCard_ID).first()
    if db_membership:
        raise HTTPException(status_code=400, detail="MembershipCard ID already exists")
    new_membership = models.Membership(**membership.dict())
    db.add(new_membership)
    db.commit()
    db.refresh(new_membership)
    return new_membership

@app.get("/memberships/", response_model=List[MembershipOut], tags=["Membership"])
def read_memberships(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    memberships = db.query(models.Membership).offset(skip).limit(limit).all()
    return memberships

@app.get("/memberships/{membership_id}", response_model=MembershipOut, tags=["Membership"])
def read_membership(membership_id: int, db: Session = Depends(get_db)):
    membership = db.query(models.Membership).filter(models.Membership.MembershipCard_ID == membership_id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    return membership

@app.put("/memberships/{membership_id}", response_model=MembershipOut, tags=["Membership"])
def update_membership(membership_id: int, membership: MembershipBase, db: Session = Depends(get_db)):
    db_membership = db.query(models.Membership).filter(models.Membership.MembershipCard_ID == membership_id).first()
    if not db_membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    for key, value in membership.dict().items():
        setattr(db_membership, key, value)
    db.commit()
    db.refresh(db_membership)
    return db_membership

@app.delete("/memberships/{membership_id}", tags=["Membership"])
def delete_membership(membership_id: int, db: Session = Depends(get_db)):
    db_membership = db.query(models.Membership).filter(models.Membership.MembershipCard_ID == membership_id).first()
    if not db_membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    db.delete(db_membership)
    db.commit()
    return {"detail": "Membership deleted"}

# CRUD for Payment
@app.post("/payments/", response_model=PaymentOut, tags=["Payment"])
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    db_payment = db.query(models.Payment).filter(models.Payment.Transaction_ID == payment.Transaction_ID).first()
    if db_payment:
        raise HTTPException(status_code=400, detail="Transaction ID already exists")
    new_payment = models.Payment(**payment.dict())
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment

@app.get("/payments/", response_model=List[PaymentOut], tags=["Payment"])
def read_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    payments = db.query(models.Payment).offset(skip).limit(limit).all()
    return payments

@app.get("/payments/{transaction_id}", response_model=PaymentOut, tags=["Payment"])
def read_payment(transaction_id: str, db: Session = Depends(get_db)):
    payment = db.query(models.Payment).filter(models.Payment.Transaction_ID == transaction_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@app.put("/payments/{transaction_id}", response_model=PaymentOut, tags=["Payment"])
def update_payment(transaction_id: str, payment: PaymentBase, db: Session = Depends(get_db)):
    db_payment = db.query(models.Payment).filter(models.Payment.Transaction_ID == transaction_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    for key, value in payment.dict().items():
        setattr(db_payment, key, value)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@app.delete("/payments/{transaction_id}", tags=["Payment"])
def delete_payment(transaction_id: str, db: Session = Depends(get_db)):
    db_payment = db.query(models.Payment).filter(models.Payment.Transaction_ID == transaction_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    db.delete(db_payment)
    db.commit()
    return {"detail": "Payment deleted"}

# CRUD for Facility
@app.post("/facilities/", response_model=FacilityOut, tags=["Facility"])
def create_facility(facility: FacilityCreate, db: Session = Depends(get_db)):
    db_facility = db.query(models.Facility).filter(models.Facility.Facility_ID == facility.Facility_ID).first()
    if db_facility:
        raise HTTPException(status_code=400, detail="Facility ID already exists")
    new_facility = models.Facility(**facility.dict())
    db.add(new_facility)
    db.commit()
    db.refresh(new_facility)
    return new_facility

@app.get("/facilities/", response_model=List[FacilityOut], tags=["Facility"])
def read_facilities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    facilities = db.query(models.Facility).offset(skip).limit(limit).all()
    return facilities

@app.get("/facilities/{facility_id}", response_model=FacilityOut, tags=["Facility"])
def read_facility(facility_id: str, db: Session = Depends(get_db)):
    facility = db.query(models.Facility).filter(models.Facility.Facility_ID == facility_id).first()
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    return facility

@app.put("/facilities/{facility_id}", response_model=FacilityOut, tags=["Facility"])
def update_facility(facility_id: str, facility: FacilityBase, db: Session = Depends(get_db)):
    db_facility = db.query(models.Facility).filter(models.Facility.Facility_ID == facility_id).first()
    if not db_facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    for key, value in facility.dict().items():
        setattr(db_facility, key, value)
    db.commit()
    db.refresh(db_facility)
    return db_facility

@app.delete("/facilities/{facility_id}", tags=["Facility"])
def delete_facility(facility_id: str, db: Session = Depends(get_db)):
    db_facility = db.query(models.Facility).filter(models.Facility.Facility_ID == facility_id).first()
    if not db_facility:
        raise HTTPException(status_code=404, detail="Facility not found")
    db.delete(db_facility)
    db.commit()
    return {"detail": "Facility deleted"}

