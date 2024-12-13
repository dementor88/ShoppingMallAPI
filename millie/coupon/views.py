from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .service import CouponService
from ..settings import PAGE_SIZE

ORDER_FIELDS = ['code', 'active', 'created_at']
@api_view(['GET'])
def get_active_coupons(request):
    '''
    Retrieve all available(active) coupons
    :param:
        include_inactive (optional): whether to include inactive coupons
        page (optional): page number for pagination
        page_size (optional): page size for pagination
        asc (optional): sort ascending (0 or 1)
        order_by (optional): sort field (default sorting is by 'created_at')
    :return: JSON response with list of coupons
    :example:
        GET /coupon/?page=1&page_size=5&asc=1&order_by=code
        Response: {
            'total_count': 11,
            'total_pages': 3,
            'current_page': 1,
            'page_size': 5,
            'coupons': [
                {
                    'id': 1,
                    'code': 'c_1',
                    ...
                }
            ]
        }
    '''
    try:
        include_inactive = min(int(request.query_params.get('include_inactive', 0)), 1)  # include_inactive should be only 0 or 1
        asc = min(int(request.query_params.get('asc', 0)), 1)   # asc should be only 0 or 1
        page = int(request.query_params.get('page', 1))
        page_size = min(int(request.query_params.get('page_size', PAGE_SIZE)), PAGE_SIZE) # page_size cannot be larger than PAGE_SIZE
    except ValueError:
        return Response({'error': 'Invalid query param'}, status=status.HTTP_400_BAD_REQUEST)
    order_by = request.query_params.get('order_by', None)
    if order_by is not None:
        if order_by not in ORDER_FIELDS:
            return Response({'error': 'Invalid order_by query'}, status=status.HTTP_400_BAD_REQUEST)

    coupon_service = CouponService()
    result = coupon_service.get_active_coupons(include_inactive=include_inactive, page=page, page_size=page_size, order_by=order_by, asc=asc)
    return Response(result)