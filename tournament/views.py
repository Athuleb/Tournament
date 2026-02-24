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
        
        # Check for existing PRN manually for a better error message
        prn = request.POST.get('prn')
        if prn and Registration.objects.filter(prn=prn).exists():
            return JsonResponse({
                'status': 'error',
                'message': f'⚠️ Warning: A student with PRN "{prn}" is already registered. Duplicate registrations are not allowed.'
            })

        if form.is_valid():
            college = form.cleaned_data['college']
            
            # Re-check limit on server side
            if college.registrations.count() >= 18:
                return JsonResponse({
                    'status': 'error', 
                    'message': f'The 18 student registration limit for {college.name} has already been reached.'
                })
            
            try:
                registration = form.save()
                
                # If this was the 18th student
                if college.registrations.count() == 18:
                     return JsonResponse({
                         'status': 'success', 
                         'message': '🎉 Registration successful! You are the final member of the team. The 18-student limit for your college is now reached.'
                     })
                
                return JsonResponse({
                    'status': 'success', 
                    'message': '✅ Registration completed successfully! Good luck for the tournament.'
                })
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Submission failed: {str(e)}'})
        else:
            # Return detailed form errors
            errors = form.errors.get_json_data()
            error_msg = "Please fix the following: "
            for field, field_errors in errors.items():
                for error in field_errors:
                    # Clean up field name and error message
                    clean_field = field.replace('_', ' ').capitalize()
                    error_msg += f"{clean_field}: {error['message']} "
            return JsonResponse({'status': 'error', 'message': error_msg})

    form = RegistrationForm()
    return render(request, 'tournament/index.html', {'form': form, 'colleges': colleges})

def teams(request):
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
            
    colleges = College.objects.all().order_by('name')
    return render(request, 'tournament/teams.html', {'colleges': colleges})

