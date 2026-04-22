from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database import SessionLocal
from crud import (
    # Employees
    get_employee, get_employees, create_employee, update_employee, delete_employee,
    # Customers
    get_customer, get_customers, get_customers_by_country,
    create_customer, update_customer, delete_customer,
    # Orders
    get_order, get_orders, get_orders_by_customer, get_orders_by_employee,
    create_order, update_order, delete_order,
    # Order Details
    get_order_detail, get_order_details_by_order,
    create_order_detail, update_order_detail, delete_order_detail,
    # Advanced queries
    get_orders_on_last_day,
    get_orders_by_top_customers,
    get_employees_no_orders_after,
    get_customer_only_countries,
    get_customers_ordered_in_year_not_other,
    get_running_total_qty_by_customer_month,
)
from schemas import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    CustomerCreate, CustomerUpdate, CustomerResponse,
    OrderCreate, OrderUpdate, OrderResponse,
    OrderDetailCreate, OrderDetailUpdate, OrderDetailResponse,
    RunningTotalResponse,
)

app = FastAPI(title="TSQL2012 API", version="0.1.0")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- Health Check ----------------

@app.get("/")
def health_check():
    return {"status": "Have a good one ZHEN"}


# ---------------- Employees ----------------

@app.get("/employees", response_model=List[EmployeeResponse])
def list_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_employees(db, skip=skip, limit=limit)

@app.get("/employees/{empid}", response_model=EmployeeResponse)
def read_employee(empid: int, db: Session = Depends(get_db)):
    emp = get_employee(db, empid)
    if not emp:
        raise HTTPException(404, "Employee not found")
    return emp

@app.post("/employees", response_model=EmployeeResponse, status_code=201)
def create_employee_endpoint(emp: EmployeeCreate, db: Session = Depends(get_db)):
    return create_employee(db, emp)

@app.put("/employees/{empid}", response_model=EmployeeResponse)
def update_employee_endpoint(empid: int, emp: EmployeeUpdate, db: Session = Depends(get_db)):
    updated = update_employee(db, empid, emp)
    if not updated:
        raise HTTPException(404, "Employee not found")
    return updated

@app.delete("/employees/{empid}", status_code=204)
def delete_employee_endpoint(empid: int, db: Session = Depends(get_db)):
    if not delete_employee(db, empid):
        raise HTTPException(404, "Employee not found")


# ---------------- Customers ----------------

@app.get("/customers", response_model=List[CustomerResponse])
def list_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_customers(db, skip=skip, limit=limit)

@app.get("/customers/{custid}", response_model=CustomerResponse)
def read_customer(custid: int, db: Session = Depends(get_db)):
    cust = get_customer(db, custid)
    if not cust:
        raise HTTPException(404, "Customer not found")
    return cust

@app.get("/customers/country/{country}", response_model=List[CustomerResponse])
def list_customers_by_country(country: str, db: Session = Depends(get_db)):
    return get_customers_by_country(db, country)

@app.post("/customers", response_model=CustomerResponse, status_code=201)
def create_customer_endpoint(cust: CustomerCreate, db: Session = Depends(get_db)):
    return create_customer(db, cust)

@app.put("/customers/{custid}", response_model=CustomerResponse)
def update_customer_endpoint(custid: int, cust: CustomerUpdate, db: Session = Depends(get_db)):
    updated = update_customer(db, custid, cust)
    if not updated:
        raise HTTPException(404, "Customer not found")
    return updated

@app.delete("/customers/{custid}", status_code=204)
def delete_customer_endpoint(custid: int, db: Session = Depends(get_db)):
    if not delete_customer(db, custid):
        raise HTTPException(404, "Customer not found")


# ---------------- Orders ----------------

@app.get("/orders", response_model=List[OrderResponse])
def list_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_orders(db, skip=skip, limit=limit)

