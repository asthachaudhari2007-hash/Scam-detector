# -*- coding: utf-8 -*-

import pickle
import re

from urllib.parse import urlparse

from flask import Flask, render_template, request, jsonify

# OCR
from scanner.ocr import extract_text_from_image


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

MODEL_PATH = "model/model.pkl"
VECTORIZER_PATH = "model/vectorizer.pkl"


try:

    with open(MODEL_PATH, "rb") as f:
        clf = pickle.load(f)

    with open(VECTORIZER_PATH, "rb") as f:
        vectorizer = pickle.load(f)

    print("========================================")
    print("ML MODEL LOADED SUCCESSFULLY")
    print("========================================")
    print("Model classes:", clf.classes_)
    print("========================================")

except Exception as e:

    print("========================================")
    print("ERROR LOADING MODEL")
    print("========================================")
    print(e)
    print("========================================")

    clf = None
    vectorizer = None
    # ============================================================
# SCAM TACTIC INFORMATION
# ============================================================

TACTIC_INFO = {

    "OTP / PIN Request": {
        "keywords": [
            "otp",
            "one time password",
            "pin",
            "cvv",
            "password",
            "verification code",
            "code",
            "share otp",
            "send otp"
        ],

        "description": (
            "The message asks for sensitive authentication "
            "information such as an OTP, PIN, CVV, or password."
        ),

        "description_hi": (
            "यह संदेश OTP, PIN, CVV या पासवर्ड जैसी "
            "संवेदनशील जानकारी मांग रहा है।"
        ),

        "tips": [
            "Never share an OTP, PIN, CVV, or password with anyone.",
            "Banks and legitimate organizations normally do not ask for your OTP over a call or message."
        ],

        "tips_hi": [
            "OTP, PIN, CVV या पासवर्ड किसी के साथ भी साझा न करें।",
            "बैंक और असली संस्थाएं सामान्यतः कॉल या मैसेज पर OTP नहीं मांगतीं।"
        ]
    },


    "Fake Bank / KYC Scam": {
        "keywords": [
            "kyc",
            "bank account",
            "bank",
            "account blocked",
            "account will be blocked",
            "update kyc",
            "verify kyc",
            "kyc expired",
            "bank verification",
            "net banking",
            "banking"
        ],

        "description": (
            "The message appears to use a bank or KYC-related "
            "request to create pressure."
        ),

        "description_hi": (
            "यह संदेश बैंक या KYC से जुड़े दबाव का उपयोग कर रहा है।"
        ),

        "tips": [
            "Do not click links claiming that your KYC must be updated immediately.",
            "Verify your bank account only through the official bank app or website.",
            "Never share banking passwords, OTPs, PINs, or card details."
        ],

        "tips_hi": [
            "KYC तुरंत अपडेट करने का दावा करने वाले लिंक पर क्लिक न करें।",
            "अपने बैंक खाते को केवल आधिकारिक बैंक ऐप या वेबसाइट से वेरिफाई करें।",
            "बैंकिंग पासवर्ड, OTP, PIN या कार्ड विवरण कभी साझा न करें।"
        ]
    },


    "Lottery / Prize Scam": {
        "keywords": [
            "lottery",
            "winner",
            "you won",
            "won a prize",
            "prize",
            "reward",
            "cash prize",
            "lucky winner",
            "congratulations",
            "claim your prize",
            "free gift"
        ],

        "description": (
            "The message mentions a prize, reward, lottery, "
            "or unexpected winnings."
        ),

        "description_hi": (
            "यह संदेश किसी इनाम, पुरस्कार, लॉटरी या अनपेक्षित "
            "जीत का उल्लेख कर रहा है।"
        ),

        "tips": [
            "Do not pay a fee to receive an unexpected prize.",
            "Do not provide banking or personal information to claim a prize.",
            "Unexpected lottery or reward messages are often scams."
        ],

        "tips_hi": [
            "अनपेक्षित इनाम पाने के लिए कोई शुल्क न दें।",
            "इनाम पाने के लिए बैंकिंग या व्यक्तिगत जानकारी न दें।",
            "अनपेक्षित लॉटरी या इनाम संदेश अक्सर धोखा होते हैं।"
        ]
    },


    "Courier / Parcel Scam": {
        "keywords": [
            "parcel",
            "courier",
            "package",
            "delivery",
            "customs",
            "shipment",
            "delivery failed",
            "parcel held",
            "package held",
            "custom duty"
        ],

        "description": (
            "The message appears to use a parcel, courier, "
            "delivery, or customs-related story."
        ),

        "description_hi": (
            "यह संदेश पार्सल, कूरियर, डिलीवरी या कस्टम्स से जुड़ी "
            "कहानी का उपयोग कर रहा है।"
        ),

        "tips": [
            "Verify deliveries directly through the courier's official website.",
            "Do not pay unexpected delivery or customs charges through unknown links.",
            "Do not share OTPs or banking details with an unknown courier caller."
        ],

        "tips_hi": [
            "डिलीवरी की पुष्टि केवल कूरियर की आधिकारिक वेबसाइट से करें।",
            "अनजान लिंक के माध्यम से अनपेक्षित डिलीवरी या कस्टम शुल्क न दें।",
            "अनजान कूरियर कॉलर के साथ OTP या बैंकिंग विवरण साझा न करें।"
        ]
    },


    "Tech Support Scam": {
        "keywords": [
            "technical support",
            "tech support",
            "computer infected",
            "virus detected",
            "your computer has a virus",
            "call support",
            "remote access",
            "remote desktop",
            "anydesk",
            "teamviewer",
            "support number"
        ],

        "description": (
            "The message claims that your computer or device "
            "has a problem and may request remote access."
        ),

        "description_hi": (
            "यह संदेश दावा करता है कि आपके डिवाइस में समस्या है "
            "और रिमोट एक्सेस मांग सकता है।"
        ),

        "tips": [
            "Do not give strangers remote access to your computer.",
            "Do not install remote-access software because of an unexpected call.",
            "Contact the device or software company through its official website."
        ],

        "tips_hi": [
            "अजनबियों को अपने कंप्यूटर का रिमोट एक्सेस न दें।",
            "अनपेक्षित कॉल के कारण रिमोट-एक्सेस सॉफ़्टवेयर इंस्टॉल न करें।",
            "डिवाइस या सॉफ़्टवेयर कंपनी से केवल आधिकारिक वेबसाइट के माध्यम से संपर्क करें।"
        ]
    },


    "Fake Authority / Threat": {
        "keywords": [
            "police",
            "court",
            "legal action",
            "arrest",
            "arrested",
            "government",
            "cyber crime",
            "cybercrime",
            "fine",
            "penalty",
            "case registered",
            "warrant",
            "official notice"
        ],

        "description": (
            "The message uses authority, threats, legal action, "
            "or fear to pressure the recipient."
        ),

        "description_hi": (
            "यह संदेश डर पैदा करने के लिए अधिकार, धमकी या कानूनी "
            "कार्रवाई का उपयोग कर रहा है।"
        ),

        "tips": [
            "Do not send money because someone threatens arrest or legal action.",
            "Verify official claims using trusted government contact information.",
            "Do not share sensitive information with an unknown caller."
        ],

        "tips_hi": [
            "गिरफ्तारी या कानूनी कार्रवाई की धमकी मिलने पर पैसे न भेजें।",
            "आधिकारिक दावों की पुष्टि विश्वसनीय सरकारी संपर्क जानकारी से करें।",
            "अनजान कॉलर के साथ संवेदनशील जानकारी साझा न करें।"
        ]
    },


    "Family Emergency Scam": {
        "keywords": [
            "help me",
            "emergency",
            "accident",
            "hospital",
            "i need money",
            "send money",
            "urgent help",
            "please send",
            "family emergency",
            "friend emergency"
        ],

        "description": (
            "The message appears to use an emergency situation "
            "to pressure you into sending money."
        ),

        "description_hi": (
            "यह संदेश किसी आपातकालीन स्थिति का उपयोग करके आपको "
            "पैसे भेजने के लिए दबाव डाल रहा है।"
        ),

        "tips": [
            "Contact the family member directly using a known phone number.",
            "Do not send money based only on an unexpected message or call.",
            "Ask a personal question that only the real person would know."
        ],

        "tips_hi": [
            "परिवार के सदस्य से सीधे किसी जाने-पहचाने नंबर पर संपर्क करें।",
            "केवल एक अनपेक्षित संदेश या कॉल के आधार पर पैसे न भेजें।",
            "ऐसा व्यक्तिगत सवाल पूछें जो केवल असली व्यक्ति ही जानता हो।"
        ]
    }
}
# ============================================================
# HINDI TRANSLATIONS — tactic labels, general tips, and
# action text, so the analysis can be shown/spoken in
# either English or Hindi based on the user's choice.
# ============================================================

