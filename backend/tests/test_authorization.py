import unittest
from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException

from app.dependencies import (
    get_assigned_order,
    get_owned_product,
    get_order_or_404,
    get_product_or_404,
    require_store_owner,
    require_user_without_store,
)


class FakeQuery:
    def __init__(self, result):
        self.result = result

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return self.result


class FakeDB:
    def __init__(self, product=None, order=None):
        self.product = product
        self.order = order

    def query(self, model):
        if getattr(model, "__tablename__", None) == "orders":
            return FakeQuery(self.order)
        return FakeQuery(self.product)


class AuthorizationTests(unittest.TestCase):
    def test_require_store_owner_rejects_user_without_store(self):
        user = SimpleNamespace(store=None)

        with self.assertRaises(HTTPException) as context:
            require_store_owner(user)

        self.assertEqual(context.exception.status_code, 403)

    def test_get_owned_product_returns_404_when_missing(self):
        store = SimpleNamespace(store_id=uuid4())
        db = FakeDB(product=None)

        with self.assertRaises(HTTPException) as context:
            get_owned_product(uuid4(), db, store)

        self.assertEqual(context.exception.status_code, 404)

    def test_get_owned_product_rejects_foreign_product(self):
        store = SimpleNamespace(store_id=uuid4())
        foreign_product = SimpleNamespace(product_id=uuid4(), store_id=uuid4())
        db = FakeDB(product=foreign_product)

        with self.assertRaises(HTTPException) as context:
            get_owned_product(foreign_product.product_id, db, store)

        self.assertEqual(context.exception.status_code, 403)

    def test_get_owned_product_accepts_store_owner(self):
        store_id = uuid4()
        store = SimpleNamespace(store_id=store_id)
        owned_product = SimpleNamespace(product_id=uuid4(), store_id=store_id)
        db = FakeDB(product=owned_product)

        result = get_owned_product(owned_product.product_id, db, store)

        self.assertIs(result, owned_product)

    def test_require_user_without_store_rejects_existing_store(self):
        user = SimpleNamespace(store=SimpleNamespace(store_id=uuid4()))

        with self.assertRaises(HTTPException) as context:
            require_user_without_store(user)

        self.assertEqual(context.exception.status_code, 400)

    def test_get_product_or_404_returns_product(self):
        product = SimpleNamespace(product_id=uuid4(), store_id=uuid4())
        db = FakeDB(product=product)

        result = get_product_or_404(product.product_id, db)

        self.assertIs(result, product)

    def test_get_order_or_404_returns_404_when_missing(self):
        db = FakeDB(order=None)

        with self.assertRaises(HTTPException) as context:
            get_order_or_404(uuid4(), db)

        self.assertEqual(context.exception.status_code, 404)

    def test_get_assigned_order_rejects_other_store_owner(self):
        store = SimpleNamespace(user_id=uuid4())
        order = SimpleNamespace(order_id=uuid4(), seller_id=uuid4())

        with self.assertRaises(HTTPException) as context:
            get_assigned_order(order.order_id, order, store)

        self.assertEqual(context.exception.status_code, 403)

    def test_get_assigned_order_accepts_assigned_store_owner(self):
        owner_id = uuid4()
        store = SimpleNamespace(user_id=owner_id)
        order = SimpleNamespace(order_id=uuid4(), seller_id=owner_id)

        result = get_assigned_order(order.order_id, order, store)

        self.assertIs(result, order)


if __name__ == "__main__":
    unittest.main()
