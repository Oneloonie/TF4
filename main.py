"""FastAPI application with comprehensive REST API endpoints."""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, init_db
import crud
from schema import (
    Employee, EmployeeCreate, EmployeeUpdate, Customer, CustomerCreate, CustomerUpdate, Order, OrderCreate,
    OrderUpdate, Message, CountResponse, ErrorResponse
)

# Initialize FastAPI app
app = FastAPI(
    title="TSQL2012 FastAPI",
    description="Complete REST API for TSQL2012 database with Employees, Customers, Orders, and OrderDetails",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on app startup."""
    init_db()


# ==================== HEALTH CHECK ===================


@app.get("/")
def health_check():
    return {"status": "Have a good one ZHEN "}


# ==================== STATISTICS ====================

@app.get("/V0/stats", tags=["Statistics"])
async def get_statistics(db: Session = Depends(get_db)):
    """Get database statistics."""
    return {
        "total_employees": crud.count_employees(db),
        "total_customers": crud.count_customers(db),
        "total_orders": crud.count_orders(db),
        "total_order_details": crud.count_order_details(db),
        "total_sales": crud.get_total_sales(db),
        "average_order_value": crud.get_average_order_value(db)
    }


# ==================== EMPLOYEES ====================

@app.get("/V0/employees", response_model=list[Employee], tags=["Employees"])
async def list_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all employees with pagination."""
    return crud.get_employees(db, skip=skip, limit=limit)


@app.get("/V0/employees/{empid}", response_model=Employee, tags=["Employees"])
async def get_employee(empid: int, db: Session = Depends(get_db)):
    """Get employee by ID."""
    employee = crud.get_employee(db, empid)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@app.post("/V0/employees", response_model=Employee, tags=["Employees"])
async def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    """Create a new employee."""
    return crud.create_employee(db, employee)


@app.put("/V0/employees/{empid}", response_model=Employee, tags=["Employees"])
async def update_employee(empid: int, employee: EmployeeUpdate, db: Session = Depends(get_db)):
    """Update an employee."""
    db_employee = crud.update_employee(db, empid, employee)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee


@app.delete("/V0/employees/{empid}", response_model=Message, tags=["Employees"])
async def delete_employee(empid: int, db: Session = Depends(get_db)):
    """Delete an employee."""
    if not crud.delete_employee(db, empid):
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}


@app.get("/V0/employees/city/{city}", response_model=list[Employee], tags=["Employees"])
async def get_employees_by_city(city: str, db: Session = Depends(get_db)):
    """Get employees by city."""
    return crud.get_employees_by_city(db, city)


@app.get("/V0/employees-with-manager", response_model=list[Employee], tags=["Employees"])
async def get_employees_with_manager(db: Session = Depends(get_db)):
    """Get employees who have a manager."""
    return crud.get_employees_with_manager(db)


# ==================== CUSTOMERS ====================

@app.get("/V0/customers", response_model=list[Customer], tags=["Customers"])
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all customers."""
    return crud.get_customers(db, skip=skip, limit=limit)


@app.get("/V0/customers/{custid}", response_model=Customer, tags=["Customers"])
async def get_customer(custid: int, db: Session = Depends(get_db)):
    """Get customer by ID."""
    customer = crud.get_customer(db, custid)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.post("/V0/customers", response_model=Customer, tags=["Customers"])
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer."""
    return crud.create_customer(db, customer)


@app.put("/V0/customers/{custid}", response_model=Customer, tags=["Customers"])
async def update_customer(custid: int, customer: CustomerUpdate, db: Session = Depends(get_db)):
    """Update a customer."""
    db_customer = crud.update_customer(db, custid, customer)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer


@app.delete("/V0/customers/{custid}", response_model=Message, tags=["Customers"])
async def delete_customer(custid: int, db: Session = Depends(get_db)):
    """Delete a customer."""
    if not crud.delete_customer(db, custid):
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted successfully"}


@app.get("/V0/customers/country/{country}", response_model=list[Customer], tags=["Customers"])
async def get_customers_by_country(country: str, db: Session = Depends(get_db)):
    """Get customers by country."""
    return crud.get_customers_by_country(db, country)


@app.get("/V0/customers/city/{city}", response_model=list[Customer], tags=["Customers"])
async def get_customers_by_city(city: str, db: Session = Depends(get_db)):
    """Get customers by city."""
    return crud.get_customers_by_city(db, city)


@app.get("/V0/customers/search/{search_term}", response_model=list[Customer], tags=["Customers"])
async def search_customers(search_term: str, db: Session = Depends(get_db)):
    """Search customers by company or contact name."""
    return crud.search_customers(db, search_term)


# ==================== ORDERS ====================

@app.get("/V0/orders", response_model=list[Order], tags=["Orders"])
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all orders."""
    return crud.get_orders(db, skip=skip, limit=limit)


@app.get("/V0/orders/{orderid}", response_model=Order, tags=["Orders"])
async def get_order(orderid: int, db: Session = Depends(get_db)):
    """Get order by ID."""
    order = crud.get_order(db, orderid)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.post("/V0/orders", response_model=Order, tags=["Orders"])
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order."""
    return crud.create_order(db, order)


@app.put("/V0/orders/{orderid}", response_model=Order, tags=["Orders"])
async def update_order(orderid: int, order: OrderUpdate, db: Session = Depends(get_db)):
    """Update an order."""
    db_order = crud.update_order(db, orderid, order)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order


@app.delete("/V0/orders/{orderid}", response_model=Message, tags=["Orders"])
async def delete_order(orderid: int, db: Session = Depends(get_db)):
    """Delete an order."""
    if not crud.delete_order(db, orderid):
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted successfully"}


@app.get("/V0/orders/customer/{custid}", response_model=list[Order], tags=["Orders"])
async def get_orders_by_customer(custid: int, db: Session = Depends(get_db)):
    """Get orders by customer."""
    return crud.get_orders_by_customer(db, custid)


@app.get("/V0/orders/employee/{empid}", response_model=list[Order], tags=["Orders"])
async def get_orders_by_employee(empid: int, db: Session = Depends(get_db)):
    """Get orders by employee."""
    return crud.get_orders_by_employee(db, empid)


@app.get("/V0/orders/unshipped", response_model=list[Order], tags=["Orders"])
async def get_unshipped_orders(db: Session = Depends(get_db)):
    """Get unshipped orders."""
    return crud.get_unshipped_orders(db)


@app.get("/V0/orders/details/{orderid}", tags=["Orders"])
async def get_order_with_details(orderid: int, db: Session = Depends(get_db)):
    """Get order with detailed information."""
    result = crud.get_orders_with_details(db, orderid)
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return result


# ==================== ANALYTICS ====================

@app.get("/V0/analytics/customer-orders", tags=["Analytics"])
async def get_customer_order_count(db: Session = Depends(get_db)):
    """Get customer with their order counts."""
    return crud.get_customer_order_count(db)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# ==================== EMPLOYEES ====================

@app.get("/V0/employees", response_model=list[Employee], tags=["Employees"])
async def list_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all employees with pagination."""
    return crud.get_employees(db, skip=skip, limit=limit)


@app.get("/V0/employees/{empid}", response_model=Employee, tags=["Employees"])
async def get_employee(empid: int, db: Session = Depends(get_db)):
    """Get employee by ID."""
    employee = crud.get_employee(db, empid)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@app.post("/V0/employees", response_model=Employee, tags=["Employees"])
async def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    """Create a new employee."""
    return crud.create_employee(db, employee)


@app.put("/V0/employees/{empid}", response_model=Employee, tags=["Employees"])
async def update_employee(empid: int, employee: EmployeeUpdate, db: Session = Depends(get_db)):
    """Update an employee."""
    db_employee = crud.update_employee(db, empid, employee)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee


@app.delete("/V0/employees/{empid}", response_model=Message, tags=["Employees"])
async def delete_employee(empid: int, db: Session = Depends(get_db)):
    """Delete an employee."""
    if not crud.delete_employee(db, empid):
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}


@app.get("/V0/employees/city/{city}", response_model=list[Employee], tags=["Employees"])
async def get_employees_by_city(city: str, db: Session = Depends(get_db)):
    """Get employees by city."""
    return crud.get_employees_by_city(db, city)


@app.get("/V0/employees-with-manager", response_model=list[Employee], tags=["Employees"])
async def get_employees_with_manager(db: Session = Depends(get_db)):
    """Get employees who have a manager."""
    return crud.get_employees_with_manager(db)


# ==================== CUSTOMERS ====================

@app.get("/V0/customers", response_model=list[Customer], tags=["Customers"])
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all customers."""
    return crud.get_customers(db, skip=skip, limit=limit)


