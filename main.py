import os
import sqlite3
import requests
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'harib_secured_multiuser_system_2026'

ADMIN_PASSWORD = "123" 
IMGBB_API_KEY = "6b7b7a66099bfae7e6e2329f6350f0ec"

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price TEXT NOT NULL,
            category TEXT NOT NULL,
            sizes TEXT NOT NULL,
            details TEXT NOT NULL,
            image TEXT NOT NULL,
            merchant_phone TEXT NOT NULL,
            merchant_name TEXT NOT NULL,
            show_name INTEGER DEFAULT 1
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            phone TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL DEFAULT 'تاجر'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    user_phone = session.get('user_phone')
    merchant_phone = session.get('merchant_phone')
    is_admin = session.get('is_admin', False)
    category_filter = request.args.get('category', 'الكل')
    
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if category_filter != 'الكل':
        cursor.execute('SELECT * FROM products WHERE category = ? ORDER BY id DESC', (category_filter,))
    else:
        cursor.execute('SELECT * FROM products ORDER BY id DESC')
    db_products = cursor.fetchall()
    
    my_products = []
    if merchant_phone:
        cursor.execute('SELECT * FROM products WHERE merchant_phone = ? ORDER BY id DESC', (merchant_phone,))
        my_products = cursor.fetchall()
        
    conn.close()

    html_content = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>متجر حريب الأول</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body { font-family: sans-serif; background-color: #f4f6f9; margin: 0; padding: 0; padding-bottom: 80px; text-align: right; }
            .classic-header { background: linear-gradient(135deg, #8d6e63, #4e342e); color: #fffde7; padding: 20px 15px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.15); }
            .classic-brand { font-size: 1.8rem; font-weight: bold; }
            .role-switcher { display: flex; justify-content: center; background: white; border-bottom: 1px solid #e0e0e0; }
            .role-btn { flex: 1; padding: 15px; text-align: center; border: none; background: none; font-weight: bold; color: #666; cursor: pointer; }
            .role-btn.active { color: #8d6e63; border-bottom: 3px solid #8d6e63; background: #f9f9f9; }
            .container { padding: 15px; max-width: 600px; margin: 0 auto; }
            .panel-box { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: none; }
            .panel-box.active { display: block; }
            .form-group { margin-bottom: 15px; }
            .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
            .form-control { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; }
            .submit-btn { background: #8d6e63; color: white; border: none; padding: 12px; width: 100%; border-radius: 6px; font-weight: bold; cursor: pointer; }
            .categories-bar { display: flex; gap: 8px; padding: 10px 0; overflow-x: auto; }
            .cat-item { background: #fff; border: 1px solid #ddd; padding: 6px 15px; border-radius: 20px; text-decoration: none; color: #333; font-size: 0.85rem; }
            .cat-item.active { background: #8d6e63; color: white; }
            .products-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 10px; }
            .product-card { background: white; border-radius: 8px; border: 1px solid #e0e0e0; padding: 10px; text-align: center; cursor: pointer; }
            .product-img { width: 100%; height: 120px; object-fit: cover; border-radius: 6px; }
            .product-title { font-size: 0.9rem; font-weight: bold; margin: 8px 0; }
            .product-price { color: #e91e63; font-weight: bold; }
            .merchant-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            .merchant-table th, .merchant-table td { border: 1px solid #ddd; padding: 8px; text-align: center; font-size: 0.85rem; }
            .btn-delete { background: #dc3545; color: white; padding: 4px 8px; text-decoration: none; border-radius: 4px; font-size: 0.8rem; }
            .btn-edit { background: #0b5ed7; color: white; border: none; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; cursor: pointer; }
            .modal { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.6); z-index: 2000; justify-content: center; align-items: center; padding: 20px; }
            .modal-content { background: white; width: 100%; max-width: 450px; border-radius: 12px; padding: 20px; position: relative; }
            .close-modal { position: absolute; top: 15px; left: 15px; font-size: 1.5rem; background: none; border: none; cursor: pointer; }
            .whatsapp-btn { background: #25D366; color: white; text-decoration: none; padding: 12px; display: block; text-align: center; border-radius: 8px; font-weight: bold; margin-top: 15px; }
            .logout-link { font-size: 0.8rem; color: #dc3545; text-decoration: none; margin-right: 10px; }
        </style>
    </head>
    <body>
        <div class="classic-header">
            <div class="classic-brand">﴿ مَتْجَرُ حَرِيبْ الأَوَّلْ ﴾</div>
        </div>

        <div class="role-switcher">
            <button id="btn-customer" class="role-btn active" onclick="switchRole('customer')"><i class="fas fa-shopping-bag"></i> العميل</button>
            <button id="btn-merchant" class="role-btn" onclick="switchRole('merchant')"><i class="fas fa-store-alt"></i> لوحة التاجر</button>
            <button id="btn-admin" class="role-btn" style="color:#d32f2f;" onclick="switchRole('admin')"><i class="fas fa-user-shield"></i> المدير</button>
        </div>

        <div class="container">
            <div id="customerView" class="panel-box active">
                {% if not user_phone %}
                <h4 style="text-align:center; color:#4e342e;"><i class="fas fa-user-check"></i> تسجيل دخول الزبون لتصفح السلع</h4>
                <form action="/customer_login" method="POST">
                    <div class="form-group">
                        <label>رقم جوالك (واتساب):</label>
                        <input type="number" name="user_phone" class="form-control" placeholder="96777XXXXXXX" required>
                    </div>
                    <button type="submit" class="submit-btn">دخول السيرفر والاقسام</button>
                </form>
                {% else %}
                <div style="font-size:0.85rem; margin-bottom:10px; color:#666;">
                    مرحباً بك زبوننا العزيز رقم: <span style="font-weight:bold; color:#8d6e63;">{{ user_phone }}</span>
                    <a href="/logout/user" class="logout-link">📴 خروج</a>
                </div>

                <div class="categories-bar">
                    <a href="/?category=الكل" class="cat-item {% if current_cat == 'الكل' %}active{% endif %}">الكل</a>
                    <a href="/?category=ملابس" class="cat-item {% if current_cat == 'ملابس' %}active{% endif %}">ملابس</a>
                    <a href="/?category=اكسسوارات" class="cat-item {% if current_cat == 'اكسسوارات' %}active{% endif %}">اكسسوارات</a>
                    <a href="/?category=تجميل" class="cat-item {% if current_cat == 'تجميل' %}active{% endif %}">تجميل</a>
                    <a href="/?category=أواني منزلية" class="cat-item {% if current_cat == 'أواني منزلية' %}active{% endif %}">أواني منزلية</a>
                </div>

                <div class="products-grid">
                    {% for product in active_products %}
                    <div class="product-card" onclick="openProductModal('{{ product.title }}', '{{ product.price }}', '{{ product.image }}', '{{ product.details }}', '{{ product.sizes }}', '{{ product.merchant_phone }}', '{% if product.show_name == 1 %}{{ product.merchant_name }}{% else %}تاجر مجهول{% endif %}')">
                        <img src="{{ product.image }}" class="product-img">
                        <div class="product-title">{{ product.title }}</div>
                        <div style="font-size:0.8rem; color:#666;">
                            🏪 {% if product.show_name == 1 %} {{ product.merchant_name }} {% else %} تاجر مستور {% endif %}
                        </div>
                        <div class="product-price">{{ product.price }} ر.ي</div>
                    </div>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
            
            <div id="merchantView" class="panel-box">
                {% if not merchant_phone %}
                <h4 style="text-align:center; color:#4e342e;"><i class="fas fa-lock"></i> دخول لوحة التاجر الخاصة بك</h4>
                <form action="/merchant_login" method="POST">
                    <div class="form-group">
                        <label>رقم جوالك المسجل بالنشر:</label>
                        <input type="number" name="merchant_phone" class="form-control" placeholder="9677........" required>
                    </div>
                    <button type="submit" class="submit-btn">عرض لوحتي وبضاعتي فقط</button>
                </form>
                {% else %}
                <div style="font-size:0.85rem; margin-bottom:15px; background:#fbe9e7; padding:8px; border-radius:6px;">
                    حساب التاجر النشط: <b>{{ merchant_phone }}</b>
                    <a href="/logout/merchant" class="logout-link" style="float:left;">📴 تبديل الحساب</a>
                </div>

                <h3 style="text-align:center; color:#4e342e; font-size:1.1rem;"><i class="fas fa-plus-circle"></i> نشر صنف جديد</h3>
                <form action="/add_product" method="POST" enctype="multipart/form-data">
                    <div class="form-group">
                        <label>اسمك التجاري:</label>
                        <input type="text" name="merchant_name" value="عبدالله علوي" class="form-control" required>
                    </div>
                    <div class="form-group" style="background:#f9f9f9; padding:8px; border-radius:6px;">
                        <input type="checkbox" name="show_name" value="1" id="showNameCheck" checked>
                        <label style="display:inline; cursor:pointer;" for="showNameCheck">إظهار اسمي للزبائن على هذه البضاعة</label>
                    </div>
                    <div class="form-group">
                        <label>اسم الصنف:</label>
                        <input type="text" name="title" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label>السعر (ريال يمني):</label>
                        <input type="text" name="price" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label>القسم:</label>
                        <select name="category" class="form-control">
                            <option>ملابس</option>
                            <option>اكسسوارات</option>
                            <option>تجميل</option>
                            <option>أواني منزلية</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>المقاسات:</label>
                        <input type="text" name="sizes" class="form-control" placeholder="S, M, L" required>
                    </div>
                    <div class="form-group">
                        <label>تفاصيل ووصف البضاعة:</label>
                        <textarea name="details" class="form-control" rows="2" required></textarea>
                    </div>
                    <div class="form-group">
                        <label>اختر صورة المنتج مباشرة من الاستوديو:</label>
                        <input type="file" name="image_file" class="form-control" accept="image/*" required>
                    </div>
                    <button type="submit" class="submit-btn">نشر البضاعة فوراً</button>
                </form>

                <h4 style="color:#4e342e; text-align:center; margin-top:25px; border-top:1px solid #eee; padding-top:15px;"><i class="fas fa-box"></i> بضاعتك المعروضة فقط ({{ my_products|length }})</h4>
                <table class="merchant-table">
                    <thead>
                        <tr>
                            <th>الصنف</th>
                            <th>السعر</th>
                            <th>التحكم الحصري</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for p in my_products %}
                        <tr>
                            <td>{{ p.title }} <br><span style="font-size:0.75rem; color:#888;">👀 {% if p.show_name == 1 %}الاسم ظاهر{% else %}الاسم مخفي{% endif %}</span></td>
                            <td>
                                <form action="/merchant_update_price/{{ p.id }}" method="POST" style="display:inline-flex; gap:4px;">
                                    <input type="text" name="new_price" value="{{ p.price }}" style="width:50px; text-align:center;">
                                    <button type="submit" class="btn-edit"><i class="fas fa-check"></i></button>
                                </form>
                            </td>
                            <td>
                                <a href="/merchant_delete_product/{{ p.id }}" class="btn-delete" onclick="return confirm('مسح الصنف نهائياً؟')"><i class="fas fa-trash-alt"></i> مسح</a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% endif %}
            </div>

            <div id="adminView" class="panel-box">
                {% if not is_admin %}
                <h4 style="color:#d32f2f; text-align:center;"><i class="fas fa-lock"></i> إدارة المنصة العليا</h4>
                <form action="/admin_login" method="POST">
                    <div class="form-group">
                        <label>كلمة المرور:</label>
                        <input type="password" name="password" class="form-control" required>
                    </div>
                    <button type="submit" class="submit-btn" style="background:#d32f2f;">دخول الإدارة العامة</button>
                </form>
                {% else %}
                <div style="background:#fff3f3; padding:8px; border-radius:6px; margin-bottom:15px;">
                    <span style="color:#d32f2f; font-weight:bold;">المدير العام للمنصة</span>
                    <a href="/logout/admin" style="float:left; color:#666; text-decoration:none;">خروج المشرف</a>
                </div>
                <p style="font-size:0.85rem; text-align:center; color:#555;">المدير يمتلك كامل الصلاحيات لمراقبة السيرفر والتحكم بالحسابات.</p>
                {% endif %}
            </div>
        </div>

        <div id="productModal" class="modal" onclick="closeProductModal()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <button class="close-modal" onclick="closeProductModal()">&times;</button>
                <img id="modalImg" src="" style="width:100%; height:180px; object-fit:cover; border-radius:8px;">
                <h3 id="modalTitle" style="margin:10px 0;"></h3>
                <h4 id="modalPrice" style="color:#e91e63; margin:5px 0;"></h4>
                <p style="font-size:0.9rem;"><b>التاجر:</b> <span id="modalMerchant"></span></p>
                <p style="font-size:0.9rem;"><b>المقاسات:</b> <span id="modalSizes"></span></p>
                <p style="font-size:0.9rem;"><b>الوصف:</b> <span id="modalDetails"></span></p>
                <a id="modalWhatsAppBtn" href="" target="_blank" class="whatsapp-btn"><i class="fab fa-whatsapp"></i> اطلب الآن عبر الواتساب</a>
            </div>
        </div>

        <script>
            function switchRole(role) {
                document.querySelectorAll('.role-btn').forEach(btn => btn.classList.remove('active'));
                document.getElementById('customerView').style.display = 'none';
                document.getElementById('merchantView').style.display = 'none';
                document.getElementById('adminView').style.display = 'none';
                
                if(role === 'merchant') {
                    document.getElementById('merchantView').style.display = 'block';
                    document.getElementById('btn-merchant').classList.add('active');
                } else if(role === 'admin') {
                    document.getElementById('adminView').style.display = 'block';
                    document.getElementById('btn-admin').classList.add('active');
                } else {
                    document.getElementById('customerView').style.display = 'block';
                    document.getElementById('btn-customer').classList.add('active');
                }
            }
            function openProductModal(title, price, image, details, sizes, phone, merchantName) {
                document.getElementById('modalImg').src = image;
                document.getElementById('modalTitle').innerText = title;
                document.getElementById('modalPrice').innerText = price + " ريال يمني";
                document.getElementById('modalMerchant').innerText = merchantName;
                document.getElementById('modalSizes').innerText = sizes;
                document.getElementById('modalDetails').innerText = details;
                let msg = "مرحباً، أريد طلب صنف: (" + title + ") المعروض في متجر حريب الأول.";
                document.getElementById('modalWhatsAppBtn').href = "https://wa.me/" + phone + "?text=" + encodeURIComponent(msg);
                document.getElementById('productModal').style.display = 'flex';
            }
            function closeProductModal() { document.getElementById('productModal').style.display = 'none'; }
            
            {% if merchant_phone %} switchRole('merchant'); {% endif %}
            {% if is_admin %} switchRole('admin'); {% endif %}
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content, active_products=db_products, my_products=my_products, current_cat=category_filter, user_phone=user_phone, merchant_phone=merchant_phone, is_admin=is_admin)

@app.route('/customer_login', methods=['POST'])
def customer_login():
    session['user_phone'] = request.form.get('user_phone')
    return redirect(url_for('home'))

@app.route('/merchant_login', methods=['POST'])
def merchant_login():
    session['merchant_phone'] = request.form.get('merchant_phone')
    return redirect(url_for('home'))

@app.route('/add_product', methods=['POST'])
def add_product():
    merchant_phone = session.get('merchant_phone')
    if not merchant_phone: return redirect(url_for('home'))
    
    merchant_name = request.form.get('merchant_name')
    show_name = 1 if request.form.get('show_name') == '1' else 0
    title = request.form.get('title')
    price = request.form.get('price')
    category = request.form.get('category')
    sizes = request.form.get('sizes')
    details = request.form.get('details')
    
    file = request.files.get('image_file')
    image_url = "https://images.unsplash.com/photo-1541014741259-df5290bc008c?w=400"
    
    if file and file.filename != '':
        try:
            img_data = file.read()
            response = requests.post(
                "https://api.imgbb.com/1/upload",
                data={"key": IMGBB_API_KEY},
                files={"image": img_data}
            )
            if response.status_code == 200:
                image_url = response.json()['data']['url']
        except Exception as e:
            print("Error uploading image:", e)
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (title, price, category, sizes, details, image, merchant_phone, merchant_name, show_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, price, category, sizes, details, image_url, merchant_phone, merchant_name, show_name))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/merchant_update_price/<int:product_id>', methods=['POST'])
def merchant_update_price(product_id):
    merchant_phone = session.get('merchant_phone')
    if not merchant_phone: return redirect(url_for('home'))
    
    new_price = request.form.get('new_price')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET price = ? WHERE id = ? AND merchant_phone = ?", (new_price, product_id, merchant_phone))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/merchant_delete_product/<int:product_id>')
def merchant_delete_product(product_id):
    merchant_phone = session.get('merchant_phone')
    if not merchant_phone: return redirect(url_for('home'))
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ? AND merchant_phone = ?", (product_id, merchant_phone))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/admin_login', methods=['POST'])
def admin_login():
    if request.form.get('password') == ADMIN_PASSWORD:
        session['is_admin'] = True
    return redirect(url_for('home'))

@app.route('/logout/<string:user_type>')
def logout(user_type):
    if user_type == 'user': session.pop('user_phone', None)
    elif user_type == 'merchant': session.pop('merchant_phone', None)
    elif user_type == 'admin': session.pop('is_admin', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
