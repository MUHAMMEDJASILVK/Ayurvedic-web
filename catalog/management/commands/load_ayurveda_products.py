import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalog.models import Category, Brand, Product

BRANDS_DATA = [
    {
        "name": "Kottakkal Arya Vaidya Sala",
        "description": "Established in 1902 by Vaidyaratnam P.S. Varier, Kottakkal Arya Vaidya Sala is the century-old beacon of authentic classical Kerala Ayurveda.",
        "headquarters": "Kottakkal, Malappuram, Kerala",
        "established_year": 1902,
        "logo_badge": "AVS"
    },
    {
        "name": "Kerala Ayurveda",
        "description": "Kerala Ayurveda Limited is a pioneer in bringing classical Ayurvedic medicine backed by modern scientific quality and research.",
        "headquarters": "Aluva, Ernakulam, Kerala",
        "established_year": 1945,
        "logo_badge": "KAL"
    },
    {
        "name": "Vaidyaratnam",
        "description": "Vaidyaratnam Oushadhasala follows the sacred Ashtavaidya tradition of Kerala, manufacturing over 500 classical formulations.",
        "headquarters": "Thaikkattussery, Ollur, Thrissur, Kerala",
        "established_year": 1941,
        "logo_badge": "VOS"
    },
    {
        "name": "Oushadhi",
        "description": "The Pharmaceutical Corporation (I.M.) Kerala Ltd., the largest producer of traditional Ayurvedic medicines under the Government of Kerala.",
        "headquarters": "Kuttanellur, Thrissur, Kerala",
        "established_year": 1941,
        "logo_badge": "OSH"
    },
    {
        "name": "Nagarjuna Ayurveda",
        "description": "Nagarjuna Ayurvedic Group is known for its extensive range of specialized formulations and modern GMP manufacturing.",
        "headquarters": "Thodupuzha, Idukki, Kerala",
        "established_year": 1989,
        "logo_badge": "NAG"
    },
    {
        "name": "Sitaram Ayurveda",
        "description": "Sitaram Ayurveda was established in 1921 by the Maharaja of Cochin, delivering genuine Kerala heritage wellness for over a century.",
        "headquarters": "Thrissur, Kerala",
        "established_year": 1921,
        "logo_badge": "SIT"
    },
    {
        "name": "Ashtavaidyan Thaikkattu Mooss",
        "description": "Direct lineage of the venerable Ashtavaidyans of Kerala, famous for classical Rasayana therapy and master formulations.",
        "headquarters": "Ollur, Thrissur, Kerala",
        "established_year": 1924,
        "logo_badge": "ATM"
    },
    {
        "name": "Sreedhareeyam",
        "description": "Renowned Kerala Ayurvedic establishment famous for traditional Ayurvedic ophthalmology, eye tonics, and general herbal medicines.",
        "headquarters": "Koothattukulam, Ernakulam, Kerala",
        "established_year": 1930,
        "logo_badge": "SRD"
    }
]

CATEGORIES_DATA = [
    {
        "name": "Ayurvedic Oils",
        "slug": "ayurvedic-oils",
        "description": "Traditional Kerala medicated oils, Kerams (coconut oil base), and Thailams (sesame oil base) processed using classical Sneha Kalpana.",
        "icon_name": "fa-tint",
        "display_order": 1
    },
    {
        "name": "Ayurvedic Medicines & Tablets",
        "slug": "medicines-tablets",
        "description": "Classical Gulikas, Kwath tablets, Guggulu preparations, and potent purified mineral-herb compounds.",
        "icon_name": "fa-pills",
        "display_order": 2
    },
    {
        "name": "Beauty & Skincare",
        "slug": "beauty-skincare",
        "description": "Kumkumadi oils, natural face packs, herbal hair oils, gentle cleansers, and authentic Ayurvedic soaps.",
        "icon_name": "fa-spa",
        "display_order": 3
    },
    {
        "name": "Arishtams & Asavams",
        "slug": "arishtams-asavams",
        "description": "Self-generated natural fermented herbal wines and tonics containing bio-available active medicinal compounds.",
        "icon_name": "fa-wine-bottle",
        "display_order": 4
    },
    {
        "name": "Powders & Herbal Formulations",
        "slug": "powders-formulations",
        "description": "Finely milled herbal Choornams, decoctions, and classical Kwath powders formulated according to Ashtanga Hridaya.",
        "icon_name": "fa-mortar-pestle",
        "display_order": 5
    },
    {
        "name": "Health Supplements & Lehyams",
        "slug": "supplements-lehyams",
        "description": "Herbal jams, Rasayanams, medicated Ghrithams (clarified butter), and vitality restorative tonics.",
        "icon_name": "fa-shield-heart",
        "display_order": 6
    }
]

