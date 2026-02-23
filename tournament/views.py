import io
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import College, Registration
from .forms import RegistrationForm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.conf import settings
import os

def index(request):
    # Ensure colleges exist
    if not College.objects.exists():
        college_names = [
            "Theyagaraja polytechnic, amballur",
            "Sree rama polytechnic, thriprayar",
            "Govt. Polytechnic, kunnakulam",
            "Model polytechnic, vadakara",
            "Kkmmptc, kallettumkara",
            "Holy grace polytechnic, mala",
            "Mets polytechnic, mala",
            "Iccs polytechnic, mupliyam"
        ]
        for name in college_names:
            College.objects.get_or_create(name=name)

    colleges = College.objects.all()
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            college = form.cleaned_data['college']
            
            # Re-check limit on server side
            if college.registrations.count() >= 18:
                return JsonResponse({
                    'status': 'error', 
                    'message': f'The 18 student registration for {college.name} is already completed.'
                })
            
            try:
                registration = form.save()
                
                # If this was the 18th student
                if college.registrations.count() == 18:
                     return JsonResponse({
                         'status': 'success', 
                         'message': 'Registration successful! The 18 student limit has been reached.',
                         'download_pdf': True,
                         'college_id': college.id
                     })
                
                return JsonResponse({'status': 'success', 'message': 'Registration submitted successfully!'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Submition failed: {str(e)}'})
        else:
            # Return detailed form errors
            errors = form.errors.get_json_data()
            error_msg = "Please fix the following: "
            for field, field_errors in errors.items():
                for error in field_errors:
                    error_msg += f"{field.capitalize()}: {error['message']} "
            return JsonResponse({'status': 'error', 'message': error_msg})

    form = RegistrationForm()
    return render(request, 'tournament/index.html', {'form': form, 'colleges': colleges})

def download_pdf(request, college_id):
    college = College.objects.get(id=college_id)
    students = college.registrations.all()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="DECLARATION_LETTER_{college.name}.pdf"'

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Heading
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=22,
        alignment=1, # Center
        spaceAfter=20
    )
    elements.append(Paragraph("DECLARATION LETTER", title_style))
    elements.append(Paragraph(f"College: {college.name}", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))

    # Student Table
    data = [["SL No", "Name", "PRN", "Dept", "Photo"]]
    for i, student in enumerate(students, 1):
        # Image handling
        img_path = student.photo.path
        img = Image(img_path, width=0.5*inch, height=0.5*inch)
        data.append([str(i), student.name, student.prn, student.department, img])

    table = Table(data, colWidths=[0.5*inch, 2*inch, 1.5*inch, 1.5*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    elements.append(Spacer(1, 0.5*inch))
    
    # Signature
    sig_style = ParagraphStyle(
        'SigStyle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=2, # Right
    )
    elements.append(Paragraph("signature for principal", sig_style))

    doc.build(elements)
    
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

# Custom Admin Views
def admin_login(request):
    if request.user.is_authenticated:
        return redirect('tournament:admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('tournament:admin_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'tournament/admin_login.html')

def admin_logout(request):
    logout(request)
    return redirect('tournament:admin_login')

@login_required(login_url='tournament:admin_login')
def admin_dashboard(request):
    college_id = request.GET.get('college')
    colleges = College.objects.all()
    
    if college_id:
        students = Registration.objects.filter(college_id=college_id)
    else:
        students = Registration.objects.all()
        
    return render(request, 'tournament/admin_dashboard.html', {
        'students': students,
        'colleges': colleges,
        'selected_college': college_id
    })

@login_required(login_url='tournament:admin_login')
def export_students_pdf(request):
    college_id = request.GET.get('college')
    
    if college_id:
        college = College.objects.get(id=college_id)
        students = Registration.objects.filter(college=college)
        filename = f"Registration_Details_{college.name}.pdf"
        title = f"REGISTRATION DETAILS - {college.name}"
    else:
        students = Registration.objects.all()
        filename = "All_Registration_Details.pdf"
        title = "ALL TOURNAMENT REGISTRATIONS"

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Professional Title Style
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=20,
        alignment=1,
        spaceAfter=30,
        textColor=colors.HexColor("#0f172a")
    )
    elements.append(Paragraph(title, title_style))

    # Table Data
    data = [["SL", "Name", "PRN", "Dept", "College", "Photo"]]
    for i, student in enumerate(students, 1):
        try:
            img_path = student.photo.path
            img = Image(img_path, width=0.6*inch, height=0.6*inch)
        except:
            img = "No Photo"
            
        data.append([
            str(i), 
            student.name, 
            student.prn, 
            student.department, 
            student.college.name, 
            img
        ])

    # Table Styling
    table = Table(data, colWidths=[0.4*inch, 1.4*inch, 1.2*inch, 1.2*inch, 1.5*inch, 0.8*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4facfe")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
