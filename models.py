from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Boolean,
    Float,
    Text,
    Table,
    create_engine,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()
engine = create_engine(
    "sqlite:///shopify_app.db",
    pool_size=100,
    pool_recycle=10000,
    connect_args={"check_same_thread": False},
    echo=False,
)


class AppVersion(Base):
    __tablename__ = "app_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String, ForeignKey("apps.id"), nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    developer_id = Column(Integer, ForeignKey("developers.id"), nullable=False)
    developer_name = Column(Text)  # Store developer name directly
    languages = Column(Text)  # Use JSON to store an array of languages
    works_with = Column(
        Text
    )  # Use JSON to store different works_with values (links, strings)
    built_for_shopify = Column(Boolean, default=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    hash = Column(String, nullable=False)  # Application hash for tracking changes
    developer = relationship("Developer", backref="app_versions")

    # Relationship with Pricing (Define pricing for the app version)

    pricing = relationship(
        "Pricing", back_populates="app_version"
    )  # Correct relationship with Pricing


# Association table for many-to-many relationship between Apps and Categories


# app_category_association = Table(
#     "app_category_association",
#     Base.metadata,
#     Column("app_id", String, ForeignKey("apps.id"), primary_key=True),
#     Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
#     Column("app_rank", String),
#     Column("is_ad", Boolean),
# )


# class Category(Base):
#     __tablename__ = "categories"
#     id = Column(String, primary_key=True)
#     name = Column(String, unique=True, nullable=False)
#     subcategories = relationship(
#         "Subcategory", back_populates="category", cascade="all, delete-orphan"
#     )
#     apps = relationship(
#         "App", secondary="app_category_association", back_populates="categories"
#     )


# class Subcategory(Base):
#     __tablename__ = "subcategories"
#     id = Column(String, primary_key=True)
#     name = Column(String, nullable=False)
#     category_id = Column(
#         Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=True
#     )

#     category = relationship("Category", back_populates="subcategories")
#     tags = relationship(
#         "Tag", back_populates="subcategory", cascade="all, delete-orphan"
#     )
#     apps = relationship(
#         "App", secondary="app_subcategory_association", back_populates="subcategories"
#     )

#     __table_args__ = (
#         UniqueConstraint("name", "category_id", name="uq_subcategory_category"),
#     )


# class Tag(Base):
#     __tablename__ = "tags"
#     id = Column(String, primary_key=True)
#     name = Column(String, nullable=False)
#     subcategory_id = Column(
#         Integer, ForeignKey("subcategories.id", ondelete="CASCADE"), nullable=False
#     )

#     subcategory = relationship("Subcategory", back_populates="tags")
#     apps = relationship("App", secondary="app_tag_association", back_populates="tags")

#     __table_args__ = (
#         UniqueConstraint("name", "subcategory_id", name="uq_tag_subcategory"),
#     )


# app_subcategory_association = Table(
#     "app_subcategory_association",
#     Base.metadata,
#     Column("app_id", String, ForeignKey("apps.id"), primary_key=True),
#     Column("subcategory_id", Integer, ForeignKey("subcategories.id"), primary_key=True),
#     Column("app_rank", String, nullable=True),
#     Column("is_ad", Boolean, nullable=True),
# )

# app_tag_association = Table(
#     "app_tag_association",
#     Base.metadata,
#     Column("app_id", String, ForeignKey("apps.id"), primary_key=True),
#     Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
#     Column("app_rank", String, nullable=True),
#     Column("is_ad", Boolean, nullable=True),
# )


class Developer(Base):
    __tablename__ = "developers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    link = Column(String, nullable=True)
    address = Column(String, nullable=True)
    website = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow())
    updated_at = Column(DateTime, nullable=True)


class App(Base):
    __tablename__ = "apps"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    developer_name = Column(String, ForeignKey("developers.id"), nullable=False)
    launched_at = Column(DateTime)
    languages = Column(Text)
    works_with = Column(Text)
    built_for_shopify = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    hash = Column(String, nullable=False)  # Application hash for tracking changes
    reviews = relationship("Review", back_populates="app")

    developer = relationship("Developer")
    categories = Column(String, nullable=True) 
    categories_link = Column(String, nullable=True)  # Link to categories page
    # categories = relationship(
    #     "Category", secondary="app_category_association", back_populates="apps"
    # )
    # subcategories = relationship(
    #     "Subcategory", secondary="app_subcategory_association", back_populates="apps"
    # )
    # tags = relationship("Tag", secondary="app_tag_association", back_populates="apps")
    pricing = relationship("Pricing", back_populates="app")


class Pricing(Base):
    __tablename__ = "pricing"

    id = Column(Integer, primary_key=True, index=True)
    app_version_id = Column(Integer, ForeignKey("app_versions.id"), nullable=True)
    app_id = Column(Integer, ForeignKey("apps.id"), nullable=False)
    plan_name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    details = Column(String, nullable=True)
    # hash = Column(String, nullable=False)

    # Define the reverse relationship using back_populates

    app = relationship("App", back_populates="pricing")
    app_version = relationship("AppVersion", back_populates="pricing")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(String, ForeignKey("apps.id"), nullable=False, index=True)
    reviewer_name = Column(String, nullable=True)
    reviewer_country = Column(String, nullable=True)
    reviewer_time_using_app = Column(String, nullable=True)
    review_text = Column(Text, nullable=True)
    rating = Column(Float, nullable=True)
    time_of_update = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False)

    app = relationship("App", back_populates="reviews")


# --- Function to save or update an application ---


def save_or_update_app(app_data: dict, new_hash):
    """Saving or updating app if something changes"""
    with Session() as session:
        existing_app = session.query(App).filter_by(id=app_data["id"]).first()

        if existing_app:
            if existing_app.hash != new_hash:
                print(f"Updated app: {app_data['name']}")
                existing_app.name = app_data["name"]
                existing_app.url = app_data["url"]
                existing_app.languages = app_data["languages"]
                existing_app.works_with = app_data["works_with"]
                existing_app.built_for_shopify = app_data["built_for_shopify"]
                existing_app.hash = new_hash
                existing_app.updated_at = datetime.utcnow()
                session.commit()
        else:
            new_app = App(**app_data, hash=new_hash)
            session.add(new_app)
            session.commit()
            print(f"Added app {app_data['name']}")


# --- Function to update pricing ---


def save_pricing(app_id: str, pricing_data: list, app_version_id=None):
    """Changing or creating pricing plans"""
    with Session() as session:
        existing_prices = (
            session.query(Pricing).filter_by(app_id=app_id, app_version_id=None).all()
        )
        existing_prices_dict = {
            (p.plan_name, p.price, p.currency) for p in existing_prices
        }

        new_prices = set(
            (p["plan_name"], p["price"], p["currency"]) for p in pricing_data
        )

        if new_prices != existing_prices_dict:
            for old_price in existing_prices:
                old_price.app_version_id = app_version_id
                old_price.updated_at = datetime.utcnow()
                session.commit()
                print(f"Changed price for {app_id}")
            for price in pricing_data:
                new_price = Pricing(
                    app_id=app_id,
                    plan_name=price["plan_name"],
                    price=price["price"],
                    currency=price["currency"],
                    details=price["details"],
                    created_at=datetime.utcnow(),
                )
                session.add(new_price)
        session.commit()


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