HINDI_TACTIC_LABELS = {
    "OTP / PIN Request": "OTP / PIN अनुरोध",
    "Fake Bank / KYC Scam": "फर्जी बैंक / KYC धोखाधड़ी",
    "Lottery / Prize Scam": "लॉटरी / इनाम धोखाधड़ी",
    "Courier / Parcel Scam": "कूरियर / पार्सल धोखाधड़ी",
    "Tech Support Scam": "टेक सपोर्ट धोखाधड़ी",
    "Fake Authority / Threat": "फर्जी अधिकारी / धमकी",
    "Family Emergency Scam": "पारिवारिक आपातकाल धोखाधड़ी",
    "Unknown / General": "अज्ञात / सामान्य",
}

GENERAL_TIPS_HI = [
    "OTP, PIN, पासवर्ड या बैंकिंग विवरण कभी साझा न करें।",
    "किसी अनपेक्षित संदेश या कॉल के कारण पैसे न भेजें।",
    "संस्था से केवल उसकी आधिकारिक वेबसाइट या ऐप के माध्यम से संपर्क करें।",
    "अगर कोई आप पर दबाव डाले या धमकाए, तो रुकें और पहले पुष्टि करें।"
]

LINK_TIP_HI = (
    "जब तक आप भेजने वाले और वेबसाइट की स्वतंत्र रूप से पुष्टि "
    "न कर लें, तब तक लिंक न खोलें।"
)

