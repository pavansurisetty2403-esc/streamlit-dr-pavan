# ============================
# BLOCK 1 — IMPORTS & PATHS
# ============================
import os
import cv2
import torch
import numpy as np
from PIL import Image
from torchvision import transforms, models
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

DEVICE = "cuda" if torch.cuda.is_available() else \
         "mps" if torch.backends.mps.is_available() else "cpu"
print("Using device:", DEVICE)

# --- MODEL CHECKPOINT ---
MODEL_PATH = None

# =======================================
# BLOCK 2 — LOAD MODEL FROM CHECKPOINT
# =======================================

def load_model(model_path):
    state_dict = torch.load(model_path, map_location="cpu")

    model = models.efficientnet_b3(weights=None)
    model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, 5)

    model.load_state_dict(state_dict)
    model.eval()

    # class names are fixed for your problem
    class_names = [
        "No DR",
        "Mild",
        "Moderate",
        "Severe",
        "Proliferative DR"
    ]

    return model, class_names

# =======================================
# BLOCK 3 — FUNDUS PREPROCESSING (YOUR CODE)
# =======================================

def preprocess_fundus(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (512, 512))

    # Crop borders
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, th = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    x,y,w,h = cv2.boundingRect(th)
    img = img[y:y+h, x:x+w]

    # CLAHE
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    l,a,b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    merged = cv2.merge((cl,a,b))
    img = cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)

    img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
    return img


# =======================================
# BLOCK 4 — QUALITY ANALYSIS + ENHANCEMENT
# =======================================

def analyze_quality(img):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    brightness = np.mean(gray)
    contrast = np.std(gray)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    return brightness, contrast, sharpness

def apply_clahe(img):
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    l,a,b = cv2.split(lab)
    cl = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8)).apply(l)
    merged = cv2.merge((cl,a,b))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)

def apply_gabor(img):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    k = cv2.getGaborKernel((21,21), 8, np.pi/4, 10, 0.5)
    filtered = cv2.filter2D(gray, cv2.CV_8UC3, k)
    filtered = cv2.merge([filtered]*3)
    return cv2.addWeighted(img, 0.7, filtered, 0.3, 0)

def deep_enhance(img):
    b,c,s = analyze_quality(img)
    out = img.copy()

    if c < 35: out = apply_clahe(out)
    if s < 100: out = apply_gabor(out)

    return out

# =======================================
# BLOCK 5 — FINAL DL PREPROCESSING
# =======================================

transform_dl = transforms.Compose([
    transforms.Resize((380,380)),
    transforms.ToTensor(),
])

def to_tensor_image(img):
    pil = Image.fromarray(img)
    return transform_dl(pil).unsqueeze(0).to(DEVICE)

# =======================================
# BLOCK 6 — RUN MODEL + EXPLANATION
# =======================================

def predict(model, tensor, class_names):
    with torch.no_grad():
        out = model(tensor)
        prob = torch.softmax(out, dim=1)
        cls = torch.argmax(prob).item()
        return cls, prob[0][cls].item()

DR_EXPLANATION = {
    0: "Stage 0 – No Diabetic Retinopathy:\n"
        "There is currently no visible damage to the retina. This means your diabetes has not yet affected the blood vessels of your eye. "
        "Vision is usually normal at this stage. However, high blood sugar can still silently cause damage, so prevention is key."
        "\n\nSymptoms to watch:\n"
        "• Blurry vision\n"
        "• Floating spots (floaters)\n"
        "• Difficulty seeing at night\n"
        "• Sudden vision changes (seek help immediately)",
    1: "Stage 1 – Mild Non-Proliferative DR:\n"
        "Small bulges called microaneurysms appear in the retinal blood vessels. These may leak tiny amounts of fluid. "
        "Usually there is no major vision loss, but it is an early warning sign."
        "\n\nSymptoms to watch:\n"
        "• Mild blurry vision\n"
        "• Occasional eye strain\n"
        "• Spots or floaters may appear",
    2: "Stage 2 – Moderate Non-Proliferative DR:\n"
        "More blood vessels become blocked, and fluid leakage can increase, causing swelling in the macula (macular edema). "
        "Vision may start to worsen if untreated."
        "\n\nSymptoms to watch:\n"
        "• Noticeable blurriness\n"
        "• Difficulty reading or focusing\n"
        "• More frequent floaters\n"
        "• Mild distortion of objects",
    3: "Stage 3 – Severe Non-Proliferative DR:\n"
        "Large areas of the retina are not getting enough blood (ischemia). The eye may begin to grow abnormal vessels, "
        "a dangerous sign that proliferative DR may soon occur."
        "\n\nSymptoms to watch:\n"
        "• Significant blurry vision\n"
        "• Large floaters\n"
        "• Dark spots in central or peripheral vision\n"
        "• Sudden vision drops (red alert!)",
    4: "Stage 4 – Proliferative Diabetic Retinopathy (PDR):\n"
        "New fragile blood vessels grow on the retina and optic nerve. These can bleed easily and cause major vision loss. "
        "Scar tissue may pull on the retina and cause retinal detachment."
        "\n\nSymptoms to watch:\n"
        "• Severe floaters (blood spots)\n"
        "• Sudden vision blackout or haze\n"
        "• Dark curtains over vision (retinal detachment warning)\n"
        "• Eye pain or pressure"
}

DR_ADVICE = {
    0: "Precautions:\n"
        "• Maintain ideal blood sugar (80–130 mg/dL fasting).\n"
        "• Monitor HbA1c every 3 months — target ≤ 7%.\n"
        "• Keep blood pressure and cholesterol normal.\n\n"
        "Diet – What to Eat:\n"
        "• High-fiber foods (vegetables, whole grains, legumes).\n"
        "• Lean proteins (dal, chicken, fish, paneer).\n"
        "• Low-GI fruits (apple, orange, guava, berries).\n"
        "• Omega-3 foods (flaxseed, walnuts, fish).\n\n"
        "Avoid:\n"
        "• Sugary foods, sweets, refined flour, soft drinks.\n"
        "• Excess rice/chapati portions.\n"
        "• Trans-fat and deep-fried foods.\n\n"
        "Physical Activity:\n"
        "• 30–45 min daily walking.\n"
        "• Yoga and light exercise.\n\n"
        "Eye-care:\n"
        "• Comprehensive eye exam once a year.",
    1: "Precautions:\n"
        "• Keep HbA1c ≤ 7% to stop progression.\n"
        "• Monitor sugars more frequently.\n"
        "• Avoid blood pressure spikes.\n\n"
        "Diet – What to Eat:\n"
        "• Same as Stage 0 but stricter on sugar and salt.\n"
        "• Add green leafy vegetables daily.\n\n"
        "Avoid:\n"
        "• White rice (switch to brown rice or millets).\n"
        "• Bakery items, chips, sweets, sugary tea/coffee.\n\n"
        "Physical Activity:\n"
        "• 45–60 minutes walking.\n"
        "• Strength training 2–3 times/week.\n\n"
        "Eye-care:\n"
        "• Follow-up every 6–12 months.",
    2: "Precautions:\n"
        "• Very strict sugar control (HbA1c target 6.5–7%).\n"
        "• Control blood pressure (≤130/80).\n"
        "• Avoid smoking and alcohol.\n\n"
        "Diet – What to Eat:\n"
        "• Low-salt, low-oil diet.\n"
        "• Add antioxidant foods: carrots, spinach, beetroot.\n"
        "• Add turmeric + black pepper daily.\n\n"
        "Avoid:\n"
        "• Red meat, excess salt, pickles.\n"
        "• Fruit juices (eat whole fruits instead).\n\n"
        "Physical Activity:\n"
        "• 45–60 minutes moderate activity.\n"
        "• Avoid heavy lifting to prevent retinal stress.\n\n"
        "Eye-care:\n"
        "• Eye exam every 3–6 months.\n"
        "• OCT scan if macular swelling suspected.",
    3: "Precautions:\n"
        "• Intensive sugar control (HbA1c around 6.5%).\n"
        "• Absolutely no smoking.\n"
        "• Control BP, cholesterol aggressively.\n"
        "• Avoid anything causing strain or high pressure.\n\n"
        "Diet – What to Eat:\n"
        "• Anti-inflammatory diet: vegetables, berries, nuts.\n"
        "• Very low oil (2–3 teaspoons/day).\n"
        "• High-quality protein: dal, fish, tofu.\n\n"
        "Avoid:\n"
        "• Heavy exercise, weight lifting.\n"
        "• All sugary foods.\n"
        "• High-salt, fried food.\n\n"
        "Physical Activity:\n"
        "• Light walking only.\n"
        "• Avoid jumping, running, or straining.\n\n"
        "Eye-care:\n"
        "• Urgent retina consultation.\n"
        "• Laser treatment may be needed.",
    4: "Precautions:\n"
        "• Emergency stage — must see retina specialist immediately.\n"
        "• Avoid all heavy physical strain.\n"
        "• Avoid bending forward repeatedly (can increase bleeding).\n"
        "• Strict sugar, BP, and cholesterol control.\n\n"
        "Diet – What to Eat:\n"
        "• High-antioxidant foods.\n"
        "• Very low sodium.\n"
        "• Omega-3 rich foods.\n"
        "• Hydrate well.\n\n"
        "Avoid:\n"
        "• Any form of smoking/alcohol.\n"
        "• High sugar, junk food, red meat.\n"
        "• Heavy exercise, lifting weights, running.\n"
        "• High caffeine (coffee/energy drinks).\n\n"
        "Physical Activity:\n"
        "• Only slow walking.\n"
        "• Avoid sudden movements.\n"
        "• No yoga positions with head down.\n\n"
        "Eye-care:\n"
        "• Immediate retina treatment.\n"
        "• Anti-VEGF injections or surgery may be required.\n"
        "• Frequent monitoring every 1–2 months."
}
DR_RISK_FACTORS = {
    0: "• Long-standing diabetes (>5–10 years)\n"
       "• Poor sugar control in the past (high HbA1c)\n"
       "• High blood pressure or cholesterol\n"
       "• Obesity or sedentary lifestyle\n"
       "• Family history of diabetic complications\n"
       "• Smoking and alcohol use\n"
       "• Kidney problems (diabetic nephropathy)\n"
       "• Irregular follow-up exams",

    1: "• Chronic hyperglycemia (high HbA1c)\n"
       "• Hypertension and dyslipidemia\n"
       "• Overweight, obesity, lack of exercise\n"
       "• Smoking, alcohol consumption\n"
       "• Insulin resistance or uncontrolled diabetes\n"
       "• Anemia (reduced oxygen supply to retina)\n"
       "• Pregnancy (increases DR progression risk)",

    2: "• Poorly controlled diabetes (HbA1c > 7.5%)\n"
       "• High blood pressure (>140/90)\n"
       "• High cholesterol (LDL > 100)\n"
       "• Moderate to severe kidney disease\n"
       "• Long duration of diabetes (>10 years)\n"
       "• Smoking, alcohol\n"
       "• Previous mild DR progression",

    3: "• Advanced retinal ischemia due to long-term diabetes\n"
       "• Chronic high HbA1c (>8%)\n"
       "• Severe hypertension\n"
       "• High triglycerides and LDL\n"
       "• Smoking (major risk)\n"
       "• Fluid retention and kidney issues\n"
       "• Pregnancy (rapid worsening possible)",

    4: "• Very long-standing diabetes (>15–20 years)\n"
       "• Persistent uncontrolled sugars (HbA1c > 8%)\n"
       "• Severe hypertension or heart disease\n"
       "• Chronic kidney disease or dialysis\n"
       "• Strong smoking history\n"
       "• Severe anemia\n"
       "• Previous severe DR or macular edema"
}
DR_URGENCY_LEVEL = {
    0: "GREEN – No immediate danger. Routine monitoring required.",
    1: "GREEN–YELLOW – Early changes. Monitor closely every 6–12 months.",
    2: "YELLOW – Disease progressing. Needs ophthalmology supervision.",
    3: "ORANGE – High risk. Urgent retina specialist review Recommended.",
    4: "RED – Emergency. Immediate retina specialist intervention required."
}
DR_COMPLICATIONS = {
    0: "• Risk of future DR if sugars remain uncontrolled\n"
       "• Early macular changes possible but not present",

    1: "• Increase in microaneurysms\n"
       "• Early macular edema\n"
       "• Gradual progression to moderate DR",

    2: "• Diabetic macular edema (DME)\n"
       "• Retinal capillary non-perfusion\n"
       "• Higher chance of severe DR",

    3: "• Large ischemic retinal areas\n"
       "• Pre-proliferative neovascularization\n"
       "• High risk of progression to PDR\n"
       "• Possible macular edema",

    4: "• Vitreous hemorrhage (bleeding inside eye)\n"
       "• Tractional retinal detachment\n"
       "• Neovascular glaucoma\n"
       "• Severe vision loss or blindness"
}
DR_RED_FLAGS = {
    0: "• Sudden blurry vision\n• Flashing lights\n• Increasing floaters",

    1: "• Increase in floaters\n• Patchy blurred vision\n• Night vision difficulty",

    2: "• Central blurry or wavy vision\n• Sudden drop in clarity\n• Dark spots appearing",

    3: "• Many floaters or cobweb patterns\n• Shadow or curtain over vision\n• Eye pain or severe vision change",

    4: "• Sudden severe vision loss\n• Dark curtain falling over the eye\n• Large floaters (blood)\n• Severe pain or pressure"
}
DR_RECOMMENDED_TESTS = {
    0: "• Comprehensive dilated eye exam\n• Visual acuity test\n• Intraocular pressure check",

    1: "• Fundus photography\n• Dilated exam\n• OCT (if symptoms present)",

    2: "• OCT (macular edema assessment)\n• Fundus fluorescein angiography (FFA)\n• OCTA for blood flow mapping",

    3: "• OCT + OCTA\n• FFA (retinal ischemia mapping)\n• Ultrasound B-scan if media opacity present",

    4: "• OCT for macula status\n• FFA for neovascularization\n• Ultrasound B-scan for hemorrhage\n• Pre-surgical evaluation tests"
}
DR_FOLLOW_UP = {
    0: "Every 12 months",
    1: "Every 6–12 months",
    2: "Every 3–6 months",
    3: "Every 1–3 months",
    4: "Immediately + monthly monitoring"
}
DR_TREATMENT_OPTIONS = {
    0: "• No treatment needed\n• Focus on sugar, BP, and cholesterol control",

    1: "• No invasive treatment needed\n• Control systemic factors\n• Consider early laser only if macular edema begins",

    2: "• Anti-VEGF injections if macular edema present\n• Focal/grid laser therapy\n• BP and sugar optimization",

    3: "• Panretinal photocoagulation (PRP) laser\n• Anti-VEGF therapy\n• Combination therapy based on specialist review",

    4: "• Anti-VEGF injections (for neovascularization)\n• PRP laser\n• Vitrectomy surgery for bleeding or detachment\n"
       "• Immediate retina specialist management"
}
DR_VISION_PROTECTION = {
    0: "• Wear UV-protection glasses\n• Control diabetes tightly\n• Avoid prolonged screen strain",

    1: "• Same as stage 0 + reduce salt and sugar intake\n• Avoid smoking completely",

    2: "• Very strict sugar and BP control\n• Avoid heavy lifting\n• Maintain hydration",

    3: "• Avoid all strenuous activity\n• No forward bending or jumping\n• Follow retina precautions",

    4: "• Avoid sudden movements\n• No lifting weights\n• No yoga inversions\n• Protect eye from trauma"
}
DR_LIFESTYLE_ROUTINE = {
    0: "• 30–45 min daily walk\n• Light stretching\n• Avoid overeating carbohydrates\n• Sleep 7–8 hours",

    1: "• 45–60 min walk or cycling\n• Strength training 2–3 times/week\n• Reduce salt and sugar\n• Regular glucose monitoring",

    2: "• Moderate walking 45–60 min\n• No heavy lifting\n• Stress reduction (yoga, breathing)\n• Strict medication adherence",

    3: "• ONLY light walking\n• Avoid any strain\n• Medication timing discipline\n• Monitor sugars 2–3 times/day",

    4: "• Slow short walks only\n• Avoid bending forward\n• No physical stress\n• Follow emergency precautions"
}
DR_DIET_PLAN = {
    0: "• 50% vegetables, 25% protein, 25% whole grains\n"
       "• Low-GI fruits (apple, guava, orange)\n"
       "• Avoid sugary drinks and sweets",

    1: "• More fiber and green leafy vegetables\n• Reduce salt\n• Avoid bakery items, fried food\n"
       "• Prefer brown rice/millets",

    2: "• Anti-inflammatory diet (turmeric, ginger, spinach)\n• Reduce oil to 2–3 tsp/day\n"
       "• Avoid juices and refined sugar",

    3: "• Very low oil and salt\n• High antioxidants (berries, carrots)\n• No fried foods, no red meat\n"
       "• Hydrate 2–3 liters/day",

    4: "• Very strict low-sodium diet\n• High omega-3 foods\n• Small, frequent meals\n"
       "• No caffeine, alcohol, or sugar"
}
DR_URGENCY_LEVEL = {
    0: "🟢 Green — No immediate danger. Routine monitoring required.",
    1: "🟡 Yellow — Early changes. Monitor every 6–12 months.",
    2: "🟠 Orange — Progressing disease. Needs close monitoring.",
    3: "🟠 Orange-Red — High risk. Urgent retina review advised.",
    4: "🔴 Red — Emergency. Immediate retina specialist care needed."
}


# =======================================
# BLOCK 7 — PDF GENERATOR (FINAL CLEAN VERSION)
# =======================================

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib import colors

def bullet_to_list(text):
    """Convert bullet points into a list for table formatting."""
    lines = [line.strip("• ").strip() for line in text.split("\n") if line.strip()]
    return [[line] for line in lines]


def generate_pdf(original_path, processed_path, cls, prob, pdf_path):
    styles = getSampleStyleSheet()
    import io
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)


    story = []

    story.append(Paragraph("<b>Diabetic Retinopathy Report</b>", styles['Title']))
    story.append(Spacer(1, 12))

    # --- ORIGINAL IMAGE ---
    story.append(Paragraph("<b>Original Fundus Image</b>", styles['Heading2']))
    story.append(RLImage(original_path, width=4*inch, height=4*inch))
    story.append(Spacer(1, 12))

    # --- PROCESSED IMAGE ---
    story.append(Paragraph("<b>Processed Image</b>", styles['Heading2']))
    story.append(RLImage(processed_path, width=4*inch, height=4*inch))
    story.append(Spacer(1, 12))

    # --- RESULT ---
    story.append(Paragraph(f"<b>Predicted DR Stage:</b> {cls}", styles['Heading2']))
    story.append(Paragraph(f"<b>Confidence:</b> {prob*100:.2f}%", styles['Normal']))
    story.append(Spacer(1, 12))

    # --- EXPLANATION ---
    story.append(Paragraph("<b>Explanation:</b>", styles['Heading2']))
    story.append(Paragraph(DR_EXPLANATION[cls], styles['Normal']))
    story.append(Spacer(1, 12))

    # --- ADVICE ---
    story.append(Paragraph("<b>Patient Advice:</b>", styles['Heading2']))
    story.append(Paragraph(DR_ADVICE[cls], styles['Normal']))
    story.append(Spacer(1, 12))

    # ========================================================
    # NEW SECTIONS (COLOR CODED + TABLE FORMATTED)
    # ========================================================

    # ---------- URGENCY WITH COLOR ----------
    color = (
        colors.green if cls == 0 else
        colors.yellow if cls == 1 else
        colors.orange if cls in [2, 3] else
        colors.red
    )

    story.append(Paragraph("<b>Urgency Level:</b>", styles['Heading2']))

    urgency_table = Table([[DR_URGENCY_LEVEL[cls]]], colWidths=[450])
    urgency_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), color),
        ('TEXTCOLOR', (0,0), (0,0), colors.black),
        ('ALIGN', (0,0), (0,0), 'CENTER'),
        ('FONTSIZE', (0,0), (0,0), 12),
        ('BOX', (0,0), (0,0), 1, colors.black),
    ]))
    story.append(urgency_table)
    story.append(Spacer(1, 12))

    # ---------- RISK FACTORS TABLE ----------
    story.append(Paragraph("<b>Risk Factors:</b>", styles['Heading2']))

    risk_list = bullet_to_list(DR_RISK_FACTORS[cls])
    risk_table = Table(risk_list, colWidths=[450])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke),
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    story.append(risk_table)
    story.append(Spacer(1, 12))

    # ---------- TESTS TABLE ----------
    story.append(Paragraph("<b>Recommended Tests:</b>", styles['Heading2']))

    tests_list = bullet_to_list(DR_RECOMMENDED_TESTS[cls])
    tests_table = Table(tests_list, colWidths=[450])
    tests_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.lightblue),
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.darkblue),
    ]))
    story.append(tests_table)
    story.append(Spacer(1, 12))

    # ---------- REMAINING TEXT SECTIONS ----------
    sections = [
        ("Possible Complications", DR_COMPLICATIONS),
        ("Emergency Symptoms (Red Flags)", DR_RED_FLAGS),
        ("Follow-up Frequency", DR_FOLLOW_UP),
        ("Treatment Options", DR_TREATMENT_OPTIONS),
        ("Vision Protection Tips", DR_VISION_PROTECTION),
        ("Daily Lifestyle Routine", DR_LIFESTYLE_ROUTINE),
        ("Diet Plan Overview", DR_DIET_PLAN),
    ]

    for title, dictionary in sections:
        story.append(Paragraph(f"<b>{title}:</b>", styles['Heading2']))
        story.append(Paragraph(dictionary[cls], styles['Normal']))
        story.append(Spacer(1, 12))

    # ========================================================
    # END BLOCK
    # ========================================================

    doc.build(story)
    buffer.seek(0)
    return buffer.read()



# =======================================
# BLOCK 8 — MAIN RUN PIPELINE
# =======================================

def run_pipeline(image_bytes, model_path):
    print("Loading model...")
    model, class_names = load_model(model_path)

    print("Reading image...")
    file_bytes = np.asarray(bytearray(image_bytes), dtype=np.uint8)
    orig = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    orig_rgb = cv2.cvtColor(orig, cv2.COLOR_BGR2RGB)

    print("Step 1: Fundus preprocessing...")
    fundus = preprocess_fundus(orig)

    print("Step 2: Deep enhancement...")
    enhanced = deep_enhance(fundus)

    print("Converting to tensor...")
    tensor = to_tensor_image(enhanced)

    print("Predicting...")
    cls, prob = predict(model, tensor, class_names)

    # save images (for PDF)
    orig_save = "temp_original.png"
    proc_save = "temp_processed.png"
    cv2.imwrite(orig_save, cv2.cvtColor(orig_rgb, cv2.COLOR_RGB2BGR))
    cv2.imwrite(proc_save, cv2.cvtColor(enhanced, cv2.COLOR_RGB2BGR))

    print("Generating PDF...")
    pdf_bytes = generate_pdf(orig_save, proc_save, cls, prob, None)
    return cls, prob, pdf_bytes

