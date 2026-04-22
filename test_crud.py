"""Comprehensive pytest tests for CRUD operations and API endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
from models import Employee, Customer, Order, OrderDetail
from schema import EmployeeCreate, CustomerCreate, OrderCreate, OrderDetailCreate

# Setup test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_tsql2012.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override get_db dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def setup_database():
    """Create and drop test database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(setup_database):
    """Create test client with overridden database dependency."""
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def db_session(setup_database):
    """Create test database session."""
    db = TestingSessionLocal()
    yield db
    db.close()


# ==================== EMPLOYEE TESTS ====================

def test_create_employee(client):
    """Test creating an employee."""
    response = client.post(
        "/V0/employees",
        json={
            "lastname": "Smith",
            "firstname": "John",
            "title": "Manager",
            "titleofcourtesy": "Mr.",
            "birthdate": "1980-01-15",
            "hiredate": "2020-01-01",
            "address": "123 Main St",
            "city": "Seattle",
            "country": "USA",
            "phone": "206-555-0100"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["firstname"] == "John"
    assert data["lastname"] == "Smith"


def test_get_employees(client):
    """Test getting all employees."""
    # Create sample employees
    for i in range(3):
        client.post(
            "/V0/employees",
            json={
                "lastname": f"Smith{i}",
                "firstname": f"John{i}",
                "title": "Manager",
                "titleofcourtesy": "Mr.",
                "birthdate": "1980-01-15",
                "hiredate": "2020-01-01",
                "address": "123 Main St",
                "city": "Seattle",
                "country": "USA",
                "phone": "206-555-0100"
            }
        )
    
    response = client.get("/V0/employees")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_get_employee_by_id(client):
    """Test getting an employee by ID."""
    # Create an employee
    create_response = client.post(
        "/V0/employees",
        json={
            "lastname": "Smith",
            "firstname": "John",
            "title": "Manager",
            "titleofcourtesy": "Mr.",
            "birthdate": "1980-01-15",
            "hiredate": "2020-01-01",
            "address": "123 Main St",
            "city": "Seattle",
            "country": "USA",
            "phone": "206-555-0100"
        }
    )
    empid = create_response.json()["empid"]
    
    # Get the employee
    response = client.get(f"/V0/employees/{empid}")
    assert response.status_code == 200
    data = response.json()
    assert data["empid"] == empid
    assert data["firstname"] == "John"


def test_update_employee(client):
    """Test updating an employee."""
    # Create an employee
    create_response = client.post(
        "/V0/employees",
        json={
            "lastname": "Smith",
            "firstname": "John",
            "title": "Manager",
            "titleofcourtesy": "Mr.",
            "birthdate": "1980-01-15",
            "hiredate": "2020-01-01",
            "address": "123 Main St",
            "city": "Seattle",
            "country": "USA",
            "phone": "206-555-0100"
        }
    )
    empid = create_response.json()["empid"]
    
    # Update the employee
    response = client.put(
        f"/V0/employees/{empid}",
        json={"city": "Portland"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Portland"


def test_delete_employee(client):
    """Test deleting an employee."""
    # Create an employee
    create_response = client.post(
        "/V0/employees",
        json={
            "lastname": "Smith",
            "firstname": "John",
            "title": "Manager",
            "titleofcourtesy": "Mr.",
            "birthdate": "1980-01-15",
            "hiredate": "2020-01-01",
            "address": "123 Main St",
            "city": "Seattle",
            "country": "USA",
            "phone": "206-555-0100"
        }
    )
    empid = create_response.json()["empid"]
    
    # Delete the employee
    response = client.delete(f"/V0/employees/{empid}")
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get(f"/V0/employees/{empid}")
    assert response.status_code == 404


def test_get_employees_by_city(client):
    """Test getting employees by city."""
    # Create employees in different cities
    client.post(
        "/V0/employees",
        json={
            "lastname": "Smith",
            "firstname": "John",
            "title": "Manager",
            "titleofcourtesy": "Mr.",
            "birthdate": "1980-01-15",
            "hiredate": "2020-01-01",
            "address": "123 Main St",
            "city": "Seattle",
            "country": "USA",
            "phone": "206-555-0100"
        }
    )
    
    response = client.get("/V0/employees/city/Seattle")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["city"] == "Seattle"


# ==================== CUSTOMER TESTS ====================

def test_create_customer(client):
    """Test creating a customer."""
    response = client.post(
        "/V0/customers",
        json={
            "companyname": "Acme Corp",
            "contactname": "Jane Doe",
            "contacttitle": "Manager",
            "address": "456 Oak Ave",
            "city": "Portland",
            "country": "USA",
            "phone": "503-555-0100"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["companyname"] == "Acme Corp"


def test_search_customers(client):
    """Test searching customers."""
    # Create customers
    client.post(
        "/V0/customers",
        json={
            "companyname": "Acme Corp",
            "contactname": "Jane Doe",
            "contacttitle": "Manager",
            "address": "456 Oak Ave",
            "city": "Portland",
            "country": "USA",
            "phone": "503-555-0100"
        }
    )
    
    response = client.get("/V0/customers/search/Acme")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(c["companyname"] == "Acme Corp" for c in data)


# ==================== ORDER TESTS ====================

def test_create_order(client, db_session):
    """Test creating an order."""
    # Create required records
    emp = Employee(
        empid=1, lastname="Smith", firstname="John", title="Manager",
        titleofcourtesy="Mr.", birthdate="1980-01-15", hiredate="2020-01-01",
        address="123", city="Seattle", country="USA", phone="555"
    )
    cust = Customer(
        custid=1, companyname="Acme", contactname="Jane", contacttitle="Manager",
        address="456", city="Portland", country="USA", phone="555"
    )
    
    db_session.add(emp)
    db_session.add(cust)
    db_session.commit()
    
    response = client.post(
        "/V0/orders",
        json={
            "custid": 1,
            "empid": 1,
            "orderdate": "2024-01-01",
            "requireddate": "2024-01-15",
            "shipperid": 1,
            "freight": 10.0,
            "shipname": "Acme Corp",
            "shipaddress": "456 Oak",
            "shipcity": "Portland",
            "shipcountry": "USA"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["custid"] == 1
    assert data["empid"] == 1


# ==================== STATISTICS TESTS ====================

def test_get_statistics(client, db_session):
    """Test getting database statistics."""
    # Add sample data
    emp = Employee(
        empid=1, lastname="Smith", firstname="John", title="Manager",
        titleofcourtesy="Mr.", birthdate="1980-01-15", hiredate="2020-01-01",
        address="123", city="Seattle", country="USA", phone="555"
    )
    db_session.add(emp)
    db_session.commit()
    
    response = client.get("/V0/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_employees" in data
    assert "total_customers" in data
    assert "total_orders" in data
    assert "total_order_details" in data


# ==================== HEALTH CHECK TESTS ====================

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_v0_health_check(client):
    """Test V0 health check endpoint."""
    response = client.get("/V0/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "V0"


# ==================== ERROR HANDLING TESTS ====================

def test_get_nonexistent_employee(client):
    """Test getting nonexistent employee returns 404."""
    response = client.get("/V0/employees/999")
    assert response.status_code == 404


def test_delete_nonexistent_employee(client):
    """Test deleting nonexistent employee returns 404."""
    response = client.delete("/V0/employees/999")
    assert response.status_code == 404


def test_update_nonexistent_employee(client):
    """Test updating nonexistent employee returns 404."""
    response = client.put(
        "/V0/employees/999",
        json={"city": "Portland"}
    )
    assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