ACTION_TEXT_HI = {
    "high": (
        "इस संदेश में दिए गए लिंक पर क्लिक न करें, व्यक्तिगत जानकारी "
        "साझा न करें, पैसे न भेजें, और निर्देशों का पालन न करें। "
        "दावे की पुष्टि किसी आधिकारिक स्रोत से करें।"
    ),
    "medium": (
        "जवाब देने से पहले सावधान रहें। व्यक्तिगत या वित्तीय जानकारी "
        "साझा न करें। संदेश की स्वतंत्र रूप से पुष्टि करें।"
    ),
    "low": (
        "कोई मजबूत धोखाधड़ी संकेत नहीं मिला। फिर भी संवेदनशील जानकारी "
        "साझा करने से बचें और अनपेक्षित अनुरोधों की पुष्टि करें।"
    ),
}

ML_REASON_HIGH_HI = (
    "मशीन-लर्निंग मॉडल को इस संदेश में धोखाधड़ी वाले संदेशों से "
    "जुड़े मजबूत पैटर्न मिले।"
)

ML_REASON_MEDIUM_HI = (
    "इस संदेश में ऐसे पैटर्न हैं जो धोखाधड़ी वाले संदेशों से "
    "जुड़े हो सकते हैं।"
)

URGENCY_REASON_HI = (
    "यह संदेश जल्दी कार्रवाई करने के लिए तात्कालिकता या दबाव बना रहा है।"
)

DEFAULT_REASON_HI = (
    "कोई मजबूत धोखाधड़ी संकेत नहीं मिला, लेकिन अनपेक्षित संदेशों "
    "की फिर भी पुष्टि की जानी चाहिए।"
)
# ============================================================
# CALL CHECKER — maps each checkbox option to a descriptive
# sentence, so a selected-checkbox call description can be run
# through the SAME classify() pipeline (ML model + tactic
# keywords + urgency detection) used for typed/pasted messages.
# ============================================================

CALL_OPTION_PHRASES = {
    "otp": "The caller asked me to share my OTP.",
    "pin": "The caller asked me to share my PIN.",
    "bank_details": "The caller asked for my bank account details.",
    "money_transfer": "The caller asked me to transfer money immediately.",
    "remote_access": "The caller asked for remote access to my computer or phone.",
    "kyc_update": "The caller said my KYC needs to be updated urgently or my account will be blocked.",
    "aadhaar": "The caller asked for my Aadhaar number and details.",
    "threatened_arrest": "The caller threatened me with arrest or legal action.",
    "prize_lottery": "The caller said I won a prize or lottery and asked me to pay a fee to claim it.",
    "other": "Something else concerning happened during the call.",
}

CALL_OPTION_LABELS = {
    "otp": "OTP",
    "pin": "PIN",
    "bank_details": "Bank details",
    "money_transfer": "Money transfer",
    "remote_access": "Remote access",
    "kyc_update": "KYC update",
    "aadhaar": "Aadhaar details",
    "threatened_arrest": "Threatened arrest",
    "prize_lottery": "Prize/lottery",
    "other": "Something else",
}

CALL_OPTION_LABELS_HI = {
    "otp": "OTP",
    "pin": "PIN",
    "bank_details": "बैंक विवरण",
    "money_transfer": "पैसे ट्रांसफर",
    "remote_access": "रिमोट एक्सेस",
    "kyc_update": "KYC अपडेट",
    "aadhaar": "आधार विवरण",
    "threatened_arrest": "गिरफ्तारी की धमकी",
    "prize_lottery": "इनाम/लॉटरी",
    "other": "कुछ और",
}
# ============================================================
# URGENCY DETECTION
# ============================================================

URGENCY_KEYWORDS = [

    "urgent",
    "urgently",
    "immediately",
    "right away",
    "act now",
    "within 24 hours",
    "today",
    "final notice",
    "expires",
    "last chance",
    "blocked today",
    "will be blocked",

    # Hindi
    "तुरंत",
    "अभी",
    "आज",
    "जल्दी",
    "अंतिम चेतावनी",
    "बंद हो जाएगा",

    # Hinglish
    "turant",
    "abhi",
    "jaldi",
    "aaj",
    "final notice",
    "act now"
]


# ============================================================
# LINK DETECTION
# ============================================================

URL_PATTERN = re.compile(
    r"(https?://[^\s]+|www\.[^\s]+)",
    re.IGNORECASE
)


SUSPICIOUS_URL_WORDS = [
    "verify",
    "verification",
    "secure",
    "update",
    "kyc",
    "claim",
    "prize",
    "reward",
    "account",
    "bank",
    "parcel",
    "customs",
    "login",
    "signin"
]


SUSPICIOUS_TLDS = [
    ".xyz",
    ".top",
    ".tk",
    ".ml",
    ".ga",
    ".cf",
    ".gq",
    ".click",
    ".link",
    ".support",
    ".fit",
    ".loan",
    ".win",
    ".work",
    ".info"
]


KNOWN_BRANDS = [
    "sbi",
    "hdfc",
    "icici",
    "axis",
    "pnb",
    "paytm",
    "phonepe",
    "googlepay",
    "amazon",
    "flipkart",
    "whatsapp",
    "facebook",
    "instagram",
    "microsoft",
    "google",
    "netflix"
]


DANGEROUS_FILE_EXTENSIONS = [
    ".exe",
    ".apk",
    ".scr",
    ".bat",
    ".msi",
    ".jar"
]


def extract_links(text):

    return URL_PATTERN.findall(text)


def _normalize_for_parsing(link):

    # urlparse needs a scheme to correctly split host from path.
    if link.lower().startswith("www."):
        return "http://" + link

    return link