@app.get("/orders/{orderid}", response_model=OrderResponse)
def read_order(orderid: int, db: Session = Depends(get_db)):
    order = get_order(db, orderid)
    if not order:
        raise HTTPException(404, "Order not found")
    return order

@app.get("/orders/customer/{custid}", response_model=List[OrderResponse])
def list_orders_by_customer(custid: int, db: Session = Depends(get_db)):
    return get_orders_by_customer(db, custid)

@app.get("/orders/employee/{empid}", response_model=List[OrderResponse])
def list_orders_by_employee(empid: int, db: Session = Depends(get_db)):
    return get_orders_by_employee(db, empid)

@app.post("/orders", response_model=OrderResponse, status_code=201)
def create_order_endpoint(order: OrderCreate, db: Session = Depends(get_db)):
    return create_order(db, order)

@app.put("/orders/{orderid}", response_model=OrderResponse)
def update_order_endpoint(orderid: int, order: OrderUpdate, db: Session = Depends(get_db)):
    updated = update_order(db, orderid, order)
    if not updated:
        raise HTTPException(404, "Order not found")
    return updated

@app.delete("/orders/{orderid}", status_code=204)
def delete_order_endpoint(orderid: int, db: Session = Depends(get_db)):
    if not delete_order(db, orderid):
        raise HTTPException(404, "Order not found")


# ---------------- Order Details ----------------

@app.get("/orderdetails/{orderid}/{productid}", response_model=OrderDetailResponse)
def read_order_detail(orderid: int, productid: int, db: Session = Depends(get_db)):
    od = get_order_detail(db, orderid, productid)
    if not od:
        raise HTTPException(404, "Order detail not found")
    return od

@app.get("/orderdetails/order/{orderid}", response_model=List[OrderDetailResponse])
def list_order_details_by_order(orderid: int, db: Session = Depends(get_db)):
    return get_order_details_by_order(db, orderid)

@app.post("/orderdetails", response_model=OrderDetailResponse, status_code=201)
def create_order_detail_endpoint(od: OrderDetailCreate, db: Session = Depends(get_db)):
    return create_order_detail(db, od)

@app.put("/orderdetails/{orderid}/{productid}", response_model=OrderDetailResponse)
def update_order_detail_endpoint(orderid: int, productid: int, od: OrderDetailUpdate, db: Session = Depends(get_db)):
    updated = update_order_detail(db, orderid, productid, od)
    if not updated:
        raise HTTPException(404, "Order detail not found")
    return updated

@app.delete("/orderdetails/{orderid}/{productid}", status_code=204)
def delete_order_detail_endpoint(orderid: int, productid: int, db: Session = Depends(get_db)):
    if not delete_order_detail(db, orderid, productid):
        raise HTTPException(404, "Order detail not found")


# ---------------- Advanced Queries ----------------

@app.get("/advanced/orders-last-day", response_model=List[OrderResponse])
def orders_on_last_day(db: Session = Depends(get_db)):
    return get_orders_on_last_day(db)

@app.get("/advanced/top-customers-orders", response_model=List[OrderResponse])
def orders_by_top_customers(db: Session = Depends(get_db)):
    return get_orders_by_top_customers(db)

@app.get("/advanced/employees-no-orders-after/{date}", response_model=List[EmployeeResponse])
def employees_no_orders_after(date: str, db: Session = Depends(get_db)):
    return get_employees_no_orders_after(db, date)

@app.get("/advanced/customer-only-countries")
def customer_only_countries(db: Session = Depends(get_db)):
    return get_customer_only_countries(db)

@app.get("/advanced/customers-ordered-year-not-other")
def customers_ordered_in_year_not_other(year1: int, year2: int, db: Session = Depends(get_db)):
    return get_customers_ordered_in_year_not_other(db, year1, year2)

@app.get("/advanced/running-total", response_model=List[RunningTotalResponse])
def running_total(db: Session = Depends(get_db)):
    return get_running_total_qty_by_customer_month(db)