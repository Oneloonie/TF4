"""SQLAlchemy ORM models for the database."""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean, Numeric, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Employee(Base):
    """Employee model for HR.Employees table."""
    __tablename__ = "Employees"

    empid = Column(Integer, primary_key=True, index=True)
    lastname = Column(String(20), nullable=False)
    firstname = Column(String(10), nullable=False)
    title = Column(String(30), nullable=False)
    titleofcourtesy = Column(String(25), nullable=False)
    birthdate = Column(String, nullable=False)  # Stored as ISO string
    hiredate = Column(String, nullable=False)
    address = Column(String(60), nullable=False)
    city = Column(String(15), nullable=False)
    region = Column(String(15), nullable=True)
    postalcode = Column(String(10), nullable=True, index=True)
    country = Column(String(15), nullable=False)
    phone = Column(String(24), nullable=False)
    mgrid = Column(Integer, ForeignKey("Employees.empid"), nullable=True)

    # Relationships
    manager = relationship("Employee", remote_side=[empid], backref="subordinates")
    orders = relationship("Order", back_populates="employee")

    __table_args__ = (
        Index("idx_employees_lastname", "lastname"),
        Index("idx_employees_postalcode", "postalcode"),
    )


class Customer(Base):
    """Customer model for Sales.Customers table."""
    __tablename__ = "Customers"

    custid = Column(Integer, primary_key=True, index=True)
    companyname = Column(String(40), nullable=False, index=True)
    contactname = Column(String(30), nullable=False)
    contacttitle = Column(String(30), nullable=False)
    address = Column(String(60), nullable=False)
    city = Column(String(15), nullable=False, index=True)
    region = Column(String(15), nullable=True, index=True)
    postalcode = Column(String(10), nullable=True, index=True)
    country = Column(String(15), nullable=False)
    phone = Column(String(24), nullable=False)
    fax = Column(String(24), nullable=True)

    # Relationships
    orders = relationship("Order", back_populates="customer")

    __table_args__ = (
        Index("idx_customers_city", "city"),
        Index("idx_customers_companyname", "companyname"),
        Index("idx_customers_postalcode", "postalcode"),
        Index("idx_customers_region", "region"),
    )


class Order(Base):
    """Order model for Sales.Orders table."""
    __tablename__ = "Orders"

    orderid = Column(Integer, primary_key=True, index=True)
    custid = Column(Integer, ForeignKey("Customers.custid"), nullable=True)
    empid = Column(Integer, ForeignKey("Employees.empid"), nullable=False)
    orderdate = Column(String, nullable=False)
    requireddate = Column(String, nullable=False)
    shippeddate = Column(String, nullable=True)
    shipperid = Column(Integer, nullable=False)
    freight = Column(Float, nullable=False, default=0)
    shipname = Column(String(40), nullable=False)
    shipaddress = Column(String(60), nullable=False)
    shipcity = Column(String(15), nullable=False)
    shipregion = Column(String(15), nullable=True)
    shippostalcode = Column(String(10), nullable=True)
    shipcountry = Column(String(15), nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    employee = relationship("Employee", back_populates="orders")
    order_details = relationship("OrderDetail", back_populates="order", cascade="all, delete-orphan")


class OrderDetail(Base):
    """OrderDetail model for Sales.OrderDetails table."""
    __tablename__ = "OrderDetails"

    orderid = Column(Integer, ForeignKey("Orders.orderid"), primary_key=True, index=True)
    productid = Column(Integer, primary_key=True, index=True)
    unitprice = Column(Float, nullable=False, default=0)
    qty = Column(Integer, nullable=False, default=1)
    discount = Column(Float, nullable=False, default=0)

    # Relationships
    order = relationship("Order", back_populates="order_details")

    __table_args__ = (
        Index("idx_orderdetails_orderid", "orderid"),
        Index("idx_orderdetails_productid", "productid"),
    )
