from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..errors import *
from .service import ProductService
from ..settings import PAGE_SIZE

ORDER_FIELDS = ['name', 'category_id', 'coupon_applicable', 'created_at']

@api_view(['GET'])
def get_products(request):
    '''
    Retrieve all products, optionally filtered by category
    :param:
        category_id (optional): category_id to filter products
        page (optional): page number for pagination
        page_size (optional): page size for pagination
        asc (optional): sort ascending (0 or 1)
        order_by (optional): sort field (default sorting is by 'created_at')
    :return: JSON response with list of products
    :example:
        GET /product/?category_id=2&page=1&page_size=5&asc=1&order_by=name
        Response: {
            'total_count': 11,
            'total_pages': 3,
            'current_page': 1,
            'page_size': 5,
            'products': [
                {
                    'id': 1,
                    'name': 'Prod 1',
                    'description': 'Desc.....',
                    ...
                }
            ]
        }
    '''
    category_id = request.query_params.get('category_id', None)
    try:
        asc = min(int(request.query_params.get('asc', 0)), 1)   # asc should be only 0 or 1
        page = int(request.query_params.get('page', 1))
        page_size = min(int(request.query_params.get('page_size', PAGE_SIZE)), PAGE_SIZE) # page_size cannot be larger than PAGE_SIZE
    except ValueError:
        return Response({'error': 'Invalid query param'}, status=status.HTTP_400_BAD_REQUEST)
    order_by = request.query_params.get('order_by', None)
    if order_by is not None:
        if order_by not in ORDER_FIELDS:
            return Response({'error': 'Invalid order_by query'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product_service = ProductService()
        result = product_service.get_products(category_id=category_id, page=page, page_size=page_size, order_by=order_by, asc=asc)
        return Response(result)
    except TypeError:
        return Response({'error': 'category_id is not integer'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_product_detail(request, product_id):
    """
    Retrieve detail info of a specific product, including the final price after discount
    :param:
        product_id : product_id of product
        coupon_code (optional): coupon_code to apply
    :return: JSON response of a product data
    :example:
        GET /product/2/?coupon_code=c_1
        Response: {
            'id': 1,
            'name': 'Prod 1',
            'description': 'Desc.....',
            ...
        }
    """
    coupon_code = request.query_params.get('coupon_code', None)

    product_service = ProductService()
    try:
        result = product_service.get_product_detail(product_id=product_id, coupon_code=coupon_code)
        return Response(result)
    except TypeError:
        return Response({'error': 'product_id is not integer'}, status=status.HTTP_400_BAD_REQUEST)
    except ProductDoesNotExist:
        return Response({'error': ProductDoesNotExist.default_detail}, status=ProductDoesNotExist.status_code)
    except CouponDoesNotExist:
        return Response({'error': CouponDoesNotExist.default_detail}, status=CouponDoesNotExist.status_code)

@api_view(['GET'])
def get_available_coupons(request, product_id):
    """
    Retrieve available coupons for a specific product
    :param:
        product_id : product_id of product
    :return: JSON response  with list of coupons
    :example:
        GET /product/2/coupons/
        Response: [
            {
                'id': 1,
                'name': 'c_1',
                ...
            }
        ]
    """
    product_service = ProductService()
    try:
        result = product_service.get_available_coupons(product_id=product_id)
        return Response(result)
    except ProductDoesNotExist:
        return Response({'error': ProductDoesNotExist.default_detail}, status=ProductDoesNotExist.status_code)