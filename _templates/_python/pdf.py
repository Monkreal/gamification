from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image, Spacer
from PIL import Image as PILImage
from reportlab.lib import colors

def on_all_pages(canvas, doc):
    custom_text = getattr(doc, 'custom_text', '')
    
    width = 50
    image_path = "_static/Pictures/favicon.png"
    
    with PILImage.open(image_path) as img:
        original_width, original_height = img.size
        scale_factor = width / original_width
        new_height = int(original_height * scale_factor)
        
    lwidth, height = letter

    canvas.drawImage(image_path, lwidth - 70, 20, width=width, height=new_height)
    
    canvas.setFont("Helvetica", 10)
    canvas.setFillColor(colors.black)
    canvas.drawString(45, 45, custom_text)

def create_pdf(urls, gamename, players):
    pdf_filename = "_static/PDF/output.pdf"

    pdf = SimpleDocTemplate(pdf_filename, pagesize=letter, topMargin=60, bottomMargin=0, 
                            leftMargin=60, rightMargin=60)
    width, height = letter
    width = width - 100
    elements = []
    
    for url in urls:
        image_path = url
    
        with PILImage.open(image_path) as img:
            original_width, original_height = img.size
            scale_factor = width / original_width
            new_height = original_height * scale_factor
    
        chart = Image(image_path, width=width, height=new_height)
        chart.hAlign = 'CENTER'
        elements.append(chart)
        elements.append(Spacer(1, 30))
    
    count = 0
        
    for player in players:
        if player.participant.vars.get('checked', False):
            count += 1
        
    pdf.custom_text = str(gamename) + ', es haben ' + str(count) + ' Spieler teilgenommen'
    
    pdf.build(elements, onFirstPage=on_all_pages, onLaterPages=on_all_pages)