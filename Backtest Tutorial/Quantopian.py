import quantopian.algorithm as qa


def initialize(context):
    context.spy = sid(8554)
    context.vix = sid(40669)
    set_commission(commission.NoCommission)
    set_slippage(slippage.VolumeShareSlippage(volume_limit=0.25, price_impact=0.1))

    context.pricePostOpen = 0
    context.pricePreClose = 0
    context.yesterBuySell = 0

    context.scaleFactor = 5
    schedule_function(spyOpen, date_rules.every_day(), time_rules.market_open())
    schedule_function(
        spyPostOpen, date_rules.every_day(), time_rules.market_open(hours=0, minutes=95)
    )
    schedule_function(
        spyPreClose,
        date_rules.every_day(),
        time_rules.market_close(hours=0, minutes=60),
    )
    schedule_function(
        spyClose, date_rules.every_day(), time_rules.market_close(hours=0, minutes=5)
    )

    # schedule_function(vixDaily,
    #                   date_rules.every_day(),
    #                   time_rules.market_open())
    # schedule_function(vixOpen,
    #                   date_rules.every_day(),
    #                   time_rules.market_open(hours=0,minutes=95))
    # schedule_function(vixClose,
    #                   date_rules.every_day(),
    #                   time_rules.market_close(hours=0,minutes=60))


def handle_data(context, data):
    pass


def spyOpen(context, data):
    context.priceOpen = data.current(context.spy, "price")
    context.changeAtOpen = context.priceOpen - context.pricePreClose

    if context.changeAtOpen < 0:
        if context.scaleFactor < 20:
            context.scaleFactor += 2
    else:
        if context.scaleFactor > 2:
            context.scaleFactor /= 1.5


def spyPostOpen(context, data):
    context.pricePostOpen = data.current(context.spy, "price")
    context.prevReturn = context.pricePostOpen - context.pricePreClose

    if context.prevReturn >= 0:
        if context.yesterBuySell < 0:
            order_target_percent(context.spy, 0)
        else:
            order_target_percent(context.spy, 1)
    elif context.prevReturn <= 0:
        if context.yesterBuySell > 0:
            order_target_percent(context.spy, 0)
        else:
            order_target_percent(context.spy, -1)


def spyPreClose(context, data):
    context.pricePreClose = data.current(context.spy, "price")

    # print ("open = ", context.pricePostOpen, "\nclose = ", context.pricePreClose)


def spyClose(context, data):
    context.priceClose = data.current(context.spy, "price")

    if context.pricePostOpen < context.pricePreClose:
        order_target_percent(context.spy, 0.1 * context.scaleFactor)
        context.yesterBuySell = 1
    else:
        order_target_percent(context.spy, -0.1 * context.scaleFactor)
        context.yesterBuySell = -1

    record(Scaling=context.scaleFactor)
    record(Leverage=context.account.leverage)


# def vixDaily(context, data):
#     context.priceOpen = data.current(context.vix, 'price')
#     context.changeAtOpen = context.priceOpen - context.pricePreClose

# def vixOpen(context, data):
#     context.pricePostOpen = data.current(context.vix, 'price')

#     context.prevReturn = context.pricePostOpen-context.pricePreClose

#     if (context.prevReturn >= 0):
#         if(context.yesterBuySell < 0):
#             order_target_percent(context.vix, 0)
#         else:
#             order_target_percent(context.vix, 1)
#     elif(context.prevReturn <= 0):
#         if(context.yesterBuySell > 0):
#             order_target_percent(context.spy, 0)
#         else:
#             order_target_percent(context.spy, -1)

#     if (context.changeAtOpen < 0):
#         if(context.scaleFactor < 20):
#             context.scaleFactor += 2
#     else:
#         if (context.scaleFactor > 2):
#             context.scaleFactor /= 1.5


# def vixClose(context, data):
#     context.pricePreClose = data.current(context.vix, 'price')

#     if (context.pricePostOpen < context.pricePreClose):
#         order_target_percent(context.vix, -0.1*context.scaleFactor)
#         context.yesterBuySell = -1
#     else:
#         order_target_percent(context.vix, 0.1*context.scaleFactor)
#         context.yesterBuySell = 1

#     record(Scaling = context.scaleFactor)
#     record(Leverage = context.account.leverage)
#     # print ("open = ", context.pricePostOpen, "\nclose = ", context.pricePreClose)
