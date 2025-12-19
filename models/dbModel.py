from sqlalchemy import Column, Integer, String, ForeignKey, event
from sqlalchemy.orm import relationship
from sqlalchemy.engine import Engine
from database import Base
import sqlite3


@event.listens_for(Engine, "connect")
def enable_sqlite_fk(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

class GrafanaModel(Base):
    __tablename__ = "grafana"

    id = Column(Integer, primary_key=True, index=True)
    grafana_url = Column(String)
    username = Column(String)
    password = Column(String)
    grafana_code = Column(String, index=True)

    dashboards = relationship("GrafanaDashboardModel",back_populates="grafana", cascade="all, delete-orphan")

class GrafanaDashboardModel(Base):
    __tablename__ = "grafana_dashboard"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_url = Column(String)
    title = Column(String)
    grafana_id = Column(Integer, ForeignKey("grafana.id", ondelete="CASCADE"))
    filename = Column(String)

    grafana= relationship("GrafanaModel",back_populates="dashboards")
    api_request = relationship("ApiRequestModel",back_populates="dashboard", cascade="all, delete-orphan")

class ApiRequestModel(Base):
    __tablename__ = "api_request"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("grafana_dashboard.id", ondelete="CASCADE"))
    api_url = Column(String)
    json_payload = Column(String)
    mode = Column(String)
    caption = Column(String)

    dashboard = relationship("GrafanaDashboardModel", back_populates="api_request")