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
    """
    Retourne les styles communs pour Excel.
    MISES À JOUR: Ajout de 'header_alignment'.
    """
    header_fill = PatternFill(start_color="F59E0B", end_color="F59E0B", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_alignment = Alignment(horizontal='center', vertical='center')
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    return {
        'header_fill': header_fill,
        'header_font': header_font,
        'header_alignment': header_alignment,
        'border': border
    }


def setup_pdf_styles():
    """Configure les styles pour les PDF (incluant la police pour les accents)."""
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
        cell.alignment = styles['header_alignment'] # Mise à jour
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
        ('FONTNAME', (0, 1), (-1, -1), font_name),
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
        cell.alignment = styles['header_alignment'] # Mise à jour
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
        ('FONTNAME', (0, 1), (-1, -1), font_name),
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
        cell.alignment = styles['header_alignment'] # Mise à jour
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
        ('FONTNAME', (0, 1), (-1, -1), font_name),
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"Emargements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response


# ======================== EXPORTS ÉVALUATIONS (CORRIGÉ) ========================

def export_evaluations_to_excel(queryset):
    """
    Exporte les évaluations vers Excel.
    CORRECTION: Utilisation des noms de champs du modèle : resume_ap et recommandation
    """
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="Evaluations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'

    wb = Workbook()
    ws = wb.active
    ws.title = "Évaluations"

    styles = get_excel_styles() 

    # En-têtes 
    headers = [
        'Cours', 
        'Code', 
        'Professeur', 
        'Niveau', 
        'Filière',
        'Résumé de l\'Évaluation',
        'Appréciation AP', # Le libellé reste le même pour l'utilisateur
        'Recommandations',  # Le libellé reste le même pour l'utilisateur
        'Évalué par'
    ]
    
    ws.append(headers)
    
    # Styling en-têtes
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.font = styles['header_font']
        cell.fill = styles['header_fill']
        cell.alignment = styles['header_alignment'] 
        cell.border = styles['border']

    # Données (Utilisation des champs réels du modèle : resume_ap et recommandation)
    for eval_obj in queryset:
        ws.append([
            eval_obj.matiere_programmer.matiere.libelle,
            eval_obj.matiere_programmer.matiere.code,
            str(eval_obj.matiere_programmer.professeur),
            f"{eval_obj.matiere_programmer.niveau.libelle} {eval_obj.matiere_programmer.niveau.niv}", 
            eval_obj.matiere_programmer.filiere.code, 
            eval_obj.resume_evaluation or 'Non renseigné',
            # CORRIGÉ : utilise resume_ap au lieu de appreciation_ap
            eval_obj.resume_ap or 'Non renseigné',
            # CORRIGÉ : utilise recommandation (singulier) au lieu de recommandations
            eval_obj.recommandation or 'Non renseigné',
            eval_obj.utilisateur_evaluation.get_full_name() if eval_obj.utilisateur_evaluation and hasattr(eval_obj.utilisateur_evaluation, 'get_full_name') else (eval_obj.utilisateur_evaluation.username if eval_obj.utilisateur_evaluation else 'Système')
        ])

    # Ajustement des largeurs
    column_widths = [30, 15, 25, 20, 20, 40, 40, 40, 25]
    for i, width in enumerate(column_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = width

    # Styling des données (Wrap Text)
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        for cell in row:
            cell.border = styles['border']
            cell.alignment = Alignment(wrapText=True, vertical='top')

    wb.save(response)
    return response


def export_evaluations_to_pdf(queryset):
    """
    Exporte les évaluations vers PDF.
    CORRECTION: Utilisation des noms de champs du modèle : resume_ap et recommandation
    """
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Evaluations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'

    # Format paysage pour accommoder les 3 colonnes
    doc = SimpleDocTemplate(
        response, 
        pagesize=landscape(A4),
        rightMargin=1*cm, 
        leftMargin=1*cm,
        topMargin=2*cm, 
        bottomMargin=2*cm
    )

    elements = []
    
    # Utiliser les styles configurés (avec gestion de la police)
    styles, font_name = setup_pdf_styles()
    
    # Titre (utilise le style CustomTitle défini dans setup_pdf_styles)
    title_style = styles['CustomTitle']
    elements.append(Paragraph("Liste des Évaluations Qualitatives", title_style))
    elements.append(Spacer(1, 0.5*cm))

    # Info génération (doit utiliser la bonne police)
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=1,
        fontName=font_name 
    )
    elements.append(Paragraph(
        f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        date_style
    ))
    elements.append(Spacer(1, 0.5*cm))

    # Données du tableau (CORRECTION: 3 colonnes d'évaluation)
    data = [['Cours', 'Professeur', 'Résumé\nÉvaluation', 'Appréciation\nAP', 'Recommandations', 'Évalué par']]
    
    # Définir un style 'TableNormal' pour les cellules de données (avec gestion de la police)
    table_normal_style = ParagraphStyle(
        'TableNormal',
        parent=styles['Normal'],
        fontSize=7,
        fontName=font_name, 
        alignment=0, # LEFT
        leading=8,
    )

    for eval_obj in queryset:
        # Tronquer les textes longs pour le PDF
        resume = eval_obj.resume_evaluation[:100] + '...' if eval_obj.resume_evaluation and len(eval_obj.resume_evaluation) > 100 else (eval_obj.resume_evaluation or 'N/A')
        
        # CORRIGÉ : utilise resume_ap au lieu de appreciation_ap
        appreciation = eval_obj.resume_ap[:100] + '...' if eval_obj.resume_ap and len(eval_obj.resume_ap) > 100 else (eval_obj.resume_ap or 'N/A')
        
        # CORRIGÉ : utilise recommandation (singulier)
        recommandations_txt = eval_obj.recommandation[:100] + '...' if eval_obj.recommandation and len(eval_obj.recommandation) > 100 else (eval_obj.recommandation or 'N/A')
        
        # Gestion du nom de l'évaluateur
        eval_par = eval_obj.utilisateur_evaluation.get_full_name() if eval_obj.utilisateur_evaluation and hasattr(eval_obj.utilisateur_evaluation, 'get_full_name') else (eval_obj.utilisateur_evaluation.username if eval_obj.utilisateur_evaluation else 'Système')

        data.append([
            Paragraph(eval_obj.matiere_programmer.matiere.libelle, table_normal_style),
            Paragraph(str(eval_obj.matiere_programmer.professeur), table_normal_style),
            Paragraph(resume, table_normal_style),
            Paragraph(appreciation, table_normal_style),
            Paragraph(recommandations_txt, table_normal_style), # Utilise la variable corrigée
            Paragraph(eval_par, table_normal_style)
        ])

    # Création du tableau avec largeurs ajustées
    col_widths = [4.5*cm, 3.5*cm, 5*cm, 5*cm, 5*cm, 3*cm] 
    table = Table(data, colWidths=col_widths)
    
    table.setStyle(TableStyle([
        # En-tête
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F59E0B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), font_name if font_name != 'Helvetica' else 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Données
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),
        
        # Bordures et couleurs d'alternance
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FEF3C7')]),
    ]))

    elements.append(table)
    
    # Note de bas de page
    elements.append(Spacer(1, 0.5*cm))
    note_style = ParagraphStyle(
        'NoteStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=0,
        fontName=font_name
    )
    elements.append(Paragraph(
        "<b>Note :</b> Les textes longs sont tronqués dans ce PDF. Pour voir le contenu complet, consultez l'interface web ou exportez en Excel.",
        note_style
    ))

    doc.build(elements)
    return response