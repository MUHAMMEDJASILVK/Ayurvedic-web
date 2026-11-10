# 🌿 Kerala Ayurveda Store - Full Stack E-Commerce & Inventory Portal

An **Amazon / Flipkart style e-commerce portal** specialized in authentic **Kerala Ayurvedic medicines, herbal oils, arishtams, lehyams, choornams, and wellness formulations** from established century-old Kerala Ayurvedic pharmacies.

Built with **Python & Django 6**, **HTML5, CSS3, JavaScript**, and **SQLite**.

---

## 🌟 Key Highlights & Features

### 1. 100 Kerala Ayurveda Products Preloaded
Pre-seeded with all 100 authentic classical formulations organized across 6 distinct categories and 8 Kerala manufacturers:
- **Ayurvedic Oils (1–20):** Dhanwantharam Thailam, Ksheerabala Thailam, Neelibringadi Keram, Pinda Thailam, Sahacharadi Thailam, Karpasasthyadi Thailam, Bala Thailam, Gandha Thailam, Chemparuthyadi Keram, Myaxyl Oil, etc.
- **Ayurvedic Medicines & Tablets (21–40):** Triphala Tablets, Yogaraja Guggulu, Kanchanar Guggulu, Chandraprabha Gulika, Maharasnadi Kwath, Nimbadi Kwath, Nisakathakadi Kwath, Varanadi Kwath, Sukumaram Kwath, etc.
- **Beauty & Skincare (41–55):** Kumkumadi Oil, Swarnamukhi Face Pack, Herbal Neem Face Pack, Aloe Vera Herbal Gel, Kumkumadi Cream, Bhringraj Hair Oil, Ayurvedic Herbal Soap, etc.
- **Arishtams & Asavams (56–70):** Asokarishta, Aswagandharishtam, Balarishta, Abhayarishtam, Amrutharishtam, Draksharishta, Dasamoolarishta, Saraswatharishta, Punarnavasavam, etc.
- **Powders & Formulations (71–85):** Avipathi Choornam, Triphala Choornam, Aswagandha Choornam, Brahmi Choornam, Rasnadi Choornam, Kolakulathadi Choornam, Sitopaladi Choornam, etc.
- **Health Supplements & Lehyams (86–100):** Chyavanprash, Narasimha Rasayanam, Vilwadi Lehyam, Ashwagandhadi Lehyam, Brahmi Ghritham, Indukantham Ghritham, Balakalpam, Mathrukalpam, etc.

### 2. Authentic Kerala Ayurvedic Manufacturers
1. **Kottakkal Arya Vaidya Sala (AVS)** (Est. 1902)
2. **Kerala Ayurveda Limited (KAL)** (Est. 1945)
3. **Vaidyaratnam Oushadhasala** (Est. 1941)
4. **Oushadhi (Govt of Kerala)** (Est. 1941)
5. **Nagarjuna Ayurvedic Group** (Est. 1989)
6. **Sitaram Ayurveda Pharmacy** (Est. 1921)
7. **Ashtavaidyan Thaikkattu Mooss** (Est. 1924)
8. **Sreedhareeyam Ayurvedic Eye Hospital & Medicines** (Est. 1930)

---

## 🔐 Real Email & Mobile OTP Verification System

> **Zero Leakage Security:** Unlike prototype applications that print the OTP on the webpage or alert box, **the OTP is strictly NEVER rendered on the registration or verification page.**

### How it Works:
1. **User Registration:**
   - User inputs their Full Name, Email, 10-digit Mobile Number, and Password.
   - The backend validates uniqueness and generates two cryptographically secure 6-digit random codes: `email_otp` and `phone_otp`.
   - The user account is saved in unverified / inactive state (`is_verified=False`, `is_active=False`).
   - Only registered, verified users can log in!
2. **Email OTP Dispatch:**
   - Sent directly to the user's registered inbox using Django's `send_mail` with an authentic Kerala Ayurveda HTML template.
   - In `.env`, plug in your Gmail or any SMTP server credentials (`EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`).
   - If SMTP is not yet configured, Django safely outputs the dispatch event to the server terminal for developers while keeping the browser page completely clean.
3. **Mobile SMS OTP Dispatch:**
   - Dispatched via SMS Gateway (e.g. Fast2SMS / Twilio) using `SMS_API_KEY` in `.env`.
   - If `SMS_API_KEY` is not set, it logs cleanly to the backend server console.
4. **Verification Screen:**
   - Prompts for the Email OTP and Mobile SMS OTP received by the user.
   - 60-second cooldown timer for "Resend OTP".
   - 10-minute validity with automatic expiration.
   - Upon successful verification of both codes, the account is activated and the user is logged in automatically!

---

## 🛒 Amazon & Flipkart Style E-Commerce Features

- **Header Bar:**
  - Kerala Ayurveda logo with herbal leaf emblem.
  - Delivery Pincode selector ("Deliver to Kochi 682001").
  - Search bar with Category dropdown filter and live autocomplete suggestions via AJAX (`/api/search-suggest/`).
  - Account & Lists dropdown menu (My Profile, My Orders, Seller Inventory, Sign Out).
  - Returns & Orders tracker.
  - Cart button with live count badge and bounce animation.
