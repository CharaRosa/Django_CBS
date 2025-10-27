"""
Utilitaires d'exportation complets pour Excel et PDF
Gère l'exportation de tous les modules : Professeurs, Cours, Émargements, Évaluations
"""
from io import BytesIO
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime


# ======================== STYLES COMMUNS ========================

def get_excel_styles():
    """Retourne les styles communs pour Excel."""
    header_fill = PatternFill(start_color="F59E0B", end_color="F59E0B", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    return {
        'header_fill': header_fill,
        'header_font': header_font,
        'border': border
    }


def setup_pdf_styles():
    """Configure les styles pour les PDF."""
    try:
        # Tenter d'enregistrer une police supportant les accents
        pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
        font_name = 'DejaVu'
    except:
        font_name = 'Helvetica'
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#F59E0B'),
        spaceAfter=30,
        alignment=1,  # Centré
        fontName=font_name
    ))
    return styles, font_name


# ======================== EXPORT PROFESSEURS ========================

def export_professeurs_to_excel(professeurs_list):
    """Exporte la liste des professeurs vers Excel."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Professeurs"
    
    styles = get_excel_styles()
    
    # En-tête
    headers = ['Nom', 'Prénoms', 'Contact', 'Email', 'Grade', "Domaine d'expertise"]
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.fill = styles['header_fill']
        cell.font = styles['header_font']
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = styles['border']
    
    # Données
    for row_num, prof in enumerate(professeurs_list, 2):
        ws.cell(row=row_num, column=1).value = prof.nom
        ws.cell(row=row_num, column=2).value = prof.prenoms
        ws.cell(row=row_num, column=3).value = prof.contact
        ws.cell(row=row_num, column=4).value = prof.email
        ws.cell(row=row_num, column=5).value = prof.grade or 'N/A'
        ws.cell(row=row_num, column=6).value = prof.domaine or 'N/A'
        
        for col in range(1, 7):
            ws.cell(row=row_num, column=col).border = styles['border']
    
    # Ajuster les largeurs
    for col in range(1, 7):
        ws.column_dimensions[get_column_letter(col)].width = 20
    
    # Créer la réponse HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"Professeurs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    wb.save(response)
    return response


def export_professeurs_to_pdf(professeurs_list):
    """Exporte la liste des professeurs vers PDF."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []
    
    styles, font_name = setup_pdf_styles()
    
    # Titre
    title = Paragraph(f"Liste des Professeurs - {datetime.now().strftime('%d/%m/%Y')}", styles['CustomTitle'])
    elements.append(title)
    elements.append(Spacer(1, 0.5*cm))
    
    # Données du tableau
    data = [['Nom', 'Prénoms', 'Contact', 'Email', 'Grade', "Domaine"]]
    
    for prof in professeurs_list:
        data.append([
            prof.nom,
            prof.prenoms,
            prof.contact,
            prof.email,
            prof.grade or 'N/A',
            prof.domaine or 'N/A'
        ])
    
    # Créer le tableau
    table = Table(data, colWidths=[4*cm, 4*cm, 3*cm, 5*cm, 3*cm, 4*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F59E0B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"Professeurs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response


# ======================== EXPORT COURS PROGRAMMÉS ========================

def export_cours_to_excel(cours_list):
    """Exporte la liste des cours programmés vers Excel."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Cours Programmés"
    
    styles = get_excel_styles()
    
    # En-tête
    headers = ['Matière', 'Filière', 'Niveau', 'Professeur', 'Semestre', 'Volume Horaire', 'Heures Faites', 'Date Début', 'Date Fin']
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.fill = styles['header_fill']
        cell.font = styles['header_font']
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = styles['border']
    
    # Données
    for row_num, cours in enumerate(cours_list, 2):
        heures_faites = cours.total_heures_faites if hasattr(cours, 'total_heures_faites') else 0
        
        ws.cell(row=row_num, column=1).value = cours.matiere.libelle
        ws.cell(row=row_num, column=2).value = cours.filiere.code
        ws.cell(row=row_num, column=3).value = f"{cours.niveau.libelle} {cours.niveau.niv}"
        ws.cell(row=row_num, column=4).value = str(cours.professeur)
        ws.cell(row=row_num, column=5).value = cours.get_semestre_display()
        ws.cell(row=row_num, column=6).value = float(cours.nbr_heure)
        ws.cell(row=row_num, column=7).value = float(heures_faites or 0)
        ws.cell(row=row_num, column=8).value = cours.date_debut_estimee.strftime('%d/%m/%Y') if cours.date_debut_estimee else 'N/A'
        ws.cell(row=row_num, column=9).value = cours.date_fin_estimee.strftime('%d/%m/%Y') if cours.date_fin_estimee else 'N/A'
        
        for col in range(1, 10):
            ws.cell(row=row_num, column=col).border = styles['border']
    
    # Ajuster les largeurs
    for col in range(1, 10):
        ws.column_dimensions[get_column_letter(col)].width = 18
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"Cours_Programmes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    wb.save(response)
    return response


def export_cours_to_pdf(cours_list):
    """Exporte la liste des cours programmés vers PDF."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []
    
    styles, font_name = setup_pdf_styles()
    
    title = Paragraph(f"Cours Programmés - {datetime.now().strftime('%d/%m/%Y')}", styles['CustomTitle'])
    elements.append(title)
    elements.append(Spacer(1, 0.5*cm))
    
    data = [['Matière', 'Filière', 'Niveau', 'Professeur', 'Sem.', 'Vol. H', 'H. Faites']]
    
    for cours in cours_list:
        heures_faites = cours.total_heures_faites if hasattr(cours, 'total_heures_faites') else 0
        
        data.append([
            cours.matiere.libelle[:20],
            cours.filiere.code,
            f"{cours.niveau.libelle} {cours.niveau.niv}",
            str(cours.professeur)[:20],
            cours.get_semestre_display(),
            f"{float(cours.nbr_heure)}h",
            f"{float(heures_faites or 0)}h"
        ])
    
    table = Table(data, colWidths=[4*cm, 2*cm, 2.5*cm, 4*cm, 2*cm, 2*cm, 2*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F59E0B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"Cours_Programmes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response


# ======================== EXPORT ÉMARGEMENTS ========================

def export_emargements_to_excel(emargements_list):
    """Exporte la liste des émargements vers Excel."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Émargements"
    
    styles = get_excel_styles()
    
    headers = ['Date', 'Matière', 'Professeur', 'Filière', 'Niveau', 'Semestre', 'Heures Effectuées']
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.fill = styles['header_fill']
        cell.font = styles['header_font']
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = styles['border']
    
    for row_num, emarg in enumerate(emargements_list, 2):
        ws.cell(row=row_num, column=1).value = emarg.date_emar.strftime('%d/%m/%Y')
        ws.cell(row=row_num, column=2).value = emarg.matiere_programmer.matiere.libelle
        ws.cell(row=row_num, column=3).value = str(emarg.matiere_programmer.professeur)
        ws.cell(row=row_num, column=4).value = emarg.matiere_programmer.filiere.code
        ws.cell(row=row_num, column=5).value = f"{emarg.matiere_programmer.niveau.libelle} {emarg.matiere_programmer.niveau.niv}"
        ws.cell(row=row_num, column=6).value = emarg.matiere_programmer.get_semestre_display()
        ws.cell(row=row_num, column=7).value = float(emarg.heure_eff)
        
        for col in range(1, 8):
            ws.cell(row=row_num, column=col).border = styles['border']
    
    for col in range(1, 8):
        ws.column_dimensions[get_column_letter(col)].width = 18
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"Emargements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    wb.save(response)
    return response


def export_emargements_to_pdf(emargements_list):
    """Exporte la liste des émargements vers PDF."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []
    
    styles, font_name = setup_pdf_styles()
    
    title = Paragraph(f"Émargements - {datetime.now().strftime('%d/%m/%Y')}", styles['CustomTitle'])
    elements.append(title)
    elements.append(Spacer(1, 0.5*cm))
    
    data = [['Date', 'Matière', 'Professeur', 'Filière', 'Niveau', 'Sem.', 'Heures']]
    
    for emarg in emargements_list:
        data.append([
            emarg.date_emar.strftime('%d/%m/%Y'),
            emarg.matiere_programmer.matiere.libelle[:20],
            str(emarg.matiere_programmer.professeur)[:20],
            emarg.matiere_programmer.filiere.code,
            f"{emarg.matiere_programmer.niveau.libelle} {emarg.matiere_programmer.niveau.niv}",
            emarg.matiere_programmer.get_semestre_display(),
            f"{float(emarg.heure_eff)}h"
        ])
    
    table = Table(data, colWidths=[2.5*cm, 4*cm, 4*cm, 2*cm, 2.5*cm, 2*cm, 2*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F59E0B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"Emargements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response


# ======================== EXPORT ÉVALUATIONS ========================

def export_evaluations_to_excel(evaluations_list):
    """Exporte la liste des évaluations vers Excel."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Évaluations"
    
    styles = get_excel_styles()
    
    headers = ['Matière', 'Professeur', 'Filière', 'Niveau', 'Semestre', 'Évalué par', 'Résumé Évaluation']
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.fill = styles['header_fill']
        cell.font = styles['header_font']
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = styles['border']
    
    for row_num, eval in enumerate(evaluations_list, 2):
        ws.cell(row=row_num, column=1).value = eval.matiere_programmer.matiere.libelle
        ws.cell(row=row_num, column=2).value = str(eval.matiere_programmer.professeur)
        ws.cell(row=row_num, column=3).value = eval.matiere_programmer.filiere.code
        ws.cell(row=row_num, column=4).value = f"{eval.matiere_programmer.niveau.libelle} {eval.matiere_programmer.niveau.niv}"
        ws.cell(row=row_num, column=5).value = eval.matiere_programmer.get_semestre_display()
        ws.cell(row=row_num, column=6).value = eval.utilisateur_evaluation.username if eval.utilisateur_evaluation else 'N/A'
        ws.cell(row=row_num, column=7).value = eval.resume_evaluation[:100] + '...' if len(eval.resume_evaluation) > 100 else eval.resume_evaluation
        
        for col in range(1, 8):
            ws.cell(row=row_num, column=col).border = styles['border']
    
    for col in range(1, 8):
        ws.column_dimensions[get_column_letter(col)].width = 20
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"Evaluations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    wb.save(response)
    return response


def export_evaluations_to_pdf(evaluations_list):
    """Exporte la liste des évaluations vers PDF."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []
    
    styles, font_name = setup_pdf_styles()
    
    title = Paragraph(f"Évaluations Qualitatives - {datetime.now().strftime('%d/%m/%Y')}", styles['CustomTitle'])
    elements.append(title)
    elements.append(Spacer(1, 0.5*cm))
    
    data = [['Matière', 'Professeur', 'Filière', 'Niveau', 'Sem.', 'Évalué par']]
    
    for eval in evaluations_list:
        data.append([
            eval.matiere_programmer.matiere.libelle[:25],
            str(eval.matiere_programmer.professeur)[:20],
            eval.matiere_programmer.filiere.code,
            f"{eval.matiere_programmer.niveau.libelle} {eval.matiere_programmer.niveau.niv}",
            eval.matiere_programmer.get_semestre_display(),
            eval.utilisateur_evaluation.username if eval.utilisateur_evaluation else 'N/A'
        ])
    
    table = Table(data, colWidths=[5*cm, 4*cm, 2*cm, 3*cm, 2*cm, 3*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F59E0B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"Evaluations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response