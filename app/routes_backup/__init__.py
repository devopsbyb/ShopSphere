from .auth import register_auth_routes
from .customer import register_customer_routes
from .admin import register_admin_routes


def register_routes(app):
    register_auth_routes(app)
    register_customer_routes(app)
    register_admin_routes(app)