import os
import pdfplumber
import docx
import pytesseract
from PIL import Image
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SignUpForm, DocumentForm
from .models import Document
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
# ReportLab imports
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
# --- HELPER 1: Text Extraction Logic ---
def extract_text_from_file(file_path):
    # 1. Point to your specific Tesseract installation
    # We use r'' to handle the backslashes in the Windows path correctly
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\CIPL1658\PropertyDocumentReview\venv\Tesseract-OCR\tesseract.exe'
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    try:
        if ext == '.pdf':
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        elif ext == '.docx':
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif ext in ['.jpg', '.jpeg', '.png']:
            text = pytesseract.image_to_string(Image.open(file_path))
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""
    return text.strip()

# --- HELPER 2: AI Analysis Logic ---
def analyze_document(text):
    text_lower = text.lower()
    
    # EXPANDED Positive Keywords (Real Estate Terms)
    positive_keywords = [
        # Document Names
        'sale deed', 'title deed', 'conveyance deed', 'gift deed', 'lease deed',
        'partition deed', 'release deed', 'settlement deed', 'power of attorney',
        'encumbrance certificate', 'completion certificate', 'occupancy certificate', 
        'tax receipt', 'khata', 'patta', 'chitta', 'adangal',
        # Positive Phrases
        'absolute owner', 'clear title', 'marketable title', 'free from encumbrance',
        'registered', 'approved', 'sanctioned', 'no objection', 'noc',
        'fee simple', 'freehold', 'lawful owner', 'peaceful possession',
        'right to sell', 'valid', 'authorized', 'permit', 'paid', 'receipt'
    ]

    # EXPANDED Negative Keywords (Risks)
    negative_keywords = [
        'dispute', 'litigation', 'stay order', 'injunction', 'court case',
        'encumbrance', 'mortgage', 'lien', 'charge', 'hypothecation',
        'illegal', 'unauthorized', 'encroachment', 'violation', 'deviation',
        'forgery', 'fraud', 'cancelled', 'void', 'prohibited', 'banned',
        'arrears', 'due', 'default', 'pending', 'objection', 'rejected'
    ]

    pos_count = sum(1 for word in positive_keywords if word in text_lower)
    neg_count = sum(1 for word in negative_keywords if word in text_lower)
    
    # --- Logic remains the same below ---
    if (pos_count + neg_count) == 0:
        return "Negative", 0, 0.0 

    if neg_count > 0:
        status = "Negative"
        score = max(10, 100 - (neg_count * 20)) 
        confidence = 0.85
    else:
        status = "Positive"
        score = min(98, 50 + (pos_count * 10))
        confidence = 0.90

    return status, score, confidence

# --- VIEW 1: Registration ---
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = SignUpForm()
    
    return render(request, 'ReviewApp/form_generic.html', {
        'form': form,
        'title': 'Create Account',
        'btn_text': 'Sign Up'
    })

# --- VIEW 2: Profile (List + Upload + Analyze) ---
@login_required
def profile_view(request):
    # Handle File Upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            # 1. Save file partially
            doc = form.save(commit=False)
            doc.user = request.user
            doc.save() # Save to disk to get path

            # 2. Run Helpers (Extract & Analyze)
            extracted_text = extract_text_from_file(doc.file.path)
            status, score, confidence = analyze_document(extracted_text)

            # 3. Update Document with Results
            doc.extracted_text = extracted_text
            doc.ai_status = status
            doc.ai_score = score
            doc.ai_confidence = confidence
            doc.save()

            messages.success(request, "Document uploaded and analyzed!")
            return redirect('profile')
    else:
        form = DocumentForm()

    # Handle Displaying List
    user_documents = Document.objects.filter(user=request.user).order_by('-uploaded_at')

    return render(request, 'ReviewApp/profile.html', {
        'form': form,
        'documents': user_documents
    })


def download_report(request, doc_id):
    # 1. Get the document object
    doc = get_object_or_404(Document, id=doc_id, user=request.user)

    # 2. Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Analysis_Report_{doc.id}.pdf"'

    # 3. Create the PDF object using ReportLab
    pdf = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # --- Header Section ---
    title = Paragraph(f"Property Document Analysis Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 20))

    # --- File Information Table ---
    data = [
        ["File Name:", doc.file.name.split('/')[-1]], # Clean filename
        ["Uploaded By:", doc.user.username],
        ["Date Uploaded:", doc.uploaded_at.strftime("%Y-%m-%d %H:%M:%S")],
    ]
    
    # Style the table
    table = Table(data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # --- AI Analysis Results ---
    elements.append(Paragraph("AI Analysis Results", styles['Heading2']))
    
    # Determine color for status
    status_color = "green" if doc.ai_status == "Positive" else "red"
    
    analysis_text = f"""
    <b>Status:</b> <font color={status_color}>{doc.ai_status}</font><br/>
    <b>Risk Score:</b> {doc.ai_score}/100<br/>
    <b>Confidence Level:</b> {doc.ai_confidence}
    """
    elements.append(Paragraph(analysis_text, styles['Normal']))
    elements.append(Spacer(1, 20))

    # --- Extracted Text Preview ---
    elements.append(Paragraph("Extracted Text Preview (First 800 chars)", styles['Heading2']))
    
    # Handle text wrapping and length
    preview_text = doc.extracted_text[:800] + "..." if doc.extracted_text else "No text extracted."
    elements.append(Paragraph(preview_text, styles['Normal']))

    # --- Build PDF ---
    pdf.build(elements)
    
    return response