def check_link_risk(text, lang="en"):

    links = extract_links(text)

    if not links:

        return {
            "has_link": False,
            "risk": "none",
            "reasons": []
        }

    major_reasons = []
    minor_reasons = []

    for link in links:

        lower_link = link.lower()

        # ----------------------------------------------------
        # @ symbol trick
        # everything before an "@" in a URL is ignored by
        # browsers as userinfo — "http://sbi.com@evil.com"
        # actually goes to evil.com, not sbi.com.
        # ----------------------------------------------------

        if "@" in link:

            if lang == "hi":
                major_reasons.append(
                    "इस लिंक में '@' चिह्न का उपयोग किया गया है, जो "
                    "असली गंतव्य को छिपाने के लिए एक सामान्य तरीका है।"
                )
            else:
                major_reasons.append(
                    "The link uses an '@' symbol, a common trick "
                    "to disguise the real destination behind what "
                    "looks like a trusted domain."
                )

        # ----------------------------------------------------
        # Parse the URL properly to isolate the actual domain
        # ----------------------------------------------------

        parsed = urlparse(_normalize_for_parsing(link))

        host = parsed.hostname or ""
        path = parsed.path or ""

        # ----------------------------------------------------
        # HTTP instead of HTTPS
        # ----------------------------------------------------

        if lower_link.startswith("http://"):

            if lang == "hi":
                minor_reasons.append(
                    "यह लिंक HTTPS का उपयोग नहीं करता।"
                )
            else:
                minor_reasons.append(
                    "The link does not use HTTPS."
                )

        # ----------------------------------------------------
        # Suspicious words
        # ----------------------------------------------------

        matched_words = [
            word
            for word in SUSPICIOUS_URL_WORDS
            if word in lower_link
        ]

        if matched_words:

            if lang == "hi":
                minor_reasons.append(
                    "इस लिंक में ऐसे शब्द हैं जो आमतौर पर सत्यापन या "
                    "इनाम धोखाधड़ी में उपयोग होते हैं: "
                    + ", ".join(matched_words[:4])
                )
            else:
                minor_reasons.append(
                    "The link contains words commonly used "
                    "in verification or reward scams: "
                    + ", ".join(matched_words[:4])
                )

        # ----------------------------------------------------
        # IP address URL
        # ----------------------------------------------------

        if re.search(
            r"https?://\d{1,3}(\.\d{1,3}){3}",
            lower_link
        ):

            if lang == "hi":
                major_reasons.append(
                    "यह लिंक सामान्य डोमेन के बजाय एक IP पते का "
                    "उपयोग करता है, जो किसी वैध सेवा के लिए असामान्य है।"
                )
            else:
                major_reasons.append(
                    "The link uses an IP address instead of "
                    "a normal domain, which is unusual for a "
                    "legitimate service."
                )

        # ----------------------------------------------------
        # URL shorteners
        # ----------------------------------------------------

        shorteners = [
            "bit.ly",
            "tinyurl.com",
            "t.co",
            "goo.gl",
            "is.gd",
            "cutt.ly"
        ]

        if any(
            shortener in lower_link
            for shortener in shorteners
        ):

            if lang == "hi":
                minor_reasons.append(
                    "यह लिंक एक URL-शॉर्टनिंग सेवा का उपयोग करता है, "
                    "इसलिए इसका असली गंतव्य छुपा हुआ है।"
                )
            else:
                minor_reasons.append(
                    "The link uses a URL-shortening service, "
                    "so its final destination is hidden."
                )

        # ----------------------------------------------------
        # Punycode domain (used to fake lookalike characters)
        # ----------------------------------------------------

        if "xn--" in host:

            if lang == "hi":
                major_reasons.append(
                    "यह डोमेन पनीकोड एन्कोडिंग का उपयोग करता है, जिसका "
                    "उपयोग कभी-कभी भ्रामक अक्षरों के साथ नकली डोमेन "
                    "बनाने के लिए किया जाता है।"
                )
            else:
                major_reasons.append(
                    "The domain uses punycode encoding, which is "
                    "sometimes used to create lookalike domains "
                    "with deceptive characters."
                )

        # ----------------------------------------------------
        # Suspicious / free TLD
        # ----------------------------------------------------

        matched_tlds = [
            tld
            for tld in SUSPICIOUS_TLDS
            if host.endswith(tld)
        ]

        if matched_tlds:

            if lang == "hi":
                minor_reasons.append(
                    "यह डोमेन एक असामान्य टॉप-लेवल डोमेन ("
                    + ", ".join(matched_tlds)
                    + ") का उपयोग करता है, जो अक्सर फ़िशिंग साइटों "
                    "में उपयोग होता है क्योंकि यह सस्ता या मुफ़्त है।"
                )
            else:
                minor_reasons.append(
                    "The domain uses an uncommon top-level domain "
                    "(" + ", ".join(matched_tlds) + ") that is "
                    "frequently used in phishing sites because it "
                    "is cheap or free to register."
                )

        # ----------------------------------------------------
        # Brand impersonation
        # a real brand name appears in the domain, but the
        # domain's main part (second-level domain) isn't
        # actually that brand
        # ----------------------------------------------------

        host_parts = host.split(".")

        second_level_domain = (
            host_parts[-2] if len(host_parts) >= 2 else host
        )

        for brand in KNOWN_BRANDS:

            if brand in host and brand != second_level_domain:

                if lang == "hi":
                    major_reasons.append(
                        "इस डोमेन में ब्रांड नाम '"
                        + brand
                        + "' शामिल है, लेकिन यह उस ब्रांड की आधिकारिक "
                        "वेबसाइट नहीं लगती — यह एक सामान्य प्रतिरूपण "
                        "तरीका है।"
                    )
                else:
                    major_reasons.append(
                        "The domain contains the brand name '"
                        + brand
                        + "' but does not appear to be that "
                        "brand's official website — a common "
                        "impersonation tactic."
                    )

                break

        # ----------------------------------------------------
        # Excessive subdomains
        # ----------------------------------------------------

        if len(host_parts) >= 5:

            if lang == "hi":
                minor_reasons.append(
                    "इस डोमेन में असामान्य रूप से कई सबडोमेन हैं, जिनका "
                    "उपयोग असली गंतव्य को छिपाने के लिए किया जा सकता है।"
                )
            else:
                minor_reasons.append(
                    "The domain has an unusually large number of "
                    "subdomains, which can be used to disguise "
                    "the real destination."
                )

        # ----------------------------------------------------
        # Non-standard port
        # ----------------------------------------------------

        if parsed.port is not None and parsed.port not in (80, 443):

            if lang == "hi":
                minor_reasons.append(
                    "यह लिंक एक गैर-मानक नेटवर्क पोर्ट ("
                    + str(parsed.port)
                    + ") का उपयोग करता है, जो सामान्य वेबसाइट के लिए "
                    "असामान्य है।"
                )
            else:
                minor_reasons.append(
                    "The link uses a non-standard network port ("
                    + str(parsed.port)
                    + "), which is unusual for a normal website."
                )

        # ----------------------------------------------------
        # Dangerous file extension
        # ----------------------------------------------------

        matched_extensions = [
            ext
            for ext in DANGEROUS_FILE_EXTENSIONS
            if path.lower().endswith(ext)
        ]

        if matched_extensions:

            if lang == "hi":
                major_reasons.append(
                    "यह लिंक सीधे एक डाउनलोड करने योग्य फ़ाइल ("
                    + ", ".join(matched_extensions)
                    + ") की ओर इशारा करता है, जो आपके डिवाइस में "
                    "मैलवेयर इंस्टॉल कर सकती है।"
                )
            else:
                major_reasons.append(
                    "The link points directly to a downloadable "
                    "file (" + ", ".join(matched_extensions) + "), "
                    "which could install malware on your device."
                )

    # --------------------------------------------------------
    # Remove duplicate reasons while keeping order
    # --------------------------------------------------------

    major_reasons = list(dict.fromkeys(major_reasons))
    minor_reasons = list(dict.fromkeys(minor_reasons))

    all_reasons = major_reasons + minor_reasons

    # --------------------------------------------------------
    # Risk level
    # a single major red flag is treated as high risk on its
    # own; otherwise minor signals accumulate gradually
    # --------------------------------------------------------

    if len(major_reasons) >= 1 or len(minor_reasons) >= 3:

        risk = "high"

    elif len(minor_reasons) >= 1:

        risk = "medium"

    else:

        risk = "low"

    return {
        "has_link": True,
        "risk": risk,
        "reasons": all_reasons
    }
    # ============================================================