# The 100 Kerala Ayurveda Products precisely as specified by the user
RAW_PRODUCTS = [
    # 1. Ayurvedic oils (1–20)
    (1, "Dhanwantharam Thailam", "ayurvedic-oils", "oil", "200 ml", 280, 320,
     "Classical neuromuscular tonic and body massage oil",
     "Bala, Dasamoola, Sesame oil, Cow's milk, Ashwagandha",
     "Relieves joint stiffness, nourishes muscles, ideal for postnatal care and daily Abhyanga.",
     "Warm slightly and massage gently over body before bath.", "Ashtanga Hridaya"),
    (2, "Ksheerabala Thailam", "ayurvedic-oils", "oil", "200 ml", 310, 360,
     "Potent cooling neurological oil prepared with Sida cordifolia and pure milk",
     "Bala root, Cow's milk, Sesame oil",
     "Calms aggravated Vata, supports restful sleep, relieves sciatica and facial palsy.",
     "Apply 5-10 ml on head or body 30 mins before bathing.", "Sahasrayogam"),
    (3, "Mahanarayana Thailam", "ayurvedic-oils", "oil", "200 ml", 340, 395,
     "Legendary classical oil for joint mobility and deep muscle relaxation",
     "Bilva, Ashwagandha, Bala, Shatavari, Gokshura, Rasna",
     "Soothes severe joint stiffness, backache, and improves limb mobility.",
     "Gently massage warm oil over joints and affected areas.", "Bhaishajya Ratnavali"),
    (4, "Neelibringadi Keram", "ayurvedic-oils", "oil", "200 ml", 290, 340,
     "Traditional Kerala coconut oil formulation for luscious, deep black hair",
     "Neeli (Indigo), Bringaraja, Amla, Coconut milk, Anjana",
     "Prevents premature greying, reduces hair fall, and induces deep relaxing sleep.",
     "Apply to scalp and hair roots, leave for 30 minutes, wash with mild herbal cleanser.", "Sahasrayogam"),
    (5, "Eladi Keram", "ayurvedic-oils", "oil", "200 ml", 270, 315,
     "Soothing coconut-based herbal oil for sensitive skin, glow, and itch relief",
     "Ela (Cardamom), Cinnamon, Nagakesara, Coconut oil",
     "Clears skin blemishes, allergic dermatitis, improves complexion, suitable for children.",
     "Apply gently on skin 20 minutes before bath.", "Ashtanga Hridaya"),
    (6, "Pinda Thailam", "ayurvedic-oils", "oil", "200 ml", 240, 280,
     "Soothing cooling oil for burning sensation in feet, gout, and arthritis",
     "Manjistha, Sariva, Beeswax, Sesame oil",
     "Rapidly relieves burning sensations, gouty arthritis (Vatarakta), and plantar redness.",
     "Apply over burning joints, feet, and palms.", "Ashtanga Hridaya"),
    (7, "Sahacharadi Thailam", "ayurvedic-oils", "oil", "200 ml", 260, 305,
     "Dedicated Ayurvedic formulation for lower limb stiffness and varicose veins",
     "Sahachara, Dasamoola, Devadaru, Sesame oil",
     "Strengthens lower back, relieves sciatica, numbness, and aching legs.",
     "Massage upwards on legs and lower back.", "Ashtanga Hridaya"),
    (8, "Karpasasthyadi Thailam", "ayurvedic-oils", "oil", "200 ml", 275, 320,
     "Potent Vata pacifying oil prepared with cotton seed extract",
     "Karpasa seeds, Bala, Masha, Devadaru, Rasna",
     "Highly effective in frozen shoulder, neck stiffness, and brachial neuralgia.",
     "Apply warm oil on neck, shoulders, and arms.", "Sahasrayogam"),
    (9, "Bala Thailam", "ayurvedic-oils", "oil", "200 ml", 350, 410,
     "Premium restorative oil for nervous system rejuvenation and strength",
     "Bala, Rasna, Guduchi, Shatavari, Sesame oil",
     "Strengthens nerves, muscles, and promotes vitality in chronic neuro disorders.",
     "Used for external massage and Nasya under physician advice.", "Ashtanga Hridaya"),
    (10, "Gandha Thailam", "ayurvedic-oils", "oil", "100 ml", 420, 490,
     "Classical revered formulation for fracture healing, ligament, and bone strength",
     "Sesame seeds, Milk, Licorice, Manjistha, Shalaparni",
     "Speeds bone healing, strengthens degenerated joints and osteoporosis.",
     "Apply externally or take internally as directed by Vaidya.", "Ashtanga Hridaya"),
    (11, "Chemparuthyadi Keram", "ayurvedic-oils", "oil", "200 ml", 230, 270,
     "Traditional hibiscus leaf coconut oil for pediatric skin and scalp health",
     "Chemparuthi (Hibiscus), Tulsi, Betel leaf, Coconut oil",
     "Treats infant eczema, itchy scalp, boils, and keeps scalp healthy and cool.",
     "Apply on baby's head and body 15 minutes before bath.", "Sahasrayogam"),
    (12, "Kayyunyadi Keram", "ayurvedic-oils", "oil", "200 ml", 285, 335,
     "Classical scalp oil for eye cooling, headache relief, and strong hair roots",
     "Kayyunyam (Bhringraj), Guduchi, Amalaki, Cow's milk",
     "Relieves eye strain, burning sensation in head, and halts excessive hair shedding.",
     "Massage onto scalp daily or before bathing.", "Sahasrayogam"),
    (13, "Balahatadi Keram", "ayurvedic-oils", "oil", "200 ml", 295, 345,
     "Special herbal oil specifically for sleeplessness, tension, and migraines",
     "Bala, Hata (Amla), Chandana, Sesame & Coconut oil",
     "Calms mental restlessness, chronic headaches, and induces serene slumber.",
     "Apply generously over vertex and temples before sleep.", "Sahasrayogam"),
    (14, "Kesini Hair Oil", "ayurvedic-oils", "oil", "200 ml", 325, 380,
     "Proprietary herbal blend for rapid hair regrowth and dandruff prevention",
     "Neeli, Bringaraj, Brahmi, Gunja, Almond oil",
     "Nourishes follicles, repairs split ends, promotes dense thick hair growth.",
     "Gently massage with fingertips into scalp thrice weekly.", "Kerala Classical"),
    (15, "Durdurapatradi Keram", "ayurvedic-oils", "oil", "200 ml", 240, 280,
     "Intensive anti-dandruff oil prepared with Dhatura leaf extract",
     "Durdurapatra (Dhatura), Sesame oil, Coconut oil",
     "Eradicates persistent dandruff, fungal scalp infections, and severe pruritus.",
     "Apply on scalp 45 minutes prior to washing with herbal shampoo.", "Sahasrayogam"),
    (16, "Balaswagandhadi Thailam", "ayurvedic-oils", "oil", "200 ml", 310, 360,
     "Nourishing and energizing oil for emaciation, convalescence, and muscle tone",
     "Bala, Ashwagandha, Laksha, Cow's Curd, Sesame oil",
     "Builds muscle mass, restores stamina, relieves general debility and fatigue.",
     "Warm Abhyanga oil massage for whole body.", "Sahasrayogam"),
    (17, "Myaxyl Pain Relief Oil", "ayurvedic-oils", "oil", "100 ml", 220, 260,
     "Fast-action Ayurvedic liniment for acute muscular sprains and spasms",
     "Nandivriksha, Rasna, Lemongrass oil, Eucalyptus",
     "Non-greasy rapid penetration for stiff neck, sports injuries, and back sprain.",
     "Apply 5-10 drops to painful area and massage lightly.", "Kerala Modern Classical"),
    (18, "Santhwanam Oil", "ayurvedic-oils", "oil", "200 ml", 330, 390,
     "Relaxing restorative body massage oil for geriatric comfort and stress",
     "Dasamoola, Bala, Sesame oil, Camphor, Eucalyptus",
     "Improves peripheral circulation, eases body aches, and restores tranquility.",
     "Full body massage before warm shower.", "Kerala Ayurvedic"),
    (19, "Arimedadi Thailam", "ayurvedic-oils", "oil", "100 ml", 210, 245,
     "Classical oil pulling formulation for healthy gums, teeth, and oral hygiene",
     "Arimeda (Acacia farnesiana), Yashtimadhu, Triphala, Karpura",
     "Cures bleeding gums, halitosis, strengthens loose teeth and oral tissues.",
     "Gargle / oil pull 10-15 ml for 10 minutes every morning.", "Ashtanga Hridaya"),
    (20, "Eladi Thailam", "ayurvedic-oils", "oil", "200 ml", 280, 330,
     "Pure sesame-based Eladi oil for glowing skin texture and allergic hives",
     "Ela, Cinnamon, Tagara, Jatamansi, Sesame oil",
     "Enhances dermal glow, eliminates itching, rash, and dry flaky skin patches.",
     "Massage on face and body before bath.", "Ashtanga Hridaya"),

    # 2. Ayurvedic medicines and tablets (21–40)
    (21, "Triphala Tablets", "medicines-tablets", "tablet", "60 Tablets", 180, 210,
     "Synergistic trio of Haritaki, Bibhitaki, and Amalaki for gut and detox",
     "Pure concentrated extracts of Triphala",
     "Gentle colon cleanser, supports daily regularity, rich natural source of Vitamin C.",
     "1-2 tablets before bedtime with warm water.", "Charaka Samhita"),
    (22, "Yogaraja Guggulu", "medicines-tablets", "tablet", "60 Tablets", 260, 305,
     "Revered anti-inflammatory Guggulu compound for chronic arthritis and joint pain",
     "Shuddha Guggulu, Chitraka, Pippali, Triphala, Vidanga",
     "Reduces synovial inflammation, stiffness, and promotes joint flexibility.",
     "2 tablets twice daily after meals with warm water.", "Bhaishajya Ratnavali"),
    (23, "Kanchanar Guggulu", "medicines-tablets", "tablet", "60 Tablets", 270, 320,
     "Classical lymphatic detoxifier and glandular support formulation",
     "Kanchanar bark, Triphala, Trikatu, Varuna, Shuddha Guggulu",
     "Supports thyroid balance, assists in reduction of cysts, fibroids, and swollen glands.",
     "2 tablets twice daily with warm water.", "Sharangadhara Samhita"),
    (24, "Chandraprabha Gulika", "medicines-tablets", "tablet", "100 Tablets", 295, 350,
     "Comprehensive urinary, reproductive, and metabolic rejuvenator",
     "Shilajit, Guggulu, Loha Bhasma, Haridra, Vacha, Ativisha",
     "Balances urinary tract health, controls glucose metabolism, relieves backache.",
     "1-2 tablets twice daily with milk or water.", "Bhaishajya Ratnavali"),
    (25, "Maharasnadi Kwath Tablets", "medicines-tablets", "tablet", "100 Tablets", 340, 400,
     "Convenient concentrated tablet form of the premier anti-rheumatic Kwath",
     "Rasna, Bala, Eranda, Devadaru, Punarnava, Ashwagandha",
     "Alleviates severe Vata disorders, sciatica, cervical spondylosis, and hemiplegia.",
     "2 tablets twice daily before food with warm water.", "Sahasrayogam"),
    (26, "Nimbadi Kwath Tablets", "medicines-tablets", "tablet", "100 Tablets", 290, 340,
     "Potent blood purifier and antimicrobial herbal Kwath in tablet form",
     "Nimba (Neem), Amrita (Giloy), Duralabha, Haritaki, Vasa",
     "Treats stubborn acne, boils, skin allergies, and speeds wound healing.",
     "2 tablets twice daily before meals.", "Sahasrayogam"),
    (27, "Nisakathakadi Kwath Tablets", "medicines-tablets", "tablet", "100 Tablets", 310, 365,
     "Famous Kerala formulation for glycemic control and diabetes neuropathy",
     "Nisa (Turmeric), Kataka, Amalaki, Lodhra, Salacia",
     "Regulates blood glucose levels naturally and prevents diabetic complications.",
     "2 tablets twice daily 30 minutes before food.", "Sahasrayogam"),
    (28, "Varanadi Kwath Tablets", "medicines-tablets", "tablet", "100 Tablets", 330, 390,
     "Premier metabolic booster and lipid-reducing classical formulation",
     "Varuna, Sairyaka, Shatavari, Dahana, Bilva",
     "Clears Kapha blockages, assists weight management, fatty liver, and headache.",
     "2 tablets twice daily before food.", "Ashtanga Hridaya"),
    (29, "Sukumaram Kwath Tablets", "medicines-tablets", "tablet", "100 Tablets", 320, 375,
     "Restorative uterine and digestive tonic for female wellness",
     "Punarnava, Dasamoola, Payasya, Ashwagandha, Eranda",
     "Relieves menstrual cramps, supports fertility, eases chronic constipation.",
     "2 tablets twice daily before meals.", "Sahasrayogam"),
    (30, "Ashtavargam Kwath Tablets", "medicines-tablets", "tablet", "100 Tablets", 315, 370,
     "Classical 8-herb formulation for upper limb pain and rheumatic fever",
     "Bala, Sahachara, Eranda, Shunthi, Rasna, Devadaru",
     "Effective in cervical spondylitis, shoulder girdle pain, and neuromuscular stiffness.",
     "2 tablets twice daily with warm water.", "Sahasrayogam"),
    (31, "Normact Tablets", "medicines-tablets", "tablet", "60 Tablets", 240, 280,
     "Proprietary herbal anti-arthritic tablet for rapid joint relief",
     "Shallaki, Guggulu, Shunthi, Rasna extracts",
     "Reduces joint swelling, cartilage erosion, and improves ease of walking.",
     "1 tablet twice daily after meals.", "Kerala Ayurveda"),
    (32, "Glymin Tablets", "medicines-tablets", "tablet", "60 Tablets", 250, 295,
     "Herbal glucose regulation tablet with Gymnema and Jamun seed",
     "Meshashringi, Jambu, Karela, Haridra",
     "Supports normal pancreatic beta cell function and curbs sugar cravings.",
     "1-2 tablets twice daily before meals.", "Kerala Ayurveda"),
    (33, "Heposem Tablets", "medicines-tablets", "tablet", "60 Tablets", 230, 270,
     "Hepato-protective tablet formulation for liver rejuvenation and detox",
     "Bhumi Amalaki, Katuki, Kalmegh, Punarnava",
     "Protects liver from toxins, aids digestion, and normalizes liver enzymes.",
     "1 tablet twice daily after meals.", "Sitaram Ayurveda"),
    (34, "Menovin Tablets", "medicines-tablets", "tablet", "60 Tablets", 280, 330,
     "Balancing herbal tablet for menopausal comfort and hormonal harmony",
     "Ashoka, Lodhra, Shatavari, Praval Pishti",
     "Soothes hot flashes, mood swings, fatigue, and night sweats during menopause.",
     "1 tablet twice daily with water.", "Nagarjuna Ayurveda"),
    (35, "Evakalp Tablets", "medicines-tablets", "tablet", "60 Tablets", 265, 310,
     "Menstrual regulator and uterine tonic for cycle regularity",
     "Kanyasara (Aloe vera), Kasisa Bhasma, Hingu, Pippali",
     "Regulates delayed periods, corrects secondary amenorrhea, eases cramps.",
     "1-2 tablets daily with warm water.", "Vaidyaratnam"),
    (36, "Alsactil Tablets", "medicines-tablets", "tablet", "60 Tablets", 220, 260,
     "Fast antacid and mucosal healer for hyperacidity and stomach ulcers",
     "Yashtimadhu, Shatavari, Mustha, Triphala",
     "Provides rapid relief from heartburn, acid reflux, gastritis, and peptic discomfort.",
     "1-2 tablets after meals with warm water.", "Kerala Ayurveda"),
    (37, "Dhanwantharam Gulika", "medicines-tablets", "tablet", "50 Tablets", 160, 190,
     "Emergency Ayurvedic pill for gaseous distension, belching, and nausea",
     "Ela, Viswa, Jeeraka, Brihati, Kiratathiktha",
     "Relieves chest tightness due to gas, morning sickness in pregnancy, and hiccup.",
     "1 pill chewed or swallowed with cumin water.", "Sahasrayogam"),
    (38, "Vilwadi Pills", "medicines-tablets", "tablet", "50 Tablets", 175, 205,
     "Antitoxic classical pill for insect stings, gastroenteritis, and fever",
     "Bilva root, Surasa, Karanja, Haridra, Daruharidra",
     "Detoxifies poisonous bites, eliminates intestinal worms and microbial infections.",
     "1-2 pills crushed with honey or warm water.", "Ashtanga Hridaya"),
    (39, "Promactil Capsules", "medicines-tablets", "tablet", "60 Capsules", 480, 560,
     "Vitality, stamina, and male reproductive health booster",
     "Ashwagandha, Kapikacchu, Safed Musli, Shilajit",
     "Improves vigor, endurance, sperm count, and combats everyday fatigue.",
     "1 capsule twice daily with warm milk.", "Kerala Ayurveda"),
    (40, "Brahmi Pearls Capsules", "medicines-tablets", "tablet", "40 Softgels", 390, 460,
     "Concentrated Medhya Rasayana softgels for memory, focus, and brain health",
     "Purified Brahmi extract, Shankhapushpi, Vacha, Cow's Ghee",
     "Boosts intellectual clarity, concentration, mental retention, and eases anxiety.",
     "1-2 capsules daily after food.", "Kerala Ayurveda"),

    # 3. Ayurvedic oils and beauty products (41–55)
    (41, "Kumkumadi Oil", "beauty-skincare", "beauty", "30 ml", 650, 780,
     "Prestigious Kashmiri Saffron skin radiance elixir for spot-free luminous skin",
     "Pure Saffron (Kumkuma), Sandalwood, Manjistha, Licorice, Lotus pollen",
     "Fades dark spots, evens pigmentation, reduces fine lines, and imparts radiant glow.",
     "Apply 3-4 drops on clean damp face at night; massage gently.", "Ashtanga Hridaya"),
    (42, "Swarnamukhi Face Pack", "beauty-skincare", "beauty", "75 g", 260, 310,
     "Golden glow herbal face pack with Sandalwood, Nagakesara, and Lodhra",
     "Sandalwood, Nagakesara, Priyangu, Lodhra, Yavam",
     "Deeply cleanses pores, removes sun tan, tightens skin, and restores fresh radiance.",
     "Mix with rose water, apply evenly, wash off after 15 mins.", "Kerala Traditional"),
    (43, "Herbal Neem Face Pack", "beauty-skincare", "beauty", "100 g", 195, 230,
     "Purifying anti-acne pack for oily, blemish-prone skin",
     "Neem leaves, Multani Mitti, Tulsi, Haridra",
     "Controls excess sebum, fights pimple-causing bacteria, and prevents scarring.",
     "Apply paste twice weekly on face and neck.", "Herbal Beauty"),
    (44, "Aloe Vera Herbal Gel", "beauty-skincare", "beauty", "150 g", 180, 215,
     "Pure soothing organic aloe gel infused with cucumber and green tea",
     "Aloe barbadensis leaf extract, Cucumber extract",
     "Hydrates parched skin, cools sunburns, soothes rashes, and acts as primer.",
     "Apply generously to skin or hair as needed.", "Kerala Naturals"),
    (45, "Kumkumadi Cream", "beauty-skincare", "beauty", "50 g", 380, 450,
     "Luxurious day-and-night moisturiser enriched with Kumkumadi Thailam",
     "Kumkumadi Thailam, Shea Butter, Sandalwood oil, Almond oil",
     "Nourishes deep skin layers, combats dullness, and imparts silky youthful texture.",
     "Smooth over face and neck morning and evening.", "Ayurvedic Luxury"),
    (46, "Herbal Turmeric Face Pack", "beauty-skincare", "beauty", "100 g", 210, 250,
     "Traditional Kasturi Manjal formulation for brightening and anti-blemish care",
     "Kasturi Manjal (Wild Turmeric), Chandana, Besan, Licorice",
     "Lightens acne marks, prevents facial hair growth, gives natural bridal radiance.",
     "Make paste with milk or yogurt; apply for 15 minutes.", "Kerala Heritage"),
    (47, "Herbal Sandalwood Powder", "beauty-skincare", "beauty", "50 g", 320, 380,
     "100% Pure therapeutic Mysore Sandalwood powder for cooling skin treatments",
     "Santalum album (Pure White Sandalwood)",
     "Soothes prickly heat, calms allergic hives, and leaves captivating natural fragrance.",
     "Mix with water or milk and apply as soothing pack.", "Classical Single Herb"),
    (48, "Ayurvedic Hair Growth Oil", "beauty-skincare", "beauty", "200 ml", 340, 400,
     "Intensive herbal scalp stimulant with 18 rare Ayurvedic botanical actives",
     "Bhringraj, Amla, Brahmi, Methi, Curry leaves, Virgin coconut oil",
     "Awakens dormant hair follicles, strengthens weak strands, accelerates hair growth.",
     "Massage into scalp thrice weekly; leave overnight or wash after 1 hour.", "Kerala Special"),
    (49, "Bhringraj Hair Oil", "beauty-skincare", "beauty", "200 ml", 280, 330,
     "Pure Keshya Mahathailam processed with fresh Bhringraj juice",
     "Eclipta alba (Bhringraj), Sesame oil, Manjistha, Padmaka",
     "Prevents hair thinning, conditions dry damaged locks, and cools cranial nerves.",
     "Apply warm oil on scalp and hair shaft.", "Bhavaprakasha"),
    (50, "Hibiscus Hair Oil", "beauty-skincare", "beauty", "200 ml", 250, 295,
     "Silky conditioning oil made with fresh crimson hibiscus flowers and virgin coconut oil",
     "Hibiscus rosa-sinensis flowers, Fenugreek, Coconut oil",
     "Natural hair conditioner, stops frizz, split ends, and adds high gloss.",
     "Gentle scalp massage before bath.", "Kerala Folk Formula"),
    (51, "Herbal Anti-Dandruff Oil", "beauty-skincare", "beauty", "200 ml", 260, 305,
     "Specialized herbal concoction with Wrightia tinctoria (Danapala) for scalp health",
     "Wrightia tinctoria, Neem, Tea Tree oil, Coconut oil",
     "Clinically trusted in Kerala for clearing severe dandruff, scalp psoriasis, and flakes.",
     "Apply to scalp and leave for 30 minutes before washing.", "Kerala Siddha-Ayurveda"),
    (52, "Herbal Hair Cleanser", "beauty-skincare", "beauty", "200 ml", 225, 270,
     "Sulfate-free traditional Thaali liquid shampoo with Shikakai and Hibiscus",
     "Shikakai, Reetha, Hibiscus leaves, Amla, Fenugreek",
     "Cleanses scalp gently without stripping natural oils, leaving hair soft and bouncy.",
     "Lather into wet hair and rinse thoroughly.", "Kerala Traditional Thaali"),
    (53, "Ayurvedic Herbal Soap", "beauty-skincare", "beauty", "125 g (Pack of 3)", 195, 240,
     "Grade-1 handmade herbal soap with pure coconut oil and 18 Ayurvedic herbs",
     "Virgin Coconut oil, Turmeric, Neem, Tulsi, Vetiver",
     "Maintains skin pH balance, kills body odor bacteria, and keeps skin supple.",
     "Use daily during bath for rich, creamy herbal lather.", "Kerala Artisan"),
    (54, "Herbal Body Massage Oil", "beauty-skincare", "beauty", "200 ml", 290, 345,
     "Fragrant spa massage oil with Vetiver, Lavender, and Virgin Sesame",
     "Ushira (Vetiver), Bala, Chandana, Cold pressed sesame oil",
     "Dissolves stress, tones dry skin, and leaves subtle therapeutic woody aroma.",
     "Full body application with smooth sweeping strokes.", "Kerala Panchakarma"),
    (55, "Herbal Skin Care Cream", "beauty-skincare", "beauty", "100 g", 215, 255,
     "All-purpose barrier cream with Shatadhauta Ghritha (100-times washed ghee)",
     "Shatadhauta Ghritha, Aloe vera, Turmeric, Licorice",
     "Heals cracked heels, rough elbows, minor burns, eczema, and ultra-dry skin.",
     "Apply onto dry affected skin areas twice daily.", "Charaka Samhita"),

    # 4. Ayurvedic arishtams and asavams (56–70)
    (56, "Asokarishta", "arishtams-asavams", "arishtam", "450 ml", 195, 230,
     "The foremost Ayurvedic women's health wine and uterine tonic",
     "Ashoka bark, Dhataki, Mustha, Haritaki, Amalaki, Jaggery",
     "Relieves menorrhagia, menstrual pain, leucorrhea, and balances female hormones.",
     "15-25 ml twice daily after meals with equal quantity of water.", "Bhaishajya Ratnavali"),
    (57, "Aswagandharishtam", "arishtams-asavams", "arishtam", "450 ml", 230, 275,
     "Classical rejuvenator and nerve tonic for mental endurance and stamina",
     "Ashwagandha, Mushali, Manjistha, Haridra, Chandana, Dhataki",
     "Relieves chronic exhaustion, sleep disturbances, anxiety, and enhances vitality.",
     "20 ml twice daily after meals with equal warm water.", "Bhaishajya Ratnavali"),
    (58, "Balarishta", "arishtams-asavams", "arishtam", "450 ml", 210, 250,
     "Strengthening tonic for muscle debility, neurological conditions, and fatigue",
     "Bala root, Ashwagandha, Dhataki, Payasya, Eranda",
     "Enhances neuromuscular strength, relieves chronic joint pain and hemiparesis.",
     "15-20 ml twice daily after food.", "Bhaishajya Ratnavali"),
    (59, "Abhayarishtam", "arishtams-asavams", "arishtam", "450 ml", 185, 220,
     "Premier digestive tonic for chronic constipation, piles, and sluggish liver",
     "Abhaya (Haritaki), Draksha, Vidanga, Dhataki, Madhuka",
     "Softens stool naturally, relieves hemorrhoids, improves appetite and gut motility.",
     "20 ml twice daily after meals with equal warm water.", "Bhaishajya Ratnavali"),
    (60, "Amrutharishtam", "arishtams-asavams", "arishtam", "450 ml", 190, 225,
     "Immunity-enhancing classical fever tonic with potent Guduchi (Giloy)",
     "Amrutha (Guduchi), Bilva, Gambhari, Patala, Dhataki, Jaggery",
     "Combats recurrent chronic fevers, malarial debility, and purifies the bloodstream.",
     "15-20 ml twice daily with warm water.", "Bhaishajya Ratnavali"),
    (61, "Draksharishta", "arishtams-asavams", "arishtam", "450 ml", 225, 270,
     "Nourishing fermented tonic prepared from premium dry raisins (Draksha)",
     "Draksha (Raisins), Dhataki, Cinnamon, Cardamom, Tejpatra",
     "Relieves respiratory fatigue, chronic dry cough, constipation, and boosts hemoglobin.",
     "20 ml twice daily after food.", "Sharangadhara Samhita"),
    (62, "Dasamoolarishta", "arishtams-asavams", "arishtam", "450 ml", 240, 285,
     "Royal post-natal tonic and comprehensive vitality restorer containing 10 roots",
     "Dasamoola, Chitraka, Pushkaramoola, Guduchi, Amalaki, Dhataki",
     "Rapidly restores energy after childbirth, heals fatigue, and balances all three Doshas.",
     "20-25 ml twice daily after meals with water.", "Sharangadhara Samhita"),
    (63, "Dasamoolajeerakarishta", "arishtams-asavams", "arishtam", "450 ml", 250, 295,
     "Specialized Kerala formulation combining Dasamoola and digestive Jeeraka",
     "Dasamoola, Cumin seeds (Jeeraka), Dhataki, Jaggery",
     "Supports lactating mothers, strengthens digestion, and eases abdominal spasms.",
     "20 ml twice daily after meals.", "Kerala Sahasrayogam"),
    (64, "Saraswatharishta", "arishtams-asavams", "arishtam", "450 ml", 260, 310,
     "Master cerebral tonic for intellect, eloquence, vocal clarity, and memory",
     "Brahmi, Shatavari, Vidari, Haritaki, Ushira, Gold (Swarna foil trace)",
     "Sharpens memory, enhances learning capacity, reduces exam stress, and calms mind.",
     "10-15 ml twice daily with equal quantity of water.", "Bhaishajya Ratnavali"),
    (65, "Vasarishta", "arishtams-asavams", "arishtam", "450 ml", 190, 225,
     "Herbal bronchodilator and respiratory tonic with Adhatoda vasica",
     "Vasa (Adhatoda), Dhataki, Cinnamon, Ela, Maricha, Pippali",
     "Liquefies thick bronchial mucus, relieves chronic bronchitis, asthma, and cough.",
     "15-20 ml twice daily after food with warm water.", "Bhaishajya Ratnavali"),
    (66, "Punarnavasavam", "arishtams-asavams", "arishtam", "450 ml", 200, 240,
     "Diuretic and kidney rejuvenating Asavam for fluid retention and edema",
     "Punarnava, Gokshura, Haridra, Patola, Neem, Triphala",
     "Reduces water retention, facial puffiness, kidney stress, and pedal edema.",
     "20 ml twice daily with water.", "Bhaishajya Ratnavali"),
    (67, "Bhringarajasavam", "arishtams-asavams", "arishtam", "450 ml", 215, 255,
     "Rejuvenative hair and liver tonic for premature greying and emaciation",
     "Bhringaraja, Haritaki, Pippali, Jatiphala, Lavanga",
     "Strengthens hair roots from within, promotes stamina, and tones liver function.",
     "15-20 ml twice daily after food.", "Gada Nigraha"),
    (68, "Kumaryasavam", "arishtams-asavams", "arishtam", "450 ml", 210, 250,
     "Aloe-infused digestive and hematinic tonic for anemia and liver sluggishness",
     "Kumari (Aloe vera juice), Loha Bhasma, Haritaki, Triphala, Dhataki",
     "Treats iron-deficiency anemia, liver enlargement, and abdominal bloating.",
     "15-20 ml twice daily with water.", "Sharangadhara Samhita"),
    (69, "Chandanasavam", "arishtams-asavams", "arishtam", "450 ml", 270, 320,
     "Cooling aromatic tonic for burning micturition and kidney heat",
     "Safed Chandana (Sandalwood), Balaka, Gambhari, Nilotpala, Dhataki",
     "Quickly relieves dysuria, urinary tract burning, high pitta, and spermatorrhea.",
     "20 ml twice daily after meals with water.", "Bhaishajya Ratnavali"),
    (70, "Kanakasavam", "arishtams-asavams", "arishtam", "450 ml", 220, 260,
     "Specialized antiasthmatic bronchodilator for nocturnal cough and wheezing",
     "Kanaka (Dhatura), Vasa, Yashtimadhu, Pippali, Nagakesara, Dhataki",
     "Relieves chest tightness, sudden bronchial spasms, and heavy allergic cough.",
     "10-15 ml twice daily with warm water.", "Bhaishajya Ratnavali"),

    # 5. Ayurvedic powders and herbal formulations (71–85)
    (71, "Avipathi Choornam", "powders-formulations", "choornam", "100 g", 140, 165,
     "Classical Pitta pacifying laxative powder for hyperacidity and sour belching",
     "Trikatu, Triphala, Mustha, Ela, Patra, Lavanga, Sharkara",
     "Neutralizes stomach acid, gently cleanses bowels, and cures acid reflux.",
     "5-10 g at bedtime with warm water or milk.", "Ashtanga Hridaya"),
    (72, "Triphala Choornam", "powders-formulations", "choornam", "100 g", 110, 130,
     "Finest micro-pulverized Triphala powder for complete internal detox",
     "Equal proportions of Haritaki, Bibhitaki, and Amalaki",
     "Detoxifies the gastrointestinal tract, supports vision, and improves digestion.",
     "3-5 g twice daily with warm water or honey.", "Charaka Samhita"),
    (73, "Aswagandha Choornam", "powders-formulations", "choornam", "100 g", 160, 190,
     "Pure Withania somnifera root powder for vitality, muscle power, and sleep",
     "100% Organically cultivated Ashwagandha root powder",
     "Adapts body to stress, lowers cortisol, enhances endurance, and supports libido.",
     "3-5 g at night with warm milk and a pinch of cardamom.", "Bhavaprakasha"),
    (74, "Brahmi Choornam", "powders-formulations", "choornam", "100 g", 150, 180,
     "Pure memory-enhancing Bacopa monnieri herb powder",
     "Finely ground shade-dried Bacopa monnieri whole plant",
     "Enhances neural synaptic transmission, boosts memory recall, and lowers anxiety.",
     "2-3 g twice daily with ghee or honey.", "Charaka Samhita"),
    (75, "Rasnadi Choornam", "powders-formulations", "choornam", "50 g", 95, 115,
     "Essential Kerala postpartum and daily head powder to prevent sinus congestion",
     "Rasna, Aswagandha, Devadaru, Katuki, Sariva, Camphor",
     "Applied to crown of head immediately after bath to prevent cold, sinusitis, and headache.",
     "Rub a pinch briskly onto crown of head after bath.", "Sahasrayogam"),
    (76, "Kolakulathadi Choornam", "powders-formulations", "choornam", "100 g", 130, 155,
     "Classical powder for Udwarthanam (herbal dry powder fat-loss massage)",
     "Kola, Kulatha, Devadaru, Yava, Masha, Kushta",
     "Burns subcutaneous fat, improves blood flow, and eliminates cellulitic tissue.",
     "Used externally as dry scrub or made into warm paste with buttermilk.", "Ashtanga Hridaya"),
    (77, "Nagaraadi Choornam", "powders-formulations", "choornam", "100 g", 125, 150,
     "Herbal poultice powder for traumatic swellings, sprains, and blunt injuries",
     "Nagara (Ginger), Vacha, Manjistha, Chitraka",
     "Rapidly brings down localized inflammatory edema, sprains, and bruising.",
     "Mix with tamarind leaf juice or rice starch and apply warm paste.", "Sahasrayogam"),
    (78, "Mustha Choornam", "powders-formulations", "choornam", "100 g", 135, 160,
     "Premier gut astringent and fever-pacifying Cyperus rotundus powder",
     "Pure Mustha (Nut grass) rhizome powder",
     "Treats irritable bowel syndrome, dysentery, infantile diarrhea, and digestive weakness.",
     "2-3 g twice daily with warm water or buttermilk.", "Charaka Samhita"),
    (79, "Sitopaladi Choornam", "powders-formulations", "choornam", "100 g", 175, 210,
     "Beloved classical Ayurvedic respiratory soothing powder for all age groups",
     "Mishri, Vanshlochan, Pippali, Ela, Twak (Cinnamon)",
     "Soothes sore throats, clears phlegm, boosts lung immunity, and relieves seasonal flu.",
     "2-3 g mixed with pure honey thrice daily.", "Sharangadhara Samhita"),
    (80, "Sudarshana Choornam", "powders-formulations", "choornam", "100 g", 155, 185,
     "Master 53-herb bitter concoction for stubborn fevers and viral infections",
     "Kiratathiktha, Triphala, Trikatu, Haridra, Vacha, Neem, Katuki",
     "Powerful antipyretic, breaks chronic low-grade fevers, detoxifies liver and spleen.",
     "2-4 g with warm water twice daily.", "Bhaishajya Ratnavali"),
    (81, "Amruthotharam Kwath", "powders-formulations", "choornam", "100 g", 120, 145,
     "Triad herbal decoction powder for initial stages of fever and indigestion",
     "Nagara (Shunthi), Amrutha (Guduchi), Haritaki",
     "Ignites digestive fire, relieves toxic AMA accumulation, and clears feverish chills.",
     "Boil 10 g in 160 ml water; reduce to 40 ml, strain, and take warm.", "Sahasrayogam"),
    (82, "Guluchyadi Kwath", "powders-formulations", "choornam", "100 g", 125, 150,
     "Cooling decoction powder for burning sensations, gastritis, and bile fevers",
     "Guluchi (Giloy), Padmaka, Arishta, Dhanyaka, Chandana",
     "Cools intense systemic Pitta, relieves nausea, jaundice, and excessive thirst.",
     "Boil 10 g into concentrated decoction twice daily before meals.", "Ashtanga Hridaya"),
    (83, "Dhanwantharam Kwath", "powders-formulations", "choornam", "100 g", 145, 170,
     "Classical internal decoction powder for Vata disorders and postnatal recovery",
     "Bala, Dasamoola, Kulatha, Yava, Kola",
     "Heals pelvic pain, lumbar spondylosis, nerve degeneration, and restores muscle tone.",
     "Prepare fresh decoction twice daily before food.", "Ashtanga Hridaya"),
    (84, "Patolakatukurohinyadi Kwath", "powders-formulations", "choornam", "100 g", 140, 165,
     "Intensive dermatological and liver detox decoction powder",
     "Patola, Katuki, Rohini, Chandana, Madhusrava, Guduchi",
     "Treats severe psoriasis, eczema, toxic jaundice, and deep-seated skin infections.",
     "Take warm fresh decoction on empty stomach morning and night.", "Ashtanga Hridaya"),
    (85, "Mahathikthaka Kwath", "powders-formulations", "choornam", "100 g", 160, 190,
     "The ultimate bitter blood purifier for autoimmune and chronic skin conditions",
     "Saptaparna, Parpata, Katuki, Nimba, Haridra, Daruharidra",
     "Purifies deep tissues, pacifies severe Pitta-Rakta disorders, and heals chronic wounds.",
     "Boil 10 g into decoction twice daily before food.", "Ashtanga Hridaya"),

    # 6. Ayurvedic health supplements and lehyams (86–100)
    (86, "Chyavanprash", "supplements-lehyams", "lehyam", "500 g", 360, 425,
     "Authentic Kerala Chyavanprash enriched with wild Amla and 48 rejuvenation herbs",
     "Fresh Wild Amalaki, Dasamoola, Ashwagandha, Shatavari, Cow's Ghee, Honey",
     "Builds deep Ojas immunity, prevents seasonal infections, and rejuvenates youthfulness.",
     "1-2 tablespoons every morning followed by warm milk.", "Charaka Samhita"),
    (87, "Narasimha Rasayanam", "supplements-lehyams", "lehyam", "250 g", 290, 345,
     "Potent Medhya and Keshya herbal jam for premature greying, stamina, and libido",
     "Gayatri, Shikhi, Shimshapa, Asana, Shiva, Chitraka, Cow's Ghee, Honey",
     "Reverses early hair greying, boosts muscle power, vitality, and clears wrinkles.",
     "1 teaspoon twice daily on empty stomach followed by warm milk.", "Ashtanga Hridaya"),
    (88, "Vilwadi Lehyam", "supplements-lehyams", "lehyam", "250 g", 210, 250,
     "Palatable digestive herbal confection for nausea, anorexia, and vomiting",
     "Bilva fruit pulp, Jeeraka, Shunthi, Maricha, Pippali, Jaggery",
     "Cures morning sickness, heartburn, improves low appetite, and soothes digestion.",
     "5-10 g licked slowly 30 minutes before meals.", "Sahasrayogam"),
    (89, "Ashwagandhadi Lehyam", "supplements-lehyams", "lehyam", "500 g", 350, 410,
     "Energizing Ayurvedic herbal jam for weight gain, athletic stamina, and vigor",
     "Ashwagandha, Sariva, Jeeraka, Ela, Cow's Ghee, Jaggery",
     "Builds healthy muscle mass, combats stress fatigue, and enhances endurance.",
     "1-2 tablespoons twice daily with warm milk.", "Sahasrayogam"),
    (90, "Brahmi Ghritham", "supplements-lehyams", "lehyam", "150 g", 320, 380,
     "Medicated cow's ghee cooked with fresh Brahmi juice for brain and memory power",
     "Brahmi, Vacha, Kushtha, Shankhapushpi, Pure Cow's Ghee",
     "Improves cognitive function, speech articulation, memory retention, and calms ADHD.",
     "5-10 g in the morning on empty stomach with warm water or milk.", "Ashtanga Hridaya"),
    (91, "Indukantham Ghritham", "supplements-lehyams", "lehyam", "150 g", 310, 365,
     "Classical restorative ghee for peptic ulcer healing and deep gut immunity",
     "Putika, Devadaru, Dasamoola, Panchakola, Cow's Ghee, Milk",
     "Heals gut lining, relieves chronic abdominal colic, duodenal ulcers, and emaciation.",
     "10 ml twice daily with warm milk or lukewarm water before meals.", "Sahasrayogam"),
    (92, "Mahathikthaka Ghritham", "supplements-lehyams", "lehyam", "150 g", 340, 400,
     "Potent bitter medicated ghee for severe chronic skin diseases and psoriatic lesions",
     "Saptaparna, Parpata, Katuki, Chandana, Neem, Cow's Ghee",
     "Purifies blood, clears internal heat, and heals stubborn inflammatory dermatoses.",
     "10 ml on empty stomach early morning.", "Ashtanga Hridaya"),
    (93, "Kalyanaka Ghritham", "supplements-lehyams", "lehyam", "150 g", 330, 390,
     "Auspicious neuro-psychiatric Ayurvedic ghee for mental balance and fertility",
     "Triphala, Haridra, Shalaparni, Prishniparni, Pure Desi Ghee",
     "Promotes conception, harmonizes emotional instability, and relieves anxiety.",
     "5-10 g early morning on an empty stomach.", "Ashtanga Hridaya"),
    (94, "Balakalpam Syrup", "supplements-lehyams", "lehyam", "200 ml", 180, 215,
     "Gentle pediatric Ayurvedic tonic for children's digestion, appetite, and immunity",
     "Mustha, Amla, Pippali, Yashtimadhu, Cardamom",
     "Relieves infantile colic, eases teething troubles, and enhances natural resistance.",
     "5 ml twice daily for children with warm water or milk.", "Kerala Classical"),
    (95, "Mathrukalpam", "supplements-lehyams", "lehyam", "500 g", 380, 450,
     "Holistic post-natal restorative lehyam for nursing mothers",
     "Methi, Jeeraka, Shatavari, Ashwagandha, Dasamoola, Jaggery, Ghee",
     "Enhances wholesome breastmilk production, restores maternal vitality, and heals pelvis.",
     "10-15 g twice daily followed by warm milk.", "Kerala Ayurvedic Tradition"),
    (96, "Ajamamsa Rasayanam", "supplements-lehyams", "lehyam", "500 g", 450, 530,
     "Classical high-nutrition rejuvenation jam for emaciation, fractures, and strength",
     "Ajamamsa (Purified goat meat extract), Dasamoola, Ashwagandha, Ghee, Honey",
     "Greatly increases muscular strength, restores vitality after debilitating illness.",
     "10-15 g twice daily with warm milk.", "Bhaishajya Ratnavali"),
    (97, "Kerapookkuladi Lehyam", "supplements-lehyams", "lehyam", "250 g", 270, 320,
     "Traditional coconut inflorescence confection for menorrhagia and back pain",
     "Coconut flower inflorescence (Kerapookkula), Jeeraka, Ghee, Jaggery",
     "Relieves excessive uterine bleeding, backache, and strengthens reproductive organs.",
     "10 g twice daily after meals.", "Sahasrayogam"),
    (98, "Indukantham Kwath", "supplements-lehyams", "choornam", "100 g", 130, 155,
     "Immunity-enhancing decoction for recurrent fevers and abdominal bloating",
     "Putika, Devadaru, Dasamoola, Pippali, Chavya",
     "Protects against respiratory infections and builds digestive fire in weak individuals.",
     "Prepare warm decoction twice daily before food.", "Sahasrayogam"),
    (99, "Gandharvahasthadi Kwath", "supplements-lehyams", "choornam", "100 g", 135, 160,
     "Gentle castor-root herbal decoction for chronic gas, lumbar stiffness, and regularity",
     "Gandharvahastha (Castor root), Chirabilva, Hutasha, Punarnava, Sunthi",
     "Relieves trapped pelvic gas, lumbar backache, and promotes natural easy bowel movements.",
     "Take warm decoction morning and night.", "Sahasrayogam"),
    (100, "Kaisoravatakam", "supplements-lehyams", "tablet", "60 Tablets", 280, 330,
     "Classical Guggulu formulation for purine metabolism, gout, and skin ulcers",
     "Shuddha Guggulu, Guduchi, Triphala, Danti, Trivrit, Vidanga",
     "Controls high uric acid, relieves excruciating big toe pain in gout, and clears skin lesions.",
     "2 tablets twice daily with warm water.", "Bhaishajya Ratnavali")
]

