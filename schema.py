"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


# Employee Schemas
class EmployeeBase(BaseModel):
    lastname: str
    firstname: str
    title: str
    titleofcourtesy: str
    birthdate: str
    hiredate: str
    address: str
    city: str
    region: Optional[str] = None
    postalcode: Optional[str] = None
    country: str
    phone: str
    mgrid: Optional[int] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    lastname: Optional[str] = None
    firstname: Optional[str] = None
    title: Optional[str] = None
    titleofcourtesy: Optional[str] = None
    birthdate: Optional[str] = None
    hiredate: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    postalcode: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    mgrid: Optional[int] = None


class Employee(EmployeeBase):
    empid: int
    model_config = ConfigDict(from_attributes=True)


# Customer Schemas
class CustomerBase(BaseModel):
    companyname: str
    contactname: str
    contacttitle: str
    address: str
    city: str
    region: Optional[str] = None
    postalcode: Optional[str] = None
    country: str
    phone: str
    fax: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    companyname: Optional[str] = None
    contactname: Optional[str] = None
    contacttitle: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    postalcode: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None


class Customer(CustomerBase):
    custid: int
    model_config = ConfigDict(from_attributes=True)


# OrderDetail Schemas
class OrderDetailBase(BaseModel):
    productid: int
    unitprice: float
    qty: int
    discount: float = 0


class OrderDetailCreate(OrderDetailBase):
    pass


class OrderDetail(OrderDetailBase):
    orderid: int
    model_config = ConfigDict(from_attributes=True)


# Order Schemas
class OrderBase(BaseModel):
    custid: Optional[int] = None
    empid: int
    orderdate: str
    requireddate: str
    shippeddate: Optional[str] = None
    shipperid: int
    freight: float = 0
    shipname: str
    shipaddress: str
    shipcity: str
    shipregion: Optional[str] = None
    shippostalcode: Optional[str] = None
    shipcountry: str


class OrderCreate(OrderBase):
    order_details: Optional[List[OrderDetailCreate]] = None


class OrderUpdate(BaseModel):
    custid: Optional[int] = None
    empid: Optional[int] = None
    orderdate: Optional[str] = None
    requireddate: Optional[str] = None
    shippeddate: Optional[str] = None
    shipperid: Optional[int] = None
    freight: Optional[float] = None
    shipname: Optional[str] = None
    shipaddress: Optional[str] = None
    shipcity: Optional[str] = None
    shipregion: Optional[str] = None
    shippostalcode: Optional[str] = None
    shipcountry: Optional[str] = None


class Order(OrderBase):
    orderid: int
    order_details: List[OrderDetail] = []
    model_config = ConfigDict(from_attributes=True)


# Response Schemas
class Message(BaseModel):
    message: str


class CountResponse(BaseModel):
    count: int


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
