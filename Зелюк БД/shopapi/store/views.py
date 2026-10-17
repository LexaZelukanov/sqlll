from django.shortcuts import render, redirect
from django.contrib import messages
from .db import call_procedure, call_function
from django.db import connection

# --- Задание 1. Список товаров ---
def products_list(request):
    rows, _ = call_procedure('sp_products_list')
    products = [
        {'id': r[0], 'name': r[1], 'category': r[2], 'price': r[3], 'stock': r[4]}
        for r in rows
    ]
    return render(request, 'store/products_list.html', {'products': products})

# --- Задание 2. Добавление товара ---
def product_add(request):
    if request.method == 'POST':
        name = request.POST['name']
        category_id = int(request.POST['category_id'])
        price = float(request.POST['price'])
        stock = int(request.POST['stock'])

        _, out = call_procedure('sp_product_add', [name, category_id, price, stock], out_count=1, fetch=False)
        new_id = out[0]
        messages.success(request, f'Товар #{new_id} добавлен')
        return redirect('products_list')
    
    with connection.cursor() as cur:
        cur.execute("SELECT category_id, name FROM categories ORDER BY name")
        categories = [{'id': r[0], 'name': r[1]} for r in cur.fetchall()]
    
    return render(request, 'store/product_add.html', {'categories': categories})

# --- Задание 3. Изменение цены ---
def product_update_price(request, pk):
    if request.method == 'POST':
        new_price = float(request.POST['price'])
        call_procedure('sp_product_update_price', [pk, new_price], fetch=False)
        messages.success(request, f'Цена товара #{pk} обновлена')
        return redirect('products_list')
    
    # Передаем ID в шаблон
    return render(request, 'store/product_update_price.html', {'product_id': pk})

# --- Задание 4. Создание заказа ---
def order_create(request):
    if request.method == 'POST':
        customer_id = int(request.POST['customer_id'])
        _, out = call_procedure('sp_order_create', [customer_id], out_count=1, fetch=False)
        order_id = out[0]
        messages.success(request, f'Заказ #{order_id} создан')
        return redirect('customer_orders', pk=customer_id)
    
    with connection.cursor() as cur:
        cur.execute("SELECT customer_id, first_name, last_name FROM customers ORDER BY last_name")
        customers = [{'id': r[0], 'name': f"{r[1]} {r[2]}"} for r in cur.fetchall()]
    return render(request, 'store/order_create.html', {'customers': customers})

# --- Задание 4 (продолжение). Добавление позиции в заказ ---
def order_add_item(request, order_id):
    if request.method == 'POST':
        product_id = int(request.POST['product_id'])
        quantity = int(request.POST['quantity'])
        customer_id = int(request.POST['customer_id'])
        
        _, out = call_procedure(
            'sp_order_add_item', 
            [order_id, product_id, quantity], 
            out_count=2, 
            fetch=False
        )
        success, message = out[0], out[1]
        
        if success:
            messages.success(request, f'Позиция добавлена')
        else:
            messages.error(request, message)
        return redirect('customer_orders', pk=customer_id)
    
    with connection.cursor() as cur:
        cur.execute("SELECT product_id, name FROM products ORDER BY name")
        products = [{'id': r[0], 'name': r[1]} for r in cur.fetchall()]
    return render(request, 'store/order_add_item.html', {'order_id': order_id, 'products': products})

# --- Задание 5. Заказы клиента ---
def customer_orders(request, pk):
    rows, _ = call_procedure('sp_customer_orders', [pk])
    orders = [
        {'id': r[0], 'created_at': r[1], 'total': r[2], 'avg_check': r[3]}
        for r in rows
    ]
    return render(request, 'store/customer_orders.html', {'orders': orders, 'customer_id': pk})

# --- Задание 6. Статистика по категориям ---
def category_stats(request):
    rows, _ = call_procedure('sp_category_stats')
    stats = [
        {'category': r[0], 'products_count': r[1], 'sold_units': r[2], 'revenue': r[3]}
        for r in rows
    ]
    top_category = max(stats, key=lambda x: x['revenue'])['category'] if stats else None
    return render(request, 'store/category_stats.html', {'stats': stats, 'top_category': top_category})

# --- Задание 7. Расчёт скидки ---
def discount_view(request):
    result = None
    if request.method == 'POST':
        customer_id = int(request.POST['customer_id'])
        amount = float(request.POST['amount'])
        percent = call_function('fn_customer_discount', [customer_id, amount])
        total = amount * (1 - float(percent) / 100) # <-- ИСПРАВЛЕНО
        result = {
            'customer_id': customer_id,
            'amount': amount,
            'percent': percent,
            'total': round(total, 2),
        }
    return render(request, 'store/discount.html', {'result': result})