# LANGUAGE DETECTION
# (this detects the LANGUAGE OF THE MESSAGE ITSELF — separate
# from the `lang` parameter below, which controls what language
# the ANALYSIS/OUTPUT is shown in)
# ============================================================

def detect_language(text):

    # --------------------------------------------------------
    # Hindi / Devanagari detection
    # --------------------------------------------------------

    hindi_chars = len(
        re.findall(
            r"[\u0900-\u097F]",
            text
        )
    )

    if hindi_chars >= 3:

        return "hi"

    # --------------------------------------------------------
    # Hinglish detection
    # --------------------------------------------------------

    text_lower = text.lower()

    hinglish_words = [
        "aapka",
        "aapki",
        "hai",
        "hain",
        "ko",
        "se",
        "par",
        "mein",
        "mujhe",
        "turant",
        "batao",
        "bataiye",
        "karo",
        "karein",
        "bhejo",
        "paise",
        "khata",
        "band",
        "kyc"
    ]

    matches = 0

    for word in hinglish_words:

        if re.search(
            r"\b" + re.escape(word) + r"\b",
            text_lower
        ):

            matches += 1

    if matches >= 2:

        return "hi"

    return "en"


# ============================================================
# TACTIC MATCHING
# ============================================================

def find_matched_tactics(text):

    text_lower = text.lower()

    matches = []

    for tactic, info in TACTIC_INFO.items():

        hit_phrases = []

        for phrase in info["keywords"]:

            if phrase.lower() in text_lower:

                hit_phrases.append(phrase)

        if hit_phrases:

            matches.append({
                "tactic": tactic,
                "phrases": hit_phrases[:4]
            })

    return matches
# ============================================================
# MAIN CLASSIFICATION FUNCTION
#
# `lang` controls the OUTPUT language of reasons, tips, action
# text, and the tactic label ("en" or "hi"). It is independent
# of detect_language(), which detects the language OF THE
# MESSAGE the user submitted.
# ============================================================