def download_pdf(request, college_id):
    college = College.objects.get(id=college_id)
    students = college.registrations.all()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="DECLARATION_{college.name.replace(" ", "_")}.pdf"'

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    elements = []
    styles = getSampleStyleSheet()

    # Custom Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=1,  # Center
        spaceAfter=30,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        alignment=4,  # Justified
        spaceAfter=15
    )

    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        spaceAfter=10
    )

    # 1. Main Title
    elements.append(Paragraph("DECLARATION", title_style))

    # 2. Declaration Text
    declaration_1 = f"We hereby declare that we are bonafide students of <b>{college.name}</b> and we are participating in the Football Tournament conducted by the institution."
    elements.append(Paragraph(declaration_1, body_style))

    declaration_2 = "We assure that we will follow all the rules and regulations of the institution and the tournament committee. The above information is true to the best of our knowledge."
    elements.append(Paragraph(declaration_2, body_style))

    elements.append(Spacer(1, 0.2*inch))

    # 3. Student Table
    elements.append(Paragraph("<b>List of Participating Students:</b>", label_style))
    data = [["SL No", "Name", "PRN", "Dept", "Photo"]]
    for i, student in enumerate(students, 1):
        try:
            img_path = student.photo.path
            img = Image(img_path, width=0.5*inch, height=0.5*inch)
        except:
            img = "No Photo"
        data.append([str(i), student.name, student.prn, student.department, img])

    table = Table(data, colWidths=[0.5*inch, 1.8*inch, 1.2*inch, 1.2*inch, 0.8*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    elements.append(table)

    elements.append(Spacer(1, 0.5*inch))

    # 4. Footer info (Date, Place, Signatures)
    footer_data = [
        [Paragraph("Date: ____________", label_style), ""],
        [Paragraph("Place: ____________", label_style), ""],
        [Spacer(1, 0.4*inch), Spacer(1, 0.4*inch)],
        [Paragraph("Signature of Principal: ____________________", label_style), ""],
        [Paragraph("Signature of Sports Coordinator: ____________________", label_style), ""]
    ]
    
    # We use a table for positioning the footer elements
    footer_table = Table(footer_data, colWidths=[4*inch, 1*inch])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    elements.append(footer_table)

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
        filename = f"Registration_{college.name.replace(' ', '_')}.pdf"
    else:
        students = Registration.objects.all()
        filename = "All_Registration_Details.pdf"

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    buffer = io.BytesIO()
    # Increased margins for a formal "official paper" look
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    elements = []
    styles = getSampleStyleSheet()

    # Define Styles
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=1,
        spaceAfter=10,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#1e293b")
    )
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontSize=14,
        alignment=1,
        spaceAfter=25,
        fontName='Helvetica-Bold',
        underline=True
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        alignment=4,  # Justified
        spaceAfter=14
    )

    if college_id:
        # 1. Official Header
        elements.append(Paragraph("FOOTBALL TOURNAMENT 2026", header_style))
        elements.append(Paragraph("PARTICIPATING STUDENT LIST", header_style))
        elements.append(Paragraph("REGISTRATION DETAILS", title_style))

        # 2. Declaration Text
        declaration_1 = f"We hereby declare that we are bonafide students of <b>{college.name}</b> and we are participating in the Football Tournament conducted by the institution."
        elements.append(Paragraph(declaration_1, body_style))

        declaration_2 = "We assure that we will follow all the rules and regulations of the institution and the tournament committee. The above information is true to the best of our knowledge."
        elements.append(Paragraph(declaration_2, body_style))

        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph("<b><u>PARTICIPATING STUDENT LIST</u></b>", body_style))

        # 3. Table
        data = [["SL", "Name", "PRN", "Dept", "Photo"]]
        for i, student in enumerate(students, 1):
            try:
                img_path = student.photo.path
                img = Image(img_path, width=0.55*inch, height=0.55*inch)
            except:
                img = "No Photo"
            data.append([str(i), student.name, student.prn, student.department, img])

        # Table dimensions (Total A4 width is ~595 pts, minus margins 144 pts = 451 pts)
        table = Table(data, colWidths=[0.4*inch, 1.8*inch, 1.2*inch, 1.2*inch, 0.9*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(table)

        elements.append(Spacer(1, 0.6*inch))

        # 4. Signatures (Arranged side-by-side)
        sig_body = ParagraphStyle('SigBody', parent=styles['Normal'], fontSize=10, leading=14)
        
        sig_data = [
            [Paragraph("Date: ____________", sig_body), Paragraph("__________________________", sig_body)],
            [Paragraph("Place: ____________", sig_body), Paragraph("Signature of Principal", sig_body)],
            [Spacer(1, 0.3*inch), Spacer(1, 0.3*inch)],
            ["", Paragraph("__________________________", sig_body)],
            ["", Paragraph("Signature of Sports Coordinator", sig_body)]
        ]
        
        # Table for alignment (Left info, Right signatures)
        sig_table = Table(sig_data, colWidths=[2.5*inch, 3*inch])
        sig_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'), # Align signatures to the right
        ]))
        elements.append(sig_table)

    else:
        # General Summary for all colleges
        elements.append(Paragraph("FOOTBALL TOURNAMENT 2026", header_style))
        
        data = [["SL", "Name", "PRN", "Dept", "College", "Photo"]]
        for i, student in enumerate(students, 1):
            try:
                img_path = student.photo.path
                img = Image(img_path, width=0.5*inch, height=0.5*inch)
            except:
                img = "No Photo"
            data.append([str(i), student.name, student.prn, student.department, student.college.name, img])

        table = Table(data, colWidths=[0.3*inch, 1.2*inch, 1.1*inch, 1.1*inch, 1.3*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4facfe")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(table)

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

@login_required(login_url='tournament:admin_login')
def edit_student(request, student_id):
    student = Registration.objects.get(id=student_id)
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f"Details for {student.name} updated successfully.")
            return redirect('tournament:admin_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm(instance=student)
    
    return render(request, 'tournament/edit_student.html', {
        'form': form,
        'student': student
    })

@login_required(login_url='tournament:admin_login')
def delete_student(request, student_id):
    student = Registration.objects.get(id=student_id)
    name = student.name
    student.delete()
    messages.success(request, f"Registration for {name} has been deleted.")
    return redirect('tournament:admin_dashboard')
