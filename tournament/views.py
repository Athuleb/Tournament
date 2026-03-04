import io
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from .models import Registration
from .forms import RegistrationForm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.conf import settings
import os

# Hardcoded College Data
HARDCODED_COLLEGES = {
    "Theyagaraja polytechnic, amballur": {"username": "theyagarajapolytechnicamballur", "password_hash": "pbkdf2_sha256$1200000$21ozkFFlFLHXRAG8sCYNM6$hY4ViqbUqphA6/EiKWkIYzagfkgaoBgXVzaYncWOWEA="},
    "Sree rama polytechnic, thriprayar": {"username": "sreeramapolytechnicthriprayar", "password_hash": "pbkdf2_sha256$1200000$A2dfM2JmdJOrRJ8q44sXBp$JE9dlp0m+pWTBQofROmdPAh8J2nVft4zB4+Rkw2BN7o="},
    "Govt. Polytechnic, kunnakulam": {"username": "govtpolytechnickunnakulam", "password_hash": "pbkdf2_sha256$1200000$52uovYOAQVrlU1J5pyIV5G$N9/EV416xxxFvW65EOzzvq4PuCQavNYqz7K9tClWBbE="},
    "Model polytechnic, vadakara": {"username": "modelpolytechnicvadakara", "password_hash": "pbkdf2_sha256$1200000$2jYsYb6kgvDYl68lCotfsY$u2821neRZ1fwD/HN21hvVLdYU/G/e4V2VOlKNQq92ss="},
    "Kkmmptc, kallettumkara": {"username": "kkmmptckallettumkara", "password_hash": "pbkdf2_sha256$1200000$AHaVdL7OFJ2egjh5y2ltM2$N/cUAg4jPGBYp50yTvxmMgS8+TtWLJw2MjZiMDIknVI="},
    "Holy grace polytechnic, mala": {"username": "holygracepolytechnicmala", "password_hash": "pbkdf2_sha256$1200000$2p6LvaCFNH9hWIdfsdNVEy$2lPtIN0a7lO7lwyL4fDqGrDnibW/xEhZcqxJYG2g84Q="},
    "Mets polytechnic, mala": {"username": "metspolytechnicmala", "password_hash": "pbkdf2_sha256$1200000$gmdvUR0Pao8ILyX7GvpCYY$KN1pMixQ/doIOsp4q9uMBA63rFrHwJ1po/EbFAAIeH0="},
    "Iccs polytechnic, mupliyam": {"username": "iccspolytechnicmupliyam", "password_hash": "pbkdf2_sha256$1200000$n0P5mcgHrFy6wd7leFcmlI$SsWxNFo3hEz/W/z/7Nraov+KimrRcC3Zg8HqKvPEs/s="},
}

def index(request):
    logged_in_college_name = request.session.get('college_name')
    
    if request.method == 'POST':
        if not logged_in_college_name:
            college_name = request.POST.get('college_id') # This is the name from select
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            if college_name in HARDCODED_COLLEGES:
                creds = HARDCODED_COLLEGES[college_name]
                if username == creds['username'] and check_password(password, creds['password_hash']):
                    request.session['college_name'] = college_name
                    return JsonResponse({'status': 'login_success', 'message': f'Welcome, {college_name}!'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'Invalid credentials for the selected college.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Selected college not found.'})

    form = RegistrationForm()
    colleges = sorted(HARDCODED_COLLEGES.keys())
    
    return render(request, 'tournament/index.html', {
        'form': form, 
        'logged_in_college': {'name': logged_in_college_name} if logged_in_college_name else None,
        'colleges': colleges
    })

