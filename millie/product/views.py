from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..errors import *
from .service import ProductService

@api_view(['GET'])
def get_products(request):
    '''
    Retrieve all products, optionally filtered by category
    :param:
        category_id (optional): category_id to filter products
    :return: JSON response with list of products
    :example:
        GET /product/?category_id=2
        Response: [
            {
                'id': 1,
                'name': 'Prod 1',
                'description': 'Desc.....',
                ...
            }
        ]
    '''
    category_id = request.query_params.get('category_id', None)

    service = ProductService()
    try:
        result = service.get_products(category_id=category_id)
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

    service = ProductService()
    try:
        result = service.get_product_detail(product_id=product_id, coupon_code=coupon_code)
        return Response(result)
    except TypeError:
        return Response({'error': 'product_id is not integer'}, status=status.HTTP_400_BAD_REQUEST)
    except ProductDoesNotExist:
        return Response({'error': ProductDoesNotExist.default_detail}, status=ProductDoesNotExist.status_code)
    except CouponDoesNotExist:
        return Response({'error': CouponDoesNotExist.default_detail}, status=CouponDoesNotExist.status_code)