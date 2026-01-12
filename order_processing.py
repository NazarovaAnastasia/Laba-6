TAX_RATE = 0.21
MIN_PRICE = 0
MIN_QTY = 0
DEFAULT_CURRENCY = "USD"

SAVE10_RATE = 0.10
SAVE20_RATE_HIGH = 0.20
SAVE20_RATE_LOW = 0.05
SAVE20_THRESHOLD = 200
VIP_DISCOUNT = 50
VIP_SMALL_DISCOUNT = 10
VIP_THRESHOLD = 100


def ParseCheckoutRequest(request):
    user_id = request.get("user_id")
    items = request.get("items", [])
    coupon = request.get("coupon")
    currency = request.get("currency", DEFAULT_CURRENCY)
    return user_id, items, coupon, currency


def ValidateUserId(user_id):
    if user_id is None:
        raise ValueError("user_id is required")


def ValidateItemsStructure(items):
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    
    if len(items) == 0:
        raise ValueError("items must not be empty")


def ValidateItemFields(item):
    if "price" not in item or "qty" not in item:
        raise ValueError("item must have price and qty")
    
    if item["price"] <= MIN_PRICE:
        raise ValueError("price must be positive")
    
    if item["qty"] <= MIN_QTY:
        raise ValueError("qty must be positive")


def ComputeItemsSubtotal(items):
    return sum(item["price"] * item["qty"] for item in items)


def ApplySave10Coupon(subtotal):
    return int(subtotal * SAVE10_RATE)


def ApplySave20Coupon(subtotal):
    if subtotal >= SAVE20_THRESHOLD:
        return int(subtotal * SAVE20_RATE_HIGH)
    return int(subtotal * SAVE20_RATE_LOW)


def ApplyVipCoupon(subtotal):
    if subtotal < VIP_THRESHOLD:
        return VIP_SMALL_DISCOUNT
    return VIP_DISCOUNT


def CalculateCouponDiscount(subtotal, coupon):
    if coupon == "SAVE10":
        return ApplySave10Coupon(subtotal)
    if coupon == "SAVE20":
        return ApplySave20Coupon(subtotal)
    if coupon == "VIP":
        return ApplyVipCoupon(subtotal)
    
    raise ValueError("unknown coupon")


def ComputeDiscountAmount(subtotal, coupon):
    if not coupon:
        return 0
    return CalculateCouponDiscount(subtotal, coupon)


def CalculateTaxAmount(total_after_discount):
    return int(total_after_discount * TAX_RATE)


def BuildOrderResult(user_id, items, currency, subtotal, discount, tax, total):
    return {
        "order_id": f"{user_id}-{len(items)}-X",
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": len(items),
    }


def process_checkout(request):
    user_id, items, coupon, currency = ParseCheckoutRequest(request)
    
    ValidateUserId(user_id)
    ValidateItemsStructure(items)
    
    for item in items:
        ValidateItemFields(item)
    
    subtotal = ComputeItemsSubtotal(items)
    discount = ComputeDiscountAmount(subtotal, coupon)
    
    total_after_discount = max(subtotal - discount, 0)
    tax = CalculateTaxAmount(total_after_discount)
    total = total_after_discount + tax
    
    return BuildOrderResult(user_id, items, currency, subtotal, discount, tax, total)
