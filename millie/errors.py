class ProductDoesNotExist(Exception):
    status_code = 404
    default_detail = 'product not found'
    default_code = "product_not_found"

class CouponDoesNotExist(Exception):
    status_code = 404
    default_detail = 'coupon not found'
    default_code = "coupon_not_found"

class CategoryDoesNotExist(Exception):
    status_code = 404
    default_detail = 'category not found'
    default_code = "category_not_found"
