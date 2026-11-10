from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def render_product_image(product):
    """
    Renders rich, authentic Kerala Ayurvedic packaging artwork based on product type.
    """
    p_type = product.product_type
    brand_badge = product.brand.logo_badge or "KAS"
    brand_name = product.brand.name
    # Shorten name for the bottle label
    display_title = product.name[:16] + "..." if len(product.name) > 16 else product.name
    vol = product.volume_weight

    if p_type == 'oil':
        # Amber Ayurvedic Oil Bottle with Gold Cap & Herbal Leaf
        svg = f"""
        <svg viewBox="0 0 160 200" xmlns="http://www.w3.org/2000/svg" class="ayur-product-svg">
          <defs>
            <linearGradient id="oilGrad{product.id}" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#b45309" />
              <stop offset="35%" stop-color="#f59e0b" />
              <stop offset="70%" stop-color="#d97706" />
              <stop offset="100%" stop-color="#92400e" />
            </linearGradient>
            <linearGradient id="goldCap{product.id}" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#d4af37" />
              <stop offset="50%" stop-color="#fff4b8" />
              <stop offset="100%" stop-color="#aa8010" />
            </linearGradient>
            <linearGradient id="labelGrad{product.id}" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#fffef7" />
              <stop offset="100%" stop-color="#f5ede0" />
            </linearGradient>
            <filter id="shadow{product.id}" x="-10%" y="-10%" width="120%" height="130%">
              <feDropShadow dx="0" dy="6" stdDeviation="5" flood-color="#000" flood-opacity="0.18"/>
            </filter>
          </defs>
          
          <!-- Shadow ground -->
          <ellipse cx="80" cy="188" rx="44" ry="7" fill="#000" opacity="0.12" />

          <!-- Bottle Body -->
          <g filter="url(#shadow{product.id})">
            <!-- Neck -->
            <rect x="71" y="28" width="18" height="22" rx="3" fill="#92400e" />
            <rect x="73" y="30" width="14" height="20" fill="url(#oilGrad{product.id})" opacity="0.8" />
            <!-- Cap -->
            <rect x="68" y="14" width="24" height="16" rx="4" fill="url(#goldCap{product.id})" stroke="#8a6405" stroke-width="0.8" />
            <line x1="72" y1="16" x2="72" y2="28" stroke="#ffffff" stroke-width="0.8" opacity="0.6"/>
            <line x1="88" y1="16" x2="88" y2="28" stroke="#523902" stroke-width="0.8" opacity="0.4"/>
            <!-- Shoulder & Main Bottle -->
            <path d="M 52 70 Q 52 50 71 48 L 89 48 Q 108 50 108 70 L 110 166 Q 110 182 80 182 Q 50 182 50 166 Z" 
                  fill="url(#oilGrad{product.id})" stroke="#78350f" stroke-width="1.2" />
            
            <!-- Glass Specular Highlight -->
            <path d="M 55 74 L 55 162 Q 55 174 65 176 L 63 176 Q 53 174 53 162 L 53 74 Z" fill="#ffffff" opacity="0.45" />

            <!-- Authentic Ayurvedic Paper Label -->
            <rect x="54" y="80" width="52" height="74" rx="4" fill="url(#labelGrad{product.id})" stroke="#b59c78" stroke-width="0.8" />
            <rect x="56" y="82" width="48" height="70" rx="3" fill="none" stroke="#15803d" stroke-width="0.6" stroke-dasharray="2,1" />

            <!-- Brand Badge on Label -->
            <rect x="62" y="86" width="36" height="10" rx="2" fill="#14532d" />
            <text x="80" y="93.5" font-family="'Segoe UI', sans-serif" font-size="6.5" font-weight="bold" fill="#ffd54f" text-anchor="middle">{brand_badge}</text>

            <!-- Decorative Leaf Motif -->
            <path d="M 80 100 Q 84 96 87 101 Q 84 105 80 100 Z" fill="#15803d" />
            <path d="M 80 100 Q 76 96 73 101 Q 76 105 80 100 Z" fill="#16a34a" />

            <!-- Product Title on Label -->
            <text x="80" y="114" font-family="'Segoe UI', sans-serif" font-size="6.2" font-weight="bold" fill="#1e293b" text-anchor="middle">{display_title}</text>
            <text x="80" y="122" font-family="'Segoe UI', sans-serif" font-size="5" fill="#475569" text-anchor="middle">KERALA THAILAM</text>
            
            <!-- Kerala Gold Seal -->
            <circle cx="80" cy="133" r="6" fill="#d97706" stroke="#b45309" stroke-width="0.6" />
            <text x="80" y="135" font-family="'Segoe UI', sans-serif" font-size="4" font-weight="bold" fill="#ffffff" text-anchor="middle">100%</text>
            
            <text x="80" y="147" font-family="'Segoe UI', sans-serif" font-size="5" font-weight="600" fill="#15803d" text-anchor="middle">{vol}</text>
          </g>
        </svg>
        """
    elif p_type == 'arishtam':
        # Traditional Kerala Dark Amber Arishtam Bottle with Wax Seal
        svg = f"""
        <svg viewBox="0 0 160 200" xmlns="http://www.w3.org/2000/svg" class="ayur-product-svg">
          <defs>
            <linearGradient id="arishtamGrad{product.id}" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#451a03" />
              <stop offset="40%" stop-color="#78350f" />
              <stop offset="70%" stop-color="#92400e" />
              <stop offset="100%" stop-color="#3b1104" />
            </linearGradient>
            <filter id="shadowArish{product.id}" x="-10%" y="-10%" width="120%" height="130%">
              <feDropShadow dx="0" dy="6" stdDeviation="5" flood-color="#000" flood-opacity="0.2"/>
            </filter>
          </defs>
          <ellipse cx="80" cy="188" rx="46" ry="7" fill="#000" opacity="0.14" />
          
          <g filter="url(#shadowArish{product.id})">
            <!-- Neck & Traditional Wax Seal -->
            <rect x="71" y="24" width="18" height="26" fill="#451a03" />
            <path d="M 67 14 L 93 14 L 91 26 L 69 26 Z" fill="#991b1b" stroke="#7f1d1d" stroke-width="0.8" />
            <circle cx="80" cy="20" r="4" fill="#b91c1c" />

            <!-- Large Classical Bottle Body -->
            <path d="M 48 76 Q 50 50 71 48 L 89 48 Q 110 50 112 76 L 114 165 Q 114 182 80 182 Q 46 182 46 165 Z" 
                  fill="url(#arishtamGrad{product.id})" stroke="#270a02" stroke-width="1.2" />

            <path d="M 50 80 L 50 162 Q 50 174 58 176 L 56 176 Q 48 174 48 162 L 48 80 Z" fill="#ffffff" opacity="0.3" />

            <!-- Parchment Label -->
            <rect x="52" y="82" width="56" height="74" rx="3" fill="#fef9c3" stroke="#ca8a04" stroke-width="0.8" />
            <rect x="55" y="85" width="50" height="68" rx="2" fill="none" stroke="#78350f" stroke-width="0.5" />

            <rect x="58" y="88" width="44" height="9" rx="2" fill="#78350f" />
            <text x="80" y="94.5" font-family="'Segoe UI', sans-serif" font-size="6" font-weight="bold" fill="#fef08a" text-anchor="middle">{brand_badge} AYURVEDA</text>

            <text x="80" y="108" font-family="'Segoe UI', sans-serif" font-size="6.5" font-weight="bold" fill="#451a03" text-anchor="middle">{display_title}</text>
            <text x="80" y="116" font-family="'Segoe UI', sans-serif" font-size="5" fill="#78350f" text-anchor="middle">ASAVAM / ARISHTAM</text>
            
            <circle cx="80" cy="127" r="7" fill="#b91c1c" />
            <text x="80" y="129.5" font-family="'Segoe UI', sans-serif" font-size="4.2" font-weight="bold" fill="#ffffff" text-anchor="middle">PURE</text>

            <text x="80" y="145" font-family="'Segoe UI', sans-serif" font-size="5" font-weight="bold" fill="#78350f" text-anchor="middle">{vol}</text>
          </g>
        </svg>
        """
    elif p_type == 'tablet':
        # Ayurvedic Herbal Tablet Bottle & Blister Pack
        svg = f"""
        <svg viewBox="0 0 160 200" xmlns="http://www.w3.org/2000/svg" class="ayur-product-svg">
          <defs>
            <linearGradient id="tabBottle{product.id}" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#064e3b" />
              <stop offset="40%" stop-color="#059669" />
              <stop offset="80%" stop-color="#10b981" />
              <stop offset="100%" stop-color="#047857" />
            </linearGradient>
            <linearGradient id="tabCap{product.id}" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#f8fafc" />
              <stop offset="50%" stop-color="#ffffff" />
              <stop offset="100%" stop-color="#cbd5e1" />
            </linearGradient>
          </defs>
          <ellipse cx="80" cy="186" rx="42" ry="6" fill="#000" opacity="0.12" />

          <!-- Tablet Container Body -->
          <g filter="url(#shadow{product.id})">
            <!-- White Ribbed Cap -->
            <rect x="58" y="22" width="44" height="20" rx="3" fill="url(#tabCap{product.id})" stroke="#94a3b8" stroke-width="0.8" />
            <line x1="64" y1="24" x2="64" y2="40" stroke="#cbd5e1" stroke-width="1"/>
            <line x1="72" y1="24" x2="72" y2="40" stroke="#cbd5e1" stroke-width="1"/>
            <line x1="80" y1="24" x2="80" y2="40" stroke="#cbd5e1" stroke-width="1"/>
            <line x1="88" y1="24" x2="88" y2="40" stroke="#cbd5e1" stroke-width="1"/>
            <line x1="96" y1="24" x2="96" y2="40" stroke="#cbd5e1" stroke-width="1"/>

            <!-- Bottle Body -->
            <rect x="50" y="42" width="60" height="136" rx="10" fill="url(#tabBottle{product.id})" stroke="#064e3b" stroke-width="1" />
            
            <!-- Label -->
            <rect x="52" y="62" width="56" height="96" rx="4" fill="#ffffff" stroke="#e2e8f0" stroke-width="0.8" />
            
            <rect x="55" y="66" width="50" height="12" rx="2" fill="#065f46" />
            <text x="80" y="74.5" font-family="'Segoe UI', sans-serif" font-size="6" font-weight="bold" fill="#34d399" text-anchor="middle">{brand_badge}</text>

            <text x="80" y="93" font-family="'Segoe UI', sans-serif" font-size="6.2" font-weight="bold" fill="#0f172a" text-anchor="middle">{display_title}</text>
            <text x="80" y="102" font-family="'Segoe UI', sans-serif" font-size="5" fill="#64748b" text-anchor="middle">KWATH TABLETS</text>

            <!-- Tablet Pill Illustration on Label -->
            <ellipse cx="73" cy="118" rx="6" ry="6" fill="#a7f3d0" stroke="#059669" stroke-width="1" />
            <ellipse cx="87" cy="118" rx="6" ry="6" fill="#6ee7b7" stroke="#047857" stroke-width="1" />
            
            <rect x="60" y="134" width="40" height="14" rx="3" fill="#ecfdf5" stroke="#10b981" stroke-width="0.6" />
            <text x="80" y="143" font-family="'Segoe UI', sans-serif" font-size="5.5" font-weight="bold" fill="#065f46" text-anchor="middle">{vol}</text>
          </g>
        </svg>
        """
    elif p_type == 'lehyam':
        # Traditional Ayurvedic Lehyam & Rasayanam Golden Brass / Ceramic Jar
        svg = f"""
        <svg viewBox="0 0 160 200" xmlns="http://www.w3.org/2000/svg" class="ayur-product-svg">
          <defs>
            <linearGradient id="lehyamJar{product.id}" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#78350f" />
              <stop offset="30%" stop-color="#b45309" />
              <stop offset="60%" stop-color="#d97706" />
              <stop offset="100%" stop-color="#451a03" />
            </linearGradient>
            <linearGradient id="lehyamCap{product.id}" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#ca8a04" />
              <stop offset="50%" stop-color="#fef08a" />
              <stop offset="100%" stop-color="#854d0e" />
            </linearGradient>
          </defs>
          <ellipse cx="80" cy="186" rx="46" ry="7" fill="#000" opacity="0.14" />

          <g filter="url(#shadow{product.id})">
            <!-- Brass Dome Lid -->
            <circle cx="80" cy="30" r="5" fill="#fef08a" stroke="#854d0e" stroke-width="0.8" />
            <path d="M 52 48 Q 80 32 108 48 Z" fill="url(#lehyamCap{product.id})" stroke="#713f12" stroke-width="1" />
            <rect x="50" y="47" width="60" height="9" rx="2" fill="url(#lehyamCap{product.id})" stroke="#713f12" stroke-width="0.8" />

            <!-- Jar Body with curved authentic pot shape -->
            <path d="M 54 56 Q 40 100 48 152 Q 54 178 80 178 Q 106 178 112 152 Q 120 100 106 56 Z" 
                  fill="url(#lehyamJar{product.id})" stroke="#451a03" stroke-width="1.2" />

            <!-- Highlight Curve -->
            <path d="M 50 90 Q 48 130 55 156" fill="none" stroke="#ffffff" stroke-width="2" opacity="0.3" stroke-linecap="round" />

            <!-- Front Label -->
            <rect x="55" y="82" width="50" height="66" rx="4" fill="#fffbeb" stroke="#f59e0b" stroke-width="0.8" />
            <rect x="58" y="85" width="44" height="9" rx="2" fill="#b45309" />
            <text x="80" y="91.5" font-family="'Segoe UI', sans-serif" font-size="5.5" font-weight="bold" fill="#fffbeb" text-anchor="middle">{brand_badge} RASAYANAM</text>

            <text x="80" y="106" font-family="'Segoe UI', sans-serif" font-size="6" font-weight="bold" fill="#451a03" text-anchor="middle">{display_title}</text>
            <text x="80" y="115" font-family="'Segoe UI', sans-serif" font-size="5" fill="#92400e" text-anchor="middle">LEHYAM / GHRITHAM</text>

            <!-- Amla / Herbal emblem -->
            <circle cx="80" cy="126" r="6" fill="#15803d" />
            <circle cx="80" cy="126" r="4" fill="#22c55e" opacity="0.8" />

            <text x="80" y="141" font-family="'Segoe UI', sans-serif" font-size="5" font-weight="bold" fill="#78350f" text-anchor="middle">{vol}</text>
          </g>
        </svg>
        """
    elif p_type == 'beauty':
        # Luxury Kumkumadi Dropper Bottle & Ayurvedic Beauty Care
        svg = f"""
        <svg viewBox="0 0 160 200" xmlns="http://www.w3.org/2000/svg" class="ayur-product-svg">
          <defs>
            <linearGradient id="beautyGrad{product.id}" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#9f1239" />
              <stop offset="40%" stop-color="#e11d48" />
              <stop offset="70%" stop-color="#f43f5e" />
              <stop offset="100%" stop-color="#881337" />
            </linearGradient>
            <linearGradient id="goldDropper{product.id}" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#eab308" />
              <stop offset="50%" stop-color="#fef08a" />
              <stop offset="100%" stop-color="#ca8a04" />
            </linearGradient>
          </defs>
          <ellipse cx="80" cy="186" rx="38" ry="6" fill="#000" opacity="0.12" />

          <g filter="url(#shadow{product.id})">
            <!-- Pipette Rubber Bulb -->
            <path d="M 74 14 Q 80 8 86 14 L 86 26 L 74 26 Z" fill="#ffffff" stroke="#cbd5e1" stroke-width="0.8" />
            <!-- Gold Dropper Ring -->
            <rect x="68" y="26" width="24" height="12" rx="2" fill="url(#goldDropper{product.id})" stroke="#a16207" stroke-width="0.8" />

            <!-- Slim Sleek Bottle -->
            <path d="M 56 54 L 104 54 L 102 168 Q 102 178 80 178 Q 58 178 58 168 Z" 
                  fill="url(#beautyGrad{product.id})" stroke="#881337" stroke-width="1" />

            <!-- White Silk Label -->
            <rect x="60" y="74" width="40" height="78" rx="3" fill="#ffffff" stroke="#fecdd3" stroke-width="0.8" />
            
            <text x="80" y="85" font-family="'Segoe UI', sans-serif" font-size="5" font-weight="bold" fill="#e11d48" text-anchor="middle">{brand_badge} AYURVEDA</text>
            <line x1="68" y1="88" x2="92" y2="88" stroke="#f43f5e" stroke-width="0.6" />

            <text x="80" y="102" font-family="'Segoe UI', sans-serif" font-size="5.8" font-weight="bold" fill="#1e293b" text-anchor="middle">{display_title}</text>
            <text x="80" y="111" font-family="'Segoe UI', sans-serif" font-size="4.5" fill="#881337" text-anchor="middle">SKIN RADIANCE</text>

            <!-- Saffron Flower icon -->
            <circle cx="80" cy="124" r="5" fill="#fbbf24" />
            <path d="M 80 120 L 80 128 M 76 124 L 84 124" stroke="#d97706" stroke-width="0.8" />

            <text x="80" y="142" font-family="'Segoe UI', sans-serif" font-size="5" font-weight="bold" fill="#0f172a" text-anchor="middle">{vol}</text>
          </g>
        </svg>
        """
    else:
        # Classical Choornam / Herbal Powder Pouch
        svg = f"""
        <svg viewBox="0 0 160 200" xmlns="http://www.w3.org/2000/svg" class="ayur-product-svg">
          <defs>
            <linearGradient id="pouchGrad{product.id}" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#d6b88d" />
              <stop offset="50%" stop-color="#eddac2" />
              <stop offset="100%" stop-color="#c9a573" />
            </linearGradient>
          </defs>
          <ellipse cx="80" cy="186" rx="46" ry="6" fill="#000" opacity="0.12" />

          <g filter="url(#shadow{product.id})">
            <!-- Pouch Top Seal & Ziplock Notch -->
            <path d="M 46 36 L 114 36 L 112 48 L 48 48 Z" fill="#b08b58" stroke="#8c6a38" stroke-width="0.8" />
            <circle cx="54" cy="42" r="2" fill="#8c6a38" />

            <!-- Pouch Main Body -->
            <path d="M 48 48 L 112 48 L 116 166 Q 116 178 80 178 Q 44 178 44 166 Z" 
                  fill="url(#pouchGrad{product.id})" stroke="#a17d4a" stroke-width="1.2" />

            <!-- Earth Green Classical Label -->
            <rect x="52" y="66" width="56" height="84" rx="4" fill="#ffffff" stroke="#cbd5e1" stroke-width="0.8" />
            
            <rect x="56" y="70" width="48" height="10" rx="2" fill="#15803d" />
            <text x="80" y="77.5" font-family="'Segoe UI', sans-serif" font-size="5.5" font-weight="bold" fill="#fef08a" text-anchor="middle">{brand_badge} CHOORNAM</text>

            <text x="80" y="94" font-family="'Segoe UI', sans-serif" font-size="6" font-weight="bold" fill="#14532d" text-anchor="middle">{display_title}</text>
            <text x="80" y="103" font-family="'Segoe UI', sans-serif" font-size="4.8" fill="#475569" text-anchor="middle">PURE HERBAL POWDER</text>

            <!-- Mortar & Pestle insignia -->
            <path d="M 72 120 Q 80 128 88 120 Z" fill="#15803d" />
            <line x1="77" y1="114" x2="85" y2="124" stroke="#854d0e" stroke-width="2" stroke-linecap="round" />

            <text x="80" y="139" font-family="'Segoe UI', sans-serif" font-size="5" font-weight="bold" fill="#0f172a" text-anchor="middle">{vol}</text>
          </g>
        </svg>
        """

    return mark_safe(svg)
