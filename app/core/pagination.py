from dataclasses import dataclass
from math import ceil

from fastapi import Query

from app.schemas.common import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, PaginationMeta


@dataclass
class PageParams:
    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def page_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> PageParams:
    return PageParams(page=page, page_size=page_size)


def build_meta(params: PageParams, total_items: int) -> PaginationMeta:
    total_pages = ceil(total_items / params.page_size) if total_items else 0
    return PaginationMeta(
        page=params.page, page_size=params.page_size,
        total_items=total_items, total_pages=total_pages,
    )
