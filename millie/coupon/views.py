from rest_framework.decorators import api_view
from rest_framework.response import Response
from .service import CouponService
@api_view(['GET'])
def get_available_coupons(request):
    '''
    Retrieve all available coupons
    :return: JSON response with list of coupons
    :example:
        GET /coupon/
        Response: [
            {
                'id': 1,
                'code': 'c_1',
                ...
            }
        ]
    '''
    service = CouponService()
    result = service.get_available_coupons()
    return Response(result)