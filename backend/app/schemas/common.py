"""
Common Pydantic schemas used across all API modules.

Implements the standard API response wrapper from TECH_STACK §12:
  { "data": ..., "error": ... }
"""

from typing import Any, Optional

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Structured error payload returned in API error responses."""

    code: str
    message: str


class ApiResponse(BaseModel):
    """
    Standard API response wrapper.

    Success: { "data": {...}, "error": null }
    Error:   { "data": null, "error": {"code": "...", "message": "..."} }
    """

    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None
