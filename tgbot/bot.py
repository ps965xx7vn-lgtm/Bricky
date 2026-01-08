import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.bricky.settings')
django.setup()
import telebot
from environs import Env
from backend.users.models import *
from backend.store.models import *
from backend.orders.models import *
from telebot import types

env = Env()
env.read_env()
bot = telebot.TeleBot(env.str("TG_TOKEN"))
pay_token = env.str("PAY_TOKEN")
user_state = {}
user_data = {}


#
def create_user(tg_id, name):
    CustomUser.objects.update_or_create(tg_id=tg_id, first_name=name, username=tg_id)


def create_cart(tg_id):
    Order.objects.update_or_create(user=CustomUser.objects.get(tg_id=tg_id),is_draft=True)


def add_to_cart(tg_id, product_id):
    user = CustomUser.objects.get(tg_id=tg_id)
    order = Order.objects.get(user=user, is_draft=True)
    try:
        order_element = OrderElement.objects.get(order=order.id, product=product_id)
    except OrderElement.DoesNotExist:
        order_element = None
    product = Cake.objects.get(id=product_id)
    if order_element:
        order_element.quantity += 1
        order_element.price += product.price
        order_element.save()

    else:

        OrderElement.objects.create(order=order, product=product, quantity=1, price=product.price)


def delete_item(order_element_id):
    order_element = OrderElement.objects.get(id=order_element_id)
    if order_element.quantity > 1:
        order_element.quantity -= 1
        order_element.save()
    else:
        order_element.delete()


def start_pay(message):
    user_id = message.chat.id
    user_state[user_id] = "email"
    user_data[user_id] = {}
    bot.send_message(user_id, text="Enter your e-mail!")


def pay(message):
    user = CustomUser.objects.get(tg_id=message.chat.id)
    order = Order.objects.get(user=user,is_draft=True)
    total_price = 0
    for order_element in OrderElement.objects.filter(order=order):
        total_price += order_element.price
    prices=[types.LabeledPrice(label="Pay for Order",amount=total_price*100)]
    bot.send_invoice(message.chat.id,title="Paying",description="Pay for Order",provider_token=pay_token,currency="try",prices=prices,start_parameter="test_pay",invoice_payload="test_payload")
@bot.pre_checkout_query_handler(func=lambda q:True)
def pre_checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id,ok=True)
@bot.message_handler(content_types=["successful_payment"])
def got_payment(message):
    confirm_order(message.chat.id)
    create_cart(message.chat.id)
    bot.send_message(message.chat.id,text="Pay completed!")


@bot.message_handler(func=lambda msg: msg.chat.id in user_state)
def handle_pay_steps(message):
    user_id = message.chat.id
    state = user_state.get(user_id)
    if state == "email":
        user_data[user_id]["email"] = message.text.strip()
        user_state[user_id] = "phone"
        bot.send_message(user_id, text="Enter your phone number!")
    elif state == "phone":
        user_data[user_id]["phone"] = message.text.strip()
        user_state[user_id] = "address"
        bot.send_message(user_id, text="Enter your address!")
    elif state == "address":
        user_data[user_id]["address"] = message.text.strip()
        del user_state[user_id]
        info = user_data[user_id]
        markup = types.InlineKeyboardMarkup()
        confirm_btn = types.InlineKeyboardButton(text="Confirm", callback_data="confirm")
        cancel_btn = types.InlineKeyboardButton(text="Cancel", callback_data="cancel")
        markup.row(confirm_btn)
        markup.row(cancel_btn)
        bot.send_message(message.chat.id, f"Check your info: \n{info["email"]}\n{info["phone"]}\n{info["address"]}",
                         reply_markup=markup)

def confirm_order(tg_id):
    user=CustomUser.objects.get(tg_id=tg_id)
    order = Order.objects.get(user=user.id,is_draft=True)
    info = user_data[tg_id]
    order.email = info["email"]
    order.phone = info["phone"]
    order.address = info["address"]
    order.is_draft = False
    order.status = "M"
    order.save()

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    create_user(message.chat.id, message.chat.first_name)
    create_cart(message.chat.id)
    bot.send_message(message.chat.id, text=f"Hello!{message.chat.first_name}")
    bot.send_message(message.chat.id, text="What dessert would you like to order?")
    filter_btn = types.InlineKeyboardButton(text="Filters", callback_data=f"filter")
    markup.row(filter_btn)
    for category in CakeCategory.objects.all():
        btn = types.InlineKeyboardButton(text=category.title, callback_data=f"list|{category.id}")
        markup.row(btn)

    cart_btn = types.InlineKeyboardButton(text="My cart", callback_data="cart")
    markup.row(cart_btn)
    bot.send_message(message.chat.id, "Select an item:", reply_markup=markup)

