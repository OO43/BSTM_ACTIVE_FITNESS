# Database Schema and ERD (Fitness Centre)

## Overview
This document summarizes the database schema for the Fitness Centre Management System, originally designed for Oracle (APEX). It includes all table definitions, primary/foreign keys, and sample data. The schema can be adapted for use with PostgreSQL, MySQL, or SQLite for integration with FastAPI.

---


## Entity Relationship Diagram (ERD)

![ERD](../erd.png)

**Entities:**
- Customer
- Staff
- Branch
- Vendor
- Manager
- Membership
- Payment
- Facility
- Trainer
- Issue

**Relationships:**
- Each Customer can have one Membership and multiple Payments.
- Each Manager is a Staff member and manages a Branch.
- Memberships and Payments reference Customers.
- Managers reference Staff.
- Branches have Facilities and are supplied by Vendors.
- Staff work in Branches and can be Managers or Trainers.
- Memberships can issue Issues.

*See the ERD image above for a full visual representation.*

---

## Table Definitions

### Customer
```sql
CREATE TABLE Customer (
    Customer_ID VARCHAR(5) PRIMARY KEY,
    First_Name CHAR(20),
    Last_Name CHAR(20),
    Address VARCHAR(30),
    Phone_No BIGINT,
    Activity_Preference CHAR(30)
);
```

### Staff
```sql
CREATE TABLE Staff (
    Staff_ID VARCHAR(5) PRIMARY KEY,
    First_Name CHAR(20),
    Last_Name CHAR(20),
    Role CHAR(30),
    Qualification CHAR(20),
    Salary INT
);
```

### Branch
```sql
CREATE TABLE Branch (
    Branch_ID VARCHAR(10) PRIMARY KEY,
    Branch_Name CHAR(20),
    Branch_Location CHAR(15),
    Postcode VARCHAR(10)
);
```

### Vendor
```sql
CREATE TABLE Vendor (
    Vendor_ID VARCHAR(10) PRIMARY KEY,
    Service_Rendered CHAR(30),
    Contract_Length VARCHAR(15),
    Payment_Period CHAR(10)
);
```

### Manager
```sql
CREATE TABLE Manager (
    Manager_ID VARCHAR(10) PRIMARY KEY,
    Full_Name CHAR(15),
    Department CHAR(30),
    Branch_Location CHAR(10),
    Staff_ID VARCHAR(10),
    FOREIGN KEY (Staff_ID) REFERENCES Staff(Staff_ID)
);
```

### Membership
```sql
CREATE TABLE Membership (
    MembershipCard_ID INT PRIMARY KEY,
    Membership_Type CHAR(10),
    Subscription_Length VARCHAR(10),
    Customer_ID VARCHAR(10),
    FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID)
);
```

### Payment
```sql
CREATE TABLE Payment (
    Transaction_ID VARCHAR(5) PRIMARY KEY,
    Payment_Method CHAR(10),
    Amount_Paid DECIMAL(7,2),
    Payment_Date DATE,
    Customer_ID VARCHAR(10),
    FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID)
);
```

### Facility
```sql
CREATE TABLE Facility (
    Facility_ID VARCHAR(5) PRIMARY KEY,
    Facility_Type CHAR(15),
    Capacity INT,
    Maintenance_Schedule VARCHAR(10)
);
```

---

## Notes
- Data types and constraints may need adjustment for your target RDBMS (e.g., use `BIGINT` for phone numbers, `DECIMAL` for amounts).
- Foreign key constraints ensure referential integrity.
- Sample data (INSERT statements) can be provided in a separate file if needed.

---

*This schema is ready for adaptation to SQLAlchemy models for FastAPI integration.*