def classify(text, lang="en"):

    # --------------------------------------------------------
    # Check model
    # --------------------------------------------------------

    if clf is None or vectorizer is None:

        raise RuntimeError(
            "ML model or vectorizer could not be loaded."
        )

    # --------------------------------------------------------
    # Basic text validation
    # --------------------------------------------------------

    text = (text or "").strip()

    if not text:

        raise ValueError(
            "The message is empty."
        )

    if lang not in ("en", "hi"):
        lang = "en"

    # --------------------------------------------------------
    # Language of the MESSAGE (not the output language)
    # --------------------------------------------------------

    message_language = detect_language(text)

    # --------------------------------------------------------
    # Convert text into model features
    # --------------------------------------------------------

    vec = vectorizer.transform([text])

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    prediction = clf.predict(vec)[0]

    # --------------------------------------------------------
    # Probability
    # --------------------------------------------------------

    if hasattr(clf, "predict_proba"):

        proba = clf.predict_proba(vec)[0]

        classes = list(clf.classes_)

    else:

        proba = None
        classes = list(clf.classes_)


    # ========================================================
    # FIND SCAM CLASS
    # ========================================================

    scam_idx = None

    # First try exact "scam"
    for i, cls in enumerate(classes):

        if str(cls).lower() == "scam":

            scam_idx = i
            break

    # Try common alternatives
    if scam_idx is None:

        for i, cls in enumerate(classes):

            cls_text = str(cls).lower()

            if cls_text in [
                "spam",
                "fraud",
                "malicious",
                "suspicious",
                "1"
            ]:

                scam_idx = i
                break

    # --------------------------------------------------------
    # If still not found, use prediction
    # --------------------------------------------------------

    if scam_idx is None:

        prediction_text = str(prediction).lower()

        if prediction_text in [
            "scam",
            "spam",
            "fraud",
            "malicious",
            "suspicious",
            "1"
        ]:

            scam_probability = 1.0

        else:

            scam_probability = 0.0

    else:

        scam_probability = float(
            proba[scam_idx]
        )


    # ========================================================
    # PERCENTAGE
    # ========================================================

    scam_percentage = round(
        scam_probability * 100,
        2
    )


    # ========================================================
    # RISK LEVEL
    # ========================================================

    if scam_probability >= 0.66:

        level = "high"

        verdict = "Likely Scam"

        verdict_en = "Likely Scam"

        verdict_hi = "संभावित स्कैम"

    elif scam_probability >= 0.35:

        level = "medium"

        verdict = "Suspicious"

        verdict_en = "Suspicious"

        verdict_hi = "संदिग्ध"

    else:

        level = "low"

        verdict = "Looks Safe"

        verdict_en = "Looks Safe"

        verdict_hi = "सुरक्षित लग रहा है"

    # Show the verdict text in the requested output language
    if lang == "hi":
        verdict = verdict_hi
    else:
        verdict = verdict_en


    # ========================================================
    # TACTICS
    # ========================================================

    matched_tactics = find_matched_tactics(text)

    tactics = []

    for item in matched_tactics:

        tactics.append({
            "tactic": item["tactic"],
            "phrases": item["phrases"]
        })


    # ========================================================
    # URGENCY
    # ========================================================

    text_lower = text.lower()

    urgency_matches = [
        keyword
        for keyword in URGENCY_KEYWORDS
        if keyword.lower() in text_lower
    ]


    # ========================================================
    # LINK ANALYSIS
    # ========================================================

    link_analysis = check_link_risk(text, lang=lang)


    # ========================================================
    # REASONS
    # ========================================================

    reasons = []

    if scam_probability >= 0.66:

        reasons.append(
            ML_REASON_HIGH_HI if lang == "hi" else (
                "The machine-learning model found strong "
                "patterns associated with scam messages."
            )
        )

    elif scam_probability >= 0.35:

        reasons.append(
            ML_REASON_MEDIUM_HI if lang == "hi" else (
                "The message contains patterns that may "
                "be associated with scam messages."
            )
        )


    # Tactic reasons

    for item in matched_tactics:

        tactic = item["tactic"]

        if tactic in TACTIC_INFO:

            key = "description_hi" if lang == "hi" else "description"

            reasons.append(
                TACTIC_INFO[tactic][key]
            )


    # Urgency reason

    if urgency_matches:

        reasons.append(
            URGENCY_REASON_HI if lang == "hi" else (
                "The message creates urgency or pressure "
                "to act quickly."
            )
        )


    # Link reasons

    if link_analysis["reasons"]:

        reasons.extend(
            link_analysis["reasons"]
        )


    # Remove duplicate reasons

    reasons = list(
        dict.fromkeys(reasons)
    )


    # Default reason

    if not reasons:

        reasons.append(
            DEFAULT_REASON_HI if lang == "hi" else (
                "No strong scam indicators were detected, "
                "but unexpected messages should still be verified."
            )
        )


    # ========================================================
    # SAFETY TIPS
    # ========================================================

    tips = []

    for item in matched_tactics:

        tactic = item["tactic"]

        if tactic in TACTIC_INFO:

            key = "tips_hi" if lang == "hi" else "tips"

            for tip in TACTIC_INFO[tactic][key]:

                if tip not in tips:

                    tips.append(tip)


    if link_analysis["has_link"]:

        tips.append(
            LINK_TIP_HI if lang == "hi" else (
                "Do not open the link until you verify "
                "the sender and website independently."
            )
        )


    general_tips = GENERAL_TIPS_HI if lang == "hi" else [

        "Never share OTPs, PINs, passwords, or banking details.",

        "Do not send money because of an unexpected message or call.",

        "Contact the organization using its official website or app.",

        "If someone creates pressure or threatens you, stop and verify first."
    ]


    for tip in general_tips:

        if tip not in tips:

            tips.append(tip)


    tips = tips[:6]


    # ========================================================
    # PRIMARY TACTIC
    # ========================================================

    if matched_tactics:

        primary_tactic_key = matched_tactics[0]["tactic"]

    else:

        primary_tactic_key = "Unknown / General"

    if lang == "hi":

        primary_tactic = HINDI_TACTIC_LABELS.get(
            primary_tactic_key,
            primary_tactic_key
        )

    else:

        primary_tactic = primary_tactic_key


    # ========================================================
    # RECOMMENDED ACTION
    # ========================================================

    if lang == "hi":

        action = ACTION_TEXT_HI[level]

    else:

        if level == "high":

            action = (
                "Do not click links, share personal information, "
                "send money, or follow instructions in this message. "
                "Verify the claim using an official source."
            )

        elif level == "medium":

            action = (
                "Be careful before responding. Do not share "
                "personal or financial information. Verify the "
                "message independently."
            )

        else:

            action = (
                "No strong scam indicators were detected. "
                "Still avoid sharing sensitive information and "
                "verify unexpected requests."
            )


    # ========================================================
    # SUSPICIOUS STATUS
    # ========================================================

    is_suspicious = (

        scam_probability >= 0.35

        or len(matched_tactics) > 0

        or len(urgency_matches) > 0

        or link_analysis["risk"] in [
            "medium",
            "high"
        ]
    )


    # ========================================================
    # DISCLAIMER (bilingual)
    # ========================================================

    if lang == "hi":

        disclaimer = (
            "यह टूल एक AI-आधारित जोखिम आकलन प्रदान करता है और इसे "
            "गारंटी के रूप में नहीं माना जाना चाहिए। महत्वपूर्ण दावों "
            "की पुष्टि हमेशा आधिकारिक स्रोतों से करें।"
        )

    else:

        disclaimer = (
            "This tool provides an AI-based risk assessment "
            "and should not be treated as a guarantee. "
            "Always verify important claims through official sources."
        )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "verdict": verdict,

        "verdict_en": verdict_en,

        "verdict_hi": verdict_hi,

        "level": level,

        "scam_probability": scam_percentage,

        "language": message_language,

        "output_lang": lang,

        "primary_tactic": primary_tactic,

        "tactics": tactics,

        "reasons": reasons,

        "tips": tips,

        "action": action,

        "link_analysis": link_analysis,

        "is_suspicious": is_suspicious,

        "disclaimer": disclaimer
    }
    # ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# ============================================================