@bot.message_handler(commands=['myorders'])
def my_orders(message):
    user =CustomUser.objects.get(tg_id=message.chat.id)
    orders = Order.objects.filter(user=user.id,is_draft=False)
    counter = 0
    for order in orders:
        counter +=1
        bot.send_message(message.chat.id, f"Order{counter}:")
        bot.send_message(message.chat.id, "Products:")
        for order_element in OrderElement.objects.filter(order=order.id):
            bot.send_message(message.chat.id, f"{order_element.product.title} {order_element.quantity}")
        bot.send_message(message.chat.id, f"E-mail: {order.email} \nPhone Number: {order.phone}\nAddress: {order.address}")
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data.split("|", 1)[0] == "list":
        markup = types.InlineKeyboardMarkup()
        for cake in Cake.objects.filter(category=call.data.split("|", 1)[1]):
            btn = types.InlineKeyboardButton(text=cake.title, callback_data=f"product|{cake.id}")
            markup.row(btn)
        menu_btn = types.InlineKeyboardButton("Back", callback_data="cat_list")
        markup.row(menu_btn)
        bot.send_message(call.message.chat.id, "Select an item:", reply_markup=markup)
    if call.data.split("|", 1)[0] == "product":
        markup = types.InlineKeyboardMarkup()
        product = Cake.objects.get(id=call.data.split("|", 1)[1])

        back_btn = types.InlineKeyboardButton("Back", callback_data=f"list|{product.category.id}")
        add_to_cart_btn = types.InlineKeyboardButton("Add to cart", callback_data=f"add_to_cart|{product.id}")
        cart_btn = types.InlineKeyboardButton(text="My cart", callback_data="cart")
        markup.row(add_to_cart_btn)
        markup.row(cart_btn)
        markup.row(back_btn)
        bot.send_photo(call.message.chat.id, photo=product.image,
                       caption=f"{product.description} \nPrice: {product.price}\nSize: {product.size}\nIngredient: {product.ingredient}",
                       reply_markup=markup)
    if call.data.split("|", 1)[0] == "add_to_cart":
        add_to_cart(tg_id=call.message.chat.id, product_id=call.data.split("|", 1)[1])
        bot.send_message(call.message.chat.id, text="Product added")
    if call.data == "cart":
        markup = types.InlineKeyboardMarkup()
        user = CustomUser.objects.get(tg_id=call.message.chat.id)
        order = Order.objects.get(user=user, is_draft=True)
        order_elements = OrderElement.objects.filter(order=order)
        if order_elements.exists():
            for order_element in order_elements:
                btn = types.InlineKeyboardButton(f"Cancel {order_element.product.title} {order_element.quantity}",
                                                 callback_data=f"delete_item|{order_element.id}")
                markup.row(btn)
                bot.send_message(call.message.chat.id, text=f"{order_element.product.title} {order_element.quantity}")
            menu_btn = types.InlineKeyboardButton("Continue Shopping", callback_data="cat_list")
            pay_btn = types.InlineKeyboardButton("Pay", callback_data="pay")
            markup.row(menu_btn)
            markup.row(pay_btn)
            bot.send_message(call.message.chat.id, text="You can delete products:", reply_markup=markup)
        else:
            menu_btn = types.InlineKeyboardButton("Go Shopping", callback_data="cat_list")
            markup.row(menu_btn)
            bot.send_message(call.message.chat.id, text="Add somthing first", reply_markup=markup)
    if call.data == "cat_list":
        markup = types.InlineKeyboardMarkup()
        filter_btn = types.InlineKeyboardButton(text="Filters", callback_data=f"filter")
        markup.row(filter_btn)
        for category in CakeCategory.objects.all():
            btn = types.InlineKeyboardButton(text=category.title, callback_data=f"list|{category.id}")
            markup.row(btn)
        cart_btn = types.InlineKeyboardButton(text="My cart", callback_data="cart")
        markup.row(cart_btn)
        bot.send_message(call.message.chat.id, "Select an item:", reply_markup=markup)
    if call.data.split("|", 1)[0] == "delete_item":
        markup = types.InlineKeyboardMarkup()
        user = CustomUser.objects.get(tg_id=call.message.chat.id)
        order = Order.objects.get(user=user, is_draft=True)
        order_elements = OrderElement.objects.filter(order=order)
        if order_elements.exists():
            delete_item(call.data.split("|", 1)[1])
            bot.send_message(call.message.chat.id, text="Product canceled")
        else:
            menu_btn = types.InlineKeyboardButton("Go Shopping", callback_data="cat_list")
            markup.row(menu_btn)
            bot.send_message(call.message.chat.id, text="Add somthing first", reply_markup=markup)
    if call.data == "pay":
        markup = types.InlineKeyboardMarkup()
        user = CustomUser.objects.get(tg_id=call.message.chat.id)
        order = Order.objects.get(user=user, is_draft=True)
        order_elements = OrderElement.objects.filter(order=order)
        if order_elements.exists():
            start_pay(call.message)
        else:
            menu_btn = types.InlineKeyboardButton("Go Shopping", callback_data="cat_list")
            markup.row(menu_btn)
            bot.send_message(call.message.chat.id, text="Add somthing first", reply_markup=markup)
    if call.data == "confirm":
        pay(call.message)

    if call.data == "cancel":
        markup = types.InlineKeyboardMarkup()
        cart_btn = types.InlineKeyboardButton(text="Back", callback_data="cart")
        markup.row(cart_btn)
        bot.send_message(call.message.chat.id, text="You canceled paying", reply_markup=markup)
    if call.data == "filter":
        markup = types.InlineKeyboardMarkup()
        ing_btn = types.InlineKeyboardButton(text="Ingredients", callback_data="ingredient")
        price_btn = types.InlineKeyboardButton(text="Size", callback_data="size")
        cart_btn = types.InlineKeyboardButton(text="Back", callback_data="cart")
        markup.row(ing_btn)
        markup.row(price_btn)
        markup.row(cart_btn)
        bot.send_message(call.message.chat.id, text="Filter by:", reply_markup=markup)
    if call.data == "ingredient":
        markup = types.InlineKeyboardMarkup()
        for ingredient in Ingredient.objects.all():
            btn = types.InlineKeyboardButton(text=ingredient.title, callback_data=f"filter_ing|{ingredient.id}")
            markup.row(btn)
        back_btn = types.InlineKeyboardButton(text="Back", callback_data="filter")
        markup.row(back_btn)
        bot.send_message(call.message.chat.id, "Select an item:", reply_markup=markup)
    if call.data.split("|", 1)[0] == "filter_ing":
        markup = types.InlineKeyboardMarkup()
        for product in Cake.objects.filter(ingredient=call.data.split("|", 1)[1]):
            btn = types.InlineKeyboardButton(text=product.title, callback_data=f"product|{product.id}")
            markup.row(btn)
        info_btn = types.InlineKeyboardButton("Info", callback_data=f"ing_info|{call.data.split("|", 1)[1]}")
        ing_btn = types.InlineKeyboardButton("Back", callback_data="ingredient")
        markup.row(info_btn)
        markup.row(ing_btn)
        bot.send_message(call.message.chat.id, "Select an item:", reply_markup=markup)
    if call.data.split("|", 1)[0] == "ing_info":
        markup = types.InlineKeyboardMarkup()
        ingredient = Ingredient.objects.get(id=call.data.split("|", 1)[1])
        btn = types.InlineKeyboardButton(text="Back", callback_data=f"filter_ing|{ingredient.id}")
        markup.row(btn)
        bot.send_message(call.message.chat.id, text=ingredient.description, reply_markup=markup)
    if call.data == "size":
        markup = types.InlineKeyboardMarkup()
        for size in Size.objects.all():
            btn = types.InlineKeyboardButton(text=size.title, callback_data=f"filter_size|{size.id}")
            markup.row(btn)
        back_btn = types.InlineKeyboardButton(text="Back", callback_data="filter")
        markup.row(back_btn)
        bot.send_message(call.message.chat.id, "Select an item:", reply_markup=markup)
    if call.data.split("|", 1)[0] == "filter_size":
        markup = types.InlineKeyboardMarkup()
        for product in Cake.objects.filter(size=call.data.split("|", 1)[1]):
            btn = types.InlineKeyboardButton(text=product.title, callback_data=f"product|{product.id}")
            markup.row(btn)
        info_btn = types.InlineKeyboardButton("Info", callback_data=f"size_info|{call.data.split("|", 1)[1]}")
        size_btn = types.InlineKeyboardButton("Back", callback_data="size")
        markup.row(info_btn)
        markup.row(size_btn)
        bot.send_message(call.message.chat.id, "Select an item:", reply_markup=markup)
    if call.data.split("|", 1)[0] == "size_info":
        markup = types.InlineKeyboardMarkup()
        size = Size.objects.get(id=call.data.split("|", 1)[1])
        btn = types.InlineKeyboardButton(text="Back", callback_data=f"filter_size|{size.id}")
        markup.row(btn)
        bot.send_message(call.message.chat.id, text=size.description, reply_markup=markup)
bot.infinity_polling()
