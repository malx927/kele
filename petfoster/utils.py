#-*-coding:utf-8-*-
__author__ = 'malxin'

from .models import FosterPrice

def foster_calc_price(data):
    if data is None:
        return None

    days = data.get("days", 0)
    if days <=0:
        return None

    bigCount = data.get("big_dog", 0) or 0
    midCount = data.get("middle_dog", 0) or 0
    smallCount = data.get("small_dog", 0) or 0
    if bigCount + midCount + smallCount <= 0:
        return None

    #会员和非会员
    is_member = data.get("is_member", None)
    types = data.get("foster_type", None)
    mode = data.get("foster_mode", None)

    big_prices = FosterPrice.objects.filter(foster_type=types, pet_type=1).first()   #大型
    mid_prices = FosterPrice.objects.filter(foster_type=types, pet_type=2).first()  #中型
    sml_prices = FosterPrice.objects.filter(foster_type=types, pet_type=3).first()   #小型

    bigPrice = big_prices.vipprice if is_member ==1 else big_prices.price
    midPrice = mid_prices.vipprice if is_member ==1 else mid_prices.price
    smlPrice = sml_prices.vipprice if is_member ==1 else sml_prices.price
    print("midPrice=",midPrice)
    bPrice = mPrice = sPrice = 0
    #单舍寄养(每只犬价格，使用短期大型犬价格)
    if mode == 1:
        bPrice = bigPrice * bigCount
        mPrice = bigPrice * midCount
        sPrice = bigPrice * smallCount
    #同主人混养(第一只全价【优先顺序：大--》中--》小】，第二只以后为半价【各自的价格】)
    elif mode ==2:
        if bigCount > 0:
            bPrice = bigPrice * 1 + (bigCount - 1) *bigPrice/2
            mPrice = midPrice/2 * midCount
            sPrice = smlPrice/2 * smallCount
        elif midCount > 0:
            bPrice = 0
            mPrice = midPrice/2 * (midCount - 1) + midPrice * 1
            sPrice = smlPrice/2 * smallCount
        elif smallCount > 0:
            bPrice = 0
            mPrice = 0
            sPrice = smlPrice/2 * (smallCount -1) + smlPrice * 1
    #不同主人混养（大型犬不可以，其他取对应的价格）
    elif mode == 3:
        bPrice = 0
        mPrice = midPrice * midCount
        sPrice = smlPrice * smallCount

    result_data = {
        "big_price": bPrice ,
        "mid_price": mPrice ,
        "sml_price": sPrice ,
        "total_price": (bPrice + mPrice + sPrice)*days
    }
    return result_data