# TEXT CHECK API
# ============================================================

@app.route("/check", methods=["POST"])
def check():

    try:

        # ----------------------------------------------------
        # Get JSON
        # ----------------------------------------------------

        data = request.get_json(
            silent=True
        ) or {}


        # ----------------------------------------------------
        # Get text
        # ----------------------------------------------------

        text = (
            data.get("text") or ""
        ).strip()


        # ----------------------------------------------------
        # Get requested output language
        # ----------------------------------------------------

        lang = (
            data.get("lang") or "en"
        ).strip().lower()

        if lang not in ("en", "hi"):
            lang = "en"


        # ----------------------------------------------------
        # Empty input
        # ----------------------------------------------------

        if not text:

            error_msg = (
                "कृपया जांचने के लिए एक संदेश, कॉल का विवरण, "
                "या लिंक दर्ज करें।"
                if lang == "hi" else
                "Please enter a message, call description, "
                "or link to check."
            )

            return jsonify({
                "error": error_msg
            }), 400


        # ----------------------------------------------------
        # Limit text
        # ----------------------------------------------------

        text = text[:3000]


        # ----------------------------------------------------
        # Classify
        # ----------------------------------------------------

        result = classify(text, lang=lang)


        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------

        return jsonify(result)


    except Exception as e:

        print("\n========================================")
        print("CLASSIFICATION ERROR")
        print("========================================")
        print("Error type:", type(e).__name__)
        print("Error:", str(e))
        print("========================================\n")


        return jsonify({

            "error": (
                "Classification failed: "
                + str(e)
            ),

            "error_type": type(e).__name__

        }), 500
        # ============================================================
# CALL SCAM CHECKER API
# ============================================================