class Command(BaseCommand):
    help = "Seeds all 8 Kerala Brands, 6 Categories, and all 100 Kerala Ayurveda Products"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Brands..."))
        brand_objs = {}
        for b_data in BRANDS_DATA:
            brand, created = Brand.objects.update_or_create(
                name=b_data["name"],
                defaults={
                    "description": b_data["description"],
                    "headquarters": b_data["headquarters"],
                    "established_year": b_data["established_year"],
                    "logo_badge": b_data["logo_badge"]
                }
            )
            brand_objs[b_data["name"]] = brand
            if created:
                self.stdout.write(f"  Created brand: {brand.name}")

        self.stdout.write(self.style.NOTICE("Seeding Categories..."))
        cat_objs = {}
        for c_data in CATEGORIES_DATA:
            cat, created = Category.objects.update_or_create(
                slug=c_data["slug"],
                defaults={
                    "name": c_data["name"],
                    "description": c_data["description"],
                    "icon_name": c_data["icon_name"],
                    "display_order": c_data["display_order"]
                }
            )
            cat_objs[c_data["slug"]] = cat
            if created:
                self.stdout.write(f"  Created category: {cat.name}")

        brands_list = list(brand_objs.values())
        
        # Color accents for visually appealing cards
        color_accents = {
            'oil': '#d97706',      # Amber golden oil
            'tablet': '#059669',   # Herbal emerald green
            'beauty': '#e11d48',   # Rose / saffron radiance
            'arishtam': '#7c2d12', # Deep fermentation wine
            'choornam': '#65a30d', # Fresh herbal earth
            'lehyam': '#b45309'    # Rich jam bronze
        }

        self.stdout.write(self.style.NOTICE(f"Seeding {len(RAW_PRODUCTS)} Products..."))
        created_count = 0
        updated_count = 0

        # We will distribute the products naturally across the 8 authentic Kerala Brands
        # Special signature assignments:
        # Kottakkal Arya Vaidya Sala -> Dhanwantharam, Ksheerabala, Neelibringadi, Triphala, Chyavanprash, etc.
        # Kerala Ayurveda -> Myaxyl, Normact, Glymin, Promactil, Brahmi Pearls, Alsactil
        # Vaidyaratnam -> Evakalp, Balakalpam, Mathrukalpam, Narasimha Rasayanam
        # Oushadhi -> Asokarishta, Dasamoolarishta, Amruthotharam, Avipathi Choornam
        # Nagarjuna -> Menovin, Sahacharadi, Karpasasthyadi, Pinda Thailam
        # Sitaram -> Heposem, Vilwadi, Santhwanam, Saraswatharishta
        # Ashtavaidyan Thaikkattu Mooss -> Maharasnadi, Gandha Thailam, Mahathikthaka
        # Sreedhareeyam -> Kayyunyadi, Balahatadi, Chandanasavam, Kumkumadi

        for item in RAW_PRODUCTS:
            num, name, cat_slug, p_type, vol, price, mrp, short_desc, ingredients, benefits, dosage, reference = item
            
            # Select realistic brand based on product identity or cyclic assignment
            if "Myaxyl" in name or "Normact" in name or "Glymin" in name or "Alsactil" in name or "Pearls" in name or "Promactil" in name:
                brand = brand_objs["Kerala Ayurveda"]
            elif "Heposem" in name or "Santhwanam" in name:
                brand = brand_objs["Sitaram Ayurveda"]
            elif "Evakalp" in name or "Mathrukalpam" in name or "Ajamamsa" in name:
                brand = brand_objs["Vaidyaratnam"]
            elif "Menovin" in name or "Kesini" in name:
                brand = brand_objs["Nagarjuna Ayurveda"]
            elif num in [1, 2, 4, 21, 24, 62, 71, 72, 86, 90]:
                brand = brand_objs["Kottakkal Arya Vaidya Sala"]
            elif num in [5, 6, 11, 26, 56, 59, 61, 75, 81, 88]:
                brand = brand_objs["Oushadhi"]
            elif num in [12, 13, 41, 42, 69, 74]:
                brand = brand_objs["Sreedhareeyam"]
            elif num in [9, 10, 25, 29, 85, 92]:
                brand = brand_objs["Ashtavaidyan Thaikkattu Mooss"]
            else:
                brand = brands_list[num % len(brands_list)]

            sku = f"KAS-{num:03d}-{brand.logo_badge}"
            category = cat_objs[cat_slug]

            # Realistic ratings (4.2 - 4.9) and reviews (45 - 850)
            rating = round(random.uniform(4.3, 4.9), 1)
            rating_count = random.randint(45, 820)
            
            # Stock levels: mostly healthy stock (25 - 90), a few low stock (4-10) for Flipkart/Amazon urgency badges
            if num in [4, 21, 41, 86]:
                stock = random.randint(4, 8) # Low stock alert! "Only 4 left in stock"
            elif num in [97]:
                stock = 0 # 1 Out of Stock for testing inventory badge!
            else:
                stock = random.randint(20, 85)

            is_bestseller = num in [1, 4, 21, 41, 56, 62, 72, 86]
            is_featured = num in [1, 2, 4, 21, 22, 41, 56, 62, 71, 72, 73, 86, 89, 90]

            # Curated visual styling
            accent = color_accents.get(p_type, '#1b5e20')
            
            category_photo_pool = {
                'oil': [
                    'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1617897903246-719242758050?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?auto=format&fit=crop&w=600&q=80',
                ],
                'tablet': [
                    'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?auto=format&fit=crop&w=600&q=80',
                ],
                'beauty': [
                    'https://images.unsplash.com/photo-1608248597359-25143a537f19?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?auto=format&fit=crop&w=600&q=80',
                ],
                'arishtam': [
                    'https://images.unsplash.com/photo-1471864190281-a93a3070b6de?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?auto=format&fit=crop&w=600&q=80',
                ],
                'choornam': [
                    'https://images.unsplash.com/photo-1615485290382-441e4d049cb5?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=600&q=80',
                ],
                'lehyam': [
                    'https://images.unsplash.com/photo-1587049352847-4a222e784d38?auto=format&fit=crop&w=600&q=80',
                    'https://images.unsplash.com/photo-1587049352851-8d4e89133924?auto=format&fit=crop&w=600&q=80',
                ],
            }
            photos_for_type = category_photo_pool.get(p_type, category_photo_pool['oil'])
            chosen_photo = photos_for_type[num % len(photos_for_type)]

            product, was_created = Product.objects.update_or_create(
                sku=sku,
                defaults={
                    "name": name,
                    "category": category,
                    "brand": brand,
                    "product_type": p_type,
                    "price": price,
                    "mrp": mrp,
                    "volume_weight": vol,
                    "stock": stock,
                    "low_stock_threshold": 10,
                    "short_description": short_desc,
                    "description": f"{short_desc}. Prepared according to authentic classical Ayurvedic texts, using wild-crafted botanical ingredients harvested from the Western Ghats of Kerala.",
                    "ingredients": ingredients,
                    "key_benefits": benefits,
                    "usage_dosage": dosage,
                    "classical_reference": reference,
                    "rating": rating,
                    "rating_count": rating_count,
                    "is_featured": is_featured,
                    "is_bestseller": is_bestseller,
                    "is_kerala_certified": True,
                    "image_url": chosen_photo,
                    "image_svg_accent": accent
                }
            )

            if was_created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded Kerala Ayurveda Database! Created: {created_count}, Updated: {updated_count}. Total products: {Product.objects.count()}"
        ))

