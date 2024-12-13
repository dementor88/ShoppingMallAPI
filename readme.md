# ShoppingMallAPI
---------
상품 목록 확인 (필요 시 카테고리로 필터링 가능). 상품 상세 정보 조회 및 쿠폰에 따른 최종 할인 가격 표시.


---------
### 주요기능
* Product
  * 모든 Product 조회 (Category별 필터링 가능)
  * 특정 Product 상세 정보 및 최종 할인 가격 제공
  * 특정 Product에 적용 가능한 Coupon 목록 조회
* Coupon
  * 모든 Coupon 조회 (디폴트로 active인 것만 리턴)

### API Endpoint
* Product
  * GET /product/
    * 모든 Product 조회
      * (option) category_id: Category 필터링 가능
    * ~~cache 활용~~
    * Pagination 구현
      * (option) page, page_size
      * (option) order_by, asc: 정렬 기능 제공
  * GET /product/<product_id>/
    * Product 상세 정보 제공
    * cache 활용
    * 할인 적용 가능 시, 할인된 가격 리턴
      * 최대 할인률 제한
    * (option) coupon_code: 할인을 추가 적용할 쿠폰 코드
  * GET /product/<product_id>/coupons/
    * 해당 Product에 적용 가능한 Coupon 목록 리턴
    * Coupon이 존재해도 특정 Product와 매핑이 되지 않으면 할인 적용 불가능
* Coupon
  * GET /coupon/all/
    * 모든 Coupon 조회
      * (option) include_active: 비활성화 Coupon까지 포함
    * Pagination 구현
      * (option) page, page_size
      * (option) order_by, asc: 정렬 기능 제공

### Testing
```
python manage.py test  millie.tests.ShoppingAPITestCase
```