@app.route("/check-call", methods=["POST"])
def check_call():

    try:

        # ----------------------------------------------------
        # Get JSON
        # ----------------------------------------------------

        data = request.get_json(
            silent=True
        ) or {}


        # ----------------------------------------------------
        # Get selected checkboxes + optional notes
        # ----------------------------------------------------

        selected_options = data.get("options") or []

        notes = (
            data.get("notes") or ""
        ).strip()

        lang = (
            data.get("lang") or "en"
        ).strip().lower()

        if lang not in ("en", "hi"):
            lang = "en"


        if not isinstance(selected_options, list):

            selected_options = []


        # ----------------------------------------------------
        # Build a synthetic description of the call from the
        # selected checkboxes, so the existing classify()
        # pipeline (ML model + tactic keywords + urgency
        # detection) can analyze it exactly like a pasted
        # message. Always build this in ENGLISH regardless of
        # output language, since the ML model and keyword
        # matching were trained/written primarily in English.
        # ----------------------------------------------------

        sentences = [
            CALL_OPTION_PHRASES[opt]
            for opt in selected_options
            if opt in CALL_OPTION_PHRASES
        ]

        combined_text = " ".join(sentences)


        if notes:

            combined_text = (
                combined_text + " " + notes
            ).strip()


        # ----------------------------------------------------
        # Empty input
        # ----------------------------------------------------

        if not combined_text:

            error_msg = (
                "कृपया कम से कम एक विकल्प चुनें या बताएं कि "
                "कॉल में क्या हुआ था।"
                if lang == "hi" else
                "Please select at least one option or "
                "describe what happened on the call."
            )

            return jsonify({
                "error": error_msg
            }), 400


        # ----------------------------------------------------
        # Limit text
        # ----------------------------------------------------

        combined_text = combined_text[:3000]


        # ----------------------------------------------------
        # Classify
        # ----------------------------------------------------

        result = classify(combined_text, lang=lang)


        # ----------------------------------------------------
        # Include what was selected, so the frontend can
        # show it back to the user, in the requested language
        # ----------------------------------------------------

        label_map = CALL_OPTION_LABELS_HI if lang == "hi" else CALL_OPTION_LABELS

        result["selected_options"] = [
            label_map[opt]
            for opt in selected_options
            if opt in label_map
        ]

        result["call_notes"] = notes


        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------

        return jsonify(result)


    except Exception as e:

        print("\n========================================")
        print("CALL CHECK ERROR")
        print("========================================")
        print("Error type:", type(e).__name__)
        print("Error:", str(e))
        print("========================================\n")


        return jsonify({

            "error": (
                "Call check failed: "
                + str(e)
            ),

            "error_type": type(e).__name__

        }), 500
        # ============================================================
# SCREENSHOT SCANNER API
# ============================================================

@app.route("/scan-image", methods=["POST"])
def scan_image():

    try:

        # ----------------------------------------------------
        # Get requested output language (form field, since
        # this endpoint receives multipart/form-data, not JSON)
        # ----------------------------------------------------

        lang = (
            request.form.get("lang") or "en"
        ).strip().lower()

        if lang not in ("en", "hi"):
            lang = "en"


        # ----------------------------------------------------
        # Check image
        # ----------------------------------------------------

        if "image" not in request.files:

            error_msg = (
                "कृपया एक स्क्रीनशॉट अपलोड करें।"
                if lang == "hi" else
                "Please upload a screenshot."
            )

            return jsonify({
                "error": error_msg
            }), 400


        image = request.files["image"]


        # ----------------------------------------------------
        # Check filename
        # ----------------------------------------------------

        if image.filename == "":

            error_msg = (
                "कोई छवि चयनित नहीं की गई।"
                if lang == "hi" else
                "No image was selected."
            )

            return jsonify({
                "error": error_msg
            }), 400


        # ----------------------------------------------------
        # Allowed formats
        # ----------------------------------------------------

        allowed_extensions = {
            "png",
            "jpg",
            "jpeg",
            "webp"
        }


        filename = image.filename.lower()


        if "." not in filename:

            error_msg = (
                "कृपया PNG, JPG, JPEG या WEBP छवि अपलोड करें।"
                if lang == "hi" else
                "Please upload a PNG, JPG, JPEG, "
                "or WEBP image."
            )

            return jsonify({
                "error": error_msg
            }), 400


        extension = filename.rsplit(
            ".",
            1
        )[1]


        if extension not in allowed_extensions:

            error_msg = (
                "असमर्थित छवि प्रकार। कृपया PNG, JPG, JPEG "
                "या WEBP का उपयोग करें।"
                if lang == "hi" else
                "Unsupported image type. "
                "Please use PNG, JPG, JPEG, or WEBP."
            )

            return jsonify({
                "error": error_msg
            }), 400


        # ----------------------------------------------------
        # OCR
        # ----------------------------------------------------

        extracted_text = extract_text_from_image(
            image
        )


        # ----------------------------------------------------
        # Check OCR result
        # ----------------------------------------------------

        if not extracted_text:

            error_msg = (
                "इस छवि में कोई पठनीय पाठ नहीं मिला।"
                if lang == "hi" else
                "I could not detect readable text "
                "in this image."
            )

            return jsonify({
                "error": error_msg
            }), 400


        # ----------------------------------------------------
        # Limit OCR text
        # ----------------------------------------------------

        extracted_text = extracted_text[:3000]


        # ----------------------------------------------------
        # Classify extracted text
        # ----------------------------------------------------

        result = classify(
            extracted_text,
            lang=lang
        )


        # ----------------------------------------------------
        # Add OCR text
        # ----------------------------------------------------

        result["extracted_text"] = extracted_text


        return jsonify(result)


    except Exception as e:

        print("\n========================================")
        print("SCREENSHOT SCANNING ERROR")
        print("========================================")
        print("Error type:", type(e).__name__)
        print("Error:", str(e))
        print("========================================\n")


        return jsonify({

            "error": (
                "Screenshot scanning failed: "
                + str(e)
            ),

            "error_type": type(e).__name__

        }), 500
        # ============================================================
# RUN FLASK APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )