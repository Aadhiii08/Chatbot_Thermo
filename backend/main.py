# backend/main.py

from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import shutil
import os
from datetime import datetime
import phonenumbers
from email_validator import validate_email, EmailNotValidError
import sys
import re
import traceback
from dotenv import load_dotenv

load_dotenv()

# Internal imports
# from excel_handler import load_service_data
# from country_data import countries
from pdf_writer import create_sales_pdf
from utils import send_email_with_attachment

app = FastAPI(title="DM Thermoformer AI Agent", version="4.0.0")

@app.get("/")
async def health_check():
    return {"status": "awake"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- LOAD DATA ---
# (Keeping this for now validation if needed, though mostly using static lists for the new flow)
# services_data, main_services, sub_categories_others, app_sub_category_definitions = load_service_data()

BACK_COMMAND = "__GO_BACK__"
SALES_TEAM_EMAIL = "aadhii0803@gmail.com" # Updated per context, or keep if verified

# --- MODELS ---
class ChatRequest(BaseModel):
    stage: str
    user_details: Dict[str, Any]
    user_input: str | None = None

class ChatResponse(BaseModel):
    next_stage: str
    bot_message: str | None = None # Optional now, prefer bot_messages
    bot_messages: List[str] | None = None # Support for multiple messages
    user_details: Dict[str, Any]
    ui_elements: Dict[str, Any] | None = None

class ProposalRequest(BaseModel):
    user_details: Dict[str, Any]
    category: str | None = None

# --- UTILITIES ---
def extract_email(text: str):
    match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
    return match.group(0) if match else None

def sanitize_filename(name):
    return "".join([c if c.isalnum() else "_" for c in name])

# --- BACKGROUND TASK ---
def process_lead_and_send_email(user_details: Dict[str, Any]):
    print(f"[*] Starting process_lead_and_send_email for {user_details.get('email')}")
    try:
        # 1. Prepare Data
        user_email = user_details.get('email')
        if not user_email: 
            print("[!] No email found in user_details")
            return

        # 2. Generate Sales PDF
        output_dir = "inquiries"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        company_slug = sanitize_filename(user_details.get('company', 'Client'))
        
        pdf_filename = f"{company_slug}_Sales_Inquiry_{timestamp}.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)
        
        create_sales_pdf(user_details, pdf_path)
        
        # Prepare attachments
        attachments = [pdf_path]
        drawing_file = user_details.get('drawing_file')
        if drawing_file:
            drawing_path = os.path.join(UPLOAD_DIR, drawing_file)
            if os.path.exists(drawing_path):
                attachments.append(drawing_path)
        
        # 3. Email Client (Acknowledgement)
        send_email_with_attachment(
            receiver_email=user_email,
            subject=f"Inquiry Received: {user_details.get('division', 'Custom Plastic Solution')} - DM Thermoformer",
            body=f"""Hi {user_details.get('contact_person', user_details.get('name', 'Client'))},

Thank you for contacting DM Thermoformer.

We have received your inquiry for a {user_details.get('division', 'custom plastic solution')}. Our technical sales team is reviewing your requirements and will contact you within 24 hours with the next steps.

Best Regards,
DM Thermoformer Sales Team"""
        )

        # 4. Email Sales Team (Lead)
        send_email_with_attachment(
            receiver_email=SALES_TEAM_EMAIL,
            subject=f"🚀 NEW SALES LEAD: {user_details.get('company', 'Unknown')} - {user_details.get('division', 'Custom Plastic')}",
            body=f"""New Sales Inquiry Received.

Client Contact: {user_details.get('contact_person')}
Company: {user_details.get('company')}
Division: {user_details.get('division')}
Material: {user_details.get('material')}
Quantity: {user_details.get('quantity')}
Email: {user_email}
Phone: {user_details.get('phone')}

See full technical summary attached in the PDF.""",
            attachment_paths=attachments
        )
        
    except Exception as e:
        print(f"[!] Background Task Error: {e}")
        traceback.print_exc()

# --- REMOVED PROPOSAL TASK ---
# generate_and_send_full_proposal removed as per request

# --- BACK LOGIC ---
def go_back(current_stage, user_details):
    # Simple history pop
    if not user_details.get('stage_history'):
        return None
    prev = user_details['stage_history'].pop()
    
    # Map stage to restart message/logic if needed, or just return basic prompt
    # For now, we will rely on validity checks in main loop to re-render the proper prompt for 'prev'
    return prev

# --- UPLOAD ENDPOINT ---
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload_drawing")
async def upload_drawing(resume: UploadFile = File(...), email: Optional[str] = None):
    try:
        file_path = os.path.join(UPLOAD_DIR, resume.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)
        return {"filename": resume.filename, "message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- MAIN CHAT HANDLER ---
@app.post("/chat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest, background_tasks: BackgroundTasks):
    stage = request.stage
    user_details = request.user_details
    user_input = request.user_input.strip() if request.user_input else ""
    user_input_lower = user_input.lower()
    
    # Initialize history
    if 'stage_history' not in user_details: user_details['stage_history'] = []

    # Global Commands
    if user_input_lower in ["new proposal", "restart", "reset"]:
        user_details = {'stage_history': []}
        return ChatResponse(
            next_stage="get_name",
            bot_messages=[
                "Hello 👋 Welcome to **DM Thermoformer & RA Vacform Industries**! We’re glad to assist you with custom plastic solutions.\n\nMay I kindly know your **Name**?"
            ],
            user_details=user_details
        )
    
    # Back Command
    if user_input == BACK_COMMAND:
        prev_stage = go_back(stage, user_details)
        if prev_stage:
            stage = prev_stage
            # We "fall through" to the if/elif blocks below to re-render the prompt for 'prev_stage'
            # But we need to avoid processing 'user_input' as an answer for that stage.
            # So we set a flag or just return immediately with the prompt for that stage.
            # Simpler approach: Recursive call with empty input? No, standard flow is better.
            # We'll just set the prompt for the reverted stage.
            pass
        else:
             return ChatResponse(next_stage="get_name", bot_messages=["Welcome to **DM Thermoformer & RA Vacform Industries**! 👋\n\nWhat is your **Name**?"], user_details={'stage_history': []})

    # --- FLOW LOGIC ---

    # --- FLOW LOGIC ---

    # --- FLOW LOGIC ---

    # 1. WELCOME -> GET NAME
    if stage == "get_name":
        if not user_input: 
             return ChatResponse(
                 next_stage="get_name", 
                 bot_messages=[
                     "Hello 👋 Welcome to **DM Thermoformer & RA Vacform Industries**! We’re glad to assist you with custom plastic solutions.\n\nMay I kindly know your **Name**?"
                 ],
                 user_details=user_details
             )
        
        user_details['name'] = user_input
        user_details['stage_history'].append("get_name")
        
        division_msg = (
            "We operate through two specialized divisions. Please choose what matches your requirement:\n\n"
            "1️⃣ **DM Thermoformer**\n"
            "Custom thermoformed rigid plastic packaging solutions for product handling, protection, and presentation.\n\n"
            "2️⃣ **RA Vacform Industries**\n"
            "Manufacturing of thick vacuum formed plastic parts and housings for industrial and equipment applications."
        )
        
        return ChatResponse(
            next_stage="get_division",
            bot_messages=[
                f"Nice to meet you, **{user_input}**.",
                division_msg
            ],
            user_details=user_details,
            ui_elements={"type": "buttons", "display_style": "cards", "options": ["DM Thermoformer", "RA Vacform Industries"]}
        )

    # 2. GET DIVISION -> GET PRODUCT TYPE
    elif stage == "get_division":
        user_details['division'] = user_input
        user_details['stage_history'].append("get_division")
        
        intro = ""
        options = []
        if "DM" in user_input:
            intro = "Great! You’re looking for custom thermoformed packaging solutions."
            options = [
                "Part Handling Trays", "ESD Trays", 
                "Toy Packaging", "Medical Packaging", "Food Packaging", 
                "Cosmetic Packaging", "Electronics Packaging", "Automobile Packaging", 
                "Other"
            ]
        else:
            intro = "Great! You need vacuum formed plastic parts / housings."
            options = [
                "Robot Covers", "Drone Covers", "Medical Covers", 
                "Automobile Thick Trays", "Hydroponic System Parts", "Other"
            ]

        return ChatResponse(
            next_stage="get_product_type",
            bot_messages=[
                intro,
                "What **type of product/packaging** are you looking for?"
            ],
            user_details=user_details,
            ui_elements={"type": "buttons", "display_style": "pills", "options": options}
        )

    # 3. GET PRODUCT TYPE -> GET PROPERTIES
    elif stage == "get_product_type":
        user_details['product_type'] = user_input
        user_details['stage_history'].append("get_product_type")
        
        properties = []
        if "DM" in user_details.get('division', ''):
             properties = [
                 "Clear", "Transparent", "Food Contact Safe", "ESD", "Anti-static", 
                 "Heat Sealable", "Lightweight", "Glossy", "Premium Look", 
                 "UV Resistant", "Moisture Resistant", "Colored", "Opaque"
             ]
        else:
             properties = [
                 "High Strength", "Impact Resistant", "Lightweight", "Heat Resistant", 
                 "Chemical Resistant", "UV Resistant", "Outdoor Resistant", 
                 "Electrical Insulation", "Rigid", "Structural", "Matte", "Gloss", 
                 "Textured Surface", "Colored"
             ]

        return ChatResponse(
            next_stage="get_properties",
            bot_messages=[
                "Understood.",
                "What **plastic properties** are required for your requirement?"
            ],
            user_details=user_details,
            ui_elements={
                "type": "buttons", 
                "display_style": "pills", 
                "multi_select": True,
                "options": properties
            }
        )

    # 4. GET PROPERTIES -> CONFIRM MATERIAL
    elif stage == "get_properties":
        user_details['properties'] = user_input
        user_details['stage_history'].append("get_properties")
        
        # Simple Logic to suggest material based on properties
        suggested_material = "Unknown"
        options = []
        
        props_lower = user_input.lower()
        
        if "DM" in user_details.get('division', ''):
            if "clear" in props_lower or "transparent" in props_lower:
                suggested_material = "PET / PVC"
            elif "food" in props_lower:
                suggested_material = "PET / PP"
            elif "esd" in props_lower or "anti-static" in props_lower:
                suggested_material = "ESD PET / HIPS"
            else:
                suggested_material = "HIPS / PET"
            
            options = ["PET", "PVC", "HIPS", "PP", "PC", "Other"]
        else:
            if "outdoor" in props_lower or "uv" in props_lower:
                suggested_material = "ASA / UV ABS"
            elif "impact" in props_lower or "strength" in props_lower:
                suggested_material = "ABS / HDPE"
            elif "fire" in props_lower or "heat" in props_lower:
                suggested_material = "FR ABS / PC"
            else:
                suggested_material = "ABS / HIPS"

            options = ["ABS", "HIPS", "HDPE", "ASA", "PC", "Other"]

        return ChatResponse(
            next_stage="confirm_material",
            bot_messages=[
                f"Based on your requirements, we recommend **{suggested_material}**.",
                "Please **confirm or select** the material you prefer:"
            ],
            user_details=user_details,
            ui_elements={"type": "buttons", "display_style": "pills", "options": options}
        )

    # 5. CONFIRM MATERIAL -> GET THICKNESS
    elif stage == "confirm_material":
        user_details['material'] = user_input
        user_details['stage_history'].append("confirm_material")
        
        msg = ""
        options = []
        if "DM" in user_details.get('division', ''):
            msg = "What is the required **Material Thickness**?"
            options = ["0.3mm", "0.5mm", "0.8mm", "1.0mm", "1.5mm", "2.0mm", "Other"]
        else:
            msg = "What is the required **Material Thickness**?"
            options = ["2.0mm", "3.0mm", "4.0mm", "5.0mm", "6.0mm", "8.0mm", "Other"]

        return ChatResponse(
            next_stage="get_thickness",
            bot_messages=[msg],
            user_details=user_details,
            ui_elements={"type": "buttons", "display_style": "pills", "options": options}
        )

    # 6. GET THICKNESS -> GET DRAWING
    elif stage == "get_thickness":
        user_details['thickness'] = user_input
        user_details['stage_history'].append("get_thickness")
        return ChatResponse(
            next_stage="get_drawing",
            bot_messages=["Do you have a **technical drawing** available for this?"],
            user_details=user_details,
            ui_elements={"type": "buttons", "display_style": "pills", "options": ["2D Drawing", "3D Model", "No drawing"]}
        )

    # 7. GET DRAWING -> UPLOAD OR DIMENSIONS
    # 7. GET DRAWING -> UPLOAD OR DIMENSIONS
    elif stage == "get_drawing":
        user_details['drawing_available'] = user_input
        user_details['stage_history'].append("get_drawing")
        
        print(f"DEBUG: Processing stage '{stage}' with input: '{user_input}'")
        input_cleaned = user_input.lower().strip().replace(".", "").replace(",", "")
        
        negative_responses = [
            "no drawing", "no", "na", "n/a", "not available", "none", "nope",
            "don't have", "dont have", "skip", "no draw", "not yet", 
            "i dont have", "i don't have", "without", "later"
        ]
        
        # Check against list or if input contains key phrases
        is_negative = False
        
        # 1. Exact match check
        if input_cleaned in negative_responses:
            is_negative = True
        
        # 2. Phrase check (if not exact match)
        if not is_negative:
            for phrase in negative_responses:
                # Use word boundaries for short words like "no" or "na" to avoid false positives
                # But for now, simple substring check is likely fine for this specific domain context
                if phrase in input_cleaned:
                    is_negative = True
                    break
        
        print(f"DEBUG: Is negative response? {is_negative} (Input: '{input_cleaned}')")

        if is_negative:
            print("DEBUG: User indicated no drawing. Moving to dimensions.")
            return ChatResponse(
                next_stage="get_dimensions",
                bot_messages=["No problem. Please provide the **Dimensions** (Length × Width × Height in mm) — measured at maximum value."],
                user_details=user_details
            )
        else:
            # Transition to upload stage
            print("DEBUG: User might have drawing. Requesting upload.")
            return ChatResponse(
                 next_stage="upload_drawing_stage",
                 bot_messages=["Great! Please **upload** your technical drawing file."],
                 user_details=user_details,
                 ui_elements={"type": "file_upload", "upload_to": "/upload_drawing"}
            )

    # 7.5. UPLOAD DRAWING -> GET QUANTITY
    elif stage == "upload_drawing_stage":
        # Check if the input indicates a successful upload
        if user_input.startswith("Uploaded:"):
             user_details['drawing_file'] = user_input.replace("Uploaded: ", "").strip()
             user_details['stage_history'].append("upload_drawing_stage")
             return ChatResponse(
                next_stage="get_quantity",
                bot_messages=["File received. How many **units** do you require?"],
                user_details=user_details
             )
        else:
             # If user types something else, remind them or allow skip?
             # For now, let's assume they might be chatting, but we want the file.
             return ChatResponse(
                 next_stage="upload_drawing_stage",
                 bot_messages=["Please **upload** the drawing file using the button above."],
                 user_details=user_details,
                 ui_elements={"type": "file_upload", "upload_to": "/upload_drawing"}
             )

    # 8. GET DIMENSIONS -> GET QUANTITY

    # 8. GET DIMENSIONS -> GET QUANTITY
    elif stage == "get_dimensions":
        user_details['dimensions'] = user_input
        user_details['stage_history'].append("get_dimensions")
        return ChatResponse(
            next_stage="get_quantity",
            bot_messages=["Got it. How many **units** do you require?"],
            user_details=user_details
        )

    # 9. GET QUANTITY -> GET URGENCY
    elif stage == "get_quantity":
        user_details['quantity'] = user_input
        user_details['stage_history'].append("get_quantity")
        return ChatResponse(
            next_stage="get_urgency",
            bot_messages=["When do you **need these parts/packaging** ready?"],
            user_details=user_details,
            ui_elements={"type": "buttons", "display_style": "pills", "options": ["Urgent (within 2 weeks)", "Within 1 month", "2-3 months", "Planning stage"]}
        )

    # 10. GET URGENCY -> GET SAMPLE
    elif stage == "get_urgency":
        user_details['timeline'] = user_input
        user_details['stage_history'].append("get_urgency")
        return ChatResponse(
            next_stage="get_sample",
            bot_messages=["Would you like us to develop a **sample** before bulk production?"],
            user_details=user_details,
            ui_elements={"type": "buttons", "display_style": "pills", "options": ["Yes", "No"]}
        )

    # 11. GET SAMPLE -> GET DELIVERY
    elif stage == "get_sample":
        user_details['sample_needed'] = user_input
        user_details['stage_history'].append("get_sample")
        return ChatResponse(
            next_stage="get_delivery",
            bot_messages=["Where should the products be **delivered**? (Please mention City or Country)"],
            user_details=user_details
        )

    # 12. GET DELIVERY -> GET FORECAST
    elif stage == "get_delivery":
        user_details['delivery_location'] = user_input
        user_details['stage_history'].append("get_delivery")
        return ChatResponse(
            next_stage="get_forecast",
            bot_messages=["Last technical detail: What is your **forecast demand**? (Please mention typical Monthly or Yearly quantity)"],
            user_details=user_details
        )

    # 13. GET FORECAST -> GET COMPANY NAME
    elif stage == "get_forecast":
        user_details['forecast'] = user_input
        user_details['stage_history'].append("get_forecast")
        # Use initial name as contact person
        user_details['contact_person'] = user_details.get('name', 'N/A') 
        return ChatResponse(
            next_stage="get_company_name",
            bot_messages=["Thank you. Now, let's collect your contact details for the formal quote.", "What is your **Company Name**?"],
            user_details=user_details
        )

    # 14. COMPANY NAME -> COMPANY ADDRESS
    elif stage == "get_company_name":
        user_details['company'] = user_input
        user_details['stage_history'].append("get_company_name")
        return ChatResponse(
            next_stage="get_company_address",
            bot_messages=["What is the **Company Address**?"],
            user_details=user_details
        )

    # 15. COMPANY ADDRESS -> PHONE
    elif stage == "get_company_address":
        user_details['company_address'] = user_input
        user_details['stage_history'].append("get_company_address")
        return ChatResponse(
            next_stage="get_phone",
            bot_messages=["Please provide your **Phone Number**:"],
            user_details=user_details
        )

    # 17. PHONE -> EMAIL
    elif stage == "get_phone":
        user_details['phone'] = user_input
        user_details['stage_history'].append("get_phone")
        return ChatResponse(
            next_stage="get_email",
            bot_messages=["Finally, please share your **Official Email ID**:"],
            user_details=user_details
        )

    # 18. GET EMAIL -> CLOSE
    elif stage == "get_email":
        email = extract_email(user_input)
        user_details['email'] = email if email else user_input
        user_details['stage_history'].append("get_email")
        
        # Trigger Background Task for Sales PDF
        background_tasks.add_task(process_lead_and_send_email, user_details)

        return ChatResponse(
            next_stage="post_engagement",
            bot_messages=[
                "✅ **Inquiry Submitted!**",
                "Our team will contact you shortly to provide a formal quote.",
                "Is there anything else I can help you with?"
            ],
            user_details=user_details,
            ui_elements={"type": "buttons", "options": ["Create New Inquiry", "No, I’m good"]}
        )

    # 19. POST ENGAGEMENT
    elif stage == "post_engagement":
        if "New" in user_input or "Inquiry" in user_input:
             user_details = {'stage_history': []}
             return ChatResponse(next_stage="get_name", bot_messages=["Hello! Welcome back.", "May I kindly know your **Name**?"], user_details=user_details)
        
        if "No" in user_input or "Good" in user_input:
            return ChatResponse(
                next_stage="closing",
                bot_messages=["Thank you for reaching out to **RA & D**! 😊", "We look forward to working with you. Have a fantastic day!"],
                user_details=user_details
            )

        return ChatResponse(
            next_stage="post_engagement", 
            bot_messages=["Is there anything else I can help you with?"], 
            user_details=user_details, 
            ui_elements={"type": "buttons", "options": ["Create New Inquiry", "No, I’m good"]}
        )

    # 20. CLOSING
    elif stage == "closing":
        return ChatResponse(
            next_stage="get_name", 
            bot_messages=["If you need anything else, just say **Hi**!", "May I kindly know your **Name**?"], 
            user_details={'stage_history': []}
        )

    # FALLBACK
    return ChatResponse(next_stage="get_name", bot_messages=["Hello 👋 Welcome to **DM Thermoformer & RA Vacform Industries**! We’re glad to assist you with custom plastic solutions.\n\nMay I kindly know your **Name**?"], user_details={'stage_history': []})
