"""CRUD operations and advanced queries for the application."""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from models import Employee, Customer, Order, OrderDetail
from schema import (
    EmployeeCreate, EmployeeUpdate, CustomerCreate, CustomerUpdate,
    OrderCreate, OrderUpdate, OrderDetailCreate
)
from typing import List, Optional, Dict, Any


# ==================== EMPLOYEE CRUD ====================

def get_employee(db: Session, empid: int) -> Optional[Employee]:
    """Get employee by ID."""
    return db.query(Employee).filter(Employee.empid == empid).first()


def get_employees(db: Session, skip: int = 0, limit: int = 100) -> List[Employee]:
    """Get all employees with pagination."""
    return db.query(Employee).offset(skip).limit(limit).all()


def create_employee(db: Session, employee: EmployeeCreate) -> Employee:
    """Create a new employee."""
    db_employee = Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def update_employee(db: Session, empid: int, employee: EmployeeUpdate) -> Optional[Employee]:
    """Update an employee."""
    db_employee = get_employee(db, empid)
    if db_employee:
        update_data = employee.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_employee, key, value)
        db.commit()
        db.refresh(db_employee)
    return db_employee


def delete_employee(db: Session, empid: int) -> bool:
    """Delete an employee."""
    db_employee = get_employee(db, empid)
    if db_employee:
        db.delete(db_employee)
        db.commit()
        return True
    return False


def get_employees_by_city(db: Session, city: str) -> List[Employee]:
    """Advanced query: Get employees by city."""
    return db.query(Employee).filter(Employee.city == city).all()


def get_employees_with_manager(db: Session) -> List[Employee]:
    """Advanced query: Get employees who have a manager."""
    return db.query(Employee).filter(Employee.mgrid.isnot(None)).all()


# ==================== CUSTOMER CRUD ====================

def get_customer(db: Session, custid: int) -> Optional[Customer]:
    """Get customer by ID."""
    return db.query(Customer).filter(Customer.custid == custid).first()


def get_customers(db: Session, skip: int = 0, limit: int = 100) -> List[Customer]:
    """Get all customers."""
    return db.query(Customer).offset(skip).limit(limit).all()


def create_customer(db: Session, customer: CustomerCreate) -> Customer:
    """Create a new customer."""
    db_customer = Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def update_customer(db: Session, custid: int, customer: CustomerUpdate) -> Optional[Customer]:
    """Update a customer."""
    db_customer = get_customer(db, custid)
    if db_customer:
        update_data = customer.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_customer, key, value)
        db.commit()
        db.refresh(db_customer)
    return db_customer


def delete_customer(db: Session, custid: int) -> bool:
    """Delete a customer."""
    db_customer = get_customer(db, custid)
    if db_customer:
        db.delete(db_customer)
        db.commit()
        return True
    return False


def get_customers_by_country(db: Session, country: str) -> List[Customer]:
    """Advanced query: Get customers by country."""
    return db.query(Customer).filter(Customer.country == country).all()


def get_customers_by_city(db: Session, city: str) -> List[Customer]:
    """Advanced query: Get customers by city."""
    return db.query(Customer).filter(Customer.city == city).all()


# ==================== ORDER CRUD ====================

def get_order(db: Session, orderid: int) -> Optional[Order]:
    """Get order by ID."""
    return db.query(Order).filter(Order.orderid == orderid).first()


def get_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get all orders."""
    return db.query(Order).offset(skip).limit(limit).all()


def create_order(db: Session, order: OrderCreate) -> Order:
    """Create a new order with order details."""
    db_order = Order(**order.model_dump(exclude={"order_details"}))
    db.add(db_order)
    db.flush()

    if order.order_details:
        for detail in order.order_details:
            db_detail = OrderDetail(**detail.model_dump(), orderid=db_order.orderid)
            db.add(db_detail)

    db.commit()
    db.refresh(db_order)
    return db_order


def update_order(db: Session, orderid: int, order: OrderUpdate) -> Optional[Order]:
    """Update an order."""
    db_order = get_order(db, orderid)
    if db_order:
        update_data = order.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_order, key, value)
        db.commit()
        db.refresh(db_order)
    return db_order


def delete_order(db: Session, orderid: int) -> bool:
    """Delete an order."""
    db_order = get_order(db, orderid)
    if db_order:
        db.query(OrderDetail).filter(OrderDetail.orderid == orderid).delete()
        db.delete(db_order)
        db.commit()
        return True
    return False


def get_orders_by_customer(db: Session, custid: int) -> List[Order]:
    """Advanced query: Get orders by customer."""
    return db.query(Order).filter(Order.custid == custid).all()


def get_orders_by_employee(db: Session, empid: int) -> List[Order]:
    """Advanced query: Get orders by employee."""
    return db.query(Order).filter(Order.empid == empid).all()


def get_high_value_orders(db: Session, min_freight: float) -> List[Order]:
    """Advanced query: Get orders with high freight cost."""
    return db.query(Order).filter(Order.freight >= min_freight).order_by(desc(Order.freight)).all()


def get_unshipped_orders(db: Session) -> List[Order]:
    """Advanced query: Get orders that haven't been shipped yet."""
    return db.query(Order).filter(Order.shippeddate.is_(None)).all()