- **Left Sidebar Filtering:**
  - Category selector with live product counts (Oils, Medicines, Arishtams, Lehyams, etc.).
  - Brand filter checkboxes (Kottakkal, Kerala Ayurveda, Vaidyaratnam, Oushadhi, etc.).
  - Price range selector (Under ₹200, ₹200–₹350, ₹350–₹500, Over ₹500).
  - Customer Rating filter (4.5★ & up, 4.0★ & up).
  - Availability filter ("In Stock Only").
  - "Clear All Filters" button.
- **Product Listings & Cards:**
  - High quality authentic Ayurvedic packaging illustrations & SVGs.
  - Discount badges ("#1 Bestseller", "Kerala Pure").
  - Star ratings & review counts.
  - Current price ₹, M.R.P. strikethrough, discount percentage, savings.
  - Live stock status badges ("In Stock", "Only X left in stock - order soon", "Temporarily Out of Stock").
  - AJAX "Add to Cart" button with floating toast notification.
  - "Buy Now" one-click checkout.
- **Shopping Cart:**
  - Quantity spinners (+ / - / delete).
  - Free Delivery Progress Bar (Free Delivery over ₹499).
  - Price details breakdown: Total M.R.P., Discount savings, Delivery fee, Grand total.
- **3-Step Checkout & Payment:**
  - Step 1: Delivery Address (pre-filled from profile).
  - Step 2: Order Review.
  - Step 3: Interactive Payment Options:
    - **UPI / QR Code:** PhonePe, Google Pay, Paytm, BHIM with interactive QR display.
    - **Credit / Debit Cards:** Visa, RuPay, MasterCard.
    - **Net Banking:** Federal Bank, SBI, HDFC, ICICI, Canara.
    - **Cash on Delivery (COD)**.
- **Automated Inventory Stock Deduction:**
  - When an order is placed, stock is automatically decremented from warehouse inventory.
  - If a product reaches 0 units, it automatically displays "Temporarily Out of Stock" and disables ordering.
  - An entry is logged in the `StockLog` audit trail.
- **Tax Invoice & Order Tracking:**
  - Printable official Tax Invoice with Kerala GST details, HSN/SAC codes, and digital certification.
  - Shipment tracking stepper: Order Placed &rarr; Packed &rarr; Dispatched &rarr; Delivered.

---

## 📦 Seller Central & Inventory Management Hub (`/inventory/`)

An Amazon / Flipkart Seller Central interface for managing inventory and orders:
- **Dashboard KPIs:**
  - Total Catalog SKUs (100)
  - Total Units in Stock
  - Low Stock Alert Count (&le;12 units)
  - Out of Stock Count
  - Total Customer Orders & Revenue
- **Product Stock Control (`/inventory/stock/`):**
  - Search by SKU or Name, filter by Category or Stock Status.
  - Inline Quick Restock (+10, +50, or custom units).
- **Order Fulfillment (`/inventory/orders/`):**
  - View all customer orders.
  - Update fulfillment status (Placed &rarr; Processing &rarr; Shipped &rarr; Delivered).
  - Assign courier partner and tracking numbers.
- **Inventory Audit Trail:**
  - Full audit log of all inward shipments and order deductions.

---

## 🚀 How to Run the Project

### 1. Database & Migrations
The SQLite database `db.sqlite3` is already migrated and seeded with all 100 products!
If you ever want to re-seed:
```bash
python manage.py migrate
python manage.py load_ayurveda_products
```

### 2. Configure Real Email (Gmail / SMTP) in `.env`
Open the `.env` file in the project root:
```ini
DEBUG=True
SECRET_KEY=kerala-ayurveda-store-super-secret-key-2026

# To send real Email OTP directly to registered inboxes:
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_16_char_app_password
DEFAULT_FROM_EMAIL="Kerala Ayurveda Store <your_email@gmail.com>"

# Optional SMS Gateway (Fast2SMS / Twilio)
SMS_API_KEY=
SMS_SENDER_ID=AYURVD
```
> **Tip for Gmail:** Generate a 16-character App Password via Google Account &rarr; Security &rarr; 2-Step Verification &rarr; App Passwords. Real emails with OTP will be sent immediately to the user's inbox!

### 3. Start the Server
```bash
python manage.py runserver
```
Visit in your browser:
- **Storefront:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Register / OTP:** [http://127.0.0.1:8000/accounts/register/](http://127.0.0.1:8000/accounts/register/)
- **Sign In:** [http://127.0.0.1:8000/accounts/login/](http://127.0.0.1:8000/accounts/login/)
- **Cart:** [http://127.0.0.1:8000/cart/](http://127.0.0.1:8000/cart/)
- **Seller Inventory Hub:** [http://127.0.0.1:8000/inventory/](http://127.0.0.1:8000/inventory/)
- **Django Admin:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

### 4. Default Admin Credentials
- **Email:** `admin@keralaayurveda.com`
- **Password:** `adminpassword123`

---

## 🧪 Running Automated Tests
```bash
python manage.py test
```
All 10 test suites pass covering product seeding, filtering, registration, OTP dispatch, OTP verification, cart calculations, stock deduction, and seller dashboard controls.