@app.get("/V0/customers/{custid}", response_model=Customer, tags=["Customers"])
async def get_customer(custid: int, db: Session = Depends(get_db)):
    """Get customer by ID."""
    customer = crud.get_customer(db, custid)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.post("/V0/customers", response_model=Customer, tags=["Customers"])
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer."""
    return crud.create_customer(db, customer)


@app.put("/V0/customers/{custid}", response_model=Customer, tags=["Customers"])
async def update_customer(custid: int, customer: CustomerUpdate, db: Session = Depends(get_db)):
    """Update a customer."""
    db_customer = crud.update_customer(db, custid, customer)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer


@app.delete("/V0/customers/{custid}", response_model=Message, tags=["Customers"])
async def delete_customer(custid: int, db: Session = Depends(get_db)):
    """Delete a customer."""
    if not crud.delete_customer(db, custid):
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted successfully"}


@app.get("/V0/customers/country/{country}", response_model=list[Customer], tags=["Customers"])
async def get_customers_by_country(country: str, db: Session = Depends(get_db)):
    """Get customers by country."""
    return crud.get_customers_by_country(db, country)


@app.get("/V0/customers/city/{city}", response_model=list[Customer], tags=["Customers"])
async def get_customers_by_city(city: str, db: Session = Depends(get_db)):
    """Get customers by city."""
    return crud.get_customers_by_city(db, city)


@app.get("/V0/customers/search/{search_term}", response_model=list[Customer], tags=["Customers"])
async def search_customers(search_term: str, db: Session = Depends(get_db)):
    """Search customers by company or contact name."""
    return crud.search_customers(db, search_term)


# ==================== ORDERS ====================

@app.get("/V0/orders", response_model=list[Order], tags=["Orders"])
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all orders."""
    return crud.get_orders(db, skip=skip, limit=limit)


@app.get("/V0/orders/{orderid}", response_model=Order, tags=["Orders"])
async def get_order(orderid: int, db: Session = Depends(get_db)):
    """Get order by ID."""
    order = crud.get_order(db, orderid)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.post("/V0/orders", response_model=Order, tags=["Orders"])
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order."""
    return crud.create_order(db, order)


@app.put("/V0/orders/{orderid}", response_model=Order, tags=["Orders"])
async def update_order(orderid: int, order: OrderUpdate, db: Session = Depends(get_db)):
    """Update an order."""
    db_order = crud.update_order(db, orderid, order)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order


@app.delete("/V0/orders/{orderid}", response_model=Message, tags=["Orders"])
async def delete_order(orderid: int, db: Session = Depends(get_db)):
    """Delete an order."""
    if not crud.delete_order(db, orderid):
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted successfully"}


@app.get("/V0/orders/customer/{custid}", response_model=list[Order], tags=["Orders"])
async def get_orders_by_customer(custid: int, db: Session = Depends(get_db)):
    """Get orders by customer."""
    return crud.get_orders_by_customer(db, custid)


@app.get("/V0/orders/employee/{empid}", response_model=list[Order], tags=["Orders"])
async def get_orders_by_employee(empid: int, db: Session = Depends(get_db)):
    """Get orders by employee."""
    return crud.get_orders_by_employee(db, empid)


@app.get("/V0/orders/unshipped", response_model=list[Order], tags=["Orders"])
async def get_unshipped_orders(db: Session = Depends(get_db)):
    """Get unshipped orders."""
    return crud.get_unshipped_orders(db)


@app.get("/V0/orders/details/{orderid}", tags=["Orders"])
async def get_order_with_details(orderid: int, db: Session = Depends(get_db)):
    """Get order with detailed information."""
    result = crud.get_orders_with_details(db, orderid)
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return result


# ==================== ANALYTICS ====================

@app.get("/V0/analytics/customer-orders", tags=["Analytics"])
async def get_customer_order_count(db: Session = Depends(get_db)):
    """Get customer with their order counts."""
    return crud.get_customer_order_count(db)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
