from fastapi import FastAPI

from app.error.error_handler import (
    field_error_handler,
    variable_error_handler,
)
from app.error.exceptions import VariableException, FieldException, VariableException


def exception_handler(app: FastAPI):
    app.add_exception_handler(VariableException, variable_error_handler)
    app.add_exception_handler(FieldException, field_error_handler)
