import os
from flask import Flask, render_template_string, request, jsonify, session

app = Flask(__name__)
# مفتاح أمان لتفعيل الجلسات (السلة) داخل المتصفح
app.secret_key = os.environ.get("SECRET_KEY", "harib_market_secret_12345")

# قاعدة بيانات مؤقتة للمنتجات (يمكنك تعديل الأسماء والأسعار والصور هنا)
PRODUCTS = [
    {
            "id": 1,
                    "name": "حساب تليجرام مميز (Premium)",
                            "price": 4.99,
                                    "description": "اشتراك تليجرام رسمي لمدة شهر مع كافة المميزات الحصرية.",
                                            "image": "https://images.unsplash.com/photo-1614680376593-902f74fa0d41?w=500&q=80"
                                                },
                                                    {
                                                            "id": 2,
                                                                    "name": "رقم وهمي لتفعيل الواتساب",
                                                                            "price": 1.99,
                                                                                    "description": "رقم جاهز ومستقر لتفعيل الحسابات واستقبال أكواد التحقق فوراً.",
                                                                                            "image": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=500&q=80"
                                                                                                },
                                                                                                    {
                                                                                                            "id": 3,
                                                                                                                    "name": "أداة فحص الأرقام والاتصالات",
                                                                                                                            "price": 9.99,
                                                                                                                                    "description": "سكربت متطور لفحص حالة الشبكات والبروتوكولات بدقة عالية.",
                                                                                                                                            "image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=500&q=80"
                                                                                                                                                },
                                                                                                                                                    {
                                                                                                                                                            "id": 4,
                                                                                                                                                                    "name": "رصيد إعلانات وتطوير رقمي",
                                                                                                                                                                            "price": 15.00,
                                                                                                                                                                                    "description": "بطاقات شحن رقمية لتمويل الحملات الإعلانية وزيادة الوصول.",
                                                                                                                                                                                            "image": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=500&q=80"
                                                                                                                                                                                                }
                                                                                                                                                                                                ]

                                                                                                                                                                                                # التصميم المتكامل للموقع (HTML + CSS + JavaScript) في ملف واحد ليسهل رفعه
                                                                                                                                                                                                