def registration_page(request):
    logged_in_college_name = request.session.get('college_name')
    
    if request.method == 'POST':
        if not logged_in_college_name:
            college_name = request.POST.get('college_id')
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            if college_name in HARDCODED_COLLEGES:
                creds = HARDCODED_COLLEGES[college_name]
                if username == creds['username'] and check_password(password, creds['password_hash']):
                    request.session['college_name'] = college_name
                    return JsonResponse({'status': 'login_success', 'message': f'Welcome, {college_name}!'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'Invalid credentials.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'College not found.'})

        form = RegistrationForm(request.POST, request.FILES)
        prn = request.POST.get('prn')
        if prn and Registration.objects.filter(prn=prn).exists():
            return JsonResponse({'status': 'error', 'message': f'⚠️ PRN "{prn}" already registered.'})

        if form.is_valid():
            # Injected college from session to ensure security
            registration = form.save(commit=False)
            registration.college = logged_in_college_name
            
            if Registration.objects.filter(college=logged_in_college_name).count() >= 18:
                return JsonResponse({'status': 'error', 'message': 'Registration limit reached (18 students).'})
            
            registration.save()
            return JsonResponse({'status': 'success', 'message': 'Registration successful'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form data.'})

    students = []
    if logged_in_college_name:
        students = Registration.objects.filter(college=logged_in_college_name).order_by('-created_at')
        
    return render(request, 'tournament/registration.html', {
        'form': RegistrationForm(initial={'college': logged_in_college_name}), 
        'logged_in_college': {'name': logged_in_college_name} if logged_in_college_name else None,
        'students': students,
        'colleges': sorted(HARDCODED_COLLEGES.keys())
    })

def edit_student_college(request, student_id):
    college_name = request.session.get('college_name')
    if not college_name:
        return redirect('tournament:registration_page')
        
    try:
        student = Registration.objects.get(id=student_id, college=college_name)
    except Registration.DoesNotExist:
        return redirect('tournament:registration_page')

    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            reg = form.save(commit=False)
            reg.college = college_name
            reg.save()
            messages.success(request, f"Details for {student.name} updated.")
            return redirect('tournament:registration_page')
    else:
        form = RegistrationForm(instance=student)
    
    return render(request, 'tournament/edit_student_college.html', {
        'form': form,
        'student': student,
        'college': {'name': college_name}
    })

def college_logout(request):
    if 'college_name' in request.session:
        del request.session['college_name']
    return redirect('tournament:index')

def teams(request):
    colleges_data = []
    for name in sorted(HARDCODED_COLLEGES.keys()):
        count = Registration.objects.filter(college=name).count()
        colleges_data.append({'name': name, 'registration_count': count})
    return render(request, 'tournament/teams.html', {'colleges': colleges_data})

def download_pdf(request, college_id=None):
    # Note: id is now name for backward compatibility in URLs or just use name
    # But since current URL is /download-pdf/<int:college_id>/, we might need to adjust or handle it
    # For now, let's assume it's passed or taken from session
    college_name = request.session.get('college_name')
    if not college_name:
         return HttpResponse("Unauthorized", status=401)
         
    students = Registration.objects.filter(college=college_name)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="DECLARATION_{college_name.replace(" ", "_")}.pdf"'

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, alignment=1, spaceAfter=10, fontName='Helvetica-Bold')
    header_style = ParagraphStyle('HeaderStyle', parent=title_style, spaceAfter=30)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=12, leading=16, alignment=4, spaceAfter=15)
    label_style = ParagraphStyle('LabelStyle', parent=styles['Normal'], fontSize=12, leading=16, spaceAfter=10)
    
    elements.append(Paragraph("FOOTBALL TOURNAMENT 2026", title_style))
    elements.append(Paragraph("PARTICIPATING STUDENT LIST", title_style))
    elements.append(Paragraph("REGISTRATION DETAILS", header_style))

    declaration_1 = f"We hereby declare that we are bonafide students of <b>{college_name}</b> and we are participating in the Football Tournament conducted by the institution."
    elements.append(Paragraph(declaration_1, body_style))
    
    declaration_2 = "We assure that we will follow all the rules and regulations of the institution and the tournament committee. The above information is true to the best of our knowledge."
    elements.append(Paragraph(declaration_2, body_style))
    elements.append(Spacer(1, 0.2*inch))

    elements.append(Paragraph("<b>List of Participating Students:</b>", label_style))
    data = [["SL No", "Name", "PRN", "Dept", "Photo"]]
    for i, student in enumerate(students, 1):
        try:
            img = Image(student.photo.path, width=0.5*inch, height=0.5*inch)
        except:
            img = "No Photo"
        data.append([str(i), student.name, student.prn, student.department, img])

    table = Table(data, colWidths=[0.5*inch, 1.8*inch, 1.2*inch, 2.0*inch, 0.8*inch])
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

    # Footer info
    footer_data = [
        [Paragraph("Date: ____________", label_style), Paragraph("__________________________", label_style)],
        [Paragraph("Place: ____________", label_style), Paragraph("Signature of Principal", label_style)],
        [Spacer(1, 0.4*inch), Spacer(1, 0.4*inch)],
        ["", Paragraph("__________________________", label_style)],
        ["", Paragraph("Signature of Sports Coordinator", label_style)]
    ]
    
    footer_table = Table(footer_data, colWidths=[2.5*inch, 3*inch])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    elements.append(footer_table)

    doc.build(elements)
    response.write(buffer.getvalue())
    return response

@login_required(login_url='tournament:admin_login')
def admin_dashboard(request):
    college_name = request.GET.get('college')
    colleges = sorted(HARDCODED_COLLEGES.keys())
    
    if college_name:
        students = Registration.objects.filter(college=college_name)
    else:
        students = Registration.objects.all()
        
    return render(request, 'tournament/admin_dashboard.html', {
        'students': students,
        'colleges': colleges,
        'selected_college': college_name
    })

def admin_login(request):
    if request.user.is_authenticated: return redirect('tournament:admin_dashboard')
    if request.method == 'POST':
        username, password = request.POST.get('username'), request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user: login(request, user); return redirect('tournament:admin_dashboard')
        else: messages.error(request, "Invalid admin credentials.")
    return render(request, 'tournament/admin_login.html')

def admin_logout(request):
    logout(request)
    return redirect('tournament:index')

@login_required(login_url='tournament:admin_login')
def export_students_pdf(request):
    college_name = request.GET.get('college')
    students = Registration.objects.filter(college=college_name) if college_name else Registration.objects.all()
    
    response = HttpResponse(content_type='application/pdf')
    filename = f"Registration_{college_name.replace(' ', '_')}.pdf" if college_name else "All_Registrations.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=72, bottomMargin=72)
    elements = []
    styles = getSampleStyleSheet()
    
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Heading1'], fontSize=18, alignment=1, spaceAfter=10, fontName='Helvetica-Bold')
    title_style = ParagraphStyle('TitleStyle', parent=styles['Normal'], fontSize=14, alignment=1, spaceAfter=25, fontName='Helvetica-Bold', underline=True)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=11, leading=16, alignment=4, spaceAfter=14)
    label_style = ParagraphStyle('LabelStyle', parent=styles['Normal'], fontSize=11, leading=16)

    elements.append(Paragraph("FOOTBALL TOURNAMENT 2026", header_style))
    elements.append(Paragraph("PARTICIPATING STUDENT LIST", header_style))
    elements.append(Paragraph("REGISTRATION DETAILS", title_style))

    if college_name:
        declaration_1 = f"We hereby declare that we are bonafide students of <b>{college_name}</b> and we are participating in the Football Tournament conducted by the institution."
        elements.append(Paragraph(declaration_1, body_style))
        declaration_2 = "We assure that we will follow all the rules and regulations of the institution and the tournament committee. The above information is true to the best of our knowledge."
        elements.append(Paragraph(declaration_2, body_style))
    
    data = [["SL No", "Name", "PRN", "Dept", "College", "Photo"]] if not college_name else [["SL No", "Name", "PRN", "Dept", "Photo"]]
    for i, s in enumerate(students, 1):
        try: img = Image(s.photo.path, width=0.5*inch, height=0.5*inch)
        except: img = "No Photo"
        if not college_name:
            data.append([str(i), s.name, s.prn, s.department, s.college, img])
        else:
            data.append([str(i), s.name, s.prn, s.department, img])
    
    col_widths = [0.4*inch, 1.2*inch, 1.1*inch, 1.8*inch, 1.7*inch, 0.8*inch] if not college_name else [0.5*inch, 1.8*inch, 1.2*inch, 2.0*inch, 0.8*inch]
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(table)

    if college_name:
        elements.append(Spacer(1, 0.6*inch))
        footer_data = [
            [Paragraph("Date: ____________", label_style), Paragraph("__________________________", label_style)],
            [Paragraph("Place: ____________", label_style), Paragraph("Signature of Principal", label_style)],
            [Spacer(1, 0.4*inch), Spacer(1, 0.4*inch)],
            ["", Paragraph("__________________________", label_style)],
            ["", Paragraph("Signature of Sports Coordinator", label_style)]
        ]
        footer_table = Table(footer_data, colWidths=[2.5*inch, 3*inch])
        footer_table.setStyle(TableStyle([('ALIGN', (1, 0), (1, -1), 'RIGHT')]))
        elements.append(footer_table)

    doc.build(elements)
    response.write(buffer.getvalue())
    return response

@login_required(login_url='tournament:admin_login')
def edit_student(request, student_id):
    student = Registration.objects.get(id=student_id)
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated {student.name}")
            return redirect('tournament:admin_dashboard')
    else:
        form = RegistrationForm(instance=student)
    return render(request, 'tournament/edit_student.html', {'form': form, 'student': student})

@login_required(login_url='tournament:admin_login')
def delete_student(request, student_id):
    Registration.objects.get(id=student_id).delete()
    messages.success(request, "Deleted.")
    return redirect('tournament:admin_dashboard')
