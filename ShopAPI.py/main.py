from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
from sqlalchemy import create_engine, Column, String, Float, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session

# --- НАСТРОЙКА БАЗЫ ДАННЫХ (SQLite) ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./shop.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- МОДЕЛИ БАЗЫ ДАННЫХ (по вашей схеме) ---
class Client(Base):
    __tablename__ = "clients"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone_number = Column(String(30))
    
    orders = relationship("Order", back_populates="client")

class Product(Base):
    __tablename__ = "products"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text)
    
    order_products = relationship("OrderProduct", back_populates="product")

class Order(Base):
    __tablename__ = "orders"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    client_id = Column(String, ForeignKey("clients.id"))
    address = Column(String(100), nullable=False) # Исправил опечатку addres из схемы
    
    client = relationship("Client", back_populates="orders")
    order_products = relationship("OrderProduct", back_populates="order")

class OrderProduct(Base):
    __tablename__ = "order_products"
    order_id = Column(String, ForeignKey("orders.id"), primary_key=True)
    product_id = Column(String, ForeignKey("products.id"), primary_key=True)
    
    order = relationship("Order", back_populates="order_products")
    product = relationship("Product", back_populates="order_products")

# Создаем таблицы в файле shop.db
Base.metadata.create_all(bind=engine)

# --- СХЕМЫ ДЛЯ ВАЛИДАЦИИ (Pydantic) ---
class ClientCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str] = None

class ProductCreate(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

class OrderCreate(BaseModel):
    client_id: str
    address: str
    product_ids: List[str] # Передаем список ID товаров для заказа

# --- НАСТРОЙКА API ---
app = FastAPI(title="Shop API")

# Вспомогательная функция для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- CRUD ДЛЯ КЛИЕНТОВ ---
@app.post("/clients/", tags=["Clients"])
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    db_client = Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@app.get("/clients/", tags=["Clients"])
def get_clients(db: Session = Depends(get_db)):
    return db.query(Client).all()

# --- CRUD ДЛЯ ТОВАРОВ ---
@app.post("/products/", tags=["Products"])
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/", tags=["Products"])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

# --- CRUD ДЛЯ ЗАКАЗОВ ---
@app.post("/orders/", tags=["Orders"])
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == order.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db_order = Order(client_id=order.client_id, address=order.address)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    for prod_id in order.product_ids:
        product = db.query(Product).filter(Product.id == prod_id).first()
        if product:
            op = OrderProduct(order_id=db_order.id, product_id=product.id)
            db.add(op)
            
    db.commit()
    return db_order

@app.get("/orders/", tags=["Orders"])
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()
# ==========================================
# ДОПОЛНИТЕЛЬНЫЕ РУЧКИ ДЛЯ ПОЛНОГО CRUD
# ==========================================

# --- UPDATE и DELETE для КЛИЕНТОВ ---
@app.put("/clients/{client_id}", tags=["Clients"])
def update_client(client_id: str, client_data: ClientCreate, db: Session = Depends(get_db)):
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Обновляем поля
    db_client.first_name = client_data.first_name
    db_client.last_name = client_data.last_name
    db_client.email = client_data.email
    db_client.phone_number = client_data.phone_number
    db.commit()
    db.refresh(db_client)
    return db_client

@app.delete("/clients/{client_id}", tags=["Clients"])
def delete_client(client_id: str, db: Session = Depends(get_db)):
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(db_client)
    db.commit()
    return {"message": "Client deleted"}

# --- UPDATE и DELETE для ТОВАРОВ ---
@app.put("/products/{product_id}", tags=["Products"])
def update_product(product_id: str, product_data: ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db_product.name = product_data.name
    db_product.price = product_data.price
    db_product.description = product_data.description
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}", tags=["Products"])
def delete_product(product_id: str, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted"}

# --- DELETE для ЗАКАЗОВ (и обновление адреса) ---
@app.put("/orders/{order_id}", tags=["Orders"])
def update_order(order_id: str, order_data: OrderCreate, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db_order.address = order_data.address
    # (Для простоты мы не меняем список товаров в заказе при обновлении, 
    # но адрес обновить можем)
    db.commit()
    db.refresh(db_order)
    return db_order

@app.delete("/orders/{order_id}", tags=["Orders"])
def delete_order(order_id: str, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(db_order)
    db.commit()
    return {"message": "Order deleted"}

# --- Ручка для чтения таблицы связей (Order_Product) ---
# Преподаватель просил на КАЖДУЮ сущность, поэтому добавим GET для связей
@app.get("/order-products/", tags=["Order_Product"])
def get_order_products(db: Session = Depends(get_db)):
    return db.query(OrderProduct).all()