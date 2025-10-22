"""
F24 PDF generation utilities for IMU payments
"""
import os
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import logging

logger = logging.getLogger(__name__)

class F24Generator:
    """Generator for F24 payment forms"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for F24 document"""
        self.styles.add(ParagraphStyle(
            name='F24Title',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.black
        ))
        
        self.styles.add(ParagraphStyle(
            name='F24Section',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=10,
            alignment=TA_LEFT,
            textColor=colors.black
        ))
        
        self.styles.add(ParagraphStyle(
            name='F24Normal',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT
        ))
        
        self.styles.add(ParagraphStyle(
            name='F24Small',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_LEFT,
            textColor=colors.grey
        ))
    
    def generate_imu_f24(
        self,
        taxpayer_data: Dict[str, Any],
        property_data: Dict[str, Any],
        imu_calculation: Dict[str, Any],
        payment_type: str = "primo",  # "primo" or "secondo"
        output_path: Optional[str] = None
    ) -> str:
        """Generate F24 form for IMU payment"""
        try:
            # Create output directory if it doesn't exist
            if not output_path:
                output_dir = "static/f24"
                os.makedirs(output_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"{output_dir}/F24_IMU_{payment_type}_{timestamp}.pdf"
            
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )
            
            # Build document content
            story = []
            
            # Title
            story.append(Paragraph("MODELLO F24 - PAGAMENTO IMU", self.styles['F24Title']))
            story.append(Spacer(1, 12))
            
            # Payment type section
            payment_desc = "PRIMO ACCONTO" if payment_type == "primo" else "SECONDO ACCONTO/SALDO"
            story.append(Paragraph(f"<b>{payment_desc} IMU {datetime.now().year}</b>", self.styles['F24Section']))
            story.append(Spacer(1, 12))
            
            # Taxpayer information
            story.append(Paragraph("DATI DEL CONTRIBUENTE", self.styles['F24Section']))
            taxpayer_table = self._create_taxpayer_table(taxpayer_data)
            story.append(taxpayer_table)
            story.append(Spacer(1, 12))
            
            # Property information
            story.append(Paragraph("DATI DELL'IMMOBILE", self.styles['F24Section']))
            property_table = self._create_property_table(property_data)
            story.append(property_table)
            story.append(Spacer(1, 12))
            
            # Payment calculation
            story.append(Paragraph("CALCOLO DELL'IMPOSTA", self.styles['F24Section']))
            calculation_table = self._create_calculation_table(imu_calculation, payment_type)
            story.append(calculation_table)
            story.append(Spacer(1, 12))
            
            # Payment details
            story.append(Paragraph("SEZIONE ERARIO", self.styles['F24Section']))
            payment_table = self._create_payment_table(imu_calculation, payment_type)
            story.append(payment_table)
            story.append(Spacer(1, 20))
            
            # Instructions
            story.append(Paragraph("ISTRUZIONI PER IL PAGAMENTO", self.styles['F24Section']))
            instructions = self._create_instructions()
            story.append(instructions)
            
            # Footer
            story.append(Spacer(1, 20))
            story.append(Paragraph(
                f"Documento generato automaticamente da Casa&Più il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}",
                self.styles['F24Small']
            ))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"F24 generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating F24: {str(e)}")
            raise
    
    def _create_taxpayer_table(self, taxpayer_data: Dict[str, Any]) -> Table:
        """Create taxpayer information table"""
        data = [
            ["Codice Fiscale:", taxpayer_data.get("codice_fiscale", "")],
            ["Cognome e Nome:", taxpayer_data.get("nome_completo", "")],
            ["Indirizzo:", taxpayer_data.get("indirizzo", "")],
            ["Comune:", taxpayer_data.get("comune", "")],
            ["CAP:", taxpayer_data.get("cap", "")],
            ["Provincia:", taxpayer_data.get("provincia", "")]
        ]
        
        table = Table(data, colWidths=[40*mm, 120*mm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey)
        ]))
        
        return table
    
    def _create_property_table(self, property_data: Dict[str, Any]) -> Table:
        """Create property information table"""
        data = [
            ["Indirizzo:", property_data.get("indirizzo", "")],
            ["Comune:", property_data.get("comune", "")],
            ["Categoria Catastale:", property_data.get("categoria_catastale", "")],
            ["Rendita Catastale:", f"€ {property_data.get('rendita', 0):.2f}"],
            ["Quota di possesso:", property_data.get("quota", "100%")]
        ]
        
        table = Table(data, colWidths=[50*mm, 110*mm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey)
        ]))
        
        return table
    
    def _create_calculation_table(self, imu_calculation: Dict[str, Any], payment_type: str) -> Table:
        """Create calculation details table"""
        amount = imu_calculation.get(f"{payment_type}_acconto", Decimal("0"))
        
        data = [
            ["Base Imponibile:", f"€ {imu_calculation.get('base_imponibile', 0):.2f}"],
            ["Aliquota:", f"{imu_calculation.get('aliquota', 0):.2f}%"],
            ["Imposta Lorda:", f"€ {imu_calculation.get('imu_lordo', 0):.2f}"],
            ["Detrazione:", f"€ {imu_calculation.get('detrazione', 0):.2f}"],
            ["Imposta Netta Annua:", f"€ {imu_calculation.get('imu_netto', 0):.2f}"],
            [f"Importo {payment_type.capitalize()} Acconto:", f"€ {amount:.2f}"]
        ]
        
        table = Table(data, colWidths=[70*mm, 90*mm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (-1, -1), (-1, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (-1, -1), (-1, -1), colors.yellow)
        ]))
        
        return table
    
    def _create_payment_table(self, imu_calculation: Dict[str, Any], payment_type: str) -> Table:
        """Create payment section table"""
        amount = imu_calculation.get(f"{payment_type}_acconto", Decimal("0"))
        scadenza = "16/06" if payment_type == "primo" else "16/12"
        
        data = [
            ["Codice Tributo", "Rateazione", "Anno di Riferimento", "Importi a Debito", "Importi a Credito"],
            ["3944", "", str(datetime.now().year), f"€ {amount:.2f}", ""],
            ["", "", "", "", ""],
            ["Totale", "", "", f"€ {amount:.2f}", "€ 0,00"]
        ]
        
        table = Table(data, colWidths=[30*mm, 30*mm, 40*mm, 40*mm, 40*mm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey)
        ]))
        
        return table
    
    def _create_instructions(self) -> Paragraph:
        """Create payment instructions"""
        instructions_text = """
        <b>ISTRUZIONI:</b><br/>
        1. Compilare tutti i campi richiesti<br/>
        2. Il codice tributo per l'IMU è 3944<br/>
        3. Il pagamento deve essere effettuato entro il 16 giugno (primo acconto) o 16 dicembre (secondo acconto/saldo)<br/>
        4. È possibile pagare presso banche, poste, tabaccherie abilitate o online<br/>
        5. Conservare la ricevuta di pagamento<br/>
        6. Per informazioni consultare il sito del comune di riferimento
        """
        
        return Paragraph(instructions_text, self.styles['F24Normal'])

def generate_f24_for_asset(
    asset_data: Dict[str, Any],
    user_data: Dict[str, Any],
    payment_type: str = "primo"
) -> str:
    """Convenience function to generate F24 for an asset"""
    try:
        from utils.imu_calc import IMUCalculator
        
        # Calculate IMU
        calculator = IMUCalculator()
        imu_result = calculator.calculate_imu_for_property(asset_data["details_json"])
        
        # Generate F24
        generator = F24Generator()
        f24_path = generator.generate_imu_f24(
            taxpayer_data=user_data,
            property_data=asset_data["details_json"],
            imu_calculation=imu_result,
            payment_type=payment_type
        )
        
        return f24_path
        
    except Exception as e:
        logger.error(f"Error generating F24 for asset: {str(e)}")
        raise