# ==================== ORDER DETAIL CRUD ====================

def get_order_detail(db: Session, orderid: int, productid: int) -> Optional[OrderDetail]:
    """Get order detail by order ID and product ID."""
    return db.query(OrderDetail).filter(
        and_(OrderDetail.orderid == orderid, OrderDetail.productid == productid)
    ).first()


def create_order_detail(db: Session, order_detail: OrderDetailCreate) -> OrderDetail:
    """Create a new order detail."""
    db_order_detail = OrderDetail(**order_detail.model_dump())
    db.add(db_order_detail)
    db.commit()
    db.refresh(db_order_detail)
    return db_order_detail


def update_order_detail(db: Session, orderid: int, productid: int, unitprice: float = None,
                       qty: int = None, discount: float = None) -> Optional[OrderDetail]:
    """Update an order detail."""
    db_order_detail = get_order_detail(db, orderid, productid)
    if db_order_detail:
        if unitprice is not None:
            db_order_detail.unitprice = unitprice
        if qty is not None:
            db_order_detail.qty = qty
        if discount is not None:
            db_order_detail.discount = discount
        db.commit()
        db.refresh(db_order_detail)
    return db_order_detail


def delete_order_detail(db: Session, orderid: int, productid: int) -> bool:
    """Delete an order detail."""
    db_order_detail = get_order_detail(db, orderid, productid)
    if db_order_detail:
        db.delete(db_order_detail)
        db.commit()
        return True
    return False


# ==================== STATISTICS & ANALYTICS ====================

def count_employees(db: Session) -> int:
    """Count total employees."""
    return db.query(func.count(Employee.empid)).scalar()


def count_customers(db: Session) -> int:
    """Count total customers."""
    return db.query(func.count(Customer.custid)).scalar()


def count_orders(db: Session) -> int:
    """Count total orders."""
    return db.query(func.count(Order.orderid)).scalar()


def count_order_details(db: Session) -> int:
    """Count total order details."""
    return db.query(func.count(OrderDetail.orderid)).scalar()


def get_total_sales(db: Session) -> float:
    """Advanced query: Calculate total sales from order details."""
    result = db.query(func.sum(OrderDetail.unitprice * OrderDetail.qty)).scalar()
    return float(result) if result else 0.0


def get_average_order_value(db: Session) -> float:
    """Advanced query: Calculate average order freight value."""
    result = db.query(func.avg(Order.freight)).scalar()
    return float(result) if result else 0.0


def get_customer_order_count(db: Session) -> List[Dict[str, Any]]:
    """Advanced query: Get customer with their order counts."""
    results = db.query(
        Customer.custid,
        Customer.companyname,
        func.count(Order.orderid).label("order_count")
    ).outerjoin(Order).group_by(Customer.custid).all()

    return [{"custid": r[0], "companyname": r[1], "order_count": r[2]} for r in results]


def search_customers(db: Session, search_term: str) -> List[Customer]:
    """Advanced query: Search customers by company name or contact name."""
    return db.query(Customer).filter(
        or_(
            Customer.companyname.ilike(f"%{search_term}%"),
            Customer.contactname.ilike(f"%{search_term}%")
        )
    ).all()


def get_orders_with_details(db: Session, orderid: int) -> Optional[Dict[str, Any]]:
    """Advanced query: Get order with all details."""
    order = get_order(db, orderid)
    if not order:
        return None

    return {
        "orderid": order.orderid,
        "orderdate": order.orderdate,
        "custid": order.custid,
        "empid": order.empid,
        "freight": order.freight,
        "items": [
            {
                "productid": od.productid,
                "unitprice": od.unitprice,
                "qty": od.qty,
                "discount": od.discount,
                "linetotal": od.unitprice * od.qty * (1 - od.discount)
            }
            for od in order.order_details
        ]
    }


# ==================== EMPLOYEE CRUD ====================

def get_employee(db: Session, empid: int) -> Optional[Employee]:
    """Get employee by ID."""
    return db.query(Employee).filter(Employee.empid == empid).first()


def get_employees(db: Session, skip: int = 0, limit: int = 100) -> List[Employee]:
    """Get all employees with pagination."""
    return db.query(Employee).offset(skip).limit(limit).all()


def create_employee(db: Session, employee: EmployeeCreate) -> Employee:
    """Create a new employee."""
    db_employee = Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def update_employee(db: Session, empid: int, employee: EmployeeUpdate) -> Optional[Employee]:
    """Update an employee."""
    db_employee = get_employee(db, empid)
    if db_employee:
        update_data = employee.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_employee, key, value)
        db.commit()
        db.refresh(db_employee)
    return db_employee


def delete_employee(db: Session, empid: int) -> bool:
    """Delete an employee."""
    db_employee = get_employee(db, empid)
    if db_employee:
        db.delete(db_employee)
        db.commit()
        return True
    return False


def get_employees_by_city(db: Session, city: str) -> List[Employee]:
    """Advanced query: Get employees by city."""
    return db.query(Employee).filter(Employee.city == city).all()


def get_employees_with_manager(db: Session) -> List[Employee]:
    """Advanced query: Get employees who have a manager."""
    return db.query(Employee).filter(Employee.mgrid.isnot(None)